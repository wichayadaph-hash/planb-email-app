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
        display: block;
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
            
            # แยก Subject และ Body ให้ชัดเจน
            st.session_state["email_subject"] = f"[Update] ยกระดับการมองเห็นให้แบรนด์ {client_name} ด้วยสื่อ Bus Half Wrap โฉมใหม่ (พื้นที่ใหญ่ขึ้น ในราคาเดิม)"
            
            st.session_state["email_body"] = f"""เรียน ทีมการตลาด {client_name}

บริษัท แพลน บี มีเดีย จำกัด (มหาชน) ขอขอบพระคุณที่ท่านให้ความไว้วางใจเลือกใช้บริการสื่อโฆษณาของเรามาโดยตลอด

เพื่อเพิ่มประสิทธิภาพการสื่อสารของแบรนด์ {client_name} ทาง Plan B ขอแจ้งปรับโฉมสื่อโฆษณาบนตัวรถโดยสารประจำทาง รูปแบบ Half Wrap โดยเพิ่มขนาดพื้นที่สื่อให้ใหญ่และสะดุดตายิ่งขึ้น ภายใต้อัตราค่าโฆษณาและค่าผลิตเท่าเดิม โดยเริ่มตั้งแต่วันที่ 1 กันยายน 2569 เป็นต้นไป

เงื่อนไขสำหรับสถานะของคุณ ({client_status}):
ทางเรายินดีนำเสนอรูปแบบใหม่นี้เพื่อช่วยสร้าง Impact สูงสุดให้กับแคมเปญของท่าน

หากต้องการข้อมูลเพิ่มเติมหรือ Media Spec ขนาดใหม่ สามารถติดต่อ AE ผู้ดูแลได้ทันทีครับ

ขอแสดงความนับถือ
ทีมงาน Plan B Media"""

            st.success("สร้างร่างอีเมลสำเร็จ! กดไปที่เมนู '02 Preview & Edit Email' ด้านซ้ายเพื่อดู/แก้ไข")
        else:
            st.warning("กรุณากรอกชื่อลูกค้าก่อนครับ")

# --- STEP 02: ตรวจแก้ไข ---
elif "02" in step:
    st.subheader("STEP 02 / 03 : ตรวจสอบและแก้ไขอีเมล")
    if "email_body" in st.session_state:
        subj = st.text_input("แก้ไขหัวข้ออีเมล (Subject):", value=st.session_state.get("email_subject", ""))
        body = st.text_area("แก้ไขเนื้อหาอีเมล (Body):", value=st.session_state.get("email_body", ""), height=280)
        
        st.session_state["email_subject"] = subj
        st.session_state["email_body"] = body
        st.info("แก้ไขเสร็จแล้ว กดไปที่เมนู '03 Send Email' ด้านซ้าย")
    else:
        st.warning("กรุณาไปที่ STEP 01 เพื่อสร้างอีเมลก่อนครับ")

# --- STEP 03: ส่งอีเมล ---
elif "03" in step:
    st.subheader("STEP 03 / 03 : ส่งอีเมลด้วยบัญชี @planbmedia.co.th")
    
    if "email_body" in st.session_state:
        recipient = st.session_state.get('recipient_email', '')
        subj = st.session_state.get('email_subject', '')
        body = st.session_state.get('email_body', '')
        
        st.write(f"**อีเมลผู้รับ:** `{recipient if recipient else 'ยังไม่ได้ระบุ'}`")
        st.text_input("หัวข้ออีเมล:", value=subj, disabled=True)
        st.text_area("เนื้อหาอีเมล:", value=body, height=200, disabled=True)
        
        # Encode URL ให้ปลอดภัย
        encoded_subj = urllib.parse.quote(subj)
        encoded_body = urllib.parse.quote(body)
        
        # ลิงก์ Gmail แบบดึงทั้ง Subject และ Body เข้าไปอัตโนมัติ
        gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&to={recipient}&su={encoded_subj}&body={encoded_body}"
        
        st.markdown("---")
        st.markdown(f'<a href="{gmail_url}" target="_blank" class="action-btn">✉️ กดตรงนี้เพื่อเปิดร่างอีเมลใน Gmail (พร้อมเนื้อหา)</a>', unsafe_allow_html=True)
            
    else:
        st.warning("กรุณาไปที่ STEP 01 เพื่อสร้างอีเมลก่อนครับ")
