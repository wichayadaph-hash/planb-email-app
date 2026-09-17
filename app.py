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

# 2. รายชื่อลูกค้าหลักสกัดจากไฟล์ Excel ใน Google Drive (150 แบรนด์)
CLIENT_DATABASE = [
    {"company": "บริษัท คอสเมคอน จำกัด", "email": "cosmecon.th@gmail.com", "contact": "ทีมการตลาด"},
    {"company": "บริษัท โอสปา อินเตอร์เนชั่นแนล จำกัด", "email": "marketing@o-spa.co.th", "contact": "ฝ่ายการตลาด"},
    {"company": "บริษัท นีโอ สุกี้ไทยเรสเทอรองส์ จำกัด", "email": "info@neosuki.com", "contact": "ทีมการตลาด"},
    {"company": "มัสตาร์ด สนีกเกอร์", "email": "hello@mustardsneakers.com", "contact": "คุณมาร์เก็ตติ้ง"},
    {"company": "บริษัท ได้เงิน ดอทคอม จำกัด", "email": "hr@asnbroker.co.th", "contact": "ทีมการตลาด"},
    {"company": "บริษัท เมดดิเวลเล่ จำกัด", "email": "info@mediwelle.com", "contact": "ทีมการตลาด"},
    {"company": "บริษัท แอสเซนด์ คอมเมิร์ซ จำกัด", "email": "support@amaze.shop", "contact": "ทีมการตลาด"},
    {"company": "บริษัท วทานิกา กรุ๊ป จำกัด", "email": "info@vatanika-design.com", "contact": "ทีมการตลาด"},
    {"company": "บริษัท ธีระมงคล อุตสาหกรรม จำกัด (มหาชน)", "email": "webmaster@thaiballast.com", "contact": "ทีมการตลาด"},
    {"company": "บริษัท พาภิญโญ กรุ๊ป จำกัด (สบู่เบนเนท)", "email": "bennettsoap@gmail.com", "contact": "ทีมการตลาด"},
    {"company": "บริษัท บิวทีเอสเดอร์มา จำกัด (Mediheal)", "email": "beauteousderma@gmail.com", "contact": "คุณบิวตี้"},
    {"company": "บริษัท บีดีเอ็มเอส เวลเนส คลินิก จำกัด", "email": "kunta.th@bdmswellness.com", "contact": "คุณกุนตา"},
    {"company": "บริษัท บริลเลียนท์แพลนส์ จำกัด (Parle)", "email": "marketing@brilliantplans.co.th", "contact": "ทีมการตลาด"},
    {"company": "บริษัท สตาร์ริชเชอร์ส กรุ๊ป จำกัด (MG)", "email": "warissara.benz@starrich.co.th", "contact": "ทีมการตลาด MG"},
    {"company": "บริษัท ยูนิเวอร์ซัล มิวสิค (ประเทศไทย) จำกัด", "email": "vasee.seehamat@umusic.com", "contact": "คุณ Bibi Ramida"},
    {"company": "บริษัท ศรีฟ้าโฟรเซนฟู้ด จำกัด", "email": "chairut.ru@srifabakery.co.th", "contact": "คุณ Chairut"},
    {"company": "บริษัท วีโว่ เซอร์วิส (ประเทศไทย) จำกัด (vivo)", "email": "chitchanok.h@viq.group", "contact": "คุณ Chitchanok"},
    {"company": "บริษัท มอนเดลีซ อินเตอร์เนชันแนล (ประเทศไทย) จำกัด", "email": "chidchanok.limvattana@mdlz.com", "contact": "คุณ Beauty Marketing"},
    {"company": "บริษัท บิ๊กซี ซูเปอร์เซ็นเตอร์ จำกัด (มหาชน)", "email": "customer.service@bigc.co.th", "contact": "ทีมการตลาด"},
    {"company": "บริษัท สยามพารากอน รีเทล จำกัด", "email": "contact@siamparagon.co.th", "contact": "ทีมการตลาด"}
]

# รูปภาพประกอบสำหรับสื่อแต่ละประเภท
MEDIA_IMAGES = {
    "The 20": "https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=800&q=80",
    "Central Park": "https://images.unsplash.com/photo-1519501025264-65ba15a82390?auto=format&fit=crop&w=800&q=80",
    "Outthere": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=800&q=80",
    "Report": "https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=800&q=80"
}

