import csv

vals = {}
with open('d:/ADG-Dealer/KhachHang_TatCa_2026-03-30 (1).csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    headers = reader.fieldnames
    print("CSV Headers:", headers)
    for r in reader:
        v = r.get('Loại KH', '').strip() if r.get('Loại KH') else 'EMPTY'
        vals[v] = vals.get(v, 0) + 1

print(f"\nTotal: {sum(vals.values())} rows")
print(f"Distinct Loai KH values: {len(vals)}")
print()
for v, c in sorted(vals.items(), key=lambda x: -x[1]):
    print(f"  {c:>5}x  '{v}'")
