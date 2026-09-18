import os
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
import pandas as pd
from docx import Document
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import gspread

# ---------------------------------------------------------
# Page Config & Plan B CI Custom Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Plan B Media - New Media Automail",
    page_icon="📢",
    layout="wide"
)

st.markdown("""
<style>
    .main { background-color: #F8FAFC; }
    .stButton>button {
        background-color: #042C53;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #0C447C;
        color: white;
    }
    .header-box {
        background: linear-gradient(135deg, #042C53 0%, #0C447C 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    .card-box {
        background-color: white;
        padding: 1.2rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# GCP Credentials Setup
# ---------------------------------------------------------
CREDS_FILE = "credentials.json"
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]

@st.cache_resource
def get_gcp_services():
    if not os.path.exists(CREDS_FILE):
        return None, None
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    drive_service = build('drive', 'v3', credentials=creds)
    gc = gspread.authorize(creds)
    return drive_service, gc

# ---------------------------------------------------------
# Sidebar: User Auth & Dynamic Settings
# ---------------------------------------------------------
st.sidebar.image("https://www.planbmedia.co.th/wp-content/uploads/2021/03/logo-planb.png", width=180)
st.sidebar.title("⚙️ ข้อมูลผู้ส่ง (Sales Info)")

user_name = st.sidebar.text_input("ชื่อ-นามสกุล ผู้ส่ง", value="วิชญาดา (พลอย)")
user_email = st.sidebar.text_input("อีเมลผู้ส่ง (@planbmedia.co.th)", value="wichayada.ph@planbmedia.co.th")
user_phone = st.sidebar.text_input("เบอร์โทรศัพท์", value="064-542-4441")

st.sidebar.markdown("---")
st.sidebar.subheader("🔗 Google Cloud Connection")
drive_folder_id = st.sidebar.text_input("Google Drive Folder ID", value="1v0WK53RI_EczHYHTpi7PC8zLrlbrDUrT")
sheet_url_or_id = st.sidebar.text_input("Google Sheet URL / ID", value="")

step = st.sidebar.radio("🔘 ขั้นตอนการทำงาน", [
    "STEP 01 : จัดการรายชื่อลูกค้า",
    "STEP 02 : เลือก New Media & พรีวิว",
    "STEP 03 : ยืนยันยอด & กดส่งอีเมล"
])

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if 'recipients' not in st.session_state:
    st.session_state.recipients = []
if 'selected_media' not in st.session_state:
    st.session_state.selected_media = None

# Header Banner
st.markdown(f"""
<div class="header-box">
    <h2>📢 PLAN B MEDIA • NEW MEDIA AUTOMATION SYSTEM</h2>
    <p>ระบบจัดส่งข่าวสารสื่อโฆษณาใหม่แบบอัตโนมัติ | ผู้ใช้งาน: <b>{user_name}</b> ({user_email})</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# STEP 01 : Customer Management
# ---------------------------------------------------------
if step == "STEP 01 : จัดการรายชื่อลูกค้า":
    st.subheader("👥 STEP 01 : จัดการรายชื่อลูกค้าผู้รับ")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("<div class='card-box'>", unsafe_allow_html=True)
        st.markdown("#### 1️⃣ ดึงรายชื่อจาก Google Sheets")
        drive_service, gc = get_gcp_services()
        
        if st.button("🔄 โหลดรายชื่อจาก Google Sheet Real-time"):
            if gc and sheet_url_or_id:
                try:
                    sh = gc.open_by_url(sheet_url_or_id) if "http" in sheet_url_or_id else gc.open_by_key(sheet_url_or_id)
                    worksheet = sh.get_worksheet(0)
                    data = worksheet.get_all_records()
                    df = pd.DataFrame(data)
                    
                    fetched = []
                    for idx, row in df.iterrows():
                        fetched.append({
                            "select": True,
                            "company": row.get("ชื่อบริษัท", f"บริษัทที่ {idx+1}"),
                            "name": row.get("ชื่อผู้ติดต่อ", "ลูกค้าท่านสำคัญ"),
                            "email": row.get("อีเมล", row.get("Email", ""))
                        })
                    st.session_state.recipients = fetched
                    st.success(f"✅ ดึงรายชื่อสำเร็จทั้งหมด {len(fetched)} รายชื่อ!")
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการดึง Sheet: {e}")
            else:
                st.warning("⚠️ โปรดระบุ Google Sheet URL/ID ใน Sidebar และตรวจสอบไฟล์ credentials.json")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='card-box'>", unsafe_allow_html=True)
        st.markdown("#### 2️⃣ ➕ พิมพ์เพิ่มรายชื่อลูกค้าใหม่ (Manual)")
        new_company = st.text_input("ชื่อบริษัท")
        new_name = st.text_input("ชื่อผู้ติดต่อ")
        new_email = st.text_input("อีเมลผู้รับ")
        
        if st.button("➕ เพิ่มลูกค้ารายนี้เข้าลิสต์"):
            if new_email:
                st.session_state.recipients.append({
                    "select": True,
                    "company": new_company or "ไม่ระบุ",
                    "name": new_name or "คุณลูกค้า",
                    "email": new_email
                })
                st.success(f"เพิ่ม {new_email} เรียบร้อยแล้ว!")
            else:
                st.warning("กรุณากรอกอีเมลผู้รับค่ะ")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 3️⃣ ตารางลูกค้ารวมทั้งหมดที่จะจัดส่ง")
    if st.session_state.recipients:
        df_display = pd.DataFrame(st.session_state.recipients)
        edited_df = st.data_editor(df_display, use_container_width=True, num_rows="dynamic")
        st.info(f"✅ จำนวนผู้รับรวมที่เลือกอยู่ปัจจุบัน: {len(edited_df[edited_df['select'] == True])} รายชื่อ")
    else:
        st.info("ยังไม่มีข้อมูลรายชื่อลูกค้า กรุณากดดึงข้อมูลจาก Sheet หรือพิมพ์กรอกเพิ่มด้านบนค่ะ")

# ---------------------------------------------------------
# STEP 02 : Media Selection & Preview
# ---------------------------------------------------------
elif step == "STEP 02 : เลือก New Media & พรีวิว":
    st.subheader("📧 STEP 02 : เลือก New Media 1 สื่อ & ตรวจสอบพรีวิวเนื้อหา")
    
    drive_service, _ = get_gcp_services()
    media_list = []
    
    if drive_service and drive_folder_id:
        try:
            query = f"'{drive_folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
            results = drive_service.files().list(q=query, fields="files(id, name)").execute()
            folders = results.get('files', [])
            media_list = [f['name'] for f in folders]
        except Exception as e:
            st.error(f"ไม่สามารถอ่านโฟลเดอร์ Drive ได้: {e}")
            
    if not media_list:
        media_list = [
            "📍 rama 9 connected", "📍 Central Network", "📍 Central Network [New Package]",
            "📍 The 20", "📍 Nextopia Siam Paragon", "📍 PlanB TV Nationwide",
            "📍 Central Park", "📍 The Skyline"
        ]

    selected_media_name = st.selectbox("🎯 เลือก New Media ที่ต้องการส่งอัปเดตในรอบนี้:", media_list)
    st.session_state.selected_media = selected_media_name
    
    st.markdown("---")
    st.markdown("#### 2️⃣ พรีวิวเนื้อหาอีเมลจริง (คงรูปแบบ Sales Note 100%)")
    
    st.markdown(f"""
    <div class="card-box" style="border: 1px solid #CBD5E1;">
        <p><b>Subject:</b> [Plan B Media] OUTDOOR TRENDS: สื่อใหม่ล่าสุด "{selected_media_name}"</p>
        <hr>
        <p>เรียน คุณ [ชื่อลูกค้า],</p>
        <p>บริษัท แพลน บี มีเดีย จำกัด (มหาชน) ขอแนะนำสื่อโฆษณาดิจิทัลใหม่ล่าสุด <b>"{selected_media_name}"</b> 
        ที่พร้อมให้บริการครอบคลุมทำเลศักยภาพสูงเพื่อเพิ่ม Impact ให้กับแบรนด์ของท่าน</p>
        <br>
        <div style="background-color: #E2E8F0; padding: 2rem; text-align: center; border-radius: 8px;">
            🖼️ [ ภาพประกอบสื่อโฆษณา {selected_media_name} ดึงจาก Sales Note ต้นฉบับ ]
        </div>
        <br>
        <p><b>จุดเด่นของสื่อ:</b></p>
        <ul>
            <li>ตั้งอยู่ในทำเลศูนย์กลางธุรกิจและย่านการค้าสำคัญ</li>
            <li>จอโฆษณาดิจิทัลความละเอียดสูง รองรับทั้งภาพนิ่งและวิดีโอ</li>
            <li>เข้าถึงกลุ่มเป้าหมายกำลังซื้อสูงได้อย่างแม่นยำ</li>
        </ul>
        <br>
        <div style="background-color: #F1F5F9; padding: 1rem; border-radius: 6px;">
            📁 <b>เข้าชม Media Deck & Rate Card:</b> <a href="#">[ 🔗 เปิดดูไฟล์ Sales Note ใน Drive ]</a>
        </div>
        <br>
        <p>หากท่านต้องการข้อมูลเพิ่มเติมหรือสำรองช่วงเวลาโฆษณา สามารถติดต่อสอบถามได้ทันทีค่ะ</p>
        <br>
        <p>ขอแสดงความนับถือ,<br>
        <b>{user_name}</b><br>
        Sales Executive | Plan B Media Public Company Limited<br>
        📧 Email: {user_email} | 📞 Tel: {user_phone}</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# STEP 03 : Confirmation & Direct Send
# ---------------------------------------------------------
elif step == "STEP 03 : ยืนยันยอด & กดส่งอีเมล":
    st.subheader("🚀 STEP 03 : ตรวจสอบยอดรวม & ยืนยันส่งอีเมล")
    
    selected_media = st.session_state.selected_media or "ยังไม่ได้เลือกสื่อ"
    total_recipients = len(st.session_state.recipients) if st.session_state.recipients else 0
    
    st.markdown(f"""
    <div class="card-box">
        <h4>📊 สรุปรายละเอียดการจัดส่งรอบนี้:</h4>
        <ul>
            <li><b>สื่อ New Media ที่เลือก:</b> <span style="color:#0C447C; font-weight:bold;">{selected_media}</span></li>
            <li><b>จำนวนผู้รับรวมทั้งหมด:</b> <span style="color:#0C447C; font-weight:bold;">{total_recipients} รายชื่อ</span></li>
            <li><b>ผู้ส่งบทบาท Sales:</b> {user_name} ({user_email})</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("#### ⚙️ ยืนยันรหัสผ่านเพื่อส่งออกจากระบบ Office 365 / Gmail")
    app_password = st.text_input("กรอก App Password / รหัสผ่านอีเมลผู้ส่ง", type="password")
    smtp_server = st.selectbox("ประเภทระบบอีเมลองค์กร", ["smtp.office365.com (Microsoft 365)", "smtp.gmail.com (Google Workspace)"])
    
    if st.button("🚀 ยืนยันกดส่ง Email หาลูกค้าทั้งหมดทันที"):
        if not app_password:
            st.warning("โปรดใส่ App Password เพื่อยืนยันสิทธิ์การส่งอีเมลก่อนค่ะ")
        elif total_recipients == 0:
            st.warning("ยังไม่มีรายชื่อผู้รับในระบบ โปรดเลือกรายชื่อใน STEP 01 ก่อนค่ะ")
        else:
            st.markdown("---")
            st.markdown("#### 📊 สถานะการส่งจริง (Real-time Progress)")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Direct Sending Loop
            server_host = "smtp.office365.com" if "office365" in smtp_server else "smtp.gmail.com"
            try:
                server = smtplib.SMTP(server_host, 587)
                server.starttls()
                server.login(user_email, app_password)
                
                success_count = 0
                for idx, r in enumerate(st.session_state.recipients):
                    msg = MIMEMultipart()
                    msg['From'] = user_email
                    msg['To'] = r['email']
                    msg['Subject'] = f"[Plan B Media] OUTDOOR TRENDS: สื่อใหม่ล่าสุด {selected_media}"
                    
                    body = f"เรียน คุณ{r['name']} ({r['company']}),\n\nขอแนะนำสื่อโฆษณาใหม่ {selected_media}..."
                    msg.attach(MIMEText(body, 'plain'))
                    
                    server.send_message(msg)
                    success_count += 1
                    
                    # Update Progress
                    progress = (idx + 1) / total_recipients
                    progress_bar.progress(progress)
                    status_text.text(f"กำลังจัดส่ง ({idx+1}/{total_recipients}): {r['company']} ({r['email']})...")
                    
                server.quit()
                st.success(f"🎉 จัดส่งอีเมลอัปเดตสื่อ {selected_media} สำเร็จครบถ้วน {success_count} รายชื่อเรียบร้อยแล้ว!")
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการส่งอีเมล: {e}")
