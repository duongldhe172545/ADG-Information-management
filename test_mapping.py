from database import get_db
from services import import_service
import traceback

try:
    with get_db() as conn:
        print('DB accessed')
    
    filepath = 'web/uploads/v0.5.xlsx'
    
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
