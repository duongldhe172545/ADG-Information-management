import sqlite3
import traceback

def main():
    try:
        conn = sqlite3.connect(r'd:\ADG-Dealer\web\data\app.db', timeout=10)
        
        print("Xóa customers...")
        conn.execute('DELETE FROM customers')
        
        print("Xóa change_log...")
        conn.execute('DELETE FROM change_log')
        
        print("Reset ID auto increment...")
        try:
            conn.execute("DELETE FROM sqlite_sequence WHERE name='customers'")
        except Exception:
            pass
            
        print("Commiting...")
        conn.commit()
        conn.close()
        print('Đã dọn dẹp xong dữ liệu Database!')
    except Exception as e:
        print(f"Lỗi: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    main()
