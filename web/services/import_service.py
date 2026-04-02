"""Import service — import Excel files with validation, duplicate checking, smart merge."""

import openpyxl
from services.customer_service import normalize_sdt, extract_all_phones, INPUT_COLUMNS
from services.scoring_service import compute_scores
from services.log_service import add_log
from services.gemini_service import score_with_ai, FIELD_TO_CRITERIA
from database.db import get_db

# Mapping Excel header → DB column
HEADER_MAP = {
    'Loại KH': 'loai_kh',
    'Tên Công Ty/Đơn Vị': 'ten_cong_ty',
    'Họ Tên Chủ': 'ho_ten',
    'SĐT': 'sdt',
    'Tỉnh': 'tinh',
    'Xã': 'xa',
    'Địa Chỉ': 'dia_chi',
    'Nguồn': 'nguon',
    'Thông Tin Chi Tiết': 'thong_tin_chi_tiet',
    'Khu vực': 'khu_vuc',
    'Số KH quay lại/năm': 'so_kh_quay_lai',
    'Biết lợi nhuận từng đơn?': 'biet_loi_nhuan',
    'Đội thợ thi công': 'doi_tho',
    'Chính sách BH với khách': 'chinh_sach_bh',
    'Mức quan tâm hợp tác': 'muc_quan_tam',
    'Bán kính KH gọi đến (km)': 'ban_kinh_km',
    'Cách quản lý data KH': 'quan_ly_data',
    'Kiểm soát mua hàng': 'kiem_soat_mua_hang',
    'Số người được giới thiệu': 'so_nguoi_gioi_thieu',
}


def parse_excel(filepath):
    """Parse Excel file into list of dicts. Returns (rows, errors)."""
    wb = openpyxl.load_workbook(filepath, data_only=True)
    ws = wb.active
    all_rows = list(ws.iter_rows(values_only=True))
    wb.close()

    if not all_rows:
        return [], ['File rỗng']

    # Find header row (first row with recognizable headers)
    header_row_idx = None
    headers = None
    for idx, row in enumerate(all_rows):
        row_strs = [str(c).strip() if c else '' for c in row]
        matches = sum(1 for h in row_strs if h in HEADER_MAP)
        if matches >= 3:  # at least 3 recognized headers
            header_row_idx = idx
            headers = row_strs
            break

    if header_row_idx is None:
        return [], ['Không tìm thấy header hợp lệ. Cần ít nhất: Loại KH, Họ Tên Chủ, SĐT']

    # Map header positions
    col_map = {}
    for col_idx, header in enumerate(headers):
        if header in HEADER_MAP:
            col_map[col_idx] = HEADER_MAP[header]

    # Parse data rows
    parsed = []
    errors = []
    for row_idx, row in enumerate(all_rows[header_row_idx + 1:], start=header_row_idx + 2):
        # Skip empty rows
        if not any(cell is not None and str(cell).strip() for cell in row):
            continue

        record = {}
        for col_idx, db_col in col_map.items():
            if col_idx < len(row):
                val = row[col_idx]
                if val is not None:
                    record[db_col] = str(val).strip() if not isinstance(val, (int, float)) else val
                else:
                    record[db_col] = None

        # Normalize SĐT
        if 'sdt' in record and record['sdt']:
            record['sdt'] = normalize_sdt(record['sdt'])

        # Convert number fields
        for field in ['so_kh_quay_lai', 'ban_kinh_km', 'so_nguoi_gioi_thieu']:
            if field in record and record[field] is not None:
                try:
                    record[field] = int(float(str(record[field])))
                except (ValueError, TypeError):
                    record[field] = None

        # Must have phone number (tên để trống cũng được)
        if not record.get('sdt'):
            continue

        record['_row'] = row_idx
        parsed.append(record)

    return parsed, errors


def check_duplicates(rows):
    """Check each row for duplicates in existing DB. Returns list of (row, duplicates)."""
    conn = get_db()
    results = []
    for row in rows:
        sdt = row.get('sdt', '')
        if not sdt:
            results.append((row, []))
            continue

        phones = extract_all_phones(sdt)
        dupes = []
        for phone in phones:
            if phone and len(phone) >= 8:
                existing = conn.execute(
                    "SELECT * FROM customers WHERE is_deleted = 0 AND sdt LIKE ?",
                    (f'%{phone}%',)
                ).fetchall()
                dupes.extend([dict(r) for r in existing])

        # Deduplicate
        seen = set()
        unique_dupes = []
        for d in dupes:
            if d['id'] not in seen:
                seen.add(d['id'])
                unique_dupes.append(d)

        results.append((row, unique_dupes))

    conn.close()
    return results


def _auto_ai_score(conn, customer_id):
    """Auto-score all 'Khác' fields for a customer using Gemini AI.
    
    Called automatically during import when review_status = 'needs_review'.
    Silently skips if API key is missing or API fails.
    """
    row = conn.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
    if not row:
        return
    
    cust = dict(row)
    if cust.get('review_status') != 'needs_review':
        return
    
    text = cust.get('thong_tin_chi_tiet') or ''
    any_scored = False
    
    for field_name, criteria in FIELD_TO_CRITERIA.items():
        if cust.get(field_name) == 'Khác':
            # Call AI to score this field
            score, explanation = score_with_ai(field_name, text) if text else (None, 'Không có TTCT')
            if score is not None:
                conn.execute(
                    f"UPDATE customers SET {criteria} = ? WHERE id = ?",
                    (score, customer_id)
                )
                any_scored = True
                add_log('AI chấm điểm (auto)',
                        f'{criteria}: {score}đ — {explanation}',
                        customer_id, cust.get('ten_cong_ty') or cust.get('ho_ten') or '')
    
    if any_scored:
        # Recalculate c_score and tier
        updated_row = conn.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
        scores = compute_scores(dict(updated_row))
        conn.execute(
            """UPDATE customers SET c_score = ?, tier = ?, review_status = 'ok',
               updated_at = CURRENT_TIMESTAMP WHERE id = ?""",
            (scores['c_score'], scores['tier'], customer_id)
        )


