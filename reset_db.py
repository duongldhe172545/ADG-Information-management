"""Reset database completely, restore mapping keywords."""
import sqlite3
import os

DB_PATH = r'd:\ADG-Dealer\web\data\app.db'
SCHEMA_PATH = r'd:\ADG-Dealer\web\database\schema.sql'

# Kill DB files
for ext in ['', '-wal', '-shm']:
    p = DB_PATH + ext
    if os.path.exists(p):
        os.remove(p)
        print(f'Deleted {p}')

# Create fresh DB from schema
db = sqlite3.connect(DB_PATH)
with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
    db.executescript(f.read())

# Pre-seed comprehensive keyword mappings
mappings = [
    # --- Đại lý phân phối ---
    ('đại lý', 'dai_ly_phan_phoi'),
    ('đl ', 'dai_ly_phan_phoi'),        # "ĐL Cửa Cuốn", "ĐL C2"...
    ('đlsx', 'dai_ly_phan_phoi'),       # "ĐLSX Nhóm MN", "ĐLSX Tổng Hợp"...
    ('dl ', 'dai_ly_phan_phoi'),        
    ('phân phối', 'dai_ly_phan_phoi'),
    ('nhà phân phối', 'dai_ly_phan_phoi'),
    ('npp', 'dai_ly_phan_phoi'),
    ('hội viên', 'dai_ly_phan_phoi'),   # "Đại lý (Hội viên HNC)"
    ('khách lẻ', 'dai_ly_phan_phoi'),   # "Đại lý/Khách lẻ"
    
    # --- Tổ đội thi công ---
    ('tổ đội', 'to_doi_thi_cong'),
    ('thi công', 'to_doi_thi_cong'),
    ('thợ', 'to_doi_thi_cong'),
    ('nhóm thợ', 'to_doi_thi_cong'),
    ('đội thợ', 'to_doi_thi_cong'),
    ('nhà thầu', 'to_doi_thi_cong'),
    ('thầu', 'to_doi_thi_cong'),
    ('xây dựng', 'to_doi_thi_cong'),
    ('xây', 'to_doi_thi_cong'),
    
    # --- Xưởng sản xuất ---
    ('xưởng', 'xuong_san_xuat'),
    ('sản xuất', 'xuong_san_xuat'),
    ('gia công', 'xuong_san_xuat'),
    ('chế biến', 'xuong_san_xuat'),
    ('nhà máy', 'xuong_san_xuat'),
    
    # --- Showroom / Nội thất ---
    ('showroom', 'showroom'),
    ('nội thất', 'showroom'),
    ('thiết kế', 'showroom'),
    ('decor', 'showroom'),
    ('trang trí', 'showroom'),
    
    # --- Cửa hàng VLXD ---
    ('vlxd', 'cua_hang_vlxd'),
    ('vật liệu', 'cua_hang_vlxd'),
    ('cửa hàng', 'cua_hang_vlxd'),
    ('bán lẻ', 'cua_hang_vlxd'),
    ('kinh doanh', 'cua_hang_vlxd'),
    
    # --- Chưa xác định (catch common but ambiguous terms) ---
    ('khách hàng', 'chua_xac_dinh'),
]
for kw, nhom in mappings:
    db.execute('INSERT OR IGNORE INTO loai_kh_mapping (keyword, nhom_kh) VALUES (?, ?)', (kw, nhom))
print(f'Seeded {len(mappings)} keyword mappings!')
db.commit()

# Verify
tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print(f'Tables: {tables}')
print(f'Customers: {db.execute("SELECT COUNT(*) FROM customers").fetchone()[0]}')
print(f'Mappings: {db.execute("SELECT COUNT(*) FROM loai_kh_mapping").fetchone()[0]}')
print(f'Groups: {db.execute("SELECT COUNT(*) FROM nhom_kh_groups").fetchone()[0]}')
groups = db.execute("SELECT key, label FROM nhom_kh_groups ORDER BY display_order").fetchall()
for g in groups:
    print(f'  {g[0]}: {g[1]}')
db.close()
print('Fresh DB created successfully!')
