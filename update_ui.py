import re

for filename in ['d:/ADG-Dealer/web/templates/review.html', 'd:/ADG-Dealer/web/templates/customers.html']:
    with open(filename, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Replace the read-only 'Chi tiết' block with integer inputs
    chi_tiet_pattern = r'\$\{c\.c_score \!\= null \? `[\s\S]*?</div>` : \'\'\}'
    
    score_inputs = """
                <h4 style="margin-top:20px; margin-bottom:12px; font-size:13px; font-weight:600; color:var(--text-secondary)">Chỉnh sửa điểm thủ công (Dành cho tùy chọn Khác)</h4>
                <div style="display:flex; justify-content:space-between;">
                    ${Array.from({length: 9}, (_, i) => {
                        const k = `c${i+1}`;
                        return `<div class="form-group" style="flex:1; margin-right:4px; min-width:0"><label style="margin-bottom:2px; font-size:11px">C${i+1}</label>
                                <input type="number" id="e-${k}" value="${c[k]!==null && c[k]!==undefined ? c[k] : ''}" style="width:100%; font-weight:bold; color:var(--accent); text-align:center; padding:5px; font-size:12px"></div>`;
                    }).join('')}
                </div>"""
                
    if 'Chỉnh sửa điểm thủ công' not in html:
        html = re.sub(chi_tiet_pattern, score_inputs, html)

    # 2. Update saveCustomer and saveNewCustomer fields array
    html = html.replace("'chinh_sach_bh','muc_quan_tam','ban_kinh_km','quan_ly_data','kiem_soat_mua_hang','so_nguoi_gioi_thieu'",
                        "'chinh_sach_bh','muc_quan_tam','ban_kinh_km','quan_ly_data','kiem_soat_mua_hang','so_nguoi_gioi_thieu','c1','c2','c3','c4','c5','c6','c7','c8','c9'")
    
    html = html.replace("['so_kh_quay_lai','ban_kinh_km','so_nguoi_gioi_thieu'].forEach",
                        "['so_kh_quay_lai','ban_kinh_km','so_nguoi_gioi_thieu','c1','c2','c3','c4','c5','c6','c7','c8','c9'].forEach")

    # 3. For review.html only: update buttons layout
    if 'review.html' in filename:
        btn_ai_pattern = r'`<button class="btn btn-sm" onclick="aiScore\(.*?\)">(🤖 AI \${f\.label})</button>`'
        html = re.sub(btn_ai_pattern, r'`<button class="btn btn-sm" title="AI \${f.label}" onclick="aiScore(${c.id},\'${f.field}\',\'${c.thong_tin_chi_tiet||""}\')">🤖</button>`', html)
        
        # Remove "Xong" button
        html = re.sub(r'\+[\s\n]*?` <button class="btn btn-sm btn-success" style="margin-left:4px" onclick="markReviewed\(.*?\)">✅ Xong</button>`;', ';', html)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)

print("Updated both forms")
