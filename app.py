import streamlit as st
import smtplib
import urllib.request
import io
import base64
from docx import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

st.set_page_config(page_title="Plan B - Full Word Parser", page_icon="🏢", layout="wide")

CLIENT_DATABASE = [
    {"company": "บริษัท คอสเมคอน จำกัด", "contact_name": "คุณคอสเมคอน", "email": "cosmecon.th@gmail.com"},
    {"company": "บริษัท บิวทีเอสเดอร์มา จำกัด (Mediheal)", "contact_name": "คุณเมดิฮีล", "email": "beauteousderma@gmail.com"},
    {"company": "บริษัท สตาร์ริชเชอร์ส กรุ๊ป จำกัด (MG)", "contact_name": "คุณเอ็มจี", "email": "warissara.benz@starrich.co.th"}
]

DRIVE_DOCX_LINKS = {
    "Central Park (TH)": "https://docs.google.com/document/d/1UrsGlV-f3OKLugCLoJH6AzhIp0O01o9t/export?format=docx",
    "Central Park (ENG)": "https://docs.google.com/document/d/1UrsGlV-f3OKLugCLoJH6AzhIp0O01o9t/export?format=docx",
    "The 20 (TH)": "https://docs.google.com/document/d/1UrsGlV-f3OKLugCLoJH6AzhIp0O01o9t/export?format=docx"
}

