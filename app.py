import streamlit as st
import smtplib
import urllib.request
import io
import re
import mammoth
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

st.set_page_config(page_title="Plan B Media Email Engine", page_icon="🏢", layout="wide")

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

def convert_docx_to_clean_html(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    file_bytes = urllib.request.urlopen(req).read()
    
    image_store = []
    
    # ฟังก์ชันสกัดภาพเพื่อนำไปแปลงเป็น Inline CID สำหรับอีเมล
    def convert_image(image):
        with image.open() as image_bytes:
            data = image_bytes.read()
            cid = f"img_{len(image_store)}"
            image_store.append((cid, data, image.content_type))
            return {"src": f"cid:{cid}"}

    # แปลง Word เป็น HTML แบบเก็บโครงสร้าง รูปภาพ และตารางเป๊ะ 100%
    result = mammoth.convert_to_html(io.BytesIO(file_bytes), convert_image=mammoth.images.inline(convert_image))
    raw_html = result.value
    
    # ดึง Subject จากบรรทัดที่ขึ้นต้นด้วย Subject: ในไฟล์ Word
    subject = "เปิดตัวสื่อใหม่ล่าสุด Central Park"
    subject_match = re.search(r'Subject:\s*(.*?)(</p>|<br>|\n|$)', raw_html, re.IGNORECASE)
    if subject_match:
        subject = subject_match.group(1).strip()
        # ลบแถบ Subject: ออกจากเนื้อหาหลักเพื่อไม่ให้แสดงซ้ำ
        raw_html = re.sub(r'<p>.*?Subject:\s*.*?</p>', '', raw_html, flags=re.IGNORECASE)

    return raw_html, subject, image_store

with st.sidebar:
    st.title("Plan B Media")
    st.caption("EXACT DOCX CONVERTER")
    step = st.radio("ขั้นตอน", ["01 เลือกสื่อและจัดการลูกค้ารายเป้าหมาย", "02 ตรวจสอบพรีวิวและแก้ไขข้อมูล", "03 ยืนยันการส่ง Email"])

st.markdown("## 🏢 PLAN B MEDIA • EMAIL AUTOMATION")

# --- STEP 01 ---
if "01" in step:
    st.subheader("STEP 01 : เลือกสื่อและระบุข้อมูลผู้รับ")
    col1, col2 = st.columns(2)
    with col1:
        selected_media = st.selectbox("เลือกสื่อที่ต้องการส่ง:", list(DRIVE_DOCX_LINKS.keys()))
        sender_phone = st.text_input("เบอร์โทรศัพท์ติดต่อกลับ (แทนค่า {{Tel}}):", value="0645424441")

    with col2:
        all_client_options = [f"{c['company']} ({c['email']})" for c in CLIENT_DATABASE]
        select_all = st.checkbox("✅ เลือกทั้งหมดจากฐานข้อมูล Drive", value=True)
        default_selected = all_client_options if select_all else []
        selected_clients = st.multiselect("เลือกลูกค้า:", options=all_client_options, default=default_selected)
        
        custom_company = st.text_input("ชื่อบริษัท/ชื่อลูกค้าใหม่:", value="", placeholder="เช่น Boploy")
        custom_email = st.text_input("อีเมลลูกค้าใหม่:", value="", placeholder="เช่น wichayada.ph@planbmedia.co.th")

    st.markdown("---")
    if st.button("🚀 ดึงไฟล์ Word ล่าสุดจาก Drive", type="primary"):
        with st.spinner("กำลังดึงไฟล์และประมวลผลรูปแบบตาม Word..."):
            raw_html, subject, image_store = convert_docx_to_clean_html(DRIVE_DOCX_LINKS[selected_media])
            
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
                st.session_state["raw_html"] = raw_html
                st.session_state["subject"] = subject
                st.session_state["image_store"] = image_store
                st.session_state["sender_phone"] = sender_phone
                st.success("อ่านไฟล์ Word และโครงสร้างสำเร็จ! ไปที่ STEP 02 ได้เลยค่ะ")

# --- STEP 02 ---
elif "02" in step:
    st.subheader("STEP 02 : ตรวจสอบพรีวิวและแก้ไขชื่อผู้รับ")
    if "raw_html" in st.session_state:
        targets = st.session_state.get("targets", [])
        raw_html = st.session_state.get("raw_html", "")
        subject = st.session_state.get("subject", "")
        image_store = st.session_state.get("image_store", [])
        phone = st.session_state.get("sender_phone", "")
        
        st.info(f"📌 **Subject ที่ดึงจาก Word:** {subject}")
        
        st.write("📋 **แก้ไขชื่อผู้รับ/ลูกค้าที่จะปรากฏตรง `{{Client name}}`:**")
        updated_targets = []
        for idx, t in enumerate(targets):
            col_t1, col_t2 = st.columns([2, 2])
            with col_t1:
                c_name = st.text_input(f"ชื่อผู้รับ รายที่ {idx+1}:", value=t.get("contact_name", t["company"]), key=f"c_name_{idx}")
            with col_t2:
                st.text_input(f"อีเมล:", value=t["email"], disabled=True, key=f"c_email_{idx}")
            updated_targets.append({"company": t["company"], "contact_name": c_name, "email": t["email"]})
            
        st.session_state["targets"] = updated_targets
        st.markdown("---")
        
        first_client = updated_targets[0]
        c_name = first_client["contact_name"]
        
        # แทนค่าตัวแปรและปรับ CSS ฟอนต์ให้เท่ากับ Word ดั้งเดิม
        preview_body = raw_html.replace("{{Client name}}", c_name).replace("{{Tel}}", phone)
        
        # แปลง cid: เป็น base64 สำหรับพรีวิวใน Streamlit
        for cid, img_data, content_type in image_store:
            import base64
            b64_str = base64.b64encode(img_data).decode()
            preview_body = preview_body.replace(f"cid:{cid}", f"data:{content_type};base64,{b64_str}")

        styled_preview = f"""
        <div style="font-family: 'Aptos', 'Calibri', 'Tahoma', sans-serif; font-size: 15px; color: #000000; line-height: 1.5; padding: 20px; border: 1px solid #ccc; max-width: 750px; margin: 0 auto; background-color: #ffffff;">
            {preview_body}
        </div>
        <style>
            img {{ max-width: 100%; height: auto; }}
            table {{ width: 100% !important; border-collapse: collapse; }}
            td {{ padding: 4px; vertical-align: top; }}
        </style>
        """
        st.components.v1.html(styled_preview, height=650, scrolling=True)

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
            
        if st.button("🚀 ส่ง Email ด้วยฟอนต์และรูปตาม Word ดั้งเดิม", type="primary"):
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
                    
                    c_name = client.get("contact_name", client["company"])
                    client_html_body = raw_html.replace("{{Client name}}", c_name).replace("{{Tel}}", phone)
                    
                    full_email_html = f"""
                    <html>
                    <head>
                        <style>
                            body {{ font-family: 'Aptos', 'Calibri', 'Tahoma', sans-serif; font-size: 15px; color: #000000; line-height: 1.5; }}
                            img {{ max-width: 100%; height: auto; display: block; }}
                            table {{ width: 100% !important; border-collapse: collapse; }}
                            td {{ padding: 4px; vertical-align: top; }}
                        </style>
                    </head>
                    <body>
                        <div style="max-width: 750px;">
                            {client_html_body}
                        </div>
                    </body>
                    </html>
                    """
                    
                    msg_alt.attach(MIMEText(full_email_html, 'html', 'utf-8'))
                    
                    # แนบไฟล์ภาพจริงเข้ากับ Email ตาม CID
                    for cid, img_data, content_type in image_store:
                        maintype, subtype = content_type.split('/')
                        img_mime = MIMEImage(img_data, _subtype=subtype)
                        img_mime.add_header('Content-ID', f'<{cid}>')
                        msg.attach(img_mime)
                        
                    server.sendmail(sender, client['email'], msg.as_string())
                    
                server.quit()
                st.balloons()
                st.success("🎉 ส่งอีเมลสำเร็จ! Subject, ฟอนต์ และการวางรูปเป๊ะตามไฟล์ Word แล้วครับ")
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการส่ง: {str(e)}")
