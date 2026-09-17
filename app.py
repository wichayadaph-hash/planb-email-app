import streamlit as st
import urllib.parse

# 1. ตั้งค่าหน้าเว็บสไตล์ Plan B Corporate Theme (Dark Luxury)
st.set_page_config(page_title="Plan B - AI Email Automation", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b1118; }
    .stApp { background-color: #0b1118; color: #ffffff; }
    div[data-testid="stSidebar"] { background-color: #060a0f; }
    
    /* สไตล์การ์ดเลือกข้อมูล */
    .card-box {
        background-color: #16202c;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #233346;
        margin-bottom: 15px;
    }
    
    /* ปุ่มกดส่งอีเมลสีแดงสดใส สไตล์ Gmail */
    .gmail-btn {
        display: block;
        background: linear-gradient(135deg, #EA4335 0%, #C5221F 100%);
        color: #ffffff !important;
        font-weight: bold;
        padding: 16px 24px;
        text-align: center;
        border-radius: 10px;
        text-decoration: none;
        font-size: 18px;
        box-shadow: 0 4px 15px rgba(234, 67, 53, 0.4);
        margin-top: 20px;
    }
    .gmail-btn:hover {
        background: linear-gradient(135deg, #FF5242 0%, #D92723 100%);
    }
    </style>
""", unsafe_allow_html=True)

# 2. คลังข้อมูลลูกค้า (ตัวอย่างจากไฟล์รายชื่อลูกค้าใน Drive คุณพลอย)
CLIENT_DATABASE = {
    "บริษัท คอสเมคอน จำกัด": {"email": "cosmecon.th@gmail.com", "contact": "คุณลูกค้า"},
    "บริษัท บิวทีเอสเดอร์มา จำกัด (Mediheal)": {"email": "beauteousderma@gmail.com", "contact": "คุณบิวตี้"},
    "บริษัท บีดีเอ็มเอส เวลเนส คลินิก จำกัด": {"email": "kunta.th@bdmswellness.com", "contact": "คุณกุนตา"},
    "บริษัท บริลเลียนท์แพลนส์ จำกัด (Parle)": {"email": "marketing@brilliantplans.co.th", "contact": "ทีมการตลาด"},
    "บริษัท สตาร์ริชเชอร์ส กรุ๊ป จำกัด (MG)": {"email": "warissara.benz@starrich.co.th", "contact": "ทีมการตลาด MG"},
    "กรอกชื่อและอีเมลเอง (Manual Input)": {"email": "", "contact": ""}
}

# ลิงก์ Drive หลักตามที่คุณพลอยส่งมา
DRIVE_OUTTHERE_2026 = "https://drive.google.com/drive/folders/1RLAZiNBp1WoCO2QpgHlwAlsoSJBr74-w"
DRIVE_REPORTS = "https://drive.google.com/drive/folders/1v0WK53RI_EczHYHTpi7PC8zLrlbrDUrT"

# 3. เมนูด้านซ้าย (Sidebar)
with st.sidebar:
    st.title("Plan B Media")
    st.caption("AI AUTOMATED EMAIL SYSTEM")
    st.markdown("---")
    step = st.radio("ขั้นตอนการทำงาน", ["01 เลือกลูกค้าและสื่อ", "02 ตรวจทานข้อความ", "03 กดส่ง Auto Mail"])

st.markdown("## 🏢 PLAN B MEDIA • EMAIL AUTOMATION")

# --- STEP 01: เลือกข้อมูล ---
if "01" in step:
    st.markdown("### STEP 01 : เลือกข้อมูลลูกค้าและประเภทสื่อที่ต้องการส่ง")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.subheader("👤 1. ข้อมูลลูกค้า")
        selected_client = st.selectbox("เลือกชื่อบริษัทลูกค้าจากฐานข้อมูล:", list(CLIENT_DATABASE.keys()))
        
        if selected_client == "กรอกชื่อและอีเมลเอง (Manual Input)":
            client_name = st.text_input("ชื่อบริษัทลูกค้า", placeholder="เช่น บริษัท ชาโออิชิ จำกัด")
            recipient_email = st.text_input("อีเมลผู้รับ", placeholder="client@example.com")
            contact_name = st.text_input("ชื่อผู้ติดตอบ/ตำแหน่ง", value="ทีมการตลาด")
        else:
            client_name = selected_client
            recipient_email = st.text_input("อีเมลผู้รับ", value=CLIENT_DATABASE[selected_client]["email"])
            contact_name = st.text_input("ชื่อผู้ติดต่อ", value=CLIENT_DATABASE[selected_client]["contact"])
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.subheader("📢 2. สื่อและเรื่องที่ต้องการส่ง")
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

    if st.button("✨ คลิกเดียว! ให้ AI สร้างร่างอีเมลอัตโนมัติ"):
        st.session_state["client_name"] = client_name
        st.session_state["recipient_email"] = recipient_email
        st.session_state["contact_name"] = contact_name
        
        # --- ดึง Template จริงจาก Sales Note ใน Drive ---
        if "The 20" in email_category:
            st.session_state["email_subject"] = f"[Plan B Media] OUTDOOR TRENDS: สื่อใหม่ล่าสุด 'The 20' สัมผัสประสบการณ์ใหม่กับ DOOH ที่ยาวที่สุดในโลก"
            st.session_state["email_body"] = f"""เรียน คุณ {contact_name} ({client_name}),

ทาง Plan B ขอแนะนำสื่อ "The 20" สื่อดิจิทัลใหม่ล่าสุดจาก Plan B เพื่อเฉลิมฉลองครบรอบ 20 ปีของเรา โดยได้พลิกโฉมป้ายโฆษณา Serie Poles เดิม ให้กลายเป็นจอ LED กว่า 74 จอ เรียงรายตลอดเส้นทางยาวกว่า 2.5 กม. บนทางด่วนพิเศษเฉลิมมหานคร ใจกลาง Prime CBD มุ่งหน้าสู่ถนนวิภาวดี และถนนพระราม 4

จุดเด่นสื่อ The 20:
- ความคมชัดสูงขึ้น 2 เท่า สะกดทุกสายตา มองเห็นชัดเจนจากระยะไกล
- รองรับ Storytelling ทรงพลัง เล่นลูกเล่นต่อเนื่องตลอด 74 จอ
- มีทีม Sunbeam (Creative Agency) ดูแลการออกแบบและพัฒนาคอนเทนต์ให้อย่างครบวงจร

หากคุณ {contact_name} สนใจข้อมูลหรือต้องการใบเสนอราคาเพิ่มเติม สามารถตอบกลับอีเมลนี้ได้ทันทีครับ

ขอแสดงความนับถือ
ทีมงาน Plan B Media"""

        elif "Central Park" in email_category:
            st.session_state["email_subject"] = f"[Plan B Media] เปิดตัวจอ Signature ใหม่ล่าสุด! Central Park – สื่อดิจิทัลพรีเมียมใจกลางกรุงเทพฯ"
            st.session_state["email_body"] = f"""เรียน คุณ {contact_name} ({client_name}),

ทาง Plan B มีความยินดีนำเสนอ "Central Park" จอดิจิทัลใหม่ล่าสุด บนโครงการมิกซ์ยูสระดับโลก Dusit Central Park บริเวณหัวมุมถนนสีลม – พระราม 4 เชื่อมต่อกับทั้ง BTS ศาลาแดง และ MRT สีลม

จุดเด่นของสื่อ Central Park:
- จอ LED Digital Curved ขนาดใหญ่กว่า 518 sq.m. บน facade ห้าง Central Park
- ออกแบบเพื่อรองรับงาน Creative Content โดยเฉพาะ 3D Visual
- เข้าถึงผู้คนมากกว่า 8 ล้าน eyeballs/เดือน และ Reach กว่า 2.6 ล้านคน/เดือน

หากสนใจแพ็กเกจหรือต้องการข้อมูลเพิ่มเติม สามารถตอบกลับอีเมลนี้ได้ตลอดเวลาครับ

ขอแสดงความนับถือ
ทีมงาน Plan B Media"""

        elif "Report" in email_category:
            drive_link = custom_drive.strip() if custom_drive.strip() else DRIVE_REPORTS
            st.session_state["email_subject"] = f"[Report] รายงานภาพการขึ้นสื่อโฆษณา - แบรนด์ {client_name}"
            st.session_state["email_body"] = f"""เรียน ทีมการตลาด {client_name},

บริษัท แพลน บี มีเดีย จำกัด (มหาชน) ขอส่งมอบรายงานภาพถ่ายการขึ้นสื่อโฆษณา (Media Execution Report) เพื่อยืนยันการดำเนินงานสำหรับแคมเปญของท่าน

ท่านสามารถเข้าชมและดาวน์โหลดรูปภาพการขึ้นสื่อฉบับเต็มได้ที่ลิงก์นี้ครับ:
🔗 ลิงก์รายงานภาพการขึ้นสื่อ: {drive_link}

ขอแสดงความนับถือ
ทีมงาน Plan B Media"""

        else: # Outthere
            drive_link = custom_drive.strip() if custom_drive.strip() else DRIVE_OUTTHERE_2026
            st.session_state["email_subject"] = f"[Plan B Outthere 2026] อัปเดตเทรนด์และแพ็กเกจสื่อประจำเดือนสำหรับ {client_name}"
            st.session_state["email_body"] = f"""เรียน ทีมการตลาด {client_name},

ทาง Plan B ขอส่งมอบ Newsletter และ Case Study ล่าสุดประจำปี 2026 เพื่ออัปเดตอินไซต์การสื่อสาร OOH และแพ็กเกจสื่อ Outthere สำหรับแบรนด์ {client_name}

ท่านสามารถเข้าชมและดาวน์โหลดเอกสารอัปเดตประจำเดือนได้จากคลัง Google Drive นี้ครับ:
🔗 คลังเอกสาร Outthere 2026: {drive_link}

ขอแสดงความนับถือ
ทีมงาน Plan B Media"""

        st.success("สร้างเนื้อหาสำเร็จ! กดไปที่ '02 ตรวจทานข้อความ' หรือ '03 กดส่ง Auto Mail' ได้เลยครับ")

# --- STEP 02: ตรวจทาน ---
elif "02" in step:
    st.markdown("### STEP 02 : ตรวจทานและแก้ไขข้อความ")
    if "email_body" in st.session_state:
        subj = st.text_input("หัวข้ออีเมล (Subject):", value=st.session_state.get("email_subject", ""))
        body = st.text_area("เนื้อหาอีเมล (Body):", value=st.session_state.get("email_body", ""), height=300)
        st.session_state["email_subject"] = subj
        st.session_state["email_body"] = body
        st.info("ตรวจสอบเรียบร้อยแล้ว กดไปที่เมนู '03 กดส่ง Auto Mail' ด้านซ้าย")
    else:
        st.warning("กรุณาไปที่ STEP 01 เพื่อเลือกข้อมูลก่อนครับ")

# --- STEP 03: ส่งอีเมล ---
elif "03" in step:
    st.markdown("### STEP 03 : ส่งอีเมลออกจากบัญชี Plan B (@planbmedia.co.th)")
    if "email_body" in st.session_state:
        recipient = st.session_state.get('recipient_email', '')
        subj = st.session_state.get('email_subject', '')
        body = st.session_state.get('email_body', '')
        
        st.write(f"**ผู้รับ (To):** `{recipient}`")
        st.write(f"**หัวข้อ (Subject):** {subj}")
        st.text_area("ข้อความที่จะส่ง:", value=body, height=200, disabled=True)
        
        # URL Encode สำหรับ Gmail
        encoded_subj = urllib.parse.quote(subj)
        encoded_body = urllib.parse.quote(body)
        gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&to={recipient}&su={encoded_subj}&body={encoded_body}"
        
        st.markdown(f'<a href="{gmail_url}" target="_blank" class="gmail-btn">🚀 กดตรงนี้เพื่อเปิด Gmail และกดส่งได้ทันที</a>', unsafe_allow_html=True)
    else:
        st.warning("กรุณาไปที่ STEP 01 เพื่อเลือกข้อมูลก่อนครับ")
