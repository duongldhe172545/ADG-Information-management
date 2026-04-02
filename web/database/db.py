import sqlite3
import os

from config import DB_PATH

def get_db():
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Initialize database with schema + seed default keywords."""
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    conn = get_db()
    with open(schema_path, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    
    # Seed default keyword mappings if empty
    count = conn.execute('SELECT COUNT(*) FROM loai_kh_mapping').fetchone()[0]
    if count == 0:
        defaults = [
            ('đại lý', 'dai_ly_phan_phoi'), ('đl ', 'dai_ly_phan_phoi'),
            ('đlsx', 'dai_ly_phan_phoi'), ('dl ', 'dai_ly_phan_phoi'),
            ('phân phối', 'dai_ly_phan_phoi'), ('nhà phân phối', 'dai_ly_phan_phoi'),
            ('npp', 'dai_ly_phan_phoi'), ('hội viên', 'dai_ly_phan_phoi'),
            ('khách lẻ', 'dai_ly_phan_phoi'),
            ('tổ đội', 'to_doi_thi_cong'), ('thi công', 'to_doi_thi_cong'),
            ('thợ', 'to_doi_thi_cong'), ('nhóm thợ', 'to_doi_thi_cong'),
            ('đội thợ', 'to_doi_thi_cong'), ('nhà thầu', 'to_doi_thi_cong'),
            ('thầu', 'to_doi_thi_cong'), ('xây dựng', 'to_doi_thi_cong'),
            ('xây', 'to_doi_thi_cong'),
            ('xưởng', 'xuong_san_xuat'), ('sản xuất', 'xuong_san_xuat'),
            ('gia công', 'xuong_san_xuat'), ('chế biến', 'xuong_san_xuat'),
            ('nhà máy', 'xuong_san_xuat'),
            ('showroom', 'showroom'), ('nội thất', 'showroom'),
            ('thiết kế', 'showroom'), ('decor', 'showroom'), ('trang trí', 'showroom'),
            ('vlxd', 'cua_hang_vlxd'), ('vật liệu', 'cua_hang_vlxd'),
            ('cửa hàng', 'cua_hang_vlxd'), ('bán lẻ', 'cua_hang_vlxd'),
            ('kinh doanh', 'cua_hang_vlxd'),
            ('khách hàng', 'chua_xac_dinh'),
        ]
        for kw, nhom in defaults:
            conn.execute('INSERT OR IGNORE INTO loai_kh_mapping (keyword, nhom_kh) VALUES (?, ?)', (kw, nhom))
        print(f"Seeded {len(defaults)} default keyword mappings")
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


def dict_from_row(row):
    """Convert sqlite3.Row to dict."""
    if row is None:
        return None
    return dict(row)


def dicts_from_rows(rows):
    """Convert list of sqlite3.Row to list of dicts."""
    return [dict(row) for row in rows]
