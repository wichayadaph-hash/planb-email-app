import streamlit as st
import smtplib
import io
import re
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 📌 ตั้งค่าหน้าเว็บ Streamlit
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

# 📌 HTML แม่แบบจากไฟล์ planb_email_template.html
V1_COLD_OUTREACH_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<style>
  body { background: #edf2f7; font-family: 'Sarabun', 'Tahoma', sans-serif; padding: 20px 0; margin: 0; }
  .email-outer { max-width: 620px; margin: 0 auto; }
  .email-card { background: #ffffff; border-radius: 4px; overflow: hidden; border: 1px solid #d8e6f5; }
  .hero { background: #042C53; padding: 0; position: relative; }
  .hero-top-bar { background: #0C447C; padding: 14px 36px; display: flex; justify-content: space-between; align-items: center; }
  .hero-logo { font-family: 'Kanit', sans-serif; font-size: 17px; color: #ffffff; font-weight: 500; }
  .hero-logo span { color: #85B7EB; font-weight: 300; }
  .hero-main { padding: 36px; }
  .hero-eyebrow { background: rgba(55, 138, 221, 0.2); border: 1px solid rgba(55, 138, 221, 0.4); padding: 5px 12px; font-size: 10px; color: #85B7EB; display: inline-block; margin-bottom: 15px; }
  .hero-headline { font-family: 'Kanit', sans-serif; font-size: 26px; color: #ffffff; line-height: 1.3; margin-bottom: 12px; }
  .hero-headline em { font-style: normal; color: #85B7EB; }
  .hero-sub { font-size: 13px; color: rgba(255,255,255,0.75); line-height: 1.6; }
  .stats-band { background: #185FA5; padding: 15px 0; text-align: center; }
  .email-body { padding: 30px 36px; }
  .greeting-line { font-size: 15px; color: #0C447C; font-weight: 600; margin-bottom: 14px; font-family: 'Kanit', sans-serif; }
  .body-text { font-size: 14px; color: #3a3a3a; line-height: 1.7; margin-bottom: 20px; }
  .section-label { font-size: 11px; text-transform: uppercase; color: #378ADD; font-weight: 600; margin-bottom: 12px; font-family: 'Kanit', sans-serif; }
  .insight-box { background: #f0f6fd; border-left: 4px solid #185FA5; padding: 15px 18px; margin-bottom: 24px; }
  .insight-box-text { font-size: 13px; color: #0C447C; line-height: 1.6; }
  .creds-row { padding: 12px 16px; border: 1px solid #D4E6F7; border-radius: 4px; margin-bottom: 24px; background: #ffffff; }
  .creds-title { font-size: 13px; font-weight: 600; color: #042C53; font-family: 'Kanit', sans-serif; }
  .creds-sub { font-size: 11px; color: #777; }
  .creds-btn { font-size: 12px; color: #185FA5; font-weight: 600; text-decoration: none; border: 1px solid #B5D4F4; padding: 5px 12px; border-radius: 3px; display: inline-block; margin-top: 6px; }
  .cta-wrap { text-align: center; margin: 24px 0 10px; }
  .cta-btn { background: #0C447C; color: #ffffff !important; font-family: 'Kanit', sans-serif; font-size: 14px; padding: 12px 30px; border-radius: 4px; text-decoration: none; display: inline-block; font-weight: 500; }
  .sig-card { padding: 14px 16px; background: #f0f6fd; border: 1px solid #D4E6F7; border-radius: 4px; margin-top: 20px; }
  .sig-name { font-family: 'Kanit', sans-serif; font-size: 14px; font-weight: 600; color: #042C53; }
  .sig-title { font-size: 11px; color: #777; margin-bottom: 6px; }
  .sig-contacts { font-size: 11px; color: #378ADD; }
  .email-footer { background: #042C53; padding: 16px; text-align: center; color: rgba(133, 183, 235, 0.6); font-size: 10px; }
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
      <div class="greeting-line">เรียน คุณ {{Contact Name}},</div>
      <p class="body-text">
        สวัสดีค่ะ ดิฉัน <strong>{{Sales Name}}</strong> จาก Plan B Media ค่ะ<br><br>
        เห็นว่า <strong>{{Company Name}}</strong> กำลังขยาย reach ในกลุ่ม {{Target Audience}} ซึ่งตรงกับ audience ที่สื่อของเราเข้าถึงได้ทุกวันในทุก touchpoint ค่ะ — ไม่ว่าจะเป็นขณะเดินทาง ช็อปปิ้ง หรือผ่านสนามบิน
      </p>
      <div class="section-label">Plan B Media Ecosystem</div>
      <div class="body-text" style="background:#f0f6fd; padding:12px; border-radius:4px; font-size:12px;">
        📍 <strong>Classic:</strong> Billboard ทั่วประเทศ<br>
        📍 <strong>Digital:</strong> จอดิจิทัลกลางเมือง & ห้างสรรพสินค้าชั้นนำ<br>
        📍 <strong>Retail:</strong> Siam Piwat, Central, The Mall, 7-Eleven<br>
        📍 <strong>Transit:</strong> BTS, MRT, Bus, EV Muvmi<br>
        📍 <strong>Airport:</strong> สุวรรณภูมิ ดอนเมือง + 25 แห่งทั่วประเทศ
      </div>
      <div class="insight-box">
        <div class="insight-box-text">
          เรามี data และ location strategy ที่คิดว่าจะเหมาะกับ <strong>{{Company Name}}</strong> โดยเฉพาะ — ขอนัดเพียง <strong>20 นาที</strong> เพื่อนำเสนอแนวทางที่ตรงกับ target audience ของคุณในวันและเวลาที่สะดวกค่ะ
        </div>
      </div>
      <div class="creds-row">
        <div class="creds-title">Plan B Media — Credentials & Portfolio</div>
        <div class="creds-sub">ดูผลงาน case study และข้อมูลสื่อเพิ่มเติม</div>
        <a href="https://drive.google.com/drive/folders/17zsuHUxw8JddzTGYUyB_lVslAOq4aEgC?usp=sharing" class="creds-btn">ดู Credentials →</a>
      </div>
      <div class="cta-wrap">
        <a href="mailto:{{Sales Email}}?subject=นัดหมาย Plan B Media" class="cta-btn">นัดพบเพื่อนำเสนอ — ใช้เวลาเพียง 20 นาที</a>
      </div>
    </div>
    <div class="email-body" style="padding-top:0;">
      <p class="body-text" style="font-size:12px;">ขอบคุณมากนะคะ หากมีข้อสงสัยหรืออยากให้ส่งข้อมูลเพิ่มเติม ติดต่อได้ตลอดค่ะ</p>
      <div class="sig-card">
        <div class="sig-name">{{Sales Name}}</div>
        <div class="sig-title">Sales Executive · Plan B Media PCL.</div>
        <div class="sig-contacts">
          📞 เบอร์โทร: {{Sales Phone}} | ✉ อีเมล: {{Sales Email}}
        </div>
      </div>
    </div>
    <div class="email-footer">© 2026 Plan B Media PCL. · 123 ถนนวิภาวดี กรุงเทพฯ 10400</div>
  </div>
</div>
</body>
</html>
"""

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.title("PLAN B MEDIA")
    st.caption("EMAIL AUTOMATION SYSTEM")
    st.markdown("---")
    
    st.subheader("⚙️ ข้อมูลผู้ส่ง (Sales Info)")
    sales_name = st.text_input("ชื่อผู้ส่ง (Sales Name):", value="วิชญาดา (พลอย)")
    sales_email = st.text_input("อีเมลผู้ส่ง (@planbmedia.co.th):", value="wichayada.ph@planbmedia.co.th")
    sales_phone = st.text_input("เบอร์โทรศัพท์ติดต่อ:", value="064-542-4441")
    
    st.markdown("---")
    st.subheader("👥 นำเข้าข้อมูลลูกค้าเป้าหมาย")
    input_method = st.radio("เลือกวิธีนำเข้าข้อมูล:", ["ใช้ข้อมูลตัวอย่าง", "แปะลิงก์ Google Sheets", "อัปโหลด Excel/CSV"])
    
    user_clients = []
    if input_method == "แปะลิงก์ Google Sheets":
        sheet_url = st.text_input("วางลิงก์ Google Sheets (เปิด Public):")
        if sheet_url:
            try:
                sheet_match = re.search(r'/d/([a-zA-Z0-9_-]+)', sheet_url)
                if sheet_match:
                    sheet_id = sheet_match.group(1)
                    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
                    df = pd.read_csv(csv_url)
                    for _, row in df.iterrows():
                        user_clients.append({
                            "company": str(row.iloc[0]),
                            "contact_name": str(row.iloc[1]) if len(row) > 1 else str(row.iloc[0]),
                            "email": str(row.iloc[2]) if len(row) > 2 else "",
                            "target": str(row.iloc[3]) if len(row) > 3 else "Mass Audience / Working Adult"
                        })
                    st.success(f"✅ โหลดสำเร็จ {len(user_clients)} รายชื่อ!")
            except Exception:
                st.error("⚠️ ไม่สามารถอ่านลิงก์ได้ กรุณาเช็คการเปิดสิทธิ์แชร์ Sheets")
                
    elif input_method == "อัปโหลด Excel/CSV":
        uploaded_file = st.file_uploader("เลือกไฟล์ Excel/CSV:", type=['xlsx', 'csv'])
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
                for _, row in df.iterrows():
                    user_clients.append({
                        "company": str(row.iloc[0]),
                        "contact_name": str(row.iloc[1]) if len(row) > 1 else str(row.iloc[0]),
                        "email": str(row.iloc[2]) if len(row) > 2 else "",
                        "target": str(row.iloc[3]) if len(row) > 3 else "Mass Audience / Working Adult"
                    })
                st.success(f"✅ โหลดสำเร็จ {len(user_clients)} รายชื่อ!")
            except Exception:
                st.error("⚠️ โครงสร้างไฟล์ไม่ถูกต้อง")

    st.markdown("---")
    step = st.radio("ขั้นตอนการทำงาน", ["01 จัดการกลุ่มเป้าหมาย", "02 พรีวิว HTML Email", "03 ยืนยันการส่ง Email"])

st.markdown("# 🏢 PLAN B MEDIA • HTML EMAIL ENGINE")

# --- STEP 01 ---
if "01" in step:
    st.subheader("STEP 01 : เลือกลูกค้าเป้าหมายและกำหนดหัวข้ออีเมล")
    
    subject_input = st.text_input("📌 Subject (หัวข้ออีเมล):", value="แนะนำสื่อนอกบ้าน Out-of-Home Media ครบวงจรจาก Plan B Media")
    
    active_db = user_clients if user_clients else [
        {"company": "บริษัท คอสเมคอน จำกัด", "contact_name": "คุณคอสเมคอน", "email": "cosmecon.th@gmail.com", "target": "กลุ่มบิวตี้และสกินแคร์"},
        {"company": "บริษัท บิวทีเอสเดอร์มา จำกัด (Mediheal)", "contact_name": "คุณเมดิฮีล", "email": "beauteousderma@gmail.com", "target": "กลุ่มคนรักสุขภาพและความงาม"},
        {"company": "บริษัท สตาร์ริชเชอร์ส กรุ๊ป จำกัด (MG)", "contact_name": "คุณเอ็มจี", "email": "warissara.benz@starrich.co.th", "target": "กลุ่มคนใช้รถยนต์ส่วนตัว"}
    ]
    
    st.write("👥 **เลือกรายชื่อที่จะจัดส่ง:**")
    client_options = [f"{c['company']} ({c['contact_name']})" for c in active_db]
    select_all = st.checkbox("✅ เลือกทั้งหมด", value=True)
    selected = client_options if select_all else []
    chosen_clients = st.multiselect("รายชื่อที่เลือก:", options=client_options, default=selected)

    if st.button("🚀 ประมวลผลและไปที่ STEP 02", type="primary"):
        final_list = [c for c in active_db if f"{c['company']} ({c['contact_name']})" in chosen_clients]
        if not final_list:
            st.error("กรุณาเลือกผู้รับอย่างน้อย 1 รายการค่ะ")
        else:
            st.session_state["final_targets"] = final_list
            st.session_state["email_subject"] = subject_input
            st.session_state["sales_name"] = sales_name
            st.session_state["sales_email"] = sales_email
            st.session_state["sales_phone"] = sales_phone
            st.success("บันทึกข้อมูลเรียบร้อยแล้ว! กรุณาคลิกเลือก '02 พรีวิว HTML Email' ทางแถบซ้ายมือค่ะ")

# --- STEP 02 ---
elif "02" in step:
    st.subheader("STEP 02 : ตรวจสอบพรีวิว HTML Template")
    if "final_targets" in st.session_state:
        targets = st.session_state["final_targets"]
        first = targets[0]
        
        st.info(f"📌 **Subject:** {st.session_state['email_subject']}")
        st.write(f"👁️ **ตัวอย่างพรีวิวอีเมลที่จะส่งถึง:** {first['company']} ({first['contact_name']})")
        
        # แทนค่าตัวแปรลงใน HTML Template
        preview_html = V1_COLD_OUTREACH_TEMPLATE\
            .replace("{{Contact Name}}", first["contact_name"])\
            .replace("{{Company Name}}", first["company"])\
            .replace("{{Target Audience}}", first.get("target", "Target Audience"))\
            .replace("{{Sales Name}}", st.session_state["sales_name"])\
            .replace("{{Sales Email}}", st.session_state["sales_email"])\
            .replace("{{Sales Phone}}", st.session_state["sales_phone"])
            
        st.components.v1.html(preview_html, height=750, scrolling=True)
    else:
        st.warning("⚠️ กรุณทำขั้นตอน STEP 01 ให้เสร็จสิ้นก่อนค่ะ")

# --- STEP 03 ---
elif "03" in step:
    st.subheader("STEP 03 : ยืนยันการส่ง Batch Email")
    if "final_targets" in st.session_state:
        targets = st.session_state["final_targets"]
        
        col1, col2 = st.columns(2)
        with col1:
            sender_acc = st.text_input("ใส่อีเมลผู้ส่ง (Google Account):", value=st.session_state.get("sales_email", ""))
        with col2:
            app_pwd = st.text_input("ใส่ Google App Password (16 หลัก):", type="password")
            
        if st.button("🚀 ยืนยันส่ง Email หาผู้รับทั้งหมดทันที", type="primary"):
            if not sender_acc or not app_pwd:
                st.error("กรุณากรอกอีเมลและ App Password ให้ครบถ้วนค่ะ")
            else:
                try:
                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    server.login(sender_acc, app_pwd)
                    
                    progress_bar = st.progress(0)
                    for i, client in enumerate(targets):
                        msg = MIMEMultipart('alternative')
                        msg['From'] = sender_acc
                        msg['To'] = client['email']
                        msg['Subject'] = st.session_state['email_subject']
                        
                        custom_html = V1_COLD_OUTREACH_TEMPLATE\
                            .replace("{{Contact Name}}", client["contact_name"])\
                            .replace("{{Company Name}}", client["company"])\
                            .replace("{{Target Audience}}", client.get("target", "Target Audience"))\
                            .replace("{{Sales Name}}", st.session_state["sales_name"])\
                            .replace("{{Sales Email}}", st.session_state["sales_email"])\
                            .replace("{{Sales Phone}}", st.session_state["sales_phone"])
                        
                        msg.attach(MIMEText(custom_html, 'html', 'utf-8'))
                        server.sendmail(sender_acc, client['email'], msg.as_string())
                        
                        progress_bar.progress((i + 1) / len(targets))
                        
                    server.quit()
                    st.balloons()
                    st.success("🎉 ส่งอีเมลสำเร็จ! จัดส่งหาลูกค้าทุกรายด้วย Template HTML สวยงามเรียบร้อยแล้วค่ะ")
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการส่ง: {str(e)}")
    else:
        st.warning("⚠️ กรุณทำขั้นตอน STEP 01 ให้เสร็จสิ้นก่อนค่ะ")
