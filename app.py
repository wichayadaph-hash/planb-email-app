import streamlit as st
import smtplib
import urllib.request
import io
import base64
from docx import Document
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

st.set_page_config(page_title="Plan B - Dynamic Email Automation", page_icon="🏢", layout="wide")

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

def parse_docx_from_url(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    file_bytes = urllib.request.urlopen(req).read()
    doc = Document(io.BytesIO(file_bytes))
    
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip() != ""]
    
    images = []
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            img_part = rel.target_part
            images.append(img_part.blob)
            
    return paragraphs, images

with st.sidebar:
    st.title("Plan B Media")
    st.caption("EMAIL AUTOMATION ENGINE")
    step = st.radio("ขั้นตอน", ["01 เลือกสื่อและจัดการลูกค้ารายเป้าหมาย", "02 ตรวจสอบพรีวิวและแก้ไขข้อมูล", "03 ยืนยันการส่ง Email"])

st.markdown("## 🏢 PLAN B MEDIA • DYNAMIC EMAIL ENGINE")

# --- STEP 01 ---
if "01" in step:
    st.subheader("STEP 01 : เลือกสื่อ Sales Note และลูกค้ารายเป้าหมาย")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("📂 **1. เลือกไฟล์ Sales Note จาก Google Drive:**")
        selected_media = st.selectbox("สื่อที่ต้องการเสนอขาย:", list(DRIVE_DOCX_LINKS.keys()))
        
        st.markdown("---")
        st.write("📞 **2. เบอร์โทรติดต่อกลับของคุณพลอย/ทีมงาน:**")
        sender_phone = st.text_input("ระบุเบอร์โทรศัพท์ (จะนำไปใส่แทน {{Tel}} ในไฟล์ Word):", value="02-123-4567")

    with col2:
        st.write("👥 **3. เลือกหรือกรอกลูกค้ารายเป้าหมาย:**")
        
        all_client_options = [f"{c['company']} ({c['email']})" for c in CLIENT_DATABASE]
        select_all = st.checkbox("✅ เลือกทั้งหมดจากฐานข้อมูล Drive", value=True)
        default_selected = all_client_options if select_all else []
        
        selected_clients = st.multiselect("เลือกจากฐานข้อมูล:", options=all_client_options, default=default_selected)
        
        st.caption("➕ เพิ่ม/แก้ไข ข้อมูลลูกค้ารายใหม่:")
        custom_company = st.text_input("ชื่อบริษัท/ชื่อลูกค้าใหม่:", value="", placeholder="เช่น Boploy / บริษัท เอสซีบี เอกซ์ จำกัด")
        custom_contact = st.text_input("ชื่อผู้รับ (Contact Name):", value="", placeholder="เช่น คุณพลอย")
        custom_email = st.text_input("อีเมลลูกค้าใหม่:", value="", placeholder="เช่น wichayada.ph@planbmedia.co.th")

    st.markdown("---")
    if st.button("🚀 ดึงข้อมูลจาก Drive และเตรียมส่ง", type="primary"):
        with st.spinner("กำลังโหลดข้อมูล..."):
            docx_url = DRIVE_DOCX_LINKS[selected_media]
            paragraphs, images = parse_docx_from_url(docx_url)
            
            final_targets = []
            for c in CLIENT_DATABASE:
                if f"{c['company']} ({c['email']})" in selected_clients:
                    final_targets.append(c)
                    
            if custom_company.strip() and custom_email.strip():
                final_targets.append({
                    "company": custom_company.strip(),
                    "contact_name": custom_contact.strip() if custom_contact.strip() else custom_company.strip(),
                    "email": custom_email.strip()
                })
                
            if not final_targets:
                st.error("กรุณาเลือกลูกค้าอย่างน้อย 1 รายการครับ")
            else:
                st.session_state["targets"] = final_targets
                st.session_state["docx_paragraphs"] = paragraphs
                st.session_state["docx_images"] = images
                st.session_state["media_title"] = selected_media
                st.session_state["sender_phone"] = sender_phone
                
                st.success(f"ดึงข้อมูลสำเร็จ! พบลูกค้า {len(final_targets)} รายบริษัท ➔ ไปที่ STEP 02")

