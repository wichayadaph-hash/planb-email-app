import streamlit as st
import smtplib
import re
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 📌 ตั้งค่าหน้าเว็บ Streamlit (อ้างอิงตามแอปเดิมของคุณพลอย)
st.set_page_config(page_title="Plan B Media Email Automation", page_icon="🏢", layout="wide")

# 🎨 Custom CSS สำหรับหน้าเว็บ Streamlit (Theme CI: Plan B Media)
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    h1, h2, h3 { color: #042C53 !important; font-family: 'Kanit', sans-serif !important; }
    .stButton>button {
        background-color: #0C447C !important;
        color: #ffffff !important;
        border-radius: 4px !important;
        border: none !important;
        font-weight: 500 !important;
    }
    .stButton>button:hover { background-color: #185FA5 !important; color: #ffffff !important; }
    section[data-testid="stSidebar"] { background-color: #042C53 !important; }
    section[data-testid="stSidebar"] * { color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

# 📌 ฟังก์ชันดึงข้อมูลจาก Google Sheets แบบอัตโนมัติ (อ่านครบทุกแถว)
def load_google_sheet(sheet_url):
    try:
        sheet_match = re.search(r'/d/([a-zA-Z0-9_-]+)', sheet_url)
        if not sheet_match:
            return None, "รูปแบบ URL ของ Google Sheets ไม่ถูกต้อง"
        
        sheet_id = sheet_match.group(1)
        gid_match = re.search(r'gid=([0-9]+)', sheet_url)
        gid_str = f"&gid={gid_match.group(1)}" if gid_match else ""
        
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv{gid_str}"
        df = pd.read_csv(csv_url)
        df.columns = df.columns.astype(str).str.strip()
        
        clients = []
        for _, row in df.iterrows():
            company = str(row.get('Company', row.get('บริษัท', row.iloc[0]))).strip()
            contact = str(row.get('Contact Name', row.get('ชื่อผู้ติดต่อ', row.iloc[1] if len(row) > 1 else company))).strip()
            email = str(row.get('Email', row.get('อีเมล', row.iloc[2] if len(row) > 2 else ''))).strip()
            target = str(row.get('Target Audience', row.get('กลุ่มเป้าหมาย', row.iloc[3] if len(row) > 3 else 'Mass Audience'))).strip()
            
            if company and company.lower() != 'nan' and email and email.lower() != 'nan':
                clients.append({
                    "company": company,
                    "contact_name": contact if contact.lower() != 'nan' else company,
                    "email": email,
                    "target": target if target.lower() != 'nan' else "Mass Audience"
                })
        return clients, None
    except Exception as e:
        return None, str(e)

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.title("PLAN B MEDIA")
    st.caption("EMAIL AUTOMATION SYSTEM")
    st.markdown("---")
    
    st.subheader("⚙️ ข้อมูลผู้ส่ง (Sales Info)")
    sales_name = st.text_input("ชื่อผู้ส่ง (Sales Name):", value="วิชญาดา (พลอย)")
    sales_email = st.text_input("อีเมลองค์กร Plan B (@planbmedia.co.th):", value="wichayada.ph@planbmedia.co.th")
    sales_phone = st.text_input("เบอร์โทรศัพท์ติดต่อ:", value="064-542-4441")
    
    is_valid_email = sales_email.lower().endswith("@planbmedia.co.th")
    if not is_valid_email:
        st.error("⚠️ กรุณาระบุอีเมลองค์กร @planbmedia.co.th เท่านั้น")

    st.markdown("---")
    st.subheader("📁 Google Drive สื่อการขาย")
    drive_folder_link = st.text_input(
        "ลิงก์ Google Drive Folder สื่อ:",
        value="https://drive.google.com/drive/folders/1v0WK53RI_EczHYHTpi7PC8zLrlbrDUrT"
    )

    st.markdown("---")
    st.subheader("👥 ดึงข้อมูลรายชื่อลูกค้า")
    input_method = st.radio("เลือกวิธีนำเข้าข้อมูล:", ["แปะลิงก์ Google Sheets (แนะนำ)", "อัปโหลด Excel/CSV", "ใช้ข้อมูลตัวอย่าง"])
    
    user_clients = []
    if input_method == "แปะลิงก์ Google Sheets (แนะนำ)":
        sheet_url = st.text_input("วางลิงก์ Google Sheets (เปิดแชร์แบบ ใครที่มีลิงก์ดูได้):")
        if sheet_url:
            loaded_clients, err = load_google_sheet(sheet_url)
            if err:
                st.error(f"⚠️ ไม่สามารถอ่านข้อมูลได้: {err}")
            else:
                user_clients = loaded_clients
                st.success(f"✅ โหลดสำเร็จครบถ้วน! พบข้อมูล {len(user_clients)} รายชื่อ")
                
    elif input_method == "อัปโหลด Excel/CSV":
        uploaded_file = st.file_uploader("เลือกไฟล์ Excel/CSV:", type=['xlsx', 'csv'])
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
                df.columns = df.columns.astype(str).str.strip()
                for _, row in df.iterrows():
                    user_clients.append({
                        "company": str(row.iloc[0]).strip(),
                        "contact_name": str(row.iloc[1] if len(row) > 1 else row.iloc[0]).strip(),
                        "email": str(row.iloc[2] if len(row) > 2 else "").strip(),
                        "target": str(row.iloc[3] if len(row) > 3 else "Mass Audience").strip()
                    })
                st.success(f"✅ โหลดสำเร็จ {len(user_clients)} รายชื่อ!")
            except Exception as e:
                st.error(f"⚠️ โครงสร้างไฟล์ไม่ถูกต้อง: {str(e)}")

    st.markdown("---")
    step = st.radio("ขั้นตอนการทำงาน", ["01 จัดการกลุ่มเป้าหมาย & เลือกสื่อ", "02 พรีวิว HTML Email", "03 ยืนยันการส่ง Email"])

st.markdown("# 🏢 PLAN B MEDIA • EMAIL AUTOMATION SYSTEM")

# --- STEP 01 ---
if "01" in step:
    st.subheader("STEP 01 : เลือกสื่อจาก Google Drive และกำหนดกลุ่มเป้าหมาย")
    
    subject_input = st.text_input("📌 Subject (หัวข้ออีเมล):", value="แนะนำสื่อนอกบ้าน Out-of-Home Media ครบวงจรจาก Plan B Media")
    
    st.markdown("### 1️⃣ เลือกรายการสื่อที่จะนำเสนอในครั้งนี้")
    default_medias = [
        "📍 Classic: Billboard ทั่วประเทศ",
        "📍 Digital: จอดิจิทัลกลางเมือง & ห้างสรรพสินค้าชั้นนำ",
        "📍 Retail: Siam Piwat, Central, The Mall, 7-Eleven",
        "📍 Transit: BTS, MRT, Bus, EV Muvmi",
        "📍 Airport: สุวรรณภูมิ ดอนเมือง + 25 แห่งทั่วประเทศ"
    ]
    selected_medias = st.multiselect("เลือกสื่อที่มีใน Google Drive:", options=default_medias, default=default_medias)
    
    custom_media = st.text_input("➕ เพิ่มสื่อรายการใหม่ (กรณีเพิ่งเพิ่มสื่อใหม่ลง Google Drive):", placeholder="เช่น 📍 Sport Marketing & Live Experience")
    if custom_media:
        selected_medias.append(custom_media)
        
    media_html_formatted = "<br>".join(selected_medias)
    
    st.markdown("---")
    st.markdown("### 2️⃣ ตรวจสอบรายชื่อลูกค้าที่จะจัดส่ง")
    
    active_db = user_clients if user_clients else [
        {"company": "บริษัท คอสเมคอน จำกัด", "contact_name": "คุณคอสเมคอน", "email": "cosmecon.th@gmail.com", "target": "กลุ่มบิวตี้และสกินแคร์"},
        {"company": "บริษัท บิวทีเอสเดอร์มา จำกัด (Mediheal)", "contact_name": "คุณเมดิฮีล", "email": "beauteousderma@gmail.com", "target": "กลุ่มคนรักสุขภาพและความงาม"},
        {"company": "บริษัท สตาร์ริชเชอร์ส กรุ๊ป จำกัด (MG)", "contact_name": "คุณเอ็มจี", "email": "warissara.benz@starrich.co.th", "target": "กลุ่มคนใช้รถยนต์ส่วนตัว"}
    ]
    
    st.dataframe(pd.DataFrame(active_db), use_container_width=True)
    
    client_options = [f"{c['company']} ({c['contact_name']}) - {c['email']}" for c in active_db]
    select_all = st.checkbox("✅ เลือกรายชื่อทั้งหมด", value=True)
    selected = client_options if select_all else []
    chosen_clients = st.multiselect("เลือกรายชื่อผู้รับที่จะส่ง:", options=client_options, default=selected)

    if st.button("🚀 บันทึกข้อมูลและไปที่ STEP 02 (Preview)", type="primary"):
        if not is_valid_email:
            st.error("❌ ไม่อนุญาตให้ใช้อีเมลอื่นที่ไม่ใช่ @planbmedia.co.th ส่งค่ะ")
        else:
            final_list = [c for c in active_db if f"{c['company']} ({c['contact_name']}) - {c['email']}" in chosen_clients]
            if not final_list:
                st.error("กรุณาเลือกผู้รับอย่างน้อย 1 รายการค่ะ")
            else:
                st.session_state["final_targets"] = final_list
                st.session_state["email_subject"] = subject_input
                st.session_state["sales_name"] = sales_name
                st.session_state["sales_email"] = sales_email
                st.session_state["sales_phone"] = sales_phone
                st.session_state["drive_link"] = drive_folder_link
                st.session_state["media_formatted"] = media_html_formatted
                st.success("บันทึกข้อมูลสำเร็จ! กรุณาเลือกเมนู '02 พรีวิว HTML Email' ทางซ้ายมือได้เลยค่ะ")

# --- STEP 02 ---
elif "02" in step:
    st.subheader("STEP 02 : ตรวจสอบพรีวิว HTML Template")
    if "final_targets" in st.session_state:
        targets = st.session_state["final_targets"]
        first = targets[0]
        
        st.info(f"📌 **Subject:** {st.session_state['email_subject']}")
        st.write(f"👁️ **ตัวอย่างพรีวิวอีเมลที่จะส่งถึง:** {first['company']} ({first['contact_name']})")
        
        # HTML Template ของระบบ Plan B Automation
        preview_html = f"""
        <!DOCTYPE html>
        <html lang="th">
        <head>
        <meta charset="UTF-8">
        <style>
          body {{ background: #edf2f7; font-family: 'Sarabun', 'Tahoma', sans-serif; padding: 20px 0; margin: 0; }}
          .email-outer {{ max-width: 620px; margin: 0 auto; }}
          .email-card {{ background: #ffffff; border-radius: 4px; overflow: hidden; border: 1px solid #d8e6f5; }}
          .hero {{ background: #042C53; padding: 0; position: relative; }}
          .hero-top-bar {{ background: #0C447C; padding: 14px 36px; display: flex; justify-content: space-between; align-items: center; }}
          .hero-logo {{ font-family: 'Kanit', sans-serif; font-size: 17px; color: #ffffff; font-weight: 500; }}
          .hero-logo span {{ color: #85B7EB; font-weight: 300; }}
          .hero-main {{ padding: 36px; }}
          .hero-eyebrow {{ background: rgba(55, 138, 221, 0.2); border: 1px solid rgba(55, 138, 221, 0.4); padding: 5px 12px; font-size: 10px; color: #85B7EB; display: inline-block; margin-bottom: 15px; }}
          .hero-headline {{ font-family: 'Kanit', sans-serif; font-size: 26px; color: #ffffff; line-height: 1.3; margin-bottom: 12px; }}
          .hero-headline em {{ font-style: normal; color: #85B7EB; }}
          .hero-sub {{ font-size: 13px; color: rgba(255,255,255,0.75); line-height: 1.6; }}
          .email-body {{ padding: 30px 36px; }}
          .greeting-line {{ font-size: 15px; color: #0C447C; font-weight: 600; margin-bottom: 14px; font-family: 'Kanit', sans-serif; }}
          .body-text {{ font-size: 14px; color: #3a3a3a; line-height: 1.7; margin-bottom: 20px; }}
          .section-label {{ font-size: 11px; text-transform: uppercase; color: #378ADD; font-weight: 600; margin-bottom: 12px; font-family: 'Kanit', sans-serif; }}
          .insight-box {{ background: #f0f6fd; border-left: 4px solid #185FA5; padding: 15px 18px; margin-bottom: 24px; }}
          .insight-box-text {{ font-size: 13px; color: #0C447C; line-height: 1.6; }}
          .creds-row {{ padding: 12px 16px; border: 1px solid #D4E6F7; border-radius: 4px; margin-bottom: 24px; background: #ffffff; }}
          .creds-title {{ font-size: 13px; font-weight: 600; color: #042C53; font-family: 'Kanit', sans-serif; }}
          .creds-sub {{ font-size: 11px; color: #777; }}
          .creds-btn {{ font-size: 12px; color: #185FA5; font-weight: 600; text-decoration: none; border: 1px solid #B5D4F4; padding: 5px 12px; border-radius: 3px; display: inline-block; margin-top: 6px; }}
          .cta-wrap {{ text-align: center; margin: 24px 0 10px; }}
          .cta-btn {{ background: #0C447C; color: #ffffff !important; font-family: 'Kanit', sans-serif; font-size: 14px; padding: 12px 30px; border-radius: 4px; text-decoration: none; display: inline-block; font-weight: 500; }}
          .sig-card {{ padding: 14px 16px; background: #f0f6fd; border: 1px solid #D4E6F7; border-radius: 4px; margin-top: 20px; }}
          .sig-name {{ font-family: 'Kanit', sans-serif; font-size: 14px; font-weight: 600; color: #042C53; }}
          .sig-title {{ font-size: 11px; color: #777; margin-bottom: 6px; }}
          .sig-contacts {{ font-size: 11px; color: #378ADD; }}
          .email-footer {{ background: #042C53; padding: 16px; text-align: center; color: rgba(133, 183, 235, 0.6); font-size: 10px; }}
        </style>
        </head>
        <body>
        <div class="email-outer">
          <div class="email-card">
            <div class="hero">
              <div class="hero-top-bar">
                <span class="hero-logo">PLAN B<span> MEDIA</span></span>
              </div>
              <div class="hero-main">
                <div class="hero-eyebrow">Introduction · Out-of-Home Media</div>
                <h1 class="hero-headline">เข้าถึงคนไทย<br><em>ทุก touchpoint</em><br>ในชีวิตประจำวัน</h1>
                <p class="hero-sub">Plan B Media มี ecosystem สื่อนอกบ้านครบวงจรที่ใหญ่ที่สุดในประเทศไทย — พร้อม location insight ที่คิดมาสำหรับแบรนด์ของคุณโดยเฉพาะ</p>
              </div>
            </div>
            <div class="email-body">
              <div class="greeting-line">เรียน คุณ {first['contact_name']},</div>
              <p class="body-text">
                สวัสดีค่ะ ดิฉัน <strong>{st.session_state['sales_name']}</strong> จาก Plan B Media ค่ะ<br><br>
                เห็นว่า <strong>{first['company']}</strong> กำลังขยาย reach ในกลุ่ม {first.get('target', 'Target Audience')} ซึ่งตรงกับ audience ที่สื่อของเราเข้าถึงได้ทุกวันในทุก touchpoint ค่ะ — ไม่ว่าจะเป็นขณะเดินทาง ช็อปปิ้ง หรือผ่านสนามบิน
              </p>
              <div class="section-label">Plan B Media Ecosystem & Media Packages</div>
              <div class="body-text" style="background:#f0f6fd; padding:15px; border-radius:4px; font-size:13px; line-height:1.8;">
                {st.session_state.get('media_formatted', '')}
              </div>
              <div class="insight-box">
                <div class="insight-box-text">
                  เรามี data และ location strategy ที่คิดว่าจะเหมาะกับ <strong>{first['company']}</strong> โดยเฉพาะ — ขอนัดเพียง <strong>20 นาที</strong> เพื่อนำเสนอแนวทางที่ตรงกับ target audience ของคุณในวันและเวลาที่สะดวกค่ะ
                </div>
              </div>
              <div class="creds-row">
                <div class="creds-title">Plan B Media — Credentials & Media Portfolio</div>
                <div class="creds-sub">สามารถเข้าดูโฟลเดอร์สื่อและ Credentials ล่าสุดได้จากลิงก์ Google Drive ด้านล่างนี้ค่ะ</div>
                <a href="{st.session_state.get('drive_link', 'https://drive.google.com')}" class="creds-btn" target="_blank">📁 เปิดโฟลเดอร์ Google Drive สื่อทั้งหมด →</a>
              </div>
              <div class="cta-wrap">
                <a href="mailto:{st.session_state['sales_email']}?subject=นัดหมาย Plan B Media" class="cta-btn">นัดพบเพื่อนำเสนอ — ใช้เวลาเพียง 20 นาที</a>
              </div>
            </div>
            <div class="email-body" style="padding-top:0;">
              <p class="body-text" style="font-size:12px;">ขอบคุณมากนะคะ หากมีข้อสงสัยหรืออยากให้ส่งข้อมูลเพิ่มเติม ติดต่อได้ตลอดค่ะ</p>
              <div class="sig-card">
                <div class="sig-name">{st.session_state['sales_name']}</div>
                <div class="sig-title">Sales Executive · Plan B Media PCL.</div>
                <div class="sig-contacts">
                  📞 เบอร์โทร: {st.session_state['sales_phone']} | ✉ อีเมล: {st.session_state['sales_email']}
                </div>
              </div>
            </div>
            <div class="email-footer">© 2026 Plan B Media PCL. · 123 ถนนวิภาวดี กรุงเทพฯ 10400</div>
          </div>
        </div>
        </body>
        </html>
        """
            
        st.components.v1.html(preview_html, height=750, scrolling=True)
    else:
        st.warning("⚠️ กรุณทำขั้นตอน STEP 01 ให้เสร็จสิ้นก่อนค่ะ")

# --- STEP 03 ---
elif "03" in step:
    st.subheader("STEP 03 : ยืนยันการส่ง Email ด้วยบัญชี Plan B Media")
    if "final_targets" in st.session_state:
        targets = st.session_state["final_targets"]
        sender_acc = st.session_state.get("sales_email", "")
        
        st.info(f"📧 **อีเมลผู้ส่ง:** {sender_acc} | **จำนวนผู้รับที่จะจัดส่ง:** {len(targets)} ราย")
        
        col1, col2 = st.columns(2)
        with col1:
            provider = st.selectbox(
                "ระบบอีเมลของ Plan B ที่ใช้งานอยู่:",
                ["Microsoft 365 / Outlook (แนะนำสำหรับองค์กร)", "Google Workspace (Gmail)"]
            )
        with col2:
            acc_password = st.text_input("รหัสผ่านอีเมล / App Password:", type="password")
            
        if st.button("🚀 ยืนยันส่ง Email หาผู้รับทั้งหมดทันที", type="primary"):
            if not sender_acc.lower().endswith("@planbmedia.co.th"):
                st.error("❌ ไม่อนุญาตให้ใช้อีเมลอื่นที่ไม่ใช่ @planbmedia.co.th ส่งค่ะ")
            elif not acc_password:
                st.error("กรุณากรอกรหัสผ่านอีเมลก่อนส่งค่ะ")
            else:
                try:
                    if "Microsoft" in provider:
                        server = smtplib.SMTP('smtp.office365.com', 587)
                        server.starttls()
                        server.login(sender_acc, acc_password)
                    else:
                        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                        server.login(sender_acc, acc_password)
                    
                    progress_bar = st.progress(0)
                    for i, client in enumerate(targets):
                        msg = MIMEMultipart('alternative')
                        msg['From'] = sender_acc
                        msg['To'] = client['email']
                        msg['Subject'] = st.session_state['email_subject']
                        
                        email_html = f"""
                        <!DOCTYPE html>
                        <html lang="th">
                        <head><meta charset="UTF-8"></head>
                        <body style="background:#edf2f7; font-family:'Sarabun', 'Tahoma', sans-serif; padding:20px 0; margin:0;">
                        <div style="max-width:620px; margin:0 auto; background:#ffffff; border-radius:4px; border:1px solid #d8e6f5; overflow:hidden;">
                          <div style="background:#042C53; padding:36px; color:#ffffff;">
                            <div style="font-family:'Kanit',sans-serif; font-size:17px; margin-bottom:15px; font-weight:500;">PLAN B<span style="color:#85B7EB;"> MEDIA</span></div>
                            <h1 style="font-family:'Kanit',sans-serif; font-size:26px; line-height:1.3; margin:0 0 12px 0;">เข้าถึงคนไทย<br><span style="color:#85B7EB;">ทุก touchpoint</span><br>ในชีวิตประจำวัน</h1>
                            <p style="font-size:13px; color:rgba(255,255,255,0.75); line-height:1.6; margin:0;">Plan B Media มี ecosystem สื่อนอกบ้านครบวงจรที่ใหญ่ที่สุดในประเทศไทย</p>
                          </div>
                          <div style="padding:30px 36px;">
                            <div style="font-size:15px; color:#0C447C; font-weight:600; margin-bottom:14px; font-family:'Kanit',sans-serif;">เรียน คุณ {client['contact_name']},</div>
                            <p style="font-size:14px; color:#3a3a3a; line-height:1.7; margin-bottom:20px;">
                              สวัสดีค่ะ ดิฉัน <strong>{st.session_state['sales_name']}</strong> จาก Plan B Media ค่ะ<br><br>
                              เห็นว่า <strong>{client['company']}</strong> กำลังขยาย reach ในกลุ่ม {client.get('target', 'Target Audience')} ซึ่งตรงกับ audience ที่สื่อของเราเข้าถึงได้ทุกวันในทุก touchpoint ค่ะ
                            </p>
                            <div style="font-size:11px; text-transform:uppercase; color:#378ADD; font-weight:600; margin-bottom:12px; font-family:'Kanit',sans-serif;">Plan B Media Ecosystem & Media Packages</div>
                            <div style="background:#f0f6fd; padding:15px; border-radius:4px; font-size:13px; line-height:1.8; color:#3a3a3a; margin-bottom:20px;">
                              {st.session_state.get('media_formatted', '')}
                            </div>
                            <div style="background:#f0f6fd; border-left:4px solid #185FA5; padding:15px 18px; margin-bottom:24px; font-size:13px; color:#0C447C; line-height:1.6;">
                              เรามี data และ location strategy ที่คิดว่าจะเหมาะกับ <strong>{client['company']}</strong> โดยเฉพาะ — ขอนัดเพียง <strong>20 นาที</strong> เพื่อนำเสนอแนวทางที่ตรงกับ target audience ของคุณในวันและเวลาที่สะดวกค่ะ
                            </div>
                            <div style="padding:12px 16px; border:1px solid #D4E6F7; border-radius:4px; margin-bottom:24px; background:#ffffff;">
                              <div style="font-size:13px; font-weight:600; color:#042C53; font-family:'Kanit',sans-serif;">Plan B Media — Credentials & Media Portfolio</div>
                              <div style="font-size:11px; color:#777; margin-bottom:6px;">สามารถเข้าดูโฟลเดอร์สื่อและ Credentials ล่าสุดได้จากลิงก์ Google Drive ด้านล่างนี้ค่ะ</div>
                              <a href="{st.session_state.get('drive_link', 'https://drive.google.com')}" style="font-size:12px; color:#185FA5; font-weight:600; text-decoration:none; border:1px solid #B5D4F4; padding:5px 12px; border-radius:3px; display:inline-block;">📁 เปิดโฟลเดอร์ Google Drive สื่อทั้งหมด →</a>
                            </div>
                            <div style="text-align:center; margin:24px 0 10px;">
                              <a href="mailto:{st.session_state['sales_email']}?subject=นัดหมาย Plan B Media" style="background:#0C447C; color:#ffffff !important; font-family:'Kanit',sans-serif; font-size:14px; padding:12px 30px; border-radius:4px; text-decoration:none; display:inline-block; font-weight:500;">นัดพบเพื่อนำเสนอ — ใช้เวลาเพียง 20 นาที</a>
                            </div>
                          </div>
                          <div style="padding:0 36px 30px 36px;">
                            <p style="font-size:12px; color:#3a3a3a;">ขอบคุณมากนะคะ หากมีข้อสงสัยหรืออยากให้ส่งข้อมูลเพิ่มเติม ติดต่อได้ตลอดค่ะ</p>
                            <div style="padding:14px 16px; background:#f0f6fd; border:1px solid #D4E6F7; border-radius:4px;">
                              <div style="font-family:'Kanit',sans-serif; font-size:14px; font-weight:600; color:#042C53;">{st.session_state['sales_name']}</div>
                              <div style="font-size:11px; color:#777; margin-bottom:6px;">Sales Executive · Plan B Media PCL.</div>
                              <div style="font-size:11px; color:#378ADD;">📞 เบอร์โทร: {st.session_state['sales_phone']} | ✉ อีเมล: {st.session_state['sales_email']}</div>
                            </div>
                          </div>
                          <div style="background:#042C53; padding:16px; text-align:center; color:rgba(133, 183, 235, 0.6); font-size:10px;">© 2026 Plan B Media PCL. · 123 ถนนวิภาวดี กรุงเทพฯ 10400</div>
                        </div>
                        </body>
                        </html>
                        """
                        
                        msg.attach(MIMEText(email_html, 'html', 'utf-8'))
                        server.sendmail(sender_acc, client['email'], msg.as_string())
                        
                        progress_bar.progress((i + 1) / len(targets))
                        
                    server.quit()
                    st.balloons()
                    st.success("🎉 ส่งอีเมลด้วยบัญชี Plan B Media สำเร็จเรียบร้อยแล้วค่ะ!")
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {str(e)}")
    else:
        st.warning("⚠️ กรุณทำขั้นตอน STEP 01 ให้เสร็จสิ้นก่อนค่ะ")
