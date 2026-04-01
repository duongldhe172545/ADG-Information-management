import pandas as pd
import os

def clean_excel():
    file_path = r'd:\ADG-Dealer\KhachHang_TatCa_2026-03-30 (1).xlsx'
    out_path = r'd:\ADG-Dealer\KhachHang_TatCa_2026-03-30_Cleaned.xlsx'
    
    print(f"Reading {file_path}...")
    df = pd.read_excel(file_path)
    
    # Bỏ các dòng không có cột SĐT
    if 'SĐT' not in df.columns:
        print("Lỗi: Không tìm thấy cột SĐT!")
        return
        
    original_len = len(df)
    
    # Xoá hoàn toàn những dòng rác không có dữ liệu SĐT (NaN)
    df = df.dropna(subset=['SĐT'])
    
    # Tạo chuỗi SĐT để check trùng (bỏ khoảng trắng hai đầu để chính xác)
    df['SĐT_str'] = df['SĐT'].astype(str).str.strip()
    
    # Xoá tiếp các dòng số ĐT rỗng ('') hoặc ghi là 'nan'
    df = df[df['SĐT_str'] != '']
    df = df[df['SĐT_str'].str.lower() != 'nan']
    
    # Tiến hành xoá trùng lặp, giữ lại dòng xuất hiện ĐẦU TIÊN (bỏ các bản copy ở dưới đáy file)
    df_clean = df.drop_duplicates(subset=['SĐT_str'], keep='first').copy()
    
    # Bỏ cột hỗ trợ
    df_clean.drop(columns=['SĐT_str'], inplace=True)
    
    print(f"Bắt đầu xuất file cleaned, số dòng: {len(df_clean)}...")
    df_clean.to_excel(out_path, index=False)
    
    print("="*40)
    print(f"Hoàn tất dọn dẹp!")
    print(f"Tổng số dòng ban đầu: {original_len}")
    print(f"Số dòng SẠCH (đã lọc rác + xoá trùng): {len(df_clean)}")
    print(f"File mới đã được lưu tại: {out_path}")

if __name__ == '__main__':
    clean_excel()
