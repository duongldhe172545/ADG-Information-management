"""Scoring service — auto-score C1-C9, calculate c_score, assign tier."""

from database.db import get_db


# Mapping dropdown text → score for C2-C5, C7-C8
DROPDOWN_SCORES = {
    'biet_loi_nhuan': {
        'Không biết': 0,
        'Biết LN nhưng DSO>60 ngày': 1,
        'Biết LN>15% và DSO≤60 ngày': 2,
    },
    'doi_tho': {
        'Không có đội': 0,
        '1-3 thợ rời theo vụ': 1,
        '≥2 thợ cơ hữu SLA ổn': 2,
    },
    'chinh_sach_bh': {
        'Đổ lỗi NCC': 0,
        'BH nhưng đòi hoàn NCC': 1,
        'Tự ký BH chịu CP': 2,
    },
    'muc_quan_tam': {
        'Không muốn đổi': 0,
        'Quan tâm chưa rõ lợi ích': 1,
        'Có nỗi đau cụ thể muốn giải': 2,
    },
    'quan_ly_data': {
        'Không ghi chép': 0,
        'Ghi Zalo/Excel rải rác': 1,
        'Có hệ thống xuất được lịch sử': 2,
    },
    'kiem_soat_mua_hang': {
        'Theo chỉ định NCC': 0,
        'Có 2-3 NCC lựa chọn': 1,
        'Chủ động thương lượng giá': 2,
    },
}


def score_c1(value):
    """C1: Số KH quay lại/năm → 0/1/2."""
    if value is None:
        return 0
    try:
        v = int(value)
    except (ValueError, TypeError):
        return 0
    if v <= 0:
        return 0
    elif v < 50:
        return 1
    else:
        return 2


def score_c6(value):
    """C6: Bán kính KH gọi đến (km) → 0/1/2."""
    if value is None:
        return 0
    try:
        v = int(value)
    except (ValueError, TypeError):
        return 0
    if v <= 0:
        return 0
    elif v < 5:
        return 1
    else:
        return 2


def score_c9(value):
    """C9: Số người được giới thiệu → 0/1/2."""
    if value is None:
        return 0
    try:
        v = int(value)
    except (ValueError, TypeError):
        return 0
    if v <= 3:
        return 0
    elif v <= 7:
        return 1
    else:
        return 2


def score_dropdown(field_name, value):
    """Score a dropdown field → 0/1/2. Returns None if 'Khác'."""
    if value is None or value == '':
        return 0
    if value == 'Khác':
        return None  # needs review or AI
    mapping = DROPDOWN_SCORES.get(field_name, {})
    return mapping.get(value, 0)


def get_weights():
    """Get scoring weights as dict {c_id: weight}."""
    conn = get_db()
    rows = conn.execute("SELECT c_id, name, weight FROM scoring_weights ORDER BY c_id").fetchall()
    conn.close()
    return {row['c_id']: {'name': row['name'], 'weight': row['weight']} for row in rows}


def compute_scores(customer_data):
    """Compute C1-C9 scores, c_score, and tier for a customer dict.

    Returns dict with c1-c9, c_score, tier, review_status.
    """
    needs_review = False
    scores = {}

    # C1: number
    scores['c1'] = score_c1(customer_data.get('so_kh_quay_lai'))

    # C2-C5, C7-C8: dropdown
    for ci, field in [('c2', 'biet_loi_nhuan'), ('c3', 'doi_tho'),
                      ('c4', 'chinh_sach_bh'), ('c5', 'muc_quan_tam'),
                      ('c7', 'quan_ly_data'), ('c8', 'kiem_soat_mua_hang')]:
        val = score_dropdown(field, customer_data.get(field))
        if val is None:
            scores[ci] = 0
            needs_review = True
        else:
            scores[ci] = val

    # C6: number
    scores['c6'] = score_c6(customer_data.get('ban_kinh_km'))

    # C9: number
    scores['c9'] = score_c9(customer_data.get('so_nguoi_gioi_thieu'))

    # Calculate c_score
    weights = get_weights()
    raw = 0
    for i in range(1, 10):
        ci = f'c{i}'
        cid = f'C{i}'
        w = weights.get(cid, {}).get('weight', 0)
        raw += scores[ci] * w

    scores['c_score'] = round(raw * 50)

    # Assign tier
    if scores['c_score'] >= 75:
        scores['tier'] = 'A'
    elif scores['c_score'] >= 50:
        scores['tier'] = 'B'
    elif scores['c_score'] >= 30:
        scores['tier'] = 'C'
    else:
        scores['tier'] = 'D'

    scores['review_status'] = 'needs_review' if needs_review else 'ok'
    return scores


def recalc_all():
    """Recalculate c_score and tier for ALL customers. Returns count."""
    conn = get_db()
    customers = conn.execute(
        "SELECT * FROM customers WHERE is_deleted = 0"
    ).fetchall()

    count = 0
    for cust in customers:
        data = dict(cust)
        scores = compute_scores(data)
        conn.execute(
            """UPDATE customers SET
               c1=?, c2=?, c3=?, c4=?, c5=?, c6=?, c7=?, c8=?, c9=?,
               c_score=?, tier=?, review_status=?, updated_at=CURRENT_TIMESTAMP
               WHERE id=?""",
            (scores['c1'], scores['c2'], scores['c3'], scores['c4'],
             scores['c5'], scores['c6'], scores['c7'], scores['c8'],
             scores['c9'], scores['c_score'], scores['tier'],
             scores['review_status'], data['id'])
        )
        count += 1

    conn.commit()
    conn.close()
    return count


def update_weights(new_weights):
    """Update scoring weights. new_weights = {C1: 0.20, C2: 0.15, ...}"""
    conn = get_db()
    for c_id, weight in new_weights.items():
        conn.execute(
            "UPDATE scoring_weights SET weight = ? WHERE c_id = ?",
            (weight, c_id)
        )
    conn.commit()
    conn.close()