DRIVE_OUTTHERE_2026 = "https://drive.google.com/drive/folders/1RLAZiNBp1WoCO2QpgHlwAlsoSJBr74-w"
DRIVE_REPORTS = "https://drive.google.com/drive/folders/1v0WK53RI_EczHYHTpi7PC8zLrlbrDUrT"

# 3. เมนูด้านซ้าย
with st.sidebar:
    st.title("Plan B Media")
    st.caption("BATCH EMAIL AUTOMATION")
    st.markdown("---")
    step = st.radio("ขั้นตอนการทำงาน", ["01 ติ๊กเลือกลูกค้าหลายแบรนด์ & สื่อ", "02 ตรวจทานข้อความดราฟต์", "03 กดส่ง Auto Batch Mail"])

st.markdown("## 🏢 PLAN B MEDIA • BATCH EMAIL AUTOMATION")

# --- STEP 01: เลือก/แก้ไขแบรนด์ลูกค้าได้หลายคน ---
if "01" in step:
    st.markdown("### STEP 01 : เลือกลูกค้าหลายแบรนด์ และเลือกประเภทสื่อที่ต้องการส่ง")
    
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.subheader("👥 1. เลือก/แก้ไขรายชื่อลูกค้าผู้รับ")
        
        # ตัวเลือกในการเลือกหลายๆ แบรนด์
        all_company_names = [f"{c['company']} ({c['email']})" for c in CLIENT_DATABASE]
        
        select_all = st.checkbox("เลือกรายชื่อลูกค้าทั้งหมดในคลัง")
        
        if select_all:
            selected_raw = all_company_names
        else:
            selected_raw = st.multiselect(
                "ค้นหาและติ๊กเลือกแบรนด์ลูกค้า (เลือกพร้อมกันได้หลายแบรนด์):",
                options=all_company_names,
                default=[all_company_names[0], all_company_names[1]]
            )
            
        st.info(f"📌 จำนวนแบรนด์ที่เลือกส่งทั้งหมด: **{len(selected_raw)}** แบรนด์")
        
        st.markdown("---")
        st.caption("หรือต้องการพิมพ์เพิ่มแบรนด์ใหม่ที่ไม่มีในระบบ:")
        custom_company = st.text_input("ชื่อบริษัท/แบรนด์เพิ่มเติม (ถ้ามี):", placeholder="เช่น บริษัท ชาโออิชิ จำกัด")
        custom_email = st.text_input("อีเมลผู้รับเพิ่มเติม:", placeholder="client@example.com")
        
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

    if st.button("✨ ให้ AI สร้างร่างอีเมลสำหรับทุกแบรนด์อัตโนมัติ"):
        targets = []
        for raw in selected_raw:
            for item in CLIENT_DATABASE:
                if item["company"] in raw:
                    targets.append(item)
                    break
                    
        if custom_company and custom_email:
            targets.append({"company": custom_company, "email": custom_email, "contact": "ทีมการตลาด"})
            
        st.session_state["targets"] = targets
        st.session_state["email_category"] = email_category
        st.session_state["custom_drive"] = custom_drive
        
        # เลือกรูปภาพสื่อให้ตรงหมวด
        if "The 20" in email_category:
            st.session_state["img_url"] = MEDIA_IMAGES["The 20"]
        elif "Central Park" in email_category:
            st.session_state["img_url"] = MEDIA_IMAGES["Central Park"]
        elif "Report" in email_category:
            st.session_state["img_url"] = MEDIA_IMAGES["Report"]
        else:
            st.session_state["img_url"] = MEDIA_IMAGES["Outthere"]
            
        st.success(f"สร้างร่างอีเมลสำหรับลูกค้า {len(targets)} แบรนด์สำเร็จ! กดไปที่ '02 ตรวจทานข้อความดราฟต์'")

