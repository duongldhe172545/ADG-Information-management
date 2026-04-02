import re

def process_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Remove the "Ghi chú Sale" tab button
    html = re.sub(r'<button class="tab-btn" onclick="switchTab\(event, \'tab-note\'\)">Ghi chú Sale</button>\s*', '', html)

    # 2. Extract the tab-note div content (the textarea)
    note_pattern = r'<div id="tab-note" class="tab-content">.*?<label>Thông Tin Chi Tiết \(Log làm việc\)</label>(.*?)</div>\s*</div>'
    match = re.search(note_pattern, html, re.DOTALL)
    
    if match:
        textarea_content = match.group(1).strip()
        # Remove the whole tab-note block
        html = re.sub(r'<div id="tab-note" class="tab-content">.*?</div>\s*(?=</div>)', '', html, flags=re.DOTALL)
        
        # Insert the textarea into the bottom of tab-chung
        # Finds the closing div of tab-chung form-grid and appends the full-width row
        insert_marker = r'(<div id="tab-chung" class="tab-content active">\s*<div class="form-grid">.*?</div>)'
        new_textarea = f'\n                <div class="form-group full" style="margin-top:12px;">\n                    <label>Thông Tin Chi Tiết (Log làm việc)</label>\n                    {textarea_content}\n                </div>'
        html = re.sub(insert_marker, r'\1' + new_textarea, html, flags=re.DOTALL)

    # 3. Ensure switchTab is correctly defined at the end of the script tag (before closing </script>)
    if 'function switchTab(evt, id)' not in html:
        switch_tab_code = """
    function switchTab(evt, id) {
        const tabs = document.querySelectorAll('#modal-body .tab-content');
        tabs.forEach(t => t.classList.remove('active'));
        const btns = document.querySelectorAll('#modal-body .tab-btn');
        btns.forEach(b => b.classList.remove('active'));
        document.getElementById(id).classList.add('active');
        evt.currentTarget.classList.add('active');
    }
"""
        html = html.replace('</script>', switch_tab_code + '</script>')

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Updated {filename}")

for fname in ['d:/ADG-Dealer/web/templates/customers.html', 'd:/ADG-Dealer/web/templates/review.html']:
    process_file(fname)
