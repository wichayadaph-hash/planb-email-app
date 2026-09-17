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

# รูปภาพ Banner สื่อจริงสำหรับฝังในอีเมล HTML
MEDIA_IMAGES = {
    "The 20": "https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=800&q=80",
    "Central Park": "https://images.unsplash.com/photo-1519501025264-65ba15a82390?auto=format&fit=crop&w=800&q=80",
    "Outthere": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=800&q=80",
    "Report": "https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=800&q=80"
}

# ลิงก์ Drive หลัก
DRIVE_OUTTHERE_2026 = "https://drive.google.com/drive/folders/1RLAZiNBp1WoCO2QpgHlwAlsoSJBr74-w"
DRIVE_REPORTS = "https://drive.google.com/drive/folders/1v0WK53RI_EczHYHTpi7PC8zLrlbrDUrT"

# 3. เมนูด้านซ้าย
with st.sidebar:
    st.title("Plan B Media")
    st.caption("AI AUTOMATED EMAIL SYSTEM")
    st.markdown("---")
    step = st.radio("ขั้นตอนการทำงาน", ["01 เพิ่ม/เลือกชื่อลูกค้ารายคน & สื่อ", "02 ตรวจทานและแก้ไขดราฟต์ (มีรูปภาพ)", "03 กดส่ง Auto Mail"])

st.markdown("## 🏢 PLAN B MEDIA • EMAIL AUTOMATION")

