import re

def process_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Fix parseInt() || null bug
    old_parse = r"\['so_kh_quay_lai','ban_kinh_km','so_nguoi_gioi_thieu','c1','c2','c3','c4','c5','c6','c7','c8','c9'\]\.forEach\(f => \{\s*if \(data\[f\]\) data\[f\] = parseInt\(data\[f\]\) \|\| null;\s*\}\);"
    new_parse = """['so_kh_quay_lai','ban_kinh_km','so_nguoi_gioi_thieu','c1','c2','c3','c4','c5','c6','c7','c8','c9'].forEach(f => {
            if (data[f] !== null && data[f] !== '') {
                data[f] = parseInt(data[f]);
                if (isNaN(data[f])) data[f] = null;
            } else {
                data[f] = null;
            }
        });"""
    html = re.sub(old_parse, new_parse, html)

    # 2. Add min=0 max=2 to inputs
    old_input = r'<input type="number" id="e-\$\{k\}" value="\$\{c\[k\]!==null && c\[k\]!==undefined \? c\[k\] : \'\'\}" style="width:100\%; font-weight:bold; color:var\(--accent\); text-align:center; padding:5px; font-size:12px">'
    new_input = r'<input type="number" id="e-${k}" value="${c[k]!==null && c[k]!==undefined ? c[k] : \'\'}" min="0" max="2" style="width:100%; font-weight:bold; color:var(--accent); text-align:center; padding:5px; font-size:12px">'
    html = re.sub(old_input, new_input, html)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Fixed {filename}")

for fname in ['d:/ADG-Dealer/web/templates/customers.html', 'd:/ADG-Dealer/web/templates/review.html']:
    process_file(fname)
