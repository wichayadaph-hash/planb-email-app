import streamlit as st
import smtplib
import io
from docx import Document
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

st.set_page_config(page_title="Plan B - Direct Word Content Engine", page_icon="📄", layout="wide")

CLIENT_DATABASE = [
    {"company": "บริษัท คอสเมคอน จำกัด", "email": "cosmecon.th@gmail.com"},
    {"company": "บริษัท บิวทีเอสเดอร์มา จำกัด (Mediheal)", "email": "beauteousderma@gmail.com"},
    {"company": "บริษัท บีดีเอ็มเอส เวลเนส คลินิก จำกัด", "email": "kunta.th@bdmswellness.com"},
    {"company": "บริษัท สตาร์ริชเชอร์ส กรุ๊ป จำกัด (MG)", "email": "warissara.benz@starrich.co.th"}
]

# ฟังก์ชันดึงข้อความและรูปภาพตามลำดับเดิมในไฟล์ Word 100%
def parse_exact_docx(docx_file):
    doc = Document(docx_file)
    
    # ดึงข้อความตามลำดับบรรทัดเดิมใน Word
    text_paragraphs = [p.text for p in doc.paragraphs if p.text.strip() != ""]
    
    # ดึงรูปภาพทั้งหมดที่อยู่ในไฟล์ Word
    image_list = []
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            img_part = rel.target_part
            image_list.append(img_part.blob)
            
    return text_paragraphs, image_list

with st.sidebar:
    st.title("Plan B Media")
    st.caption("EXACT WORD CONTENT ENGINE")
    step = st.radio("ขั้นตอนการทำงาน", ["01 อัปโหลด Word & เลือกลูกค้า", "02 ตรวจสอบข้อความและรูปต้นฉบับ", "03 ยืนยันการส่ง Email"])

st.markdown("## 🏢 PLAN B MEDIA • DIRECT WORD AUTOMATION")

# --- STEP 01 ---
if "01" in step:
    st.subheader("STEP 01 : อัปโหลดไฟล์ Word Sales Note (ดึงเนื้อหาและรูปภาพตรง 100%)")
    
    col1, col2 = st.columns(2)
    with col1:
        uploaded_doc = st.file_uploader("เลือกไฟล์ Sales Note (.docx):", type=["docx"])
        all_clients = [f"{c['company']} ({c['email']})" for c in CLIENT_DATABASE]
        selected_raw = st.multiselect("เลือกลูกค้าที่จะส่งหา:", options=all_clients, default=[all_clients[0]])
        
    with col2:
        subject_line = st.text_input(
            "ระบุหัวข้ออีเมล (Subject):", 
            value="[Plan B Media] เปิดตัวจอ Signature ใหม่ล่าสุด! Central Park – สื่อดิจิทัลพรีเมียมใจกลางกรุงเทพฯ"
        )

    if st.button("📥 ดึงข้อมูลตรงจากไฟล์ Word"):
        if uploaded_doc is not None:
            paragraphs, images = parse_exact_docx(uploaded_doc)
            
            targets = []
            for raw in selected_raw:
                for item in CLIENT_DATABASE:
                    if item["company"] in raw:
                        targets.append(item)
                        break
                        
            st.session_state["targets"] = targets
            st.session_state["subject"] = subject_line
            st.session_state["docx_paragraphs"] = paragraphs
            st.session_state["docx_images"] = images
            
            st.success(f"ดึงข้อมูลสำเร็จ! พบข้อความ {len(paragraphs)} ย่อหน้า และรูปภาพ {len(images)} รูป (ดึงมาตรงตามไฟล์ Word 100%)")
        else:
            st.warning("กรุณาอัปโหลดไฟล์ Word (.docx) ก่อนทำขั้นตอนถัดไปครับ")

