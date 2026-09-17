import streamlit as st
import urllib.parse

# 1. ตั้งค่าหน้าเว็บสไตล์ Plan B New Media
st.set_page_config(page_title="Plan B - New Media Generator", page_icon="🚌", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d131a; }
    .stApp { background-color: #0b1118; color: #ffffff; }
    div[data-testid="stSidebar"] { background-color: #060a0f; }
    .stButton>button { background-color: #00c6ff; color: black; font-weight: bold; border-radius: 8px; width: 100%; }
    .action-btn {
        display: inline-block;
        background-color: #ea4335;
        color: #ffffff !important;
        font-weight: bold;
        padding: 12px 20px;
        text-align: center;
        border-radius: 8px;
        text-decoration: none;
        width: 100%;
        font-size: 16px;
        margin-top: 10px;
    }
    .action-btn:hover { background-color: #c5221f; }
    </style>
""", unsafe_allow_html=True)

# 2. เมนูด้านซ้าย (Sidebar Steps)
with st.sidebar:
    st.title("Plan B New Media")
    st.caption("AUTOMATED EMAIL GENERATOR")
    st.markdown("---")
    step = st.radio("ขั้นตอนการทำงาน", ["01 Brief & Client Detail", "02 Preview & Edit Email", "03 Send Email (@planbmedia.co.th)"])

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
    st.subheader("STEP 03 / 03 : ส่งอีเมลด้วยบัญชี @planbmedia.co.th")
    
    if "final_email" in st.session_state:
        recipient = st.session_state.get('recipient_email', '')
        final_text = st.session_state.get("final_email", "")
        
        st.write(f"**อีเมลผู้รับ:** `{recipient if recipient else 'ยังไม่ได้ระบุ'}`")
        
        # แสดงข้อความอีเมลพร้อมกล่อง Copy
        st.text_area("เนื้อหาที่จะนำไปส่ง:", value=final_text, height=220)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### วิธีที่ 1: เปิดหน้า Compose ใน Gmail")
            st.markdown(f'<a href="https://mail.google.com/mail/?view=cm&fs=1&to={recipient}" target="_blank" class="action-btn">✉️ เปิดหน้าเขียนอีเมลใน Gmail Plan B</a>', unsafe_allow_html=True)
            
        with col2:
            st.markdown("#### วิธีที่ 2: ใช้โปรแกรม Mail/Outlook ในเครื่อง")
            lines = final_text.split("\n", 1)
            subj = lines[0].replace("Subject: ", "") if lines else ""
            bod = lines[1] if len(lines) > 1 else final_text
            mailto_url = f"mailto:{recipient}?subject={urllib.parse.quote(subj)}&body={urllib.parse.quote(bod)}"
            st.markdown(f'<a href="{mailto_url}" target="_blank" class="action-btn" style="background-color: #00c6ff; color: #000 !important;">🚀 เปิดโปรแกรม Mail ในเครื่อง</a>', unsafe_allow_html=True)
            
    else:
        st.warning("กรุณาไปที่ STEP 01 เพื่อสร้างอีเมลก่อนครับ")