# --- STEP 01: เพิ่ม/เลือกข้อมูลเองได้ ---
if "01" in step:
    st.markdown("### STEP 01 : กรอก/เลือกข้อมูลลูกค้า และเลือกหมวดสื่อ")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.subheader("👤 1. เพิ่มหรือแก้ไขข้อมูลลูกค้า")
        
        mode = st.radio("รูปแบบการใส่ข้อมูลลูกค้า:", ["กรอกข้อมูลเอง (Custom Input)", "เลือกจากตัวอย่างฐานข้อมูล"])
        
        if mode == "กรอกข้อมูลเอง (Custom Input)":
            company_name = st.text_input("ชื่อบริษัท / แบรนด์ลูกค้า", value=st.session_state.get("company_name", "บริษัท ชาโออิชิ จำกัด"))
            recipient_email = st.text_input("อีเมลลูกค้าผู้รับ", value=st.session_state.get("recipient_email", "client@example.com"))
            contact_name = st.text_input("ชื่อผู้ติดต่อ / ตำแหน่ง", value=st.session_state.get("contact_name", "ทีมการตลาด"))
        else:
            sample_client = st.selectbox("เลือกบริษัทตัวอย่าง:", [
                "บริษัท คอสเมคอน จำกัด (cosmecon.th@gmail.com)",
                "บริษัท บิวทีเอสเดอร์มา จำกัด (beauteousderma@gmail.com)",
                "บริษัท บีดีเอ็มเอส เวลเนส คลินิก จำกัด (kunta.th@bdmswellness.com)"
            ])
            if "คอสเมคอน" in sample_client:
                company_name, recipient_email, contact_name = "บริษัท คอสเมคอน จำกัด", "cosmecon.th@gmail.com", "ทีมการตลาด"
            elif "บิวทีเอสเดอร์มา" in sample_client:
                company_name, recipient_email, contact_name = "บริษัท บิวทีเอสเดอร์มา จำกัด (Mediheal)", "beauteousderma@gmail.com", "คุณบิวตี้"
            else:
                company_name, recipient_email, contact_name = "บริษัท บีดีเอ็มเอส เวลเนส คลินิก จำกัด", "kunta.th@bdmswellness.com", "คุณกุนตา"
            
            # เปิดให้แก้ไขได้แม้เลือกจากคลัง
            company_name = st.text_input("แก้ไขชื่อบริษัท:", value=company_name)
            recipient_email = st.text_input("แก้ไขอีเมลผู้รับ:", value=recipient_email)
            contact_name = st.text_input("แก้ไขชื่อผู้ติดต่อ:", value=contact_name)

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.subheader("📢 2. เลือกสื่อและลิงก์ประกอบ")
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

    if st.button("✨ ให้ AI สร้างร่างอีเมลพร้อมรูปภาพสื่ออัตโนมัติ"):
        st.session_state["company_name"] = company_name
        st.session_state["recipient_email"] = recipient_email
        st.session_state["contact_name"] = contact_name
        st.session_state["email_category"] = email_category
        st.session_state["custom_drive"] = custom_drive
        
        # กำหนดดราฟต์เริ่มต้น
        if "The 20" in email_category:
            st.session_state["draft_subject"] = f"[Plan B Media] OUTDOOR TRENDS: สื่อใหม่ล่าสุด 'The 20' สัมผัสประสบการณ์ใหม่กับ DOOH ที่ยาวที่สุดในโลก"
            st.session_state["draft_body"] = f"""เรียน คุณ {contact_name} ({company_name}),

ทาง Plan B ขอแนะนำสื่อ "The 20" สื่อดิจิทัลใหม่ล่าสุดจาก Plan B เพื่อเฉลิมฉลองครบรอบ 20 ปีของเรา โดยได้พลิกโฉมป้ายโฆษณา Serie Poles เดิม ให้กลายเป็นจอ LED กว่า 74 จอ เรียงรายตลอดเส้นทางยาวกว่า 2.5 กม. บนทางด่วนพิเศษเฉลิมมหานคร ใจกลาง Prime CBD มุ่งหน้าสู่ถนนวิภาวดี และถนนพระราม 4

จุดเด่นสื่อ The 20:
- ความคมชัดสูงขึ้น 2 เท่า สะกดทุกสายตา มองเห็นชัดเจนจากระยะไกล
- รองรับ Storytelling ทรงพลัง เล่นลูกเล่นต่อเนื่องตลอด 74 จอ
- มีทีม Sunbeam (Creative Agency) ดูแลการออกแบบและพัฒนาคอนเทนต์ให้อย่างครบวงจร

หากคุณ {contact_name} สนใจข้อมูลหรือต้องการใบเสนอราคาเพิ่มเติม สามารถติดต่อกลับอีเมลนี้ได้ทันทีครับ

ขอแสดงความนับถือ
ทีมงาน Plan B Media"""
            st.session_state["img_url"] = MEDIA_IMAGES["The 20"]

        elif "Central Park" in email_category:
            st.session_state["draft_subject"] = f"[Plan B Media] เปิดตัวจอ Signature ใหม่ล่าสุด! Central Park – สื่อดิจิทัลพรีเมียมใจกลางกรุงเทพฯ"
            st.session_state["draft_body"] = f"""เรียน คุณ {contact_name} ({company_name}),

ทาง Plan B มีความยินดีนำเสนอ "Central Park" จอดิจิทัลใหม่ล่าสุด บนโครงการมิกซ์ยูสระดับโลก Dusit Central Park บริเวณหัวมุมถนนสีลม – พระราม 4 เชื่อมต่อกับทั้ง BTS ศาลาแดง และ MRT สีลม

จุดเด่นของสื่อ Central Park:
- จอ LED Digital Curved ขนาดใหญ่กว่า 518 sq.m. บน facade ห้าง Central Park
- ออกแบบเพื่อรองรับงาน Creative Content โดยเฉพาะ 3D Visual
- เข้าถึงผู้คนมากกว่า 8 ล้าน eyeballs/เดือน และ Reach กว่า 2.6 ล้านคน/เดือน

หากสนใจแพ็กเกจหรือต้องการข้อมูลเพิ่มเติม สามารถตอบกลับอีเมลนี้ได้ตลอดเวลาครับ

ขอแสดงความนับถือ
ทีมงาน Plan B Media"""
            st.session_state["img_url"] = MEDIA_IMAGES["Central Park"]

        elif "Report" in email_category:
            drive_link = custom_drive.strip() if custom_drive.strip() else DRIVE_REPORTS
            st.session_state["draft_subject"] = f"[Report] รายงานภาพการขึ้นสื่อโฆษณา - แบรนด์ {company_name}"
            st.session_state["draft_body"] = f"""เรียน ทีมการตลาด {company_name},

บริษัท แพลน บี มีเดีย จำกัด (มหาชน) ขอส่งมอบรายงานภาพถ่ายการขึ้นสื่อโฆษณา (Media Execution Report) เพื่อยืนยันการดำเนินงานสำหรับแคมเปญของท่าน

ท่านสามารถเข้าชมและดาวน์โหลดรูปภาพการขึ้นสื่อฉบับเต็มได้ที่ลิงก์นี้ครับ:
🔗 ลิงก์รายงานภาพการขึ้นสื่อ: {drive_link}

ขอแสดงความนับถือ
ทีมงาน Plan B Media"""
            st.session_state["img_url"] = MEDIA_IMAGES["Report"]

        else: # Outthere
            drive_link = custom_drive.strip() if custom_drive.strip() else DRIVE_OUTTHERE_2026
            st.session_state["draft_subject"] = f"[Plan B Outthere 2026] อัปเดตเทรนด์และแพ็กเกจสื่อประจำเดือนสำหรับ {company_name}"
            st.session_state["draft_body"] = f"""เรียน ทีมการตลาด {company_name},

ทาง Plan B ขอส่งมอบ Newsletter และ Case Study ล่าสุดประจำปี 2026 เพื่ออัปเดตอินไซต์การสื่อสาร OOH และแพ็กเกจสื่อ Outthere สำหรับแบรนด์ {company_name}

ท่านสามารถเข้าชมและดาวน์โหลดเอกสารอัปเดตประจำเดือนได้จากคลัง Google Drive นี้ครับ:
🔗 คลังเอกสาร Outthere 2026: {drive_link}

ขอแสดงความนับถือ
ทีมงาน Plan B Media"""
            st.session_state["img_url"] = MEDIA_IMAGES["Outthere"]

        st.success("สร้างร่างอีเมลสำเร็จ! กดไปที่ '02 ตรวจทานและแก้ไขดราฟต์'")

