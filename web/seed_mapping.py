import sqlite3, time

DB = r'd:\ADG-Dealer\web\data\app.db'

for attempt in range(5):
    try:
        conn = sqlite3.connect(DB, timeout=10)
        conn.execute('BEGIN IMMEDIATE')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS loai_kh_mapping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            nhom_kh TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        
        seeds = [
            ('xưởng', 'xuong_san_xuat'), ('sản xuất', 'xuong_san_xuat'), ('ĐLSX', 'xuong_san_xuat'),
            ('ĐL SX', 'xuong_san_xuat'), ('cơ khí', 'xuong_san_xuat'),
            ('showroom', 'showroom'), ('nội thất', 'showroom'), ('thiết kế', 'showroom'),
            ('KTS', 'showroom'), ('tư vấn', 'showroom'),
            ('đại lý', 'dai_ly_phan_phoi'), ('phân phối', 'dai_ly_phan_phoi'),
            ('ĐLPP', 'dai_ly_phan_phoi'), ('khách hàng', 'dai_ly_phan_phoi'),
            ('thi công', 'to_doi_thi_cong'), ('thợ', 'to_doi_thi_cong'), ('lắp đặt', 'to_doi_thi_cong'),
            ('nhà thầu', 'to_doi_thi_cong'),
            ('cửa hàng', 'cua_hang_vlxd'), ('VLXD', 'cua_hang_vlxd'), ('cửa cuốn', 'cua_hang_vlxd'),
            ('cửa gỗ', 'cua_hang_vlxd'), ('cửa nhôm', 'cua_hang_vlxd'), ('cửa thép', 'cua_hang_vlxd'),
            ('chủ nhà', 'cua_hang_vlxd'), ('chủ đầu tư', 'cua_hang_vlxd'),
        ]
        
        for kw, nhom in seeds:
            existing = conn.execute('SELECT id FROM loai_kh_mapping WHERE keyword = ?', (kw,)).fetchone()
            if not existing:
                conn.execute('INSERT INTO loai_kh_mapping (keyword, nhom_kh) VALUES (?, ?)', (kw, nhom))
        
        conn.commit()
        count = conn.execute('SELECT COUNT(*) FROM loai_kh_mapping').fetchone()[0]
        print(f'OK! Seeded {count} keyword mappings')
        conn.close()
        break
    except sqlite3.OperationalError as e:
        print(f'Attempt {attempt+1}: {e}')
        time.sleep(2)
