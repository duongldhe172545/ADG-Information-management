"""Customer service — CRUD operations for customers."""

from database.db import get_db, dict_from_row, dicts_from_rows
from services.scoring_service import compute_scores
from services.log_service import add_log

# 19 input columns from Excel
INPUT_COLUMNS = [
    'loai_kh', 'loai_kh_goc', 'ten_cong_ty', 'ho_ten', 'sdt', 'tinh', 'xa',
    'dia_chi', 'nguon', 'thong_tin_chi_tiet', 'khu_vuc',
    'so_kh_quay_lai', 'biet_loi_nhuan', 'doi_tho', 'chinh_sach_bh',
    'muc_quan_tam', 'ban_kinh_km', 'quan_ly_data', 'kiem_soat_mua_hang',
    'so_nguoi_gioi_thieu'
]

SCORE_COLUMNS = ['c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9',
                 'c_score', 'tier', 'review_status']

ALL_COLUMNS = INPUT_COLUMNS + SCORE_COLUMNS


import re
import unicodedata

def normalize_sdt(sdt):
    """Normalize phone number: handle Excel artifacts, multi-number, etc."""
    if not sdt:
        return ''
    sdt = str(sdt).strip()

    # Remove Excel artifacts
    sdt = sdt.replace('_x000D_', '')       # carriage return artifact
    sdt = sdt.replace('\r', '').replace('\n', '')  # actual CR/LF

    # Remove invisible Unicode characters (LTR/RTL marks, zero-width, etc.)
    sdt = re.sub(r'[\u200e\u200f\u200b\u200c\u200d\u202a-\u202e\u2066-\u2069\ufeff]', '', sdt)
    # Remove any non-printable chars
    sdt = ''.join(c for c in sdt if unicodedata.category(c)[0] != 'C')

    # Remove leading apostrophe (Excel text prefix)
    sdt = sdt.lstrip("'")

    # Normalize separators: replace comma, apostrophe mid-string, semicolon → /
    sdt = re.sub(r"[,;']", '/', sdt)

    # Split by /
    parts = [p.strip() for p in sdt.split('/') if p.strip()]

    normalized = []
    for p in parts:
        # Remove dots, spaces, dashes
        p = p.replace('.', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if not p:
            continue
        # If too long (20 digits = likely 2 concatenated 10-digit numbers)
        if len(p) >= 18 and p.isdigit():
            # Try to split into 10-digit chunks
            chunks = []
            while len(p) >= 10:
                chunks.append(p[:10])
                p = p[10:]
            if p:
                chunks.append(p)
            for chunk in chunks:
                if not chunk.startswith('0') and len(chunk) == 9:
                    chunk = '0' + chunk
                normalized.append(chunk)
        else:
            if not p.startswith('0') and len(p) == 9 and p.isdigit():
                p = '0' + p
            normalized.append(p)

    return '/'.join(normalized)


def extract_all_phones(sdt_str):
    """Extract all phone numbers from a string like '0985586425/0365663966'."""
    if not sdt_str:
        return []
    return [p.strip() for p in sdt_str.split('/') if p.strip()]


def list_customers(search=None, search_col=None, filters=None, page=1, per_page=50, include_deleted=False):
    """List customers with search, filter, pagination."""
    conn = get_db()
    query = "SELECT * FROM customers WHERE 1=1"
    params = []

    if not include_deleted:
        query += " AND is_deleted = 0"
    else:
        query += " AND is_deleted = 1"

    if search:
        s = f'%{search}%'
        searchable = ['ma_kh', 'ho_ten', 'sdt', 'ten_cong_ty', 'tinh', 'xa', 'dia_chi', 'loai_kh', 'nguon', 'khu_vuc']
        if search_col and search_col in searchable:
            query += f" AND {search_col} LIKE ?"
            params.append(s)
        else:
            query += " AND (ma_kh LIKE ? OR ho_ten LIKE ? OR sdt LIKE ? OR ten_cong_ty LIKE ? OR tinh LIKE ?)"
            params.extend([s, s, s, s, s])

    if filters:
        for key, value in filters.items():
            if value and key in ALL_COLUMNS:
                query += f" AND {key} = ?"
                params.append(value)

    # Count
    count_query = query.replace("SELECT *", "SELECT COUNT(*)")
    total = conn.execute(count_query, params).fetchone()[0]

    # Paginate
    query += " ORDER BY id ASC LIMIT ? OFFSET ?"
    params.extend([per_page, (page - 1) * per_page])

    rows = conn.execute(query, params).fetchall()
    conn.close()

    return {
        'customers': dicts_from_rows(rows),
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': max(1, (total + per_page - 1) // per_page)
    }


def get_customer(customer_id):
    """Get a single customer by ID."""
    conn = get_db()
    row = conn.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
    conn.close()
    return dict_from_row(row)


def create_customer(data, operator='Dương'):
    """Create a new customer, auto-score, log it."""
    data['sdt'] = normalize_sdt(data.get('sdt', ''))

    # Compute scores
    scores = compute_scores(data)
    data.update(scores)

    columns = [c for c in INPUT_COLUMNS + SCORE_COLUMNS if c in data]
    placeholders = ', '.join(['?'] * len(columns))
    values = [data.get(c) for c in columns]

    conn = get_db()
    cursor = conn.execute(
        f"INSERT INTO customers ({', '.join(columns)}) VALUES ({placeholders})",
        values
    )
    customer_id = cursor.lastrowid
    conn.execute("UPDATE customers SET ma_kh = printf('KH-%05d', ?) WHERE id = ?", (customer_id, customer_id))
    conn.commit()
    conn.close()

    name = data.get('ho_ten', '') or data.get('ten_cong_ty', '')
    add_log('Thêm KH tay', f"Thêm mới: {name} — SĐT: {data.get('sdt', '')}",
            customer_id, name, operator)

    return customer_id


def update_customer(customer_id, new_data, operator='Dương'):
    """Update a customer, recalc scores, log changes."""
    conn = get_db()
    old = conn.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
    if not old:
        conn.close()
        return False

    old_data = dict(old)
    changes = []

    # Normalize SĐT if changed
    if 'sdt' in new_data:
        new_data['sdt'] = normalize_sdt(new_data['sdt'])

    # Detect changes
    for key in INPUT_COLUMNS + SCORE_COLUMNS:
        if key in new_data and str(new_data.get(key, '')) != str(old_data.get(key, '')):
            changes.append(f"{key}: '{old_data.get(key, '')}' → '{new_data[key]}'")

    if not changes:
        conn.close()
        return True  # no changes

    # Merge new data into old
    merged = {**old_data, **new_data}

    # Recompute scores
    scores = compute_scores(merged)
    merged.update(scores)

    # Update
    set_parts = []
    values = []
    for col in INPUT_COLUMNS + SCORE_COLUMNS:
        if col in merged:
            set_parts.append(f"{col} = ?")
            values.append(merged[col])
    set_parts.append("updated_at = CURRENT_TIMESTAMP")
    values.append(customer_id)

    conn.execute(
        f"UPDATE customers SET {', '.join(set_parts)} WHERE id = ?",
        values
    )
    conn.commit()
    conn.close()

    name = merged.get('ho_ten', '') or merged.get('ten_cong_ty', '')
    add_log('Sửa KH', '; '.join(changes), customer_id, name, operator)

    return True


def soft_delete(customer_id, operator='Dương'):
    """Soft delete a customer."""
    conn = get_db()
    row = conn.execute("SELECT ho_ten, ten_cong_ty FROM customers WHERE id = ?",
                       (customer_id,)).fetchone()
    if not row:
        conn.close()
        return False

    conn.execute("UPDATE customers SET is_deleted = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                 (customer_id,))
    conn.commit()
    conn.close()

    name = row['ho_ten'] or row['ten_cong_ty'] or ''
    add_log('Xóa KH', f"Soft delete: {name}", customer_id, name, operator)
    return True


def restore_customer(customer_id, operator='Dương'):
    """Restore a soft-deleted customer."""
    conn = get_db()
    row = conn.execute("SELECT ho_ten, ten_cong_ty FROM customers WHERE id = ?",
                       (customer_id,)).fetchone()
    if not row:
        conn.close()
        return False

    conn.execute("UPDATE customers SET is_deleted = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                 (customer_id,))
    conn.commit()
    conn.close()

    name = row['ho_ten'] or row['ten_cong_ty'] or ''
    add_log('Khôi phục KH', f"Khôi phục: {name}", customer_id, name, operator)
    return True


def batch_edit(customer_ids, field, value, operator='Dương'):
    """Edit one field for multiple customers."""
    conn = get_db()
    count = 0
    for cid in customer_ids:
        old = conn.execute("SELECT * FROM customers WHERE id = ? AND is_deleted = 0",
                           (cid,)).fetchone()
        if not old:
            continue

        old_val = dict(old).get(field, '')
        if str(old_val) == str(value):
            continue

        conn.execute(
            f"UPDATE customers SET {field} = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (value, cid)
        )
        count += 1

    conn.commit()

    # Recalc scores if scoring field changed
    scoring_fields = ['so_kh_quay_lai', 'biet_loi_nhuan', 'doi_tho', 'chinh_sach_bh',
                      'muc_quan_tam', 'ban_kinh_km', 'quan_ly_data',
                      'kiem_soat_mua_hang', 'so_nguoi_gioi_thieu']
    if field in scoring_fields:
        for cid in customer_ids:
            cust = conn.execute("SELECT * FROM customers WHERE id = ?", (cid,)).fetchone()
            if cust:
                scores = compute_scores(dict(cust))
                conn.execute(
                    """UPDATE customers SET c1=?, c2=?, c3=?, c4=?, c5=?, c6=?, c7=?, c8=?, c9=?,
                       c_score=?, tier=?, review_status=? WHERE id=?""",
                    (scores['c1'], scores['c2'], scores['c3'], scores['c4'],
                     scores['c5'], scores['c6'], scores['c7'], scores['c8'],
                     scores['c9'], scores['c_score'], scores['tier'],
                     scores['review_status'], cid)
                )
        conn.commit()

    conn.close()

    add_log('Batch edit', f"Sửa {count} KH: {field} → '{value}'", operator=operator)
    return count


def find_replace(field, old_value, new_value, operator='Dương'):
    """Replace all occurrences of old_value with new_value in a column."""
    if field not in ALL_COLUMNS:
        return 0

    conn = get_db()
    # Count matches first
    count = conn.execute(
        f"SELECT COUNT(*) FROM customers WHERE is_deleted = 0 AND {field} = ?",
        (old_value,)
    ).fetchone()[0]

    if count == 0:
        conn.close()
        return 0

    conn.execute(
        f"UPDATE customers SET {field} = ?, updated_at = CURRENT_TIMESTAMP WHERE is_deleted = 0 AND {field} = ?",
        (new_value, old_value)
    )
    conn.commit()
    conn.close()

    add_log('Tìm & thay thế',
            f"Cột '{field}': '{old_value}' → '{new_value}' ({count} KH)",
            operator=operator)
    return count


def find_duplicates(sdt):
    """Find existing customers with matching phone numbers."""
    phones = extract_all_phones(normalize_sdt(sdt))
    if not phones:
        return []

    conn = get_db()
    results = []
    for phone in phones:
        if len(phone) < 8: continue
        rows = conn.execute(
            "SELECT * FROM customers WHERE is_deleted = 0 AND sdt LIKE ?",
            (f'%{phone}%',)
        ).fetchall()
        results.extend(dicts_from_rows(rows))

    conn.close()
    # Deduplicate by id
    seen = set()
    unique = []
    for r in results:
        if r['id'] not in seen:
            seen.add(r['id'])
            unique.append(r)
    return unique


def get_dashboard_stats():
    """Get stats for dashboard."""
    conn = get_db()

    total = conn.execute("SELECT COUNT(*) FROM customers WHERE is_deleted = 0").fetchone()[0]

    # By loai_kh
    by_type_rows = conn.execute(
        """SELECT loai_kh, COUNT(*) as cnt FROM customers
           WHERE is_deleted = 0 AND loai_kh IS NOT NULL AND loai_kh != ''
           GROUP BY loai_kh ORDER BY cnt DESC"""
    ).fetchall()
    by_type = []
    other_cnt = 0
    for i, row in enumerate(by_type_rows):
        if i < 9:
            by_type.append(dict(row))
        else:
            other_cnt += row[1]
    if other_cnt > 0:
        by_type.append({'loai_kh': 'Khác (nhỏ lẻ)', 'cnt': other_cnt})

    # By khu_vuc
    by_region = conn.execute(
        """SELECT khu_vuc, COUNT(*) as cnt FROM customers
           WHERE is_deleted = 0 AND khu_vuc IS NOT NULL AND khu_vuc != ''
           GROUP BY khu_vuc ORDER BY cnt DESC"""
    ).fetchall()

    # By tier
    by_tier_rows = conn.execute(
        """SELECT tier, COUNT(*) as cnt FROM customers
           WHERE is_deleted = 0
           GROUP BY tier ORDER BY tier"""
    ).fetchall()
    by_tier = []
    for r in by_tier_rows:
        t = r['tier']
        by_tier.append({'tier': t if t else 'Chưa xếp hạng', 'cnt': r['cnt']})

    # Top 10 tỉnh
    top_provinces = conn.execute(
        """SELECT tinh, COUNT(*) as cnt FROM customers
           WHERE is_deleted = 0 AND tinh IS NOT NULL AND tinh != ''
           GROUP BY tinh ORDER BY cnt DESC LIMIT 10"""
    ).fetchall()

    # By nguon
    by_source = conn.execute(
        """SELECT nguon, COUNT(*) as cnt FROM customers
           WHERE is_deleted = 0 AND nguon IS NOT NULL AND nguon != ''
           GROUP BY nguon ORDER BY cnt DESC"""
    ).fetchall()

    # Review status
    needs_review = conn.execute(
        "SELECT COUNT(*) FROM customers WHERE is_deleted = 0 AND review_status = 'needs_review'"
    ).fetchone()[0]

    # Scoring completeness
    has_scoring = conn.execute(
        """SELECT COUNT(*) FROM customers WHERE is_deleted = 0
           AND (so_kh_quay_lai IS NOT NULL OR biet_loi_nhuan IS NOT NULL
                OR doi_tho IS NOT NULL)"""
    ).fetchone()[0]

    conn.close()

    return {
        'total': total,
        'by_type': by_type,
        'by_region': [dict(r) for r in by_region],
        'by_tier': [dict(r) for r in by_tier],
        'top_provinces': [dict(r) for r in top_provinces],
        'by_source': [dict(r) for r in by_source],
        'needs_review': needs_review,
        'has_scoring': has_scoring,
    }
