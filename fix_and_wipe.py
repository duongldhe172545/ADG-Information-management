import sqlite3

db = sqlite3.connect('d:/ADG-Dealer/web/data/app.db')

# 1. Revert nhom_kh back to snake_case
revert_map = {
    'Xưởng sản xuất': 'xuong_san_xuat',
    'Showroom': 'showroom',
    'Đại lý phân phối': 'dai_ly_phan_phoi',
    'Tổ đội thi công': 'to_doi_thi_cong',
    'Cửa hàng VLXD': 'cua_hang_vlxd',
    'Chưa xác định': 'chua_xac_dinh',
}
for vn_val, snake_val in revert_map.items():
    db.execute("UPDATE loai_kh_mapping SET nhom_kh = ? WHERE nhom_kh = ?", (snake_val, vn_val))
db.commit()

# Verify
rows = db.execute("SELECT DISTINCT nhom_kh FROM loai_kh_mapping").fetchall()
print("nhom_kh values after revert:", [r[0] for r in rows])

# 2. Wipe customers + change_log
db.execute("DELETE FROM customers")
db.execute("DELETE FROM change_log")
try:
    db.execute("DELETE FROM sqlite_sequence WHERE name='customers'")
    db.execute("DELETE FROM sqlite_sequence WHERE name='change_log'")
except:
    pass
db.commit()

print("Customers:", db.execute("SELECT count(*) FROM customers").fetchone()[0])
print("Change_log:", db.execute("SELECT count(*) FROM change_log").fetchone()[0])
db.close()
print("Done!")