def import_rows(rows, merge_strategy='smart', operator='Dương'):
    """Import rows into DB.

    merge_strategy:
      - 'smart': new data overwrites old only where non-empty, keep old where new is empty
      - 'skip': skip duplicates
      - 'overwrite': fully overwrite duplicates

    Returns (inserted, updated, skipped).
    """
    conn = get_db()
    inserted = 0
    updated = 0
    skipped = 0
    ai_scored = 0
    ai_records = []  # collect IDs for AI scoring after commit

    # Load standard group labels from DB
    nhom_labels_rows = conn.execute('SELECT key, label FROM nhom_kh_groups ORDER BY display_order').fetchall()
    STANDARD_GROUPS = set(r['label'] for r in nhom_labels_rows)

    for row in rows:
        # Remove internal fields
        data = {k: v for k, v in row.items() if not k.startswith('_')}

        # loai_kh_goc = raw Excel value (always preserved)
        data['loai_kh_goc'] = data.get('loai_kh', '') or ''

        # Check for duplicate
        sdt = data.get('sdt', '')
        duplicate = None
        if sdt:
            phones = extract_all_phones(sdt)
            for phone in phones:
                if phone and len(phone) >= 8:  # PREVENT bug: '0' matching everything
                    existing = conn.execute(
                        "SELECT * FROM customers WHERE is_deleted = 0 AND sdt LIKE ?",
                        (f'%{phone}%',)
                    ).fetchone()
                    if existing:
                        duplicate = dict(existing)
                        break

        if duplicate:
            if merge_strategy == 'skip':
                skipped += 1
                continue
            elif merge_strategy == 'smart':
                # Smart merge: new overwrites only where non-empty
                merged = dict(duplicate)
                changes = []
                for key in INPUT_COLUMNS:
                    new_val = data.get(key)
                    old_val = merged.get(key)
                    # PROTECT loai_kh if already classified to a standard group
                    if key == 'loai_kh' and str(old_val or '') in STANDARD_GROUPS:
                        continue
                    if new_val is not None and str(new_val).strip() != '':
                        if str(new_val) != str(old_val or ''):
                            changes.append(f"{key}: '{old_val}' → '{new_val}'")
                        merged[key] = new_val

                if changes:
                    scores = compute_scores(merged)
                    merged.update(scores)

                    set_parts = []
                    values = []
                    for col in INPUT_COLUMNS + ['c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7',
                                                 'c8', 'c9', 'c_score', 'tier', 'review_status']:
                        if col in merged:
                            set_parts.append(f"{col} = ?")
                            values.append(merged[col])
                    set_parts.append("updated_at = CURRENT_TIMESTAMP")
                    values.append(duplicate['id'])

                    conn.execute(
                        f"UPDATE customers SET {', '.join(set_parts)} WHERE id = ?",
                        values
                    )
                    if scores.get('review_status') == 'needs_review':
                        ai_records.append(duplicate['id'])
                    updated += 1
                else:
                    skipped += 1
            else:  # overwrite
                scores = compute_scores(data)
                data.update(scores)
                set_parts = []
                values = []
                for col in INPUT_COLUMNS + ['c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7',
                                             'c8', 'c9', 'c_score', 'tier', 'review_status']:
                    if col in data:
                        set_parts.append(f"{col} = ?")
                        values.append(data[col])
                set_parts.append("updated_at = CURRENT_TIMESTAMP")
                values.append(duplicate['id'])
                conn.execute(
                    f"UPDATE customers SET {', '.join(set_parts)} WHERE id = ?",
                    values
                )
                if data.get('review_status') == 'needs_review':
                    ai_records.append(duplicate['id'])
                updated += 1
        else:
            # Insert new
            scores = compute_scores(data)
            data.update(scores)

            columns = [c for c in INPUT_COLUMNS + ['c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7',
                                                    'c8', 'c9', 'c_score', 'tier', 'review_status']
                       if c in data]
            
            # Khắc phục triệt để lỗi is_deleted=NULL để check trùng xử lý được ngay trong cùng 1 vòng lặp
            columns.append('is_deleted')
            
            placeholders = ', '.join(['?'] * len(columns))
            values = [data.get(c) for c in columns[:-1]] + [0] # 0 for is_deleted

            cursor = conn.execute(
                f"INSERT INTO customers ({', '.join(columns)}) VALUES ({placeholders})",
                values
            )
            inserted_id = cursor.lastrowid
            conn.execute("UPDATE customers SET ma_kh = printf('KH-%05d', ?) WHERE id = ?", (inserted_id, inserted_id))
            if scores.get('review_status') == 'needs_review':
                ai_records.append(inserted_id)
            inserted += 1

    conn.commit()

    # Auto AI scoring for records with 'Khác' fields
    for cid in ai_records:
        try:
            _auto_ai_score(conn, cid)
            conn.commit()
            ai_scored += 1
        except Exception:
            pass  # Don't break import if AI fails

    conn.close()

    ai_note = f', {ai_scored} AI chấm điểm' if ai_scored else ''
    add_log('Import', f"Import: {inserted} thêm mới, {updated} cập nhật, {skipped} bỏ qua{ai_note}",
            operator=operator)

    return inserted, updated, skipped