# --- STEP 02 ---
elif "02" in step:
    st.subheader("STEP 02 : ตรวจสอบพรีวิวและแก้ไขข้อมูลก่อนส่ง")
    if "docx_paragraphs" in st.session_state:
        targets = st.session_state.get("targets", [])
        paragraphs = st.session_state.get("docx_paragraphs", [])
        images = st.session_state.get("docx_images", [])
        phone = st.session_state.get("sender_phone", "")
        
        st.write("📋 **รายชื่อลูกค้าที่จะได้รับอีเมล (สามารถแก้ไขชื่อผู้รับได้):**")
        
        # ช่องทางปรับแต่งชื่อผู้รับสำหรับแต่ละบริษัท
        updated_targets = []
        for idx, t in enumerate(targets):
            col_t1, col_t2 = st.columns([2, 2])
            with col_t1:
                c_name = st.text_input(f"ชื่อผู้รับ/ลูกค้า รายที่ {idx+1}:", value=t.get("contact_name", t["company"]), key=f"c_name_{idx}")
            with col_t2:
                st.text_input(f"อีเมล:", value=t["email"], disabled=True, key=f"c_email_{idx}")
            
            updated_targets.append({
                "company": t["company"],
                "contact_name": c_name,
                "email": t["email"]
            })
            
        st.session_state["targets"] = updated_targets
        st.markdown("---")
        
        st.caption("ตัวอย่างพรีวิวอีเมล (แทนค่า {{Client name}} และ {{Tel}} อัตโนมัติ + แสดงรูปภาพจริง):")
        
        first_client = updated_targets[0]
        client_name = first_client["contact_name"]
        
        # รวมเนื้อหาและแทนค่าตัวแปร {{Client name}}, {{Tel}} และบรรทัด Subject ซ้ำ
        body_html = ""
        for p in paragraphs:
            # ข้ามบรรทัดที่เป็น Subject ซ้ำในเนื้อหา
            if p.startswith("Subject:"):
                continue
            
            # แทนค่า {{Client name}} และ {{Tel}}
            p_clean = p.replace("{{Client name}}", client_name).replace("{{Tel}}", phone)
            body_html += f"<p style='margin-bottom: 12px;'>{p_clean}</p>"
            
        # สร้างรูปภาพแบบ Base64 สำหรับแสดงผลใน HTML Preview ให้ภาพขึ้น 100%
        img_preview_html = ""
        if len(images) >= 2:
            b64_img1 = base64.b64encode(images[0]).decode()
            b64_img2 = base64.b64encode(images[1]).decode()
            img_preview_html = f"""
            <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin: 20px 0;">
                <tr>
                    <td width="49%" align="center"><img src="data:image/png;base64,{b64_img1}" style="width:100%; border-radius:4px;"></td>
                    <td width="2%"></td>
                    <td width="49%" align="center"><img src="data:image/png;base64,{b64_img2}" style="width:100%; border-radius:4px;"></td>
                </tr>
            </table>
            """
        elif len(images) == 1:
            b64_img1 = base64.b64encode(images[0]).decode()
            img_preview_html = f'<div style="text-align:center; margin: 20px 0;"><img src="data:image/png;base64,{b64_img1}" style="max-width:100%; border-radius:4px;"></div>'

        preview_html = f"""
        <div style="background-color: #ffffff; color: #333333; padding: 25px; border-radius: 8px; font-family: Arial, sans-serif; line-height: 1.6; border: 1px solid #ddd; max-width: 680px;">
            {body_html}
            {img_preview_html}
        </div>
        """
        st.components.v1.html(preview_html, height=550, scrolling=True)

# --- STEP 03 ---
elif "03" in step:
    st.subheader("STEP 03 : ยืนยันการส่ง Batch Email")
    if "docx_paragraphs" in st.session_state:
        targets = st.session_state.get("targets", [])
        paragraphs = st.session_state.get("docx_paragraphs", [])
        images = st.session_state.get("docx_images", [])
        phone = st.session_state.get("sender_phone", "")
        
        col_a, col_b = st.columns(2)
        with col_a:
            sender = st.text_input("อีเมลผู้ส่ง:", value="wichayada.ph@planbmedia.co.th")
        with col_b:
            pwd = st.text_input("Google App Password:", value="szqfthyetnrmuulr", type="password")
            
        if st.button("🚀 ส่ง Email หาพร้อมกันทุกบริษัททันที", type="primary"):
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
                    
                    client_body = ""
                    for p in paragraphs:
                        if p.startswith("Subject:"):
                            continue
                        p_clean = p.replace("{{Client name}}", c_name).replace("{{Tel}}", phone)
                        client_body += f"<p style='margin-bottom: 12px;'>{p_clean}</p>"
                        
                    if len(images) >= 2:
                        img_html = """
                        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin: 20px 0;">
                            <tr>
                                <td width="49%" align="center"><img src="cid:word_img_0" style="width:100%; border-radius:4px;"></td>
                                <td width="2%"></td>
                                <td width="49%" align="center"><img src="cid:word_img_1" style="width:100%; border-radius:4px;"></td>
                            </tr>
                        </table>
                        """
                    elif len(images) == 1:
                        img_html = '<div style="text-align:center; margin: 20px 0;"><img src="cid:word_img_0" style="max-width:100%; border-radius:4px;"></div>'
                    else:
                        img_html = ""

                    final_email_html = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; color: #333333; line-height: 1.6; padding: 20px; background-color: #ffffff;">
                        <div style="max-width: 650px; margin: 0 auto;">
                            {client_body}
                            {img_html}
                        </div>
                    </body>
                    </html>
                    """
                    
                    msg_alt.attach(MIMEText(final_email_html, 'html', 'utf-8'))
                    
                    for idx, img_bytes in enumerate(images):
                        img_mime = MIMEImage(img_bytes)
                        img_mime.add_header('Content-ID', f'<word_img_{idx}>')
                        msg.attach(img_mime)
                        
                    server.sendmail(sender, client['email'], msg.as_string())
                    
                server.quit()
                st.balloons()
                st.success("🎉 ส่งอีเมลสำเร็จ! แทนค่าชื่อลูกค้า เบอร์โทร และแสดงรูปภาพถูกต้องเรียบร้อย")
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการส่ง: {str(e)}")
