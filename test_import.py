import sys
import traceback

try:
    sys.path.append('d:/ADG-Dealer/web')
    from app import app
    from services import import_service
    import os

    with app.app_context():
        filepath = 'd:/ADG-Dealer/web/uploads/v0.5.xlsx'
        if not os.path.exists(filepath):
            files = [f for f in os.listdir('d:/ADG-Dealer/web/uploads') if f.endswith('.xlsx')]
            if files:
                filepath = os.path.join('d:/ADG-Dealer/web/uploads', files[0])
            else:
                print('No excel file found.')
                sys.exit(1)
        
        print('Testing with file:', filepath)
        rows, errors = import_service.parse_excel(filepath)
        print('Parsed excel, rows:', len(rows), 'errors:', errors)
        
        if rows:
            print('Importing just 1 row...')
            ins, upd, skip = import_service.import_rows(rows[:2], merge_strategy='smart')
            print('Success!', ins, upd, skip)
        else:
            print('No rows parsed')
except Exception as e:
    print('Failed with exception:')
    traceback.print_exc()
