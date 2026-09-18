import streamlit as st
import smtplib
import urllib.request
import io
import re
import mammoth
import base64
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

st.set_page_config(page_title="Plan B Media Email Automation", page_icon="🏢", layout="wide")

# 🎨 Custom CSS - Theme CI: ฟ้า-ขาว-น้ำเงิน (Plan B Media)
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    h1, h2, h3 { color: #0A2540 !important; font-family: 'Aptos', 'Calibri', sans-serif !important; }
    .stButton>button {
        background-color: #0A2540 !important;
        color: #ffffff !important;
        border-radius: 6px !important;
        border: none !important;
        font-weight: 600 !important;
    }
    .stButton>button:hover { background-color: #00A3FF !important; color: #ffffff !important; }
    section[data-testid="stSidebar"] { background-color: #0A2540 !important; }
    section[data-testid="stSidebar"] * { color: #FFFFFF !important; }
    .stAlert { background-color: #EBF8FF !important; color: #0A2540 !important; border-left: 4px solid #00A3FF !important; }
</style>
""", unsafe_allow_html=True)

# 📌 โฟลเดอร์คลังสื่อ New Media หลักของคุณพลอย
MAIN_NEW_MEDIA_FOLDER_ID = "15nRgzuYsWDPsCfu2IrS4QeWPS89fxckQ"

def fetch_docx_files_from_folder(folder_id):
    """สแกนหาไฟล์ .docx ทั้งหมดจาก Google Drive Folder ID อัตโนมัติ"""
    files_map = {}
    try:
        url = f"https://drive.google.com/embeddedfolderview?id={folder_id}#list"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        
        matches = re.findall(r'id=([a-zA-Z0-9_-]{25,}).*?class="[^"]*entry-name[^"]*">(.*?)</div>', html)
        for fid, fname in matches:
            clean_name = re.sub(r'<[^>]*>', '', fname).strip()
            if clean_name and (clean_name.endswith('.docx') or clean_name.endswith('.doc')):
                clean_title = clean_name.replace('.docx', '').replace('.doc', '')
                files_map[clean_title] = fid
    except Exception:
        pass
    return files_map

def convert_docx_to_perfect_html(file_id):
    download_url = f"https://docs.google.com/document/d/{file_id}/export?format=docx"
    req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
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

    return raw_html, subject, image_store

EMAIL_CSS = """
<style>
    body, div { font-family: 'Aptos', 'Calibri', 'Tahoma', 'Cordia New', sans-serif !important; font-size: 16px !important; color: #222222 !important; line-height: 1.6 !important; }
    p { margin-top: 0 !important; margin-bottom: 12px !important; }
    table { width: 100% !important; border-collapse: collapse !important; margin: 15px 0 !important; }
    td { vertical-align: top !important; padding: 4px !important; }
    img { max-width: 100% !important; height: auto !important; display: block !important; border-radius: 4px !important; }
    ul, ol { margin-top: 5px !important; margin-bottom: 15px !important; padding-left: 20px !important; }
    li { margin-bottom: 6px !important; }
</style>
"""

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.title("PLAN B MEDIA")
    st.caption("EMAIL AUTOMATION SYSTEM")
    st.markdown("---")
    
    st.subheader("👥 เชื่อมข้อมูลลูกค้าส่วนตัว (Google Drive)")
    user_client_folder_id = st.text_input(
        "ระบุ Google Drive Folder ID รายชื่อลูกค้าของคุณ:",
        placeholder="เช่น 15nRgzuYsWDPsCfu2IrS4QeWPS89...",
        help="คัดลอก Folder ID จาก Google Drive ของคุณมาใส่ตรงนี้ เพื่อดึงไฟล์รายชื่อลูกค้าส่วนตัว"
    )
    
    st.markdown("---")
    input_method = st.radio("ช่องทางรองรับอื่นๆ:", ["ดึงจาก Drive Folder ID", "แปะลิงก์ Google Sheets", "อัปโหลดไฟล์ Excel/CSV"])
    
    user_clients = []
    
    if input_method == "แปะลิงก์ Google Sheets":
        sheet_url = st.text_input("ลิงก์ Google Sheets:", placeholder="https://docs.google.com/spreadsheets/d/...")
        if sheet_url:
            try:
                sheet_id = re.search(r'/d/([a-zA-Z0-9_-]+)', sheet_url).group(1)
                csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
                df = pd.read_csv(csv_url)
                for _, row in df.iterrows():
                    user_clients.append({
                        "company": str(row.iloc[0]),
                        "contact_name": str(row.iloc[1]) if len(row) > 1 else str(row.iloc[0]),
                        "email": str(row.iloc[2]) if len(row) > 2 else ""
                    })
                st.success(f"โหลดข้อมูลสำเร็จ {len(user_clients)} รายชื่อ!")
            except Exception:
                st.error("ไม่สามารถอ่านข้อมูลได้ กรุณาเปิดสิทธิ์ 'Anyone with the link'")
                
    elif input_method == "อัปโหลดไฟล์ Excel/CSV":
        uploaded_file = st.file_uploader("เลือกไฟล์รายชื่อลูกค้า:", type=['xlsx', 'csv'])
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
                for _, row in df.iterrows():
                    user_clients.append({
                        "company": str(row.iloc[0]),
                        "contact_name": str(row.iloc[1]) if len(row) > 1 else str(row.iloc[0]),
                        "email": str(row.iloc[2]) if len(row) > 2 else ""
                    })
                st.success(f"โหลดข้อมูลสำเร็จ {len(user_clients)} รายชื่อ!")
            except Exception:
                st.error("ไฟล์ไม่ถูกต้อง กรุณาตรวจสอบโครงสร้างไฟล์")

    st.markdown("---")
    step = st.radio("ขั้นตอนการทำงาน", ["01 เลือกสื่อและจัดการกลุ่มเป้าหมาย", "02 ตรวจสอบพรีวิวและแก้ไขข้อมูล", "03 ยืนยันการส่ง Email"])

st.markdown("# 🏢 PLAN B MEDIA • AUTOMATION ENGINE")

# ดึงรายการไฟล์สื่อคลังกลางอัตโนมัติ
available_media = fetch_docx_files_from_folder(MAIN_NEW_MEDIA_FOLDER_ID)

# --- STEP 01 ---
if "01" in step:
    st.subheader("STEP 01 : เลือกสื่อ Sales Note และระบุข้อมูลลูกค้ารายเป้าหมาย")
    col1, col2 = st.columns(2)
    with col1:
        st.write("📁 **สื่อจากคลังกลาง New Media:**")
        if available_media:
            selected_media_name = st.selectbox("📌 เลือกสื่อ Sales Note:", list(available_media.keys()))
        else:
            st.warning("⚠️ กำลังโหลดคลังสื่อ หรือ ใช้ตัวเลือกสื่อสำรอง")
            backup_media = {
                "Central Park (TH)": "1UrsGlV-f3OKLugCLoJH6AzhIp0O01o9t",
                "Central Park (ENG)": "1UrsGlV-f3OKLugCLoJH6AzhIp0O01o9t",
                "The 20 (TH)": "1UrsGlV-f3OKLugCLoJH6AzhIp0O01o9t"
            }
            selected_media_name = st.selectbox("📌 เลือกสื่อ Sales Note:", list(backup_media.keys()))
            available_media = backup_media
            
        sender_phone = st.text_input("เบอร์โทรศัพท์ติดต่อกลับ (แทนค่า {{Tel}}):", value="0645424441")

    with col2:
        st.write("👥 **เลือกลูกค้าเป้าหมาย:**")
        
        # ใช้รายชื่อลูกค้าที่พนักงานเชื่อมต่อจาก Drive หรือ Google Sheets / Excel
        active_client_db = user_clients if user_clients else [
            {"company": "บริษัท คอสเมคอน จำกัด", "contact_name": "คุณคอสเมคอน", "email": "cosmecon.th@gmail.com"},
            {"company": "บริษัท บิวทีเอสเดอร์มา จำกัด (Mediheal)", "contact_name": "คุณเมดิฮีล", "email": "beauteousderma@gmail.com"},
            {"company": "บริษัท สตาร์ริชเชอร์ส กรุ๊ป จำกัด (MG)", "contact_name": "คุณเอ็มจี", "email": "warissara.benz@starrich.co.th"}
        ]
        
        all_client_options = [f"{c['company']} - {c['contact_name']}" for c in active_client_db]
        select_all = st.checkbox("✅ เลือกทั้งหมด", value=True)
        default_selected = all_client_options if select_all else []
        selected_clients = st.multiselect("รายการที่เลือก:", options=all_client_options, default=default_selected)
        
        st.caption("➕ เพิ่มลูกค้ารายใหม่ด่วน (เพิ่มเฉพาะรอบนี้):")
        custom_company = st.text_input("ชื่อบริษัท:", value="", placeholder="เช่น บริษัท แพลน บี มีเดีย จำกัด (มหาชน)")
        custom_contact = st.text_input("ชื่อผู้รับ/ลูกค้า (Contact Name):", value="", placeholder="เช่น คุณพลอย")
        custom_email = st.text_input("อีเมลลูกค้า:", value="", placeholder="เช่น wichayada.ph@planbmedia.co.th")

    st.markdown("---")
    if st.button("🚀 ดึงไฟล์ Word ของสื่อที่เลือก และประมวลผล", type="primary"):
        file_id = available_media[selected_media_name]
        with st.spinner(f"กำลังดึงข้อมูลสื่อ '{selected_media_name}' จากคลังกลาง..."):
            try:
                raw_html, subject, image_store = convert_docx_to_perfect_html(file_id)
                
                final_targets = []
                for c in active_client_db:
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
                    st.success(f"ดึงข้อมูลสื่อ '{selected_media_name}' สำเร็จ! ไปที่ STEP 02 เพื่อตรวจเช็คพรีวิวค่ะ")
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการดึงไฟล์: {str(e)}")

# --- STEP 02 ---
elif "02" in step:
    st.subheader("STEP 02 : ตรวจสอบพรีวิวและแก้ไขข้อมูลผู้รับ")
    if "raw_html" in st.session_state:
        targets = st.session_state.get("targets", [])
        raw_html = st.session_state.get("raw_html", "")
        subject = st.session_state.get("subject", "")
        image_store = st.session_state.get("image_store", [])
        phone = st.session_state.get("sender_phone", "")
        
        st.info(f"📌 **Subject จากไฟล์ Word:** {subject}")
        
        st.write("✏️ **แก้ไขข้อมูลลูกค้า (ชื่อบริษัท / ชื่อผู้รับ จะถูกแทนที่ตรง `{{Client name}}`):**")
        updated_targets = []
        for idx, t in enumerate(targets):
            col_t1, col_t2, col_t3 = st.columns([2, 2, 2])
            with col_t1:
                comp_name = st.text_input(f"ชื่อบริษัท รายที่ {idx+1}:", value=t["company"], key=f"comp_{idx}")
            with col_t2:
                c_name = st.text_input(f"ชื่อผู้รับ/ลูกค้า (ใส่ลงในเนื้อหา):", value=t.get("contact_name", t["company"]), key=f"c_name_{idx}")
            with col_t3:
                st.text_input(f"อีเมล:", value=t["email"], disabled=True, key=f"c_email_{idx}")
            
            updated_targets.append({
                "company": comp_name,
                "contact_name": c_name,
                "email": t["email"]
            })
            
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
        <div style="background-color: #ffffff; padding: 30px; border-radius: 8px; border: 1px solid #00A3FF; max-width: 720px; margin: 0 auto; box-shadow: 0px 4px 12px rgba(0,0,0,0.05);">
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
            sender = st.text_input("อีเมลผู้ส่ง (บัญชี @planbmedia.co.th):", placeholder="yourname@planbmedia.co.th")
        with col_b:
            pwd = st.text_input("Google App Password ของคุณ:", type="password")
            
        if st.button("🚀 ส่ง Email หาพร้อมกันทุกบริษัททันที", type="primary"):
            if not sender or not pwd:
                st.error("กรุณากรอกอีเมลผู้ส่งและ Google App Password ให้ครบถ้วนค่ะ")
            else:
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
                        <head>
                            {EMAIL_CSS}
                        </head>
                        <body style="background-color: #ffffff; padding: 10px;">
                            <div style="max-width: 720px; margin: 0 auto;">
                                {client_html_body}
                            </div>
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
                    st.success("🎉 ส่งอีเมลสำเร็จ! จัดส่งหาลูกค้าทุกรายเรียบร้อยแล้วค่ะ")
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการส่ง: {str(e)}")
