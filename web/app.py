"""ADG Dealer — Web Quản Lý Khách Hàng."""

import os
import json
from flask import (Flask, render_template, request, jsonify, send_file)
from database.db import init_db, get_db
from services import customer_service, import_service, scoring_service
from services import export_service, log_service, gemini_service
from config import UPLOAD_FOLDER

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload
app.config['JSON_SORT_KEYS'] = False  # Preserve dictionary order for frontend previews


# ─── Page Routes ────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('customers.html')

@app.route('/import')
def import_page():
    return render_template('import.html')

@app.route('/review')
def review_page():
    return render_template('review.html')

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

@app.route('/log')
def log_page():
    return render_template('log.html')

@app.route('/deleted')
def deleted_page():
    return render_template('deleted.html')

@app.route('/settings')
def settings_page():
    return render_template('settings.html')


# ─── API: Customers ─────────────────────────────────────────────

@app.route('/api/customers', methods=['GET'])
def api_list_customers():
    search = request.args.get('search', '')
    search_col = request.args.get('search_col', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    deleted = request.args.get('deleted', '0') == '1'

    filters = {}
    for key in ['loai_kh', 'khu_vuc', 'tinh', 'tier', 'nguon', 'review_status']:
        val = request.args.get(key)
        if val:
            filters[key] = val

    result = customer_service.list_customers(
        search=search, search_col=search_col if search_col else None,
        filters=filters, page=page,
        per_page=per_page, include_deleted=deleted
    )
    return jsonify(result)


@app.route('/api/customers/<int:cid>', methods=['GET'])
def api_get_customer(cid):
    cust = customer_service.get_customer(cid)
    if not cust:
        return jsonify({'error': 'Không tìm thấy'}), 404
    return jsonify(cust)


@app.route('/api/customers', methods=['POST'])
def api_create_customer():
    data = request.json
    cid = customer_service.create_customer(data)
    return jsonify({'id': cid, 'message': 'Đã thêm KH mới'})


@app.route('/api/customers/<int:cid>', methods=['PUT'])
def api_update_customer(cid):
    data = request.json

    # Save old data for undo
    old = customer_service.get_customer(cid)

    ok = customer_service.update_customer(cid, data)
    if not ok:
        return jsonify({'error': 'Không tìm thấy'}), 404

    updated = customer_service.get_customer(cid)
    return jsonify({'message': 'Đã cập nhật', 'customer': updated, 'old': old})


@app.route('/api/customers/<int:cid>', methods=['DELETE'])
def api_delete_customer(cid):
    ok = customer_service.soft_delete(cid)
    if not ok:
        return jsonify({'error': 'Không tìm thấy'}), 404
    return jsonify({'message': 'Đã xóa (soft delete)'})


@app.route('/api/customers/<int:cid>/restore', methods=['POST'])
def api_restore_customer(cid):
    ok = customer_service.restore_customer(cid)
    if not ok:
        return jsonify({'error': 'Không tìm thấy'}), 404
    return jsonify({'message': 'Đã khôi phục'})


@app.route('/api/customers/batch-edit', methods=['POST'])
def api_batch_edit():
    data = request.json
    ids = data.get('ids', [])
    field = data.get('field', '')
    value = data.get('value', '')

    if not ids or not field:
        return jsonify({'error': 'Thiếu thông tin'}), 400

    count = customer_service.batch_edit(ids, field, value)
    return jsonify({'message': f'Đã sửa {count} KH', 'count': count})


@app.route('/api/customers/find-replace', methods=['POST'])
def api_find_replace():
    data = request.json
    field = data.get('field', '')
    old_value = data.get('old_value', '')
    new_value = data.get('new_value', '')

    if not field or not old_value:
        return jsonify({'error': 'Thiếu thông tin'}), 400

    count = customer_service.find_replace(field, old_value, new_value)
    return jsonify({
        'message': f"Đã thay '{old_value}' → '{new_value}' cho {count} KH",
        'count': count
    })


@app.route('/api/customers/<int:cid>/undo', methods=['POST'])
def api_undo(cid):
    """Undo: restore old values from the provided data."""
    old_data = request.json.get('old_data', {})
    if not old_data:
        return jsonify({'error': 'Không có dữ liệu để hoàn tác'}), 400

    # Only restore INPUT_COLUMNS
    restore_data = {k: v for k, v in old_data.items() if k in customer_service.INPUT_COLUMNS}
    ok = customer_service.update_customer(cid, restore_data, operator='Dương (Undo)')
    if not ok:
        return jsonify({'error': 'Không tìm thấy'}), 404

    log_service.add_log('Undo', f'Hoàn tác thay đổi cho KH #{cid}', cid, operator='Dương')
    updated = customer_service.get_customer(cid)
    return jsonify({'message': 'Đã hoàn tác', 'customer': updated})


# ─── API: Import ────────────────────────────────────────────────

@app.route('/api/import/preview', methods=['POST'])
def api_import_preview():
    """Preview Excel file before importing."""
    if 'file' not in request.files:
        return jsonify({'error': 'Chưa chọn file'}), 400

    file = request.files['file']
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({'error': 'Chỉ hỗ trợ file .xlsx'}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    rows, errors = import_service.parse_excel(filepath)
    if errors:
        return jsonify({'errors': errors}), 400

    # Check duplicates
    dup_results = import_service.check_duplicates(rows[:100])  # check first 100
    duplicates = [(r, d) for r, d in dup_results if d]

    return jsonify({
        'filename': file.filename,
        'filepath': filepath,
        'total_rows': len(rows),
        'preview': rows[:10],
        'duplicate_count': len(duplicates),
        'duplicates_sample': [
            {'new': r, 'existing': d} for r, d in duplicates[:5]
        ]
    })


@app.route('/api/import/confirm', methods=['POST'])
def api_import_confirm():
    """Confirm and execute import."""
    data = request.json
    filepath = data.get('filepath', '')
    merge = data.get('merge_strategy', 'smart')

    if not os.path.exists(filepath):
        return jsonify({'error': 'File không tồn tại'}), 400

    rows, errors = import_service.parse_excel(filepath)
    if errors:
        return jsonify({'errors': errors}), 400

    inserted, updated, skipped = import_service.import_rows(rows, merge_strategy=merge)

    # Clean up uploaded file
    try:
        os.remove(filepath)
    except OSError:
        pass

    return jsonify({
        'message': f'Import hoàn tất: {inserted} mới, {updated} cập nhật, {skipped} bỏ qua',
        'inserted': inserted,
        'updated': updated,
        'skipped': skipped
    })


# ─── API: Scoring ───────────────────────────────────────────────

@app.route('/api/scoring/weights', methods=['GET'])
def api_get_weights():
    weights = scoring_service.get_weights()
    return jsonify(weights)


@app.route('/api/scoring/weights', methods=['PUT'])
def api_update_weights():
    data = request.json  # {C1: 0.20, C2: 0.15, ...}

    # Validate sum = 1.0
    total = sum(data.values())
    if abs(total - 1.0) > 0.01:
        return jsonify({'error': f'Tổng trọng số = {total:.2f}, phải = 1.00'}), 400

    old_weights = scoring_service.get_weights()
    scoring_service.update_weights(data)
    count = scoring_service.recalc_all()

    old_str = ', '.join(f"{k}={v['weight']}" for k, v in old_weights.items())
    new_str = ', '.join(f"{k}={v}" for k, v in data.items())
    log_service.add_log('Đổi trọng số',
                        f'Cũ: {old_str}\nMới: {new_str}\nĐã tính lại {count} KH')

    return jsonify({'message': f'Đã cập nhật trọng số, tính lại {count} KH'})


@app.route('/api/scoring/ai/<int:cid>', methods=['POST'])
def api_ai_score(cid):
    """Use Gemini AI to score a 'Khác' field."""
    data = request.json
    field_name = data.get('field', '')
    text = data.get('text', '')

    if not field_name or not text:
        return jsonify({'error': 'Thiếu thông tin'}), 400

    score, explanation = gemini_service.score_with_ai(field_name, text)
    if score is None:
        return jsonify({'error': explanation}), 400

    # Update the C score
    criteria = gemini_service.FIELD_TO_CRITERIA.get(field_name)
    if criteria:
        conn = get_db()
        conn.execute(f"UPDATE customers SET {criteria} = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                     (score, cid))
        # Recalc c_score and tier
        cust = conn.execute("SELECT * FROM customers WHERE id = ?", (cid,)).fetchone()
        if cust:
            scores = scoring_service.compute_scores(dict(cust))
            conn.execute(
                "UPDATE customers SET c_score = ?, tier = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (scores['c_score'], scores['tier'], cid)
            )
        conn.commit()
        conn.close()

    cust = customer_service.get_customer(cid)
    name = cust.get('ho_ten', '') or cust.get('ten_cong_ty', '')
    log_service.add_log('AI chấm điểm',
                        f'{criteria}: {score}đ — {explanation}',
                        cid, name)

    return jsonify({
        'score': score,
        'explanation': explanation,
        'customer': customer_service.get_customer(cid)
    })


@app.route('/api/scoring/fix-ai/<int:cid>', methods=['PUT'])
def api_fix_ai(cid):
    """Manually fix AI score."""
    data = request.json
    criteria = data.get('criteria', '')  # e.g., 'c3'
    new_score = data.get('score', 0)

    if criteria not in ['c2', 'c3', 'c4', 'c5', 'c7', 'c8']:
        return jsonify({'error': 'Tiêu chí không hợp lệ'}), 400

    conn = get_db()
    conn.execute(f"UPDATE customers SET {criteria} = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                 (new_score, cid))
    cust = conn.execute("SELECT * FROM customers WHERE id = ?", (cid,)).fetchone()
    if cust:
        scores = scoring_service.compute_scores(dict(cust))
        conn.execute(
            "UPDATE customers SET c_score = ?, tier = ?, review_status = 'ok', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (scores['c_score'], scores['tier'], cid)
        )
    conn.commit()
    conn.close()

    cust = customer_service.get_customer(cid)
    name = cust.get('ho_ten', '') or cust.get('ten_cong_ty', '')
    log_service.add_log('Sửa điểm AI',
                        f'{criteria}: → {new_score}đ',
                        cid, name)

    return jsonify({'message': 'Đã sửa điểm', 'customer': cust})


# ─── API: Dashboard ─────────────────────────────────────────────

@app.route('/api/dashboard', methods=['GET'])
def api_dashboard():
    stats = customer_service.get_dashboard_stats()
    return jsonify(stats)


# ─── API: Change Log ────────────────────────────────────────────

@app.route('/api/log', methods=['GET'])
def api_log():
    action_type = request.args.get('action_type', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))

    result = log_service.get_logs(
        action_type=action_type if action_type else None,
        page=page, per_page=per_page
    )
    return jsonify(result)


# ─── API: Export ─────────────────────────────────────────────────

@app.route('/api/export', methods=['GET'])
def api_export():
    filters = {}
    for key in ['loai_kh', 'khu_vuc', 'tinh', 'tier', 'nguon']:
        val = request.args.get(key)
        if val:
            filters[key] = val

    filepath = export_service.export_customers(filters)
    log_service.add_log('Export', f'Export Excel: {os.path.basename(filepath)}')
    return send_file(filepath, as_attachment=True)


# ─── API: Filter options ────────────────────────────────────────

@app.route('/api/filter-options', methods=['GET'])
def api_filter_options():
    """Get unique values for filter dropdowns."""
    conn = get_db()
    options = {}
    for col in ['loai_kh', 'khu_vuc', 'tinh', 'tier', 'nguon']:
        rows = conn.execute(
            f"SELECT DISTINCT {col} FROM customers WHERE is_deleted = 0 AND {col} IS NOT NULL AND {col} != '' ORDER BY {col}"
        ).fetchall()
        options[col] = [r[0] for r in rows]
    conn.close()
    return jsonify(options)


# ─── Init ────────────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
