import sys
sys.path.append('d:/ADG-Dealer/web')
from database.db import get_db
from list_dir import * # mock
from services import import_service
import sqlite3

db = sqlite3.connect('d:/ADG-Dealer/web/data/app.db')
db.row_factory = sqlite3.Row

# insert fake
db.execute("DELETE FROM customers WHERE sdt = '0987123456'")
cursor = db.execute("INSERT INTO customers (ten_cong_ty, sdt, loai_kh, is_deleted) VALUES ('ABC Cũ', '0987123456', 'To doi thi cong', 0)")
cid = cursor.lastrowid
db.commit()

rows = [
    {
        'sdt': '0987123456',
        'ten_cong_ty': 'ABC MỚI',
        'loai_kh': 'Xưởng sản xuất'
    }
]

import_service.import_rows(rows, merge_strategy='smart')

after = db.execute("SELECT * FROM customers WHERE id = ?", (cid,)).fetchone()
print("After import:", dict(after))
db.close()
