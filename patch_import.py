import re

filename = 'd:/ADG-Dealer/web/services/import_service.py'
with open(filename, 'r', encoding='utf-8') as f:
    code = f.read()

mapping_code = """
    # Load loai_kh mapping
    rows_mapping = conn.execute("SELECT keyword, nhom_kh FROM loai_kh_mapping").fetchall()
    mappings = {r['keyword'].lower(): r['nhom_kh'] for r in rows_mapping}

    for row in rows:
        # Remove internal fields
        data = {k: v for k, v in row.items() if not k.startswith('_')}

        # Auto-map Loại KH
        if 'loai_kh' in data and data['loai_kh']:
            val = str(data['loai_kh']).strip()
            val_lower = val.lower()
            mapped_val = val
            for keyword, target in mappings.items():
                if keyword in val_lower:
                    mapped_val = target
                    break
            data['loai_kh'] = mapped_val
"""

old_code = """
    for row in rows:
        # Remove internal fields
        data = {k: v for k, v in row.items() if not k.startswith('_')}
"""

if '# Auto-map Loại KH' not in code:
    code = code.replace(old_code, mapping_code)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(code)
    print("Patched import_service.py with Auto-map Loại KH")
else:
    print("Already patched")