# --- STEP 02: ตรวจทานดราฟต์ ---
elif "02" in step:
    st.markdown("### STEP 02 : ตรวจทานดราฟต์ และพรีวิวรูปภาพสื่อ")
    if "targets" in st.session_state:
        category = st.session_state.get("email_category", "")
        custom_drive = st.session_state.get("custom_drive", "")
        targets = st.session_state.get("targets", [])
        
        col_edit, col_prev = st.columns([1.1, 1])
        
        with col_edit:
            st.subheader(f"✏️ ดราฟต์ข้อความที่จะส่งหาแบรนด์ลูกค้า ({len(targets)} ราย)")
            
            if "The 20" in category:
                subj_default = "[Plan B Media] OUTDOOR TRENDS: สื่อใหม่ล่าสุด 'The 20' สัมผัสประสบการณ์ใหม่กับ DOOH ที่ยาวที่สุดในโลก"
                body_default = """เรียน ทีมการตลาด {company_name},

ทาง Plan B ขอแนะนำสื่อ "The 20" สื่อดิจิทัลใหม่ล่าสุดจาก Plan B เพื่อเฉลิมฉลองครบรอบ 20 ปีของเรา โดยได้พลิกโฉมป้ายโฆษณา Serie Poles เดิม ให้กลายเป็นจอ LED กว่า 74 จอ เรียงรายตลอดเส้นทางยาวกว่า 2.5 กม. บนทางด่วนพิเศษเฉลิมมหานคร ใจกลาง Prime CBD มุ่งหน้าสู่ถนนวิภาวดี และถนนพระราม 4

จุดเด่นสื่อ The 20:
- ความคมชัดสูงขึ้น 2 เท่า สะกดทุกสายตา มองเห็นชัดเจนจากระยะไกล
- รองรับ Storytelling ทรงพลัง เล่นลูกเล่นต่อเนื่องตลอด 74 จอ
- มีทีม Sunbeam (Creative Agency) ดูแลการออกแบบและพัฒนาคอนเทนต์ให้อย่างครบวงจร

หากสนใจข้อมูลเพิ่มเติมหรือต้องการใบเสนอราคา สามารถตอบกลับอีเมลนี้ได้ทันทีครับ

ขอแสดงความนับถือ
ทีมงาน Plan B Media"""

            elif "Central Park" in category:
                subj_default = "[Plan B Media] เปิดตัวจอ Signature ใหม่ล่าสุด! Central Park – สื่อดิจิทัลพรีเมียมใจกลางกรุงเทพฯ"
                body_default = """เรียน ทีมการตลาด {company_name},

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
                subj_default = "[Report] รายงานภาพการขึ้นสื่อโฆษณา - แบรนด์ {company_name}"
                body_default = f"""เรียน ทีมการตลาด {{company_name}},

บริษัท แพลน บี มีเดีย จำกัด (มหาชน) ขอส่งมอบรายงานภาพถ่ายการขึ้นสื่อโฆษณา (Media Execution Report) เพื่อยืนยันการดำเนินงานสำหรับแคมเปญของท่าน

ท่านสามารถเข้าชมและดาวน์โหลดรูปภาพการขึ้นสื่อฉบับเต็มได้ที่ลิงก์นี้ครับ:
🔗 ลิงก์รายงานภาพการขึ้นสื่อ: {drive_link}

ขอแสดงความนับถือ
ทีมงาน Plan B Media"""

            else:
                drive_link = custom_drive.strip() if custom_drive.strip() else DRIVE_OUTTHERE_2026
                subj_default = "[Plan B Outthere 2026] อัปเดตเทรนด์และแพ็กเกจสื่อประจำเดือนสำหรับ {company_name}"
                body_default = f"""เรียน ทีมการตลาด {{company_name}},

ทาง Plan B ขอส่งมอบ Newsletter และ Case Study ล่าสุดประจำปี 2026 เพื่ออัปเดตอินไซต์การสื่อสาร OOH และแพ็กเกจสื่อ Outthere สำหรับแบรนด์ {{company_name}}

ท่านสามารถเข้าชมและดาวน์โหลดเอกสารอัปเดตประจำเดือนได้จากคลัง Google Drive นี้ครับ:
🔗 คลังเอกสาร Outthere 2026: {drive_link}

