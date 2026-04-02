import sqlite3

db = sqlite3.connect(r'd:\ADG-Dealer\web\data\app.db')
mappings=[
    ('tổ đội','to_doi_thi_cong'),
    ('thi công','to_doi_thi_cong'),
    ('thợ','to_doi_thi_cong'),
    ('nhóm thợ','to_doi_thi_cong'),
    ('đội thợ','to_doi_thi_cong'),
    ('nhà thầu','to_doi_thi_cong'),
    ('thầu','to_doi_thi_cong'),
    ('xây dựng','to_doi_thi_cong'),
    ('xây','to_doi_thi_cong'),
    ('xưởng','xuong_san_xuat'),
    ('sản xuất','xuong_san_xuat'),
    ('sx','xuong_san_xuat'),
    ('gia công','xuong_san_xuat'),
    ('chế biến','xuong_san_xuat'),
    ('showroom','showroom'),
    ('nội thất','showroom'),
    ('thiết kế','showroom'),
    ('decor','showroom'),
    ('trang trí','showroom'),
    ('đại lý','dai_ly_phan_phoi'),
    ('phân phối','dai_ly_phan_phoi'),
    ('nhà phân phối','dai_ly_phan_phoi'),
    ('npp','dai_ly_phan_phoi'),
    ('vlxd','cua_hang_vlxd'),
    ('vật liệu','cua_hang_vlxd'),
    ('cửa hàng','cua_hang_vlxd'),
    ('bán lẻ','cua_hang_vlxd'),
    ('kinh doanh','cua_hang_vlxd')
]

db.execute('DELETE FROM loai_kh_mapping');
for m in mappings:
    db.execute('INSERT INTO loai_kh_mapping (keyword, nhom_kh) VALUES (?,?)', m)

db.commit()
print('Mapping items restored:', db.execute('SELECT COUNT(*) FROM loai_kh_mapping').fetchone()[0])
db.close()
print('Ready for action!')
