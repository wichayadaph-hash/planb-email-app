import streamlit as st
import smtplib
import urllib.request
import io
import re
import mammoth
import base64
import fitz  # PyMuPDF
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

st.set_page_config(page_title="Plan B Media Email Automation", page_icon="🏢", layout="wide")

CLIENT_DATABASE = [
    {"company": "บริษัท คอสเมคอน จำกัด", "contact_name": "คุณคอสเมคอน", "email": "cosmecon.th@gmail.com"},
    {"company": "บริษัท บิวทีเอสเดอร์มา จำกัด (Mediheal)", "contact_name": "คุณเมดิฮีล", "email": "beauteousderma@gmail.com"},
    {"company": "บริษัท สตาร์ริชเชอร์ส กรุ๊ป จำกัด (MG)", "contact_name": "คุณเอ็มจี", "email": "warissara.benz@starrich.co.th"}
]

# 📌 ลิงก์ดึงไฟล์ตรง ปรับให้ดึงจาก ID ไฟล์เดี่ยวเพื่อป้องกัน HTTP Error
DRIVE_DOCX_LINKS = {
    "Central Park (TH)": {"url": "https://docs.google.com/document/d/1UrsGlV-f3OKLugCLoJH6AzhIp0O01o9t/export?format=docx", "type": "docx"},
    "Central Park (ENG)": {"url": "https://docs.google.com/document/d/1UrsGlV-f3OKLugCLoJH6AzhIp0O01o9t/export?format=docx", "type": "docx"},
    "The 20 (TH)": {"url": "https://docs.google.com/document/d/1UrsGlV-f3OKLugCLoJH6AzhIp0O01o9t/export?format=docx", "type": "docx"},
    
    # สำหรับ Outthere
    "Outthere - Real-life Experience Ecosystem 2026": {"url": "https://docs.google.com/document/d/1UrsGlV-f3OKLugCLoJH6AzhIp0O01o9t/export?format=docx", "type": "docx"},
    "Outthere - Sports Marketing Strategy": {"url": "https://docs.google.com/document/d/1UrsGlV-f3OKLugCLoJH6AzhIp0O01o9t/export?format=docx", "type": "docx"},
    "Outthere - Beauty 3D OOH Campaign": {"url": "https://docs.google.com/document/d/1UrsGlV-f3OKLugCLoJH6AzhIp0O01o9t/export?format=docx", "type": "docx"}
}