# --- STEP 02 ---
elif "02" in step:
    st.subheader("STEP 02 : ตรวจสอบตัวอย่างอีเมล (คงต้นฉบับเดิม + ใส่ชื่อลูกค้าให้อัตโนมัติ)")
    
    if "docx_paragraphs" in st.session_state:
        targets = st.session_state.get("targets", [])
        paragraphs = st.session_state.get("docx_paragraphs", [])
        images = st.session_state.get("docx_images", [])
        
        first_client = targets[0]
        
        st.write(f"**ตัวอย่างส่งถึง:** คุณ ทีมการตลาด ({first_client['company']})")
        st.markdown("---")
        
        # สร้างเนื้อหา HTML โดยไม่แก้ข้อความเดิม
        body_content = f"<p style='margin-bottom: 15px;'><b>เรียน คุณ ทีมการตลาด {first_client['company']}</b></p>"
        
        # ใส่ข้อความต้นฉบับทีละย่อหน้า
        for p in paragraphs:
            body_content += f"<p style='margin-bottom: 12px;'>{p}</p>"
            
        # สร้างตารางวางรูปภาพแบบคู่ตามต้นฉบับ Word
        if len(images) >= 2:
            img_table = """
            <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin: 20px 0;">
                <tr>
                    <td width="49%" align="center"><img src="cid:word_img_0" style="width:100%; max-width:320px; border-radius:4px;"></td>
                    <td width="2%"></td>
                    <td width="49%" align="center"><img src="cid:word_img_1" style="width:100%; max-width:320px; border-radius:4px;"></td>
                </tr>
            </table>
            """
        elif len(images) == 1:
            img_table = '<div style="text-align:center; margin: 20px 0;"><img src="cid:word_img_0" style="max-width:100%; border-radius:4px;"></div>'
        else:
            img_table = ""

        preview_html = f"""
        <div style="background-color: #ffffff; color: #333333; padding: 25px; border-radius: 8px; font-family: Arial, sans-serif; line-height: 1.6; border: 1px solid #ddd; max-width: 680px;">
            {body_content}
            {img_table}
        </div>
        """
        
        st.components.v1.html(preview_html, height=550, scrolling=True)

# --- STEP 03 ---
elif "03" in step:
    st.subheader("STEP 03 : ยืนยันและจัดส่งอีเมล")
    
    if "docx_paragraphs" in st.session_state:
        targets = st.session_state.get("targets", [])
        subj = st.session_state.get("subject", "")
        paragraphs = st.session_state.get("docx_paragraphs", [])
        images = st.session_state.get("docx_images", [])
        
        col_a, col_b = st.columns(2)
        with col_a:
            sender = st.text_input("อีเมลผู้ส่ง:", value="wichayada.ph@planbmedia.co.th")
        with col_b:
            pwd = st.text_input("Google App Password:", value="szqfthyetnrmuulr", type="password")
            
        if st.button("🚀 ยืนยันการส่ง Email ต้นฉบับจาก Word ทันที", type="primary"):
            try:
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.login(sender, pwd)
                
                for client in targets:
                    msg = MIMEMultipart('related')
                    msg['From'] = sender
                    msg['To'] = client['email']
                    msg['Subject'] = subj
                    
                    msg_alt = MIMEMultipart('alternative')
                    msg.attach(msg_alt)
                    
                    # ประกอบข้อความ 100% จาก Word + แทรกชื่อบริษัทลูกค้า
                    client_body = f"<p style='margin-bottom: 15px;'><b>เรียน คุณ ทีมการตลาด {client['company']}</b></p>"
                    for p in paragraphs:
                        client_body += f"<p style='margin-bottom: 12px;'>{p}</p>"
                        
                    # ตารางวางรูปภาพคู่
                    if len(images) >= 2:
                        img_html = """
                        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin: 20px 0;">
                            <tr>
                                <td width="49%" align="center"><img src="cid:word_img_0" style="width:100%; border-radius:4px;"></td>
                                <td width="2%"></td>
                                <td width="49%" align="center"><img src="cid:word_img_1" style="width:100%; border-radius:4px;"></td>
                            </tr>
                        </table>
                        """
                    elif len(images) == 1:
                        img_html = '<div style="text-align:center; margin: 20px 0;"><img src="cid:word_img_0" style="max-width:100%; border-radius:4px;"></div>'
                    else:
                        img_html = ""

                    final_email_html = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; color: #333333; line-height: 1.6; padding: 20px; background-color: #ffffff;">
                        <div style="max-width: 650px; margin: 0 auto;">
                            {client_body}
                            {img_html}
                        </div>
                    </body>
                    </html>
                    """
                    
                    msg_alt.attach(MIMEText(final_email_html, 'html', 'utf-8'))
                    
                    # ฝังไฟล์รูปภาพจาก Word ลงในอีเมลโดยตรง (กันกากบาท)
                    for idx, img_bytes in enumerate(images):
                        img_mime = MIMEImage(img_bytes)
                        img_mime.add_header('Content-ID', f'<word_img_{idx}>')
                        msg.attach(img_mime)
                        
                    server.sendmail(sender, client['email'], msg.as_string())
                    
                server.quit()
                st.balloons()
                st.success("🎉 ส่งอีเมลตรงตามไฟล์ Word ต้นฉบับสำเร็จเรียบร้อยครับ!")
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการส่ง: {str(e)}")
