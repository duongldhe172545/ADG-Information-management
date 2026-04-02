import re

with open('d:/ADG-Dealer/web/templates/customers.html', 'r', encoding='utf-8') as f:
    html = f.read()

# We need the block that starts with `function editCustomer(id)` and ends just before `async function exportExcel()`
start = html.find('function editCustomer(id)')
end = html.find('async function exportExcel()')
if start > 0 and end > 0:
    code = html[start:end]
    
    with open('d:/ADG-Dealer/web/templates/review.html', 'r', encoding='utf-8') as r:
        r_html = r.read()
    
    if 'let customersData = [];' not in r_html:
        r_html = r_html.replace('let page = 1, totalPages = 1;', 'let page = 1, totalPages = 1;\nlet customersData = [];')
    
    r_html = r_html.replace('return;\n    }\n\n    body.innerHTML', 'return;\n    }\n    customersData = d.customers;\n    body.innerHTML')
    
    code = code.replace('loadData()', 'loadReview()')
    
    if 'function editCustomer(id)' not in r_html:
        r_html = r_html.replace('function goPage(delta)', code + '\nfunction goPage(delta)')
        with open('d:/ADG-Dealer/web/templates/review.html', 'w', encoding='utf-8') as w:
            w.write(r_html)
        print('COPIED')
    else:
        print('ALREADY EXISTS')
else:
    print('REGEX NOT FOUND')
