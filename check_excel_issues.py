import openpyxl
from collections import defaultdict

def main():
    wb = openpyxl.load_workbook(r'd:\ADG-Dealer\KhachHang_TatCa_2026-03-30 (1).xlsx', data_only=True)
    sheet = wb.active
    rows = list(sheet.iter_rows(values_only=True))

    headers = rows[0]
    name_col = headers.index('Họ Tên Chủ') if 'Họ Tên Chủ' in headers else -1
    company_col = headers.index('Tên Công Ty/Đơn Vị') if 'Tên Công Ty/Đơn Vị' in headers else -1
    phone_col = headers.index('SĐT') if 'SĐT' in headers else -1

    empty_rows = []
    no_name_company = []
    phones = defaultdict(list)

    for idx, r in enumerate(rows[1:], start=2):
        # Check empty
        if not any(c is not None and str(c).strip() for c in r):
            if len(empty_rows) < 10:
                empty_rows.append(idx)
            continue
        
        # Check no name/company
        has_name = name_col >= 0 and r[name_col] and str(r[name_col]).strip()
        has_company = company_col >= 0 and r[company_col] and str(r[company_col]).strip()
        if not has_name and not has_company:
            if len(no_name_company) < 5:
                no_name_company.append((idx, r[phone_col]))
            continue
            
        # Check phone
        p = str(r[phone_col] or '').strip()
        if p:
            phones[p].append((idx, str(r[name_col] or ''), str(r[company_col] or '')))

    # Find duplicates
    dupe_samples = []
    for p, info in phones.items():
        if len(info) > 1:
            dupe_samples.append((p, info))
            if len(dupe_samples) >= 5:
                break

    print('--- Các dòng trắng hoàn toàn ---')
    print(f'Dòng số: {empty_rows}')

    print('\n--- Các dòng bị bỏ qua vì không có Tên/Công ty ---')
    for idx, p in no_name_company:
        print(f'Dòng số {idx}: (SĐT: {p})')

    print('\n--- Một số SĐT bị trùng (xuất hiện nhiều lần) ---')
    for p, info in dupe_samples:
        print(f'SĐT {p} xuất hiện ở các dòng:')
        for idx, name, company in info:
            print(f' - Dòng {idx} | Tên: {name} | Công ty: {company}')

if __name__ == '__main__':
    main()