# --- STEP 02: แก้ไขดราฟต์ + พรีวิวรูปภาพ ---
elif "02" in step:
    st.markdown("### STEP 02 : ตรวจทาน แก้ไขข้อความดราฟต์ และพรีวิวอีเมลพร้อมรูปภาพ")
    if "draft_body" in st.session_state:
        col_edit, col_preview = st.columns([1.1, 1])
        
        with col_edit:
            st.subheader("✏️ แก้ไขเนื้อหาอีเมลตามต้องการ")
            editable_subj = st.text_input("แก้ไขหัวข้ออีเมล (Subject):", value=st.session_state.get("draft_subject", ""))
            editable_body = st.text_area("แก้ไขเนื้อหาอีเมล (Body):", value=st.session_state.get("draft_body", ""), height=320)
            
            st.session_state["draft_subject"] = editable_subj
            st.session_state["draft_body"] = editable_body
            st.info("แก้ไขข้อความเสร็จแล้ว กดไปที่เมนู '03 กดส่ง Auto Mail' ด้านซ้ายได้เลยครับ")

        with col_preview:
            st.subheader("🖼️ พรีวิวตัวอย่างอีเมล (มีรูปภาพสื่อ)")
            st.markdown(f"**To:** `{st.session_state.get('recipient_email')}`")
            st.markdown(f"**Subject:** {editable_subj}")
            
            # พรีวิวการ์ดอีเมลแบบ HTML
            st.image(st.session_state.get("img_url"), caption="รูปภาพสื่อโฆษณาประกอบในอีเมล", use_column_width=True)
            st.text_area("ตัวอย่างข้อความ:", value=editable_body, height=180, disabled=True)
            
    else:
        st.warning("กรุณาไปที่ STEP 01 เพื่อสร้างอีเมลก่อนครับ")

# --- STEP 03: ส่ง Auto Mail ---
elif "03" in step:
    st.markdown("### STEP 03 : จัดส่ง Auto Mail ออกจากบัญชี @planbmedia.co.th")
    
    if "draft_body" in st.session_state:
        recipient = st.session_state.get('recipient_email', '')
        company = st.session_state.get('company_name', '')
        subj = st.session_state.get('draft_subject', '')
        body = st.session_state.get('draft_body', '')
        img_url = st.session_state.get('img_url', '')
        
        st.write(f"**บริษัทลูกค้า:** `{company}`")
        st.write(f"**อีเมลผู้รับ:** `{recipient}`")
        
        st.markdown("---")
        send_option = st.radio("เลือกวิธีการจัดส่ง:", [
            "1. Auto Mail พร้อมรูปภาพสื่อ (ส่งตรงผ่าน Google App Password / SMTP)",
            "2. เปิดสเก็ตช์ร่างใน Gmail (Gmail Webmail Parameter)"
        ])
        
        if "1." in send_option:
            st.markdown("#### 🔑 กรอกรหัสส่งอีเมลสำหรับส่งรูปภาพ HTML")
            col_x, col_y = st.columns(2)
            with col_x:
                sender_email = st.text_input("อีเมลผู้ส่ง:", value="wichayada.ph@planbmedia.co.th")
            with col_y:
                app_password = st.text_input("Google App Password (16 หลัก):", type="password")
                
            if st.button("🚀 กดส่ง Auto Mail พร้อมรูปภาพสื่อทันที", type="primary"):
                if sender_email and app_password:
                    try:
                        # สร้างโครงสร้าง HTML Email แบบมีรูปภาพ
                        html_content = f"""
                        <html>
                        <body style="font-family: Arial, sans-serif; color: #333333; line-height: 1.6;">
                            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
                                <img src="{img_url}" alt="Plan B Media" style="width: 100%; height: auto; border-radius: 6px; margin-bottom: 20px;">
                                <div style="white-space: pre-wrap;">{body}</div>
                            </div>
                        </body>
                        </html>
                        """
                        
                        msg = MIMEMultipart('alternative')
                        msg['From'] = sender_email
                        msg['To'] = recipient
                        msg['Subject'] = subj
                        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
                        
                        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                        server.login(sender_email, app_password)
                        server.sendmail(sender_email, recipient, msg.as_string())
                        server.quit()
                        
                        st.balloons()
                        st.success("🎉 จัดส่งอีเมลพร้อมรูปภาพสื่อเรียบร้อยแล้วครับ!")
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาด: {str(e)}")
                else:
                    st.warning("กรุณากรอกอีเมลและ App Password ให้ครบถ้วนครับ")
        else:
            enc_subj = urllib.parse.quote(subj)
            enc_body = urllib.parse.quote(body)
            g_url = f"https://mail.google.com/mail/?view=cm&fs=1&to={recipient}&su={enc_subj}&body={enc_body}"
            st.markdown(f'<a href="{g_url}" target="_blank" class="gmail-link-btn">✉️ กดตรงนี้เพื่อเปิด Gmail สเก็ตช์ร่าง</a>', unsafe_allow_html=True)
            
    else:
        st.warning("กรุณาไปที่ STEP 01 เพื่อสร้างอีเมลก่อนครับ")