# ฟังก์ชันดึงโครงสร้าง Word ทั้งหมดเรียงตามลำดับจริง
def parse_docx_element_by_element(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    file_bytes = urllib.request.urlopen(req).read()
    doc = Document(io.BytesIO(file_bytes))
    
    # สกัดรูปภาพทั้งหมดเก็บไว้ตาม rels
    image_dict = {}
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            image_dict[rel.target_ref] = rel.target_part.blob
            
    elements_structure = []
    
    # อ่านตาม Element ใน Body
    for child in doc.element.body:
        if isinstance(child, CT_P):
            p = Paragraph(child, doc)
            text = p.text.strip()
            
            # ตรวจหาการฝังรูปภาพในย่อหน้า
            p_images = []
            for rel_id in p._element.xpath('.//@r:embed'):
                if rel_id in doc.part.rels:
                    rel = doc.part.rels[rel_id]
                    if "image" in rel.target_ref:
                        p_images.append(rel.target_part.blob)
                        
            if text or p_images:
                elements_structure.append({
                    "type": "paragraph",
                    "text": text,
                    "is_bullet": p.style.name.startswith('List'),
                    "images": p_images
                })
                
        elif isinstance(child, CT_Tbl):
            tbl = Table(child, doc)
            tbl_images = []
            for row in tbl.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        for rel_id in p._element.xpath('.//@r:embed'):
                            if rel_id in doc.part.rels:
                                rel = doc.part.rels[rel_id]
                                if "image" in rel.target_ref:
                                    tbl_images.append(rel.target_part.blob)
            if tbl_images:
                elements_structure.append({
                    "type": "image_group",
                    "images": tbl_images
                })

    return elements_structure

with st.sidebar:
    st.title("Plan B Media")
    st.caption("EXACT WORD PARSER ENGINE")
    step = st.radio("ขั้นตอน", ["01 เลือกสื่อและจัดการลูกค้ารายเป้าหมาย", "02 ตรวจสอบพรีวิวและแก้ไขข้อมูล", "03 ยืนยันการส่ง Email"])

st.markdown("## 🏢 PLAN B MEDIA • EXACT CONTENT AUTOMATION")

# --- STEP 01 ---
if "01" in step:
    st.subheader("STEP 01 : เลือกสื่อ Sales Note และกลุ่มเป้าหมาย")
    
    col1, col2 = st.columns(2)
    with col1:
        selected_media = st.selectbox("สื่อที่ต้องการเสนอขาย:", list(DRIVE_DOCX_LINKS.keys()))
        sender_phone = st.text_input("ระบุเบอร์โทรศัพท์ (ใส่แทน {{Tel}}):", value="0645424441")

    with col2:
        all_client_options = [f"{c['company']} ({c['email']})" for c in CLIENT_DATABASE]
        select_all = st.checkbox("✅ เลือกทั้งหมดจากฐานข้อมูล Drive", value=True)
        default_selected = all_client_options if select_all else []
        selected_clients = st.multiselect("เลือกจากฐานข้อมูล:", options=all_client_options, default=default_selected)
        
        custom_company = st.text_input("ชื่อบริษัท/ลูกค้าใหม่:", value="", placeholder="เช่น Boploy")
        custom_email = st.text_input("อีเมลลูกค้าใหม่:", value="", placeholder="เช่น wichayada.ph@planbmedia.co.th")

    st.markdown("---")
    if st.button("🚀 ดึงข้อมูลจาก Drive และอ่านไฟล์ Word เต็มรูปแบบ", type="primary"):
        with st.spinner("กำลังอ่านไฟล์ Word แบบสมบูรณ์..."):
            docx_url = DRIVE_DOCX_LINKS[selected_media]
            doc_elements = parse_docx_element_by_element(docx_url)
            
            final_targets = [c for c in CLIENT_DATABASE if f"{c['company']} ({c['email']})" in selected_clients]
            if custom_company.strip() and custom_email.strip():
                final_targets.append({
                    "company": custom_company.strip(),
                    "contact_name": custom_company.strip(),
                    "email": custom_email.strip()
                })
                
            if not final_targets:
                st.error("กรุณาเลือกลูกค้าอย่างน้อย 1 รายการค่ะ")
            else:
                st.session_state["targets"] = final_targets
                st.session_state["doc_elements"] = doc_elements
                st.session_state["media_title"] = selected_media
                st.session_state["sender_phone"] = sender_phone
                
                st.success(f"ดึงข้อมูลครบถ้วนตามไฟล์ Word 100%! เตรียมส่ง {len(final_targets)} รายบริษัท ➔ ไปที่ STEP 02")

# --- STEP 02 ---
elif "02" in step:
    st.subheader("STEP 02 : ตรวจสอบพรีวิวเนื้อหาและรูปภาพตรงตามต้นฉบับ Word")
    if "doc_elements" in st.session_state:
        targets = st.session_state.get("targets", [])
        doc_elements = st.session_state.get("doc_elements", [])
        phone = st.session_state.get("sender_phone", "")
        
        st.write("📋 **รายชื่อลูกค้าที่จะได้รับอีเมล:**")
        updated_targets = []
        for idx, t in enumerate(targets):
            col_t1, col_t2 = st.columns([2, 2])
            with col_t1:
                c_name = st.text_input(f"ชื่อผู้รับ/ลูกค้า รายที่ {idx+1}:", value=t.get("contact_name", t["company"]), key=f"c_name_{idx}")
            with col_t2:
                st.text_input(f"อีเมล:", value=t["email"], disabled=True, key=f"c_email_{idx}")
            updated_targets.append({"company": t["company"], "contact_name": c_name, "email": t["email"]})
            
        st.session_state["targets"] = updated_targets
        st.markdown("---")
        
        first_client = updated_targets[0]
        c_name = first_client["contact_name"]
        
        # ประกอบ HTML ตามลำดับโครงสร้าง Word
        html_builder = ""
        for elem in doc_elements:
            if elem["type"] == "paragraph":
                txt = elem["text"].replace("{{Client name}}", c_name).replace("{{Tel}}", phone)
                if txt.startswith("Subject:"):
                    continue
                
                if elem["is_bullet"]:
                    html_builder += f"<li style='margin-bottom: 6px;'>{txt}</li>"
                elif txt:
                    if "จุดเด่นของสื่อ" in txt or "เรียน คุณ" in txt:
                        html_builder += f"<p style='margin-bottom: 10px;'><b>{txt}</b></p>"
                    else:
                        html_builder += f"<p style='margin-bottom: 12px;'>{txt}</p>"
                        
                # ถ้ามีย่อหน้าที่ฝังรูป
                if elem["images"]:
                    img_tds = ""
                    for img_b in elem["images"]:
                        b64 = base64.b64encode(img_b).decode()
                        img_tds += f'<td align="center" style="padding: 5px;"><img src="data:image/png;base64,{b64}" style="width:100%; max-width:300px; border-radius:4px;"></td>'
                    html_builder += f'<table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin: 15px 0;"><tr>{img_tds}</tr></table>'
                    
            elif elem["type"] == "image_group":
                img_tds = ""
                for img_b in elem["images"]:
                    b64 = base64.b64encode(img_b).decode()
                    img_tds += f'<td align="center" style="padding: 5px;"><img src="data:image/png;base64,{b64}" style="width:100%; max-width:300px; border-radius:4px;"></td>'
                html_builder += f'<table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin: 15px 0;"><tr>{img_tds}</tr></table>'

        preview_wrapper = f"""
        <div style="background-color: #ffffff; color: #333333; padding: 30px; border-radius: 8px; font-family: Arial, sans-serif; line-height: 1.6; border: 1px solid #ddd; max-width: 700px; margin: 0 auto;">
            {html_builder}
        </div>
        """
        st.components.v1.html(preview_wrapper, height=700, scrolling=True)

# --- STEP 03 ---
elif "03" in step:
    st.subheader("STEP 03 : ยืนยันการส่ง Batch Email")
    if "doc_elements" in st.session_state:
        targets = st.session_state.get("targets", [])
        doc_elements = st.session_state.get("doc_elements", [])
        phone = st.session_state.get("sender_phone", "")
        
        col_a, col_b = st.columns(2)
        with col_a:
            sender = st.text_input("อีเมลผู้ส่ง:", value="wichayada.ph@planbmedia.co.th")
        with col_b:
            pwd = st.text_input("Google App Password:", value="szqfthyetnrmuulr", type="password")
            
        if st.button("🚀 ส่ง Email ครบตามต้นฉบับ Word ทันที", type="primary"):
            try:
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.login(sender, pwd)
                
                for client in targets:
                    msg = MIMEMultipart('related')
                    msg['From'] = sender
                    msg['To'] = client['email']
                    msg['Subject'] = f"[Plan B Media] เปิดตัวสื่อใหม่ล่าสุด {st.session_state.get('media_title')}"
                    
                    msg_alt = MIMEMultipart('alternative')
                    msg.attach(msg_alt)
                    
                    c_name = client.get("contact_name", client["company"])
                    
                    # สร้างเนื้อหา HTML + แนบรูปตาม CID
                    client_html = ""
                    image_counter = 0
                    all_attached_images = []
                    
                    for elem in doc_elements:
                        if elem["type"] == "paragraph":
                            txt = elem["text"].replace("{{Client name}}", c_name).replace("{{Tel}}", phone)
                            if txt.startswith("Subject:"):
                                continue
                            if elem["is_bullet"]:
                                client_html += f"<li style='margin-bottom: 6px;'>{txt}</li>"
                            elif txt:
                                if "จุดเด่นของสื่อ" in txt or "เรียน คุณ" in txt:
                                    client_html += f"<p style='margin-bottom: 10px;'><b>{txt}</b></p>"
                                else:
                                    client_html += f"<p style='margin-bottom: 12px;'>{txt}</p>"
                                    
                            if elem["images"]:
                                img_tds = ""
                                for img_b in elem["images"]:
                                    cid_name = f"cid_img_{image_counter}"
                                    img_tds += f'<td align="center" style="padding: 5px;"><img src="cid:{cid_name}" style="width:100%; border-radius:4px;"></td>'
                                    all_attached_images.append((cid_name, img_b))
                                    image_counter += 1
                                client_html += f'<table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin: 15px 0;"><tr>{img_tds}</tr></table>'
                                
                        elif elem["type"] == "image_group":
                            img_tds = ""
                            for img_b in elem["images"]:
                                cid_name = f"cid_img_{image_counter}"
                                img_tds += f'<td align="center" style="padding: 5px;"><img src="cid:{cid_name}" style="width:100%; border-radius:4px;"></td>'
                                all_attached_images.append((cid_name, img_b))
                                image_counter += 1
                            client_html += f'<table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin: 15px 0;"><tr>{img_tds}</tr></table>'

                    final_email = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; color: #333333; line-height: 1.6; padding: 20px; background-color: #ffffff;">
                        <div style="max-width: 680px; margin: 0 auto;">
                            {client_html}
                        </div>
                    </body>
                    </html>
                    """
                    
                    msg_alt.attach(MIMEText(final_email, 'html', 'utf-8'))
                    
                    # Attach รูปภาพจริงลง MIME
                    for cid, img_bytes in all_attached_images:
                        img_mime = MIMEImage(img_bytes)
                        img_mime.add_header('Content-ID', f'<{cid}>')
                        msg.attach(img_mime)
                        
                    server.sendmail(sender, client['email'], msg.as_string())
                    
                server.quit()
                st.balloons()
                st.success("🎉 ส่งอีเมลสำเร็จเรียบร้อยแล้ว! เนื้อหาและรูปภาพเรียงตรงตามต้นฉบับ Word 100%")
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการส่ง: {str(e)}")