def convert_docx_to_perfect_html(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        file_bytes = urllib.request.urlopen(req).read()
        image_store = []
        
        def convert_image(image):
            with image.open() as image_bytes:
                data = image_bytes.read()
                cid = f"img_{len(image_store)}"
                image_store.append((cid, data, image.content_type))
                return {"src": f"cid:{cid}"}

        result = mammoth.convert_to_html(io.BytesIO(file_bytes), convert_image=mammoth.images.inline(convert_image))
        raw_html = result.value
        
        subject = "เปิดตัวสื่อใหม่ล่าสุดจาก Plan B Media"
        subject_match = re.search(r'Subject:\s*(.*?)(</p>|<br>|\n|$)', raw_html, re.IGNORECASE)
        if subject_match:
            subject = subject_match.group(1).strip()
            subject = re.sub(r'<[^>]*>', '', subject)
            raw_html = re.sub(r'<p>.*?Subject:\s*.*?</p>', '', raw_html, flags=re.IGNORECASE)

        return raw_html, subject, image_store, None
    except Exception as e:
        return None, None, None, str(e)

def convert_pdf_to_perfect_html(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        file_bytes = urllib.request.urlopen(req).read()
        
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        image_store = []
        html_parts = ["<p>เรียน {{Client name}}</p><p>ทาง Plan B Media ขอส่งข้อมูลสื่อ Outthere ล่าสุดให้พิจารณาค่ะ</p>"]
        
        for page_index in range(len(doc)):
            page = doc[page_index]
            pix = page.get_pixmap(dpi=150)
            img_bytes = pix.tobytes("png")
            
            cid = f"img_pdf_{page_index}"
            image_store.append((cid, img_bytes, "image/png"))
            html_parts.append(f'<div style="margin-bottom: 15px;"><img src="cid:{cid}" style="width: 100%; height: auto; display: block;" /></div>')
            
        html_parts.append("<p>หากต้องการข้อมูลเพิ่มเติม สามารถติดต่อสอบถามได้ที่เบอร์ {{Tel}} ค่ะ</p>")
        subject = "Plan B Media - สื่อใหม่ล่าสุด Outthere Newsletter"
        return "".join(html_parts), subject, image_store, None
    except Exception as e:
        return None, None, None, str(e)

EMAIL_CSS = """
<style>
    body, div {
        font-family: 'Aptos', 'Calibri', 'Tahoma', sans-serif !important;
        font-size: 16px !important;
        color: #222222 !important;
        line-height: 1.6 !important;
    }
    img {
        max-width: 100% !important;
        height: auto !important;
        display: block !important;
        border-radius: 4px !important;
    }
</style>
"""

with st.sidebar:
    st.title("Plan B Media")
    st.caption("EMAIL AUTOMATION SYSTEM")
    step = st.radio("ขั้นตอน", ["01 เลือกสื่อและจัดการกลุ่มเป้าหมาย", "02 ตรวจสอบพรีวิวและแก้ไขข้อมูล", "03 ยืนยันการส่ง Email"])

st.markdown("## 🏢 PLAN B MEDIA • AUTOMATION ENGINE")

# --- STEP 01 ---
if "01" in step:
    st.subheader("STEP 01 : เลือกสื่อ Sales Note และระบุข้อมูลลูกค้ารายเป้าหมาย")
    col1, col2 = st.columns(2)
    with col1:
        selected_media = st.selectbox("📌 เลือกสื่อ/หัวข้อ Sales Note ที่ต้องการเสนอขาย:", list(DRIVE_DOCX_LINKS.keys()))
        sender_phone = st.text_input("เบอร์โทรศัพท์ติดต่อกลับ (แทนค่า {{Tel}}):", value="0645424441")

    with col2:
        st.write("👥 **เลือกลูกค้าจากฐานข้อมูล:**")
        all_client_options = [f"{c['company']} - {c['contact_name']}" for c in CLIENT_DATABASE]
        select_all = st.checkbox("✅ เลือกทั้งหมด", value=True)
        default_selected = all_client_options if select_all else []
        selected_clients = st.multiselect("รายการที่เลือก:", options=all_client_options, default=default_selected)
        
        st.caption("➕ เพิ่มลูกค้ารายใหม่:")
        custom_company = st.text_input("ชื่อบริษัท:", value="")
        custom_contact = st.text_input("ชื่อผู้รับ/ลูกค้า:", value="")
        custom_email = st.text_input("อีเมลลูกค้า:", value="")

    st.markdown("---")
    if st.button("🚀 ดึงไฟล์ของหัวข้อที่เลือก และประมวลผล", type="primary"):
        with st.spinner(f"กำลังประมวลผลไฟล์หัวข้อ '{selected_media}'..."):
            media_info = DRIVE_DOCX_LINKS[selected_media]
            
            if media_info["type"] == "docx":
                raw_html, subject, image_store, error_msg = convert_docx_to_perfect_html(media_info["url"])
            else:
                raw_html, subject, image_store, error_msg = convert_pdf_to_perfect_html(media_info["url"])
            
            if error_msg:
                st.error(f"ไม่สามารถดาวน์โหลดไฟล์ได้: {error_msg}")
            else:
                final_targets = []
                for c in CLIENT_DATABASE:
                    if f"{c['company']} - {c['contact_name']}" in selected_clients:
                        final_targets.append(c)
                        
                if custom_company.strip() and custom_email.strip():
                    final_targets.append({
                        "company": custom_company.strip(),
                        "contact_name": custom_contact.strip() if custom_contact.strip() else custom_company.strip(),
                        "email": custom_email.strip()
                    })
                    
                if not final_targets:
                    st.error("กรุณาเลือกลูกค้าอย่างน้อย 1 รายการค่ะ")
                else:
                    st.session_state["targets"] = final_targets
                    st.session_state["raw_html"] = raw_html
                    st.session_state["subject"] = subject
                    st.session_state["image_store"] = image_store
                    st.session_state["sender_phone"] = sender_phone
                    st.success(f"ดึงข้อมูลหัวข้อ '{selected_media}' สำเร็จ! ไปที่ STEP 02 เพื่อตรวจเช็คพรีวิวค่ะ")

# --- STEP 02 ---
elif "02" in step:
    st.subheader("STEP 02 : ตรวจสอบพรีวิวและแก้ไขข้อมูลผู้รับ")
    if "raw_html" in st.session_state:
        targets = st.session_state.get("targets", [])
        raw_html = st.session_state.get("raw_html", "")
        subject = st.session_state.get("subject", "")
        image_store = st.session_state.get("image_store", [])
        phone = st.session_state.get("sender_phone", "")
        
        st.info(f"📌 **Subject:** {subject}")
        
        updated_targets = []
        for idx, t in enumerate(targets):
            col_t1, col_t2, col_t3 = st.columns([2, 2, 2])
            with col_t1:
                comp_name = st.text_input(f"ชื่อบริษัท รายที่ {idx+1}:", value=t["company"], key=f"comp_{idx}")
            with col_t2:
                c_name = st.text_input(f"ชื่อผู้รับ/ลูกค้า:", value=t.get("contact_name", t["company"]), key=f"c_name_{idx}")
            with col_t3:
                st.text_input(f"อีเมล:", value=t["email"], disabled=True, key=f"c_email_{idx}")
            
            updated_targets.append({"company": comp_name, "contact_name": c_name, "email": t["email"]})
            
        st.session_state["targets"] = updated_targets
        st.markdown("---")
        
        first_client = updated_targets[0]
        client_display = first_client["contact_name"]
        
        preview_body = raw_html.replace("{{Client name}}", client_display).replace("{{Tel}}", phone)
        
        for cid, img_data, content_type in image_store:
            b64_str = base64.b64encode(img_data).decode()
            preview_body = preview_body.replace(f"cid:{cid}", f"data:{content_type};base64,{b64_str}")

        styled_preview = f"""
        {EMAIL_CSS}
        <div style="background-color: #ffffff; padding: 30px; border-radius: 8px; border: 1px solid #ddd; max-width: 720px; margin: 0 auto;">
            {preview_body}
        </div>
        """
        st.components.v1.html(styled_preview, height=700, scrolling=True)

# --- STEP 03 ---
elif "03" in step:
    st.subheader("STEP 03 : ยืนยันการส่ง Batch Email")
    if "raw_html" in st.session_state:
        targets = st.session_state.get("targets", [])
        raw_html = st.session_state.get("raw_html", "")
        subject = st.session_state.get("subject", "")
        image_store = st.session_state.get("image_store", [])
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
                    msg['Subject'] = subject
                    
                    msg_alt = MIMEMultipart('alternative')
                    msg.attach(msg_alt)
                    
                    client_display = client.get("contact_name", client["company"])
                    client_html_body = raw_html.replace("{{Client name}}", client_display).replace("{{Tel}}", phone)
                    
                    full_email_html = f"""
                    <html>
                    <head>{EMAIL_CSS}</head>
                    <body style="background-color: #ffffff; padding: 10px;">
                        <div style="max-width: 720px; margin: 0 auto;">{client_html_body}</div>
                    </body>
                    </html>
                    """
                    
                    msg_alt.attach(MIMEText(full_email_html, 'html', 'utf-8'))
                    
                    for cid, img_data, content_type in image_store:
                        maintype, subtype = content_type.split('/')
                        img_mime = MIMEImage(img_data, _subtype=subtype)
                        img_mime.add_header('Content-ID', f'<{cid}>')
                        msg.attach(img_mime)
                        
                    server.sendmail(sender, client['email'], msg.as_string())
                    
                server.quit()
                st.balloons()
                st.success("🎉 ส่งอีเมลสำเร็จ!")
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการส่ง: {str(e)}")
