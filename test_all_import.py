"""Test ALL import features before starting server."""
import sys, os
sys.path.append('d:/ADG-Dealer/web')
os.chdir('d:/ADG-Dealer/web')

import sqlite3
from services.import_service import import_rows
from services.scoring_service import score_dropdown

DB = 'd:/ADG-Dealer/web/data/app.db'
PASS = 0
FAIL = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} — {detail}")

def get_db():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db

# ═══════════════════════════════════════════════
print("\n═══ TEST 1: Insert new record ═══")
rows = [{'sdt': '0987111222', 'ho_ten': 'Nguyen Van A', 'ten_cong_ty': 'Cty Test', 'dia_chi': 'Ha Noi', 'loai_kh': 'Tổ đội thi công'}]
ins, upd, skip = import_rows(rows, merge_strategy='smart')
check("Insert count = 1", ins == 1, f"got ins={ins}")
check("Update count = 0", upd == 0, f"got upd={upd}")

db = get_db()
r = db.execute("SELECT * FROM customers WHERE sdt = '0987111222'").fetchone()
r = dict(r) if r else {}
check("Record exists in DB", bool(r), "NOT FOUND!")
check("id is NOT NULL", r.get('id') is not None, f"id={r.get('id')}")
check("ma_kh is NOT NULL", r.get('ma_kh') is not None and r.get('ma_kh') != '', f"ma_kh={r.get('ma_kh')}")
check("ma_kh format KH-XXXXX", str(r.get('ma_kh','')).startswith('KH-'), f"ma_kh={r.get('ma_kh')}")
check("is_deleted = 0", r.get('is_deleted') == 0, f"is_deleted={r.get('is_deleted')}")
check("loai_kh preserved", r.get('loai_kh') == 'Tổ đội thi công', f"loai_kh={r.get('loai_kh')}")
db.close()

# ═══════════════════════════════════════════════
print("\n═══ TEST 2: Smart merge — update address ═══")
rows2 = [{'sdt': '0987111222', 'ho_ten': 'Nguyen Van A', 'dia_chi': 'Sai Gon MOI'}]
ins2, upd2, skip2 = import_rows(rows2, merge_strategy='smart')
check("Insert = 0 (no new)", ins2 == 0, f"got ins={ins2}")
check("Update = 1 (merged)", upd2 == 1, f"got upd={upd2}")

db = get_db()
r2 = dict(db.execute("SELECT * FROM customers WHERE sdt = '0987111222'").fetchone())
check("Address updated to 'Sai Gon MOI'", r2.get('dia_chi') == 'Sai Gon MOI', f"dia_chi={r2.get('dia_chi')}")
check("ten_cong_ty kept (smart merge)", r2.get('ten_cong_ty') == 'Cty Test', f"ten_cong_ty={r2.get('ten_cong_ty')}")
total = db.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
check("Still only 1 record (no duplicate)", total == 1, f"total={total}")
db.close()

# ═══════════════════════════════════════════════
print("\n═══ TEST 3: Smart merge — empty field does NOT overwrite ═══")
rows3 = [{'sdt': '0987111222', 'ho_ten': 'Nguyen Van A', 'dia_chi': '', 'ten_cong_ty': ''}]
ins3, upd3, skip3 = import_rows(rows3, merge_strategy='smart')
check("Skipped (no real changes)", skip3 == 1 or upd3 == 0, f"ins={ins3} upd={upd3} skip={skip3}")

db = get_db()
r3 = dict(db.execute("SELECT * FROM customers WHERE sdt = '0987111222'").fetchone())
check("Address still 'Sai Gon MOI' (not blanked)", r3.get('dia_chi') == 'Sai Gon MOI', f"dia_chi={r3.get('dia_chi')}")
check("ten_cong_ty still 'Cty Test' (not blanked)", r3.get('ten_cong_ty') == 'Cty Test', f"ten_cong_ty={r3.get('ten_cong_ty')}")
db.close()

# ═══════════════════════════════════════════════
print("\n═══ TEST 4: Scoring — Unicode ≤/≥ vs ASCII <=/>=  ═══")
# C2 (biet_loi_nhuan): max score text uses ≤ in backend
check("C2 score=2 with Unicode ≤", score_dropdown('biet_loi_nhuan', 'Biết LN>15% và DSO≤60 ngày') == 2)
check("C2 score=2 with ASCII <=", score_dropdown('biet_loi_nhuan', 'Biết LN>15% và DSO<=60 ngày') == 2)
# C3 (doi_tho): max score text uses ≥ in backend
check("C3 score=2 with Unicode ≥", score_dropdown('doi_tho', '≥2 thợ cơ hữu SLA ổn') == 2)
check("C3 score=2 with ASCII >=", score_dropdown('doi_tho', '>=2 thợ cơ hữu SLA ổn') == 2)
# Other dropdowns
check("C4 score=2", score_dropdown('chinh_sach_bh', 'Tự ký BH chịu CP') == 2)
check("C5 score=2", score_dropdown('muc_quan_tam', 'Có nỗi đau cụ thể muốn giải') == 2)
check("'Khác' returns None", score_dropdown('biet_loi_nhuan', 'Khác') is None)

# ═══════════════════════════════════════════════
print("\n═══ TEST 5: Duplicate detection across same import batch ═══")
db = get_db()
db.execute("DELETE FROM customers")
db.execute("DELETE FROM sqlite_sequence WHERE name='customers'")
db.commit()
db.close()

# Two rows with same SĐT in one batch
batch = [
    {'sdt': '0912345678', 'ho_ten': 'Anh A', 'dia_chi': 'HN'},
    {'sdt': '0912345678', 'ho_ten': 'Anh A', 'dia_chi': 'SG'},
]
ins5, upd5, skip5 = import_rows(batch, merge_strategy='smart')
db = get_db()
total5 = db.execute("SELECT COUNT(*) FROM customers WHERE sdt = '0912345678'").fetchone()[0]
r5 = dict(db.execute("SELECT * FROM customers WHERE sdt = '0912345678'").fetchone())
check("Only 1 record for same SĐT in batch", total5 == 1, f"total={total5}")
check("Address = 'SG' (2nd row merged)", r5.get('dia_chi') == 'SG', f"dia_chi={r5.get('dia_chi')}")
check("is_deleted = 0", r5.get('is_deleted') == 0, f"is_deleted={r5.get('is_deleted')}")
db.close()

# ═══════════════════════════════════════════════
print(f"\n{'='*50}")
print(f"RESULTS: {PASS} passed, {FAIL} failed")
if FAIL == 0:
    print("🎉 ALL TESTS PASSED! Safe to start server.")
else:
    print("⚠️  SOME TESTS FAILED — fix before starting server!")