ขอแสดงความนับถือ
ทีมงาน Plan B Media"""

            editable_subj = st.text_input("แก้ไขหัวข้ออีเมล (Template Subject):", value=subj_default)
            editable_body = st.text_area("แก้ไขเนื้อหาอีเมล (Template Body):", value=body_default, height=280)
            
            st.session_state["final_subj"] = editable_subj
            st.session_state["final_body"] = editable_body
            st.info("แก้ไขข้อความเสร็จแล้ว กดไปที่เมนู '03 กดส่ง Auto Batch Mail' ด้านซ้ายได้เลยครับ")

        with col_prev:
            st.subheader("🖼️ พรีวิวรูปภาพสื่อโฆษณา")
            # แก้ไขใช้ use_container_width=True ป้องกัน TypeError Error
            st.image(st.session_state.get("img_url"), caption="รูปภาพสื่อโฆษณาประกอบในอีเมล", use_container_width=True)
            st.write(f"**ตัวอย่างการส่งหา:** `{targets[0]['company']}`")
            
    else:
        st.warning("กรุณาไปที่ STEP 01 เพื่อเลือกข้อมูลก่อนครับ")

# --- STEP 03: ส่ง Auto Batch Mail ---
elif "03" in step:
    st.markdown("### STEP 03 : จัดส่ง Auto Batch Mail ออกจากบัญชี @planbmedia.co.th")
    
    if "targets" in st.session_state:
        targets = st.session_state.get("targets", [])
        subj_tmpl = st.session_state.get("final_subj", "")
        body_tmpl = st.session_state.get("final_body", "")
        img_url = st.session_state.get("img_url", "")
        
        st.subheader(f"🚀 พร้อมจัดส่งหาลูกค้าทั้งหมด {len(targets)} แบรนด์")
        
        send_method = st.radio(
            "เลือกวิธีการส่งอีเมล:",
            [
                "1. Auto Batch Mail พร้อมรูปภาพสื่อ (ส่งตรงผ่าน Google App Password / SMTP)",
                "2. เปิดสเก็ตช์ร่างใน Gmail ทีละแบรนด์ (Gmail Webmail List)"
            ]
        )
        
        st.markdown("---")
        
        if "1." in send_method:
            st.markdown("#### 🔑 กรอกรหัสส่งอีเมลสำหรับส่ง Batch พร้อมรูปภาพ")
            col_a, col_b = st.columns(2)
            with col_a:
                sender_email = st.text_input("อีเมลผู้ส่ง:", value="wichayada.ph@planbmedia.co.th")
            with col_b:
                app_password = st.text_input("Google App Password (16 หลัก):", type="password")
                
            if st.button("🚀 กดคลิกเดียว! ส่ง Batch Mail หาแบรนด์ลูกค้าทั้งหมดทันที", type="primary"):
                if sender_email and app_password:
                    success_count = 0
                    progress_bar = st.progress(0)
                    
                    try:
                        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                        server.login(sender_email, app_password)
                        
                        for idx, client in enumerate(targets):
                            cur_subj = subj_tmpl.format(company_name=client['company'])
                            cur_body = body_tmpl.format(company_name=client['company'])
                            
                            html_content = f"""
                            <html>
                            <body style="font-family: Arial, sans-serif; color: #333333; line-height: 1.6;">
                                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
                                    <img src="{img_url}" style="width: 100%; height: auto; border-radius: 6px; margin-bottom: 20px;">
                                    <div style="white-space: pre-wrap;">{cur_body}</div>
                                </div>
                            </body>
                            </html>
                            """
                            
                            msg = MIMEMultipart('alternative')
                            msg['From'] = sender_email
                            msg['To'] = client['email']
                            msg['Subject'] = cur_subj
                            msg.attach(MIMEText(html_content, 'html', 'utf-8'))
                            
                            server.sendmail(sender_email, client['email'], msg.as_string())
                            success_count += 1
                            progress_bar.progress((idx + 1) / len(targets))
                            
                        server.quit()
                        st.balloons()
                        st.success(f"🎉 ส่งอีเมลสำเร็จครบถ้วนทั้ง {success_count} แบรนด์เรียบร้อยแล้วครับ!")
                        
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาดในการส่ง: {str(e)}")
                else:
                    st.warning("กรุณากรอกอีเมลและ App Password ให้ครบถ้วนก่อนครับ")
                    
        else:
            st.markdown("#### ✉️ รายการปุ่มเปิด Compose ใน Gmail สำหรับแต่ละแบรนด์:")
            for idx, client in enumerate(targets):
                cur_subj = subj_tmpl.format(company_name=client['company'])
                cur_body = body_tmpl.format(company_name=client['company'])
                
                enc_subj = urllib.parse.quote(cur_subj)
                enc_body = urllib.parse.quote(cur_body)
                g_url = f"https://mail.google.com/mail/?view=cm&fs=1&to={client['email']}&su={enc_subj}&body={enc_body}"
                
                col_x, col_y = st.columns([3, 1])
                with col_x:
                    st.write(f"**{idx+1}. {client['company']}** (`{client['email']}`)")
                with col_y:
                    st.markdown(f'<a href="{g_url}" target="_blank" class="gmail-link-btn">✉️ เปิด Gmail ของแบรนด์นี้</a>', unsafe_allow_html=True)
                st.markdown("---")
