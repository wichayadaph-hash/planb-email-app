import streamlit as st
import urllib.parse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 1. ตั้งค่าหน้าเว็บสไตล์ Plan B Corporate Theme
st.set_page_config(page_title="Plan B - Multi-Client Email Automation", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b1118; }
    .stApp { background-color: #0b1118; color: #ffffff; }
    div[data-testid="stSidebar"] { background-color: #060a0f; }
    
    .card-box {
        background-color: #16202c;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #233346;
        margin-bottom: 15px;
    }
    
    .batch-btn {
        display: block;
        background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%);
        color: #ffffff !important;
        font-weight: bold;
        padding: 16px 24px;
        text-align: center;
        border-radius: 10px;
        text-decoration: none;
        font-size: 18px;
        box-shadow: 0 4px 15px rgba(0, 198, 255, 0.4);
        margin-top: 15px;
        border: none;
        width: 100%;
    }
    
    .gmail-link-btn {
        display: inline-block;
        background-color: #EA4335;
        color: #ffffff !important;
        font-weight: bold;
        padding: 8px 16px;
        border-radius: 6px;
        text-decoration: none;
        font-size: 14px;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. ฐานข้อมูลลูกค้า (สกัดจากไฟล์ รายชื่อลูกค้า.xlsx ของ Plan B)
CLIENT_LIST = [
    {"company": "บริษัท คอสเมคอน จำกัด", "email": "cosmecon.th@gmail.com", "contact": "ทีมการตลาด"},
    {"company": "บริษัท บิวทีเอสเดอร์มา จำกัด (Mediheal)", "email": "beauteousderma@gmail.com", "contact": "คุณบิวตี้"},
    {"company": "บริษัท บีดีเอ็มเอส เวลเนส คลินิก จำกัด", "email": "kunta.th@bdmswellness.com", "contact": "คุณกุนตา"},
    {"company": "บริษัท บริลเลียนท์แพลนส์ จำกัด (Parle)", "email": "marketing@brilliantplans.co.th", "contact": "ทีมการตลาด"},
    {"company": "บริษัท สตาร์ริชเชอร์ส กรุ๊ป จำกัด (MG)", "email": "warissara.benz@starrich.co.th", "contact": "ทีมการตลาด MG"},
    {"company": "บริษัท โอสปา อินเตอร์เนชั่นแนล จำกัด", "email": "marketing@o-spa.co.th", "contact": "ฝ่ายการตลาด"},
    {"company": "บริษัท นีโอ สุกี้ไทยเรสเทอรองส์ จำกัด", "email": "info@neosuki.com", "contact": "ทีมการตลาด"},
    {"company": "บริษัท เมดดิเวลเล่ จำกัด", "email": "info@mediwelle.com", "contact": "ทีมการตลาด"}
]

# ลิงก์ Drive หลัก
DRIVE_OUTTHERE_2026 = "https://drive.google.com/drive/folders/1RLAZiNBp1WoCO2QpgHlwAlsoSJBr74-w"
DRIVE_REPORTS = "https://drive.google.com/drive/folders/1v0WK53RI_EczHYHTpi7PC8zLrlbrDUrT"

# 3. เมนูด้านซ้าย
with st.sidebar:
    st.title("Plan B Media")
    st.caption("BATCH EMAIL AUTOMATION")
    st.markdown("---")
    step = st.radio("ขั้นตอนการทำงาน", ["01 ติ๊กเลือกลูกค้าหลายคน & สื่อ", "02 ตรวจทานร่างข้อความ", "03 กดส่ง Auto Batch Mail"])

st.markdown("## 🏢 PLAN B MEDIA • BATCH EMAIL AUTOMATION")

# --- STEP 01: เลือกหลายรายชื่อ ---
if "01" in step:
    st.markdown("### STEP 01 : เลือกกลุ่มเป้าหมายลูกค้าและประเภทสื่อที่ต้องการส่ง")
    
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.subheader("👥 1. ติ๊กเลือกรักษา/บริษัทลูกค้าที่ต้องการส่งพร้อมกัน")
        
        client_options = [f"{c['company']} ({c['email']})" for c in CLIENT_LIST]
        selected_clients_raw = st.multiselect(
            "เลือกรายชื่อลูกค้า (สามารถเลือกพร้อมกันได้หลายรายชื่อ):",
            options=client_options,
            default=[client_options[0], client_options[1]]
        )
        
        st.info(f"📌 จำนวนลูกค้าที่เลือกทั้งหมด: **{len(selected_clients_raw)}** ราย")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.subheader("📢 2. เลือกหมวดสื่อ / เรื่องที่ต้องการส่ง")
        email_category = st.selectbox(
            "เลือกเรื่องที่ต้องการเสนอขาย / แจ้งลูกค้า:",
            [
                "New Media: สื่อใหม่ 'The 20' (DOOH ยาวที่สุดบนทางด่วน)",
                "New Media: สื่อใหม่ 'Central Park' (Dusit Central Park)",
                "Report: รายงานภาพถ่ายการขึ้นสื่อ (Execution Report)",
                "Outthere: อัปเดต Outthere Newsletter & Case Study ปี 2026"
            ]
        )
        custom_drive = st.text_input("แนบลิงก์ Google Drive เฉพาะ (ถ้ามี):", placeholder="วางลิงก์ไฟล์ หรือเว้นว่างไว้เพื่อใช้ Drive หลัก")
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("✨ ให้ AI สร้างร่างอีเมล Batch อัตโนมัติ"):
        selected_targets = []
        for raw in selected_clients_raw:
            for item in CLIENT_LIST:
                if item["company"] in raw:
                    selected_targets.append(item)
                    break
                    
        st.session_state["batch_targets"] = selected_targets
        st.session_state["email_category"] = email_category
        st.session_state["custom_drive"] = custom_drive
        
        st.success(f"สร้างร่างอีเมลสำหรับลูกค้า {len(selected_targets)} รายสำเร็จ! กดไปที่ '02 ตรวจทานร่างข้อความ'")

# --- STEP 02: ตรวจทาน ---
elif "02" in step:
    st.markdown("### STEP 02 : ตรวจทานโครงสร้างข้อความก่อนจัดส่ง")
    if "batch_targets" in st.session_state:
        category = st.session_state.get("email_category", "")
        custom_drive = st.session_state.get("custom_drive", "")
        targets = st.session_state.get("batch_targets", [])
        
        st.write(f"**รายชื่อที่จะส่งไปหา ({len(targets)} รายชื่อ):**")
        for t in targets:
            st.write(f"- {t['company']} (`{t['email']}`)")
            
        st.markdown("---")
        
        if "The 20" in category:
            subj = "[Plan B Media] OUTDOOR TRENDS: สื่อใหม่ล่าสุด 'The 20' สัมผัสประสบการณ์ใหม่กับ DOOH ที่ยาวที่สุดในโลก"
            body = """เรียน คุณ {contact_name} ({company_name}),

ทาง Plan B ขอแนะนำสื่อ "The 20" สื่อดิจิทัลใหม่ล่าสุดจาก Plan B เพื่อเฉลิมฉลองครบรอบ 20 ปีของเรา โดยได้พลิกโฉมป้ายโฆษณา Serie Poles เดิม ให้กลายเป็นจอ LED กว่า 74 จอ เรียงรายตลอดเส้นทางยาวกว่า 2.5 กม. บนทางด่วนพิเศษเฉลิมมหานคร ใจกลาง Prime CBD มุ่งหน้าสู่ถนนวิภาวดี และถนนพระราม 4

จุดเด่นสื่อ The 20:
- ความคมชัดสูงขึ้น 2 เท่า สะกดทุกสายตา มองเห็นชัดเจนจากระยะไกล
- รองรับ Storytelling ทรงพลัง เล่นลูกเล่นต่อเนื่องตลอด 74 จอ
- มีทีม Sunbeam (Creative Agency) ดูแลการออกแบบและพัฒนาคอนเทนต์ให้อย่างครบวงจร

หากสนใจข้อมูลเพิ่มเติมหรือต้องการใบเสนอราคา สามารถติดต่อกลับอีเมลนี้ได้ทันทีครับ

ขอแสดงความนับถือ
ทีมงาน Plan B Media"""

        elif "Central Park" in category:
            subj = "[Plan B Media] เปิดตัวจอ Signature ใหม่ล่าสุด! Central Park – สื่อดิจิทัลพรีเมียมใจกลางกรุงเทพฯ"
            body = """เรียน คุณ {contact_name} ({company_name}),

ทาง Plan B มีความยินดีนำเสนอ "Central Park" จอดิจิทัลใหม่ล่าสุด บนโครงการมิกซ์ยูสระดับโลก Dusit Central Park บริเวณหัวมุมถนนสีลม – พระราม 4 เชื่อมต่อกับทั้ง BTS ศาลาแดง และ MRT สีลม

จุดเด่นของสื่อ Central Park:
- จอ LED Digital Curved ขนาดใหญ่กว่า 518 sq.m. บน facade ห้าง Central Park
- ออกแบบเพื่อรองรับงาน Creative Content โดยเฉพาะ 3D Visual
- เข้าถึงผู้คนมากกว่า 8 ล้าน eyeballs/เดือน และ Reach กว่า 2.6 ล้านคน/เดือน

หากสนใจแพ็กเกจหรือต้องการข้อมูลเพิ่มเติม สามารถตอบกลับอีเมลนี้ได้ตลอดเวลาครับ

ขอแสดงความนับถือ
ทีมงาน Plan B Media"""

        elif "Report" in category:
            drive_link = custom_drive.strip() if custom_drive.strip() else DRIVE_REPORTS
            subj = "[Report] รายงานภาพการขึ้นสื่อโฆษณา - แบรนด์ {company_name}"
            body = f"""เรียน ทีมการตลาด {{company_name}},

บริษัท แพลน บี มีเดีย จำกัด (มหาชน) ขอส่งมอบรายงานภาพถ่ายการขึ้นสื่อโฆษณา (Media Execution Report) เพื่อยืนยันการดำเนินงานสำหรับแคมเปญของท่าน

ท่านสามารถเข้าชมและดาวน์โหลดรูปภาพการขึ้นสื่อฉบับเต็มได้ที่ลิงก์นี้ครับ:
🔗 ลิงก์รายงานภาพการขึ้นสื่อ: {drive_link}

ขอแสดงความนับถือ
ทีมงาน Plan B Media"""

        else: # Outthere
            drive_link = custom_drive.strip() if custom_drive.strip() else DRIVE_OUTTHERE_2026
            subj = "[Plan B Outthere 2026] อัปเดตเทรนด์และแพ็กเกจสื่อประจำเดือนสำหรับ {company_name}"
            body = f"""เรียน ทีมการตลาด {{company_name}},

ทาง Plan B ขอส่งมอบ Newsletter และ Case Study ล่าสุดประจำปี 2026 เพื่ออัปเดตอินไซต์การสื่อสาร OOH และแพ็กเกจสื่อ Outthere สำหรับแบรนด์ {{company_name}}

ท่านสามารถเข้าชมและดาวน์โหลดเอกสารอัปเดตประจำเดือนได้จากคลัง Google Drive นี้ครับ:
🔗 คลังเอกสาร Outthere 2026: {drive_link}

ขอแสดงความนับถือ
ทีมงาน Plan B Media"""

        st.text_input("หัวข้ออีเมล (Template Subject):", value=subj, disabled=True)
        st.text_area("เนื้อหาอีเมล (Template Body):", value=body, height=250, disabled=True)
        
        st.session_state["final_subj"] = subj
        st.session_state["final_body"] = body
        st.info("ตรวจสอบแล้ว กดไปที่เมนู '03 กดส่ง Auto Batch Mail' ด้านซ้าย")
    else:
        st.warning("กรุณาไปที่ STEP 01 เพื่อเลือกลูกค้าก่อนครับ")

# --- STEP 03: จัดส่ง Auto Batch Mail ---
elif "03" in step:
    st.markdown("### STEP 03 : จัดส่ง Auto Batch Mail ออกจากบัญชี @planbmedia.co.th")
    
    if "batch_targets" in st.session_state:
        targets = st.session_state.get("batch_targets", [])
        subj_tmpl = st.session_state.get("final_subj", "")
        body_tmpl = st.session_state.get("final_body", "")
        
        st.subheader(f"🚀 เตรียมส่งหาลูกค้าทั้งหมด {len(targets)} ราย")
        
        send_method = st.radio(
            "เลือกวิธีการส่งอีเมล:",
            [
                "1. Auto Batch Mail ส่งตรงทันทีผ่าน Google App Password (แนะนำ - คลิกเดียวส่งครบทุกคน)",
                "2. เปิดสเก็ตช์ร่างใน Gmail ทีละฉบับ (Gmail Webmail List)"
            ]
        )
        
        st.markdown("---")
        
        if "1." in send_method:
            st.markdown("#### 🔑 กรอกรหัส Google App Password สำหรับส่ง Batch")
            col_a, col_b = st.columns(2)
            with col_a:
                sender_email = st.text_input("อีเมล Plan B ผู้ส่ง:", value="wichayada.ph@planbmedia.co.th")
            with col_b:
                app_password = st.text_input("Google App Password (16 หลัก):", type="password", placeholder="xxxx xxxx xxxx xxxx")
            
            if st.button("🚀 กดคลิกเดียว! ส่ง Batch Mail หาลูกค้าทุกคนทันที", type="primary"):
                if sender_email and app_password:
                    success_count = 0
                    progress_bar = st.progress(0)
                    
                    try:
                        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                        server.login(sender_email, app_password)
                        
                        for idx, client in enumerate(targets):
                            cur_subj = subj_tmpl.format(company_name=client['company'], contact_name=client['contact'])
                            cur_body = body_tmpl.format(company_name=client['company'], contact_name=client['contact'])
                            
                            msg = MIMEMultipart()
                            msg['From'] = sender_email
                            msg['To'] = client['email']
                            msg['Subject'] = cur_subj
                            msg.attach(MIMEText(cur_body, 'plain', 'utf-8'))
                            
                            server.sendmail(sender_email, client['email'], msg.as_string())
                            success_count += 1
                            progress_bar.progress((idx + 1) / len(targets))
                            
                        server.quit()
                        st.balloons()
                        st.success(f"🎉 ส่งอีเมลสำเร็จครบถ้วนทั้ง {success_count} รายแล้วครับ!")
                        
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาดในการส่ง: {str(e)}")
                        st.caption("หมายเหตุ: ต้องใช้ Google App Password 16 หลักจากความปลอดภัยบัญชี Google ของบริษัทครับ")
                else:
                    st.warning("กรุณากรอกอีเมลและ App Password ให้ครบถ้วนก่อนครับ")
                    
        else: # เปิด Gmail List
            st.markdown("#### ✉️ รายการปุ่มเปิด Compose ใน Gmail สำหรับลูกค้าแต่ละราย:")
            for idx, client in enumerate(targets):
                cur_subj = subj_tmpl.format(company_name=client['company'], contact_name=client['contact'])
                cur_body = body_tmpl.format(company_name=client['company'], contact_name=client['contact'])
                
                enc_subj = urllib.parse.quote(cur_subj)
                enc_body = urllib.parse.quote(cur_body)
                g_url = f"https://mail.google.com/mail/?view=cm&fs=1&to={client['email']}&su={enc_subj}&body={enc_body}"
                
                col_x, col_y = st.columns([3, 1])
                with col_x:
                    st.write(f"**{idx+1}. {client['company']}** (`{client['email']}`)")
                with col_y:
                    st.markdown(f'<a href="{g_url}" target="_blank" class="gmail-link-btn">✉️ เปิด Gmail ของลูกค้ารายนี้</a>', unsafe_allow_html=True)
                st.markdown("---")
