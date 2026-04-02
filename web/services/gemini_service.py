"""Gemini AI service — use Google Gemini to score 'Khác' answers."""

from google import genai
from config import GEMINI_API_KEY
from services.scoring_service import DROPDOWN_SCORES

# Rubric descriptions per criteria
RUBRIC = {
    'c1': {
        'name': 'Sở hữu khách hàng bền vững',
        '0': 'Không biết / không nhớ tên khách cũ, không có danh sách',
        '1': 'Nhớ theo quan hệ cá nhân, chưa có danh sách, dưới 50 khách quay lại',
        '2': 'Có danh sách ≥50 house, % quay lại ≥30%/năm hoặc referral rõ ràng',
    },
    'c2': {
        'name': 'P&L độc lập',
        '0': 'Không biết lãi/lỗ từng đơn hàng',
        '1': 'Biết biên lợi nhuận nhưng DSO > 60 ngày',
        '2': 'Biên LN > 15%, DSO ≤ 60 ngày, không phụ thuộc hàng ký gửi',
    },
    'c3': {
        'name': 'Đội thợ thi công',
        '0': 'Không có đội, tự làm hoặc gọi thợ tự do',
        '1': 'Có 1-3 thợ không cố định, gọi theo vụ',
        '2': 'Có ≥2 thợ cơ hữu, có thể điều phối lịch job, SLA ổn định',
    },
    'c4': {
        'name': 'Trách nhiệm bảo hành',
        '0': 'Đổ lỗi cho nhà sản xuất khi có sự cố',
        '1': 'Xử lý bảo hành nhưng đòi hoàn lại từ nhà SX',
        '2': 'Ký bảo hành danh nghĩa cửa hàng, chịu chi phí trực tiếp',
    },
    'c5': {
        'name': 'Động lực tham gia',
        '0': 'Không muốn thay đổi cách làm hiện tại',
        '1': 'Quan tâm nhưng chưa chỉ ra lợi ích cụ thể',
        '2': 'Chỉ rõ 1 nỗi đau muốn giải ngay (DSO/thợ/khách mới)',
    },
    'c6': {
        'name': 'Kiểm soát địa bàn vật lý',
        '0': 'Không có vùng địa lý nhất định',
        '1': 'Có quan hệ 1 khu vực nhưng không độc quyền',
        '2': 'Khách <5km gọi họ đầu tiên không cần quảng cáo',
    },
    'c7': {
        'name': 'Kỷ luật dữ liệu',
        '0': 'Không ghi gì, mọi thứ nằm trong đầu',
        '1': 'Ghi chép rải rác Zalo/Excel chưa chuẩn hóa',
        '2': 'Có hệ thống ghi chép job/tiền, có thể xuất lịch sử khách',
    },
    'c8': {
        'name': 'Chuỗi cung ứng',
        '0': 'Mua theo chỉ định nhà sản xuất, không chọn được',
        '1': 'Có 2-3 nguồn nhà cung cấp có thể lựa chọn',
        '2': 'Chủ động đặt hàng, có thể thương lượng giá/điều khoản',
    },
    'c9': {
        'name': 'Sức ảnh hưởng cộng đồng',
        '0': 'Không ai trong nghề biết đến họ',
        '1': 'Được vài người trong nghề biết và tin',
        '2': 'Người khác giới thiệu thợ/khách cho họ, có thể kéo người mới vào',
    },
}

# Mapping field name → criteria id
FIELD_TO_CRITERIA = {
    'so_kh_quay_lai': 'c1',
    'biet_loi_nhuan': 'c2',
    'doi_tho': 'c3',
    'chinh_sach_bh': 'c4',
    'muc_quan_tam': 'c5',
    'ban_kinh_km': 'c6',
    'quan_ly_data': 'c7',
    'kiem_soat_mua_hang': 'c8',
    'so_nguoi_gioi_thieu': 'c9',
}


def score_with_ai(field_name, customer_text):
    """Use Gemini to score a 'Khác' answer.

    Args:
        field_name: the DB column (e.g., 'doi_tho')
        customer_text: the text from 'Thông Tin Chi Tiết'

    Returns:
        (score: int 0/1/2, explanation: str) or (None, error_msg)
    """
    if not GEMINI_API_KEY:
        return None, 'Gemini API key chưa được cấu hình'

    criteria_id = FIELD_TO_CRITERIA.get(field_name)
    if not criteria_id or criteria_id not in RUBRIC:
        return None, f'Không tìm thấy rubric cho {field_name}'

    rubric = RUBRIC[criteria_id]

    prompt = f"""Bạn là chuyên gia phân loại dealer ngành VLXD Việt Nam.

Tiêu chí đánh giá: {rubric['name']}

Thang điểm:
- 0 điểm: {rubric['0']}
- 1 điểm: {rubric['1']}
- 2 điểm: {rubric['2']}

Thông tin khách hàng trả lời:
"{customer_text}"

Dựa trên thông tin trên, hãy chấm điểm. Trả lời theo format:
ĐIỂM: [0 hoặc 1 hoặc 2]
LÝ DO: [giải thích ngắn gọn]"""

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
        )
        text = response.text.strip()

        # Parse score from response
        score = None
        explanation = text
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('ĐIỂM:') or line.startswith('Điểm:'):
                try:
                    score_str = line.split(':')[1].strip()
                    score = int(score_str[0])
                    if score not in (0, 1, 2):
                        score = None
                except (ValueError, IndexError):
                    pass
            if line.startswith('LÝ DO:') or line.startswith('Lý do:'):
                explanation = line.split(':', 1)[1].strip()

        if score is not None:
            return score, explanation
        else:
            return None, f'Không parse được điểm từ AI response: {text}'

    except Exception as e:
        return None, f'Lỗi Gemini API: {str(e)}'
