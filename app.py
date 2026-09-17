import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. ตั้งค่าหน้าเว็บสไตล์ Plan B
st.set_page_config(page_title="Plan B - New Media Email Generator", page_icon="🚌", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d131a; }
    .stApp { background-color: #0b1118; color: #ffffff; }
    div[data-testid="stSidebar"] { background-color: #060a0f; }
    .stButton>button { background-color: #00c6ff; color: black; font-weight: bold; border-radius: 8px; width: 100%; }
    </style>
""", unsafe_allow_html=True)

# 2. เมนูด้านซ้าย (Sidebar Steps)
with st.sidebar:
    st.title("Plan B New Media")
    st.caption("AUTOMATED EMAIL GENERATOR")
    st.markdown("---")
    step = st.radio("ขั้นตอนการทำงาน", ["01 Brief & Client Detail", "02 Preview & Edit Email", "03 Send Email"])

st.markdown("### PLAN B MEDIA • NEW MEDIA AUTOMATION")

# --- STEP 01: กรอกข้อมูล ---
if "01" in step:
    st.subheader("STEP 01 / 03 : กรอกข้อมูลลูกค้าและสื่อ Bus Wrap")
    
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("ชื่อบริษัท / แบรนด์ลูกค้า", placeholder="เช่น บริษัท ชาโออิชิ จำกัด")
        recipient_email = st.text_input("อีเมลลูกค้าผู้รับ", placeholder="client@example.com")
    with col2:
        client_status = st.selectbox(
            "สถานะลูกค้าตามประกาศ",
            [
                "1. ลูกค้าใหม่ / ยังไม่ได้ยืนยันซื้อสื่อ",
                "2. ยืนยันซื้อสื่อแล้ว (ยังไม่ได้เริ่มผลิต)",
                "3. อยู่ระหว่างขึ้นสื่อเดิม (ต้องการเปลี่ยนเป็นรูปแบบใหม่)"
            ]
        )

    if st.button("✨ ให้ AI สร้างเนื้อหาอีเมล"):
        if client_name:
            st.session_state["client_name"] = client_name
            st.session_state["recipient_email"] = recipient_email
            
            # ร่างข้อความตามประกาศจริงของ Plan B
            template_text = f"""Subject: [Update] ยกระดับการมองเห็นให้แบรนด์ {client_name} ด้วยสื่อ Bus Half Wrap โฉมใหม่ (พื้นที่ใหญ่ขึ้น ในราคาเดิม)

เรียน ทีมการตลาด {client_name}

บริษัท แพลน บี มีเดีย จำกัด (มหาชน) ขอขอบพระคุณที่ท่านให้ความไว้วางใจเลือกใช้บริการสื่อโฆษณาของเรามาโดยตลอด

เพื่อเพิ่มประสิทธิภาพการสื่อสารของแบรนด์ {client_name} ทาง Plan B ขอแจ้งปรับโฉมสื่อโฆษณาบนตัวรถโดยสารประจำทาง รูปแบบ Half Wrap โดยเพิ่มขนาดพื้นที่สื่อให้ใหญ่และสะดุดตายิ่งขึ้น ภายใต้อัตราค่าโฆษณาและค่าผลิตเท่าเดิม โดยเริ่มตั้งแต่วันที่ 1 กันยายน 2569 เป็นต้นไป

เงื่อนไขสำหรับสถานะของคุณ ({client_status}):
ทางเรายินดีนำเสนอรูปแบบใหม่นี้เพื่อช่วยสร้าง Impact สูงสุดให้กับแคมเปญของท่าน

หากต้องการข้อมูลเพิ่มเติมหรือ Media Spec ขนาดใหม่ สามารถติดต่อ AE ผู้ดูแลได้ทันทีครับ

ขอแสดงความนับถือ
ทีมงาน Plan B Media
"""
            st.session_state["generated_email"] = template_text
            st.success("สร้างร่างอีเมลสำเร็จ! กดไปที่เมนู '02 Preview & Edit Email' ด้านซ้ายเพื่อดู/แก้ไข")
        else:
            st.warning("กรุณากรอกชื่อลูกค้าก่อนครับ")

# --- STEP 02: ตรวจแก้ไข ---
elif "02" in step:
    st.subheader("STEP 02 / 03 : ตรวจสอบและแก้ไขอีเมล")
    if "generated_email" in st.session_state:
        edited = st.text_area("ปรับแก้ไขข้อความได้ตามต้องการ:", value=st.session_state["generated_email"], height=320)
        st.session_state["final_email"] = edited
        st.info("แก้ไขเสร็จแล้ว กดไปที่เมนู '03 Send Email' ด้านซ้าย")
    else:
        st.warning("กรุณาไปที่ STEP 01 เพื่อสร้างอีเมลก่อนครับ")

# --- STEP 03: ส่งอีเมล ---
elif "03" in step:
    st.subheader("STEP 03 / 03 : ส่งอีเมลหาลูกค้า")
    
    if "final_email" in st.session_state:
        st.write(f"**ผู้รับ:** {st.session_state.get('recipient_email', 'ยังไม่ได้ระบุ')}")
        st.text_area("ตัวอย่างข้อความที่จะส่ง:", value=st.session_state.get("final_email"), height=200, disabled=True)
        
        st.markdown("---")
        sender_email = st.text_input("Gmail ผู้ส่ง", placeholder="your_email@gmail.com")
        app_password = st.text_input("Gmail App Password (16 หลัก)", type="password")
        
        if st.button("🚀 ส่งอีเมลหาลูกค้าทันที"):
            if sender_email and app_password and st.session_state.get("recipient_email"):
                try:
                    lines = st.session_state["final_email"].split("\n", 1)
                    subject = lines[0].replace("Subject: ", "")
                    body = lines[1] if len(lines) > 1 else ""

                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = st.session_state["recipient_email"]
                    msg['Subject'] = subject
                    msg.attach(MIMEText(body, 'plain'))

                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(sender_email, app_password)
                    server.send_message(msg)
                    server.quit()

                    st.balloons()
                    st.success("ส่งอีเมลสำเร็จเรียบร้อยแล้ว!")
                except Exception as e:
                    st.error(f"การส่งล้มเหลว: {e}")
            else:
                st.warning("กรุณากรอกข้อมูลให้ครบถ้วน")
