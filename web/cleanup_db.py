"""Clean up DB: remove c10-c15 and extra scoring_weights columns."""
import sqlite3
import sys

DB = r'd:\ADG-Dealer\web\data\app.db'

def main():
    conn = sqlite3.connect(DB, timeout=30)
    
    # 1. Remove c10-c15 from customers
    cols = [r[1] for r in conn.execute('PRAGMA table_info(customers)').fetchall()]
    drop_cols = {'c10','c11','c12','c13','c14','c15'}
    found = drop_cols & set(cols)
    
    if found:
        keep_cols = [c for c in cols if c not in drop_cols]
        cols_str = ', '.join(keep_cols)
        print(f"Removing {sorted(found)} from customers...")
        conn.executescript(f"""
            BEGIN;
            CREATE TABLE customers_backup AS SELECT {cols_str} FROM customers;
            DROP TABLE customers;
            ALTER TABLE customers_backup RENAME TO customers;
            COMMIT;
        """)
        print("  Done!")
    else:
        print("c10-c15 not found in customers, skipping.")
    
    # 2. Clean scoring_weights extra columns
    sw_cols = [r[1] for r in conn.execute('PRAGMA table_info(scoring_weights)').fetchall()]
    base = {'c_id', 'name', 'weight'}
    extra = [c for c in sw_cols if c not in base]
    
    if extra:
        print(f"Removing {extra} from scoring_weights...")
        conn.executescript("""
            BEGIN;
            CREATE TABLE sw_backup AS SELECT c_id, name, weight FROM scoring_weights;
            DROP TABLE scoring_weights;
            ALTER TABLE sw_backup RENAME TO scoring_weights;
            COMMIT;
        """)
        print("  Done!")
    else:
        print("scoring_weights clean, skipping.")
    
    # Verify
    final_cols = [r[1] for r in conn.execute('PRAGMA table_info(customers)').fetchall()]
    c_cols = [c for c in final_cols if c.startswith('c')]
    print(f"\nFinal check - C columns: {c_cols}")
    
    sw_final = [r[1] for r in conn.execute('PRAGMA table_info(scoring_weights)').fetchall()]
    print(f"Final check - scoring_weights columns: {sw_final}")
    
    count = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    print(f"Total customers: {count}")
    
    conn.close()
    print("\n✅ Cleanup complete!")

if __name__ == '__main__':
    main()
