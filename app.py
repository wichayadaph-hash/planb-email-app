import streamlit as st
import smtplib
import urllib.request
import io
from docx import Document
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

st.set_page_config(page_title="Plan B - Direct Drive Engine", page_icon="🏢", layout="wide")

# ฐานข้อมูลลูกค้าและอีเมลที่เชื่อมไว้ในระบบ (ดึงมาให้อัตโนมัติ ไม่ต้องกรอกเอง)
CLIENT_DATABASE = [
    {"company": "บริษัท คอสเมคอน จำกัด", "email": "cosmecon.th@gmail.com"},
    {"company": "บริษัท บิวทีเอสเดอร์มา จำกัด (Mediheal)", "email": "beauteousderma@gmail.com"},
    {"company": "บริษัท บีดีเอ็มเอส เวลเนส คลินิก จำกัด", "email": "kunta.th@bdmswellness.com"},
    {"company": "บริษัท สตาร์ริชเชอร์ส กรุ๊ป จำกัด (MG)", "email": "warissara.benz@starrich.co.th"}
]

# ลิงก์ตรงไฟล์ Word Sales Note ใน Google Drive ของ Plan B
DRIVE_DOCX_LINKS = {
    "Central Park (TH)": "https://docs.google.com/document/d/1UrsGlV-f3OKLugCLoJH6AzhIp0O01o9t/export?format=docx",
    "Central Park (ENG)": "https://docs.google.com/document/d/1UrsGlV-f3OKLugCLoJH6AzhIp0O01o9t/export?format=docx",
    "The 20 (TH)": "https://docs.google.com/document/d/1UrsGlV-f3OKLugCLoJH6AzhIp0O01o9t/export?format=docx"
}

def parse_docx_from_url(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    file_bytes = urllib.request.urlopen(req).read()
    doc = Document(io.BytesIO(file_bytes))
    
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip() != ""]
    
    images = []
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            img_part = rel.target_part
            images.append(img_part.blob)
            
    return paragraphs, images

with st.sidebar:
    st.title("Plan B Media")
    st.caption("DIRECT GOOGLE DRIVE ENGINE")
    step = st.radio("ขั้นตอน", ["01 เลือกสื่อและกลุ่มลูกค้า", "02 พรีวิวเนื้อหาจาก Drive", "03 ยืนยันการส่ง Email"])

st.markdown("## 🏢 PLAN B MEDIA • GOOGLE DRIVE AUTOMATION")

# --- STEP 01 ---
if "01" in step:
    st.subheader("STEP 01 : เลือกสื่อ Sales Note และลูกค้ารายเป้าหมาย (ดึงตรงจาก Drive)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("📂 **เลือกไฟล์ Sales Note จาก Google Drive:**")
        selected_media = st.selectbox("สื่อที่ต้องการเสนอขาย:", list(DRIVE_DOCX_LINKS.keys()))
        
    with col2:
        st.write("👥 **เลือกกลุ่มลูกค้าจากฐานข้อมูล (ไม่ต้องกรอกเอง):**")
        client_options = [f"{c['company']} ({c['email']})" for c in CLIENT_DATABASE]
        selected_clients = st.multiselect("รายชื่อลูกค้าเป้าหมาย:", options=client_options, default=client_options)

    if st.button("🚀 ดึงข้อความและรูปภาพตรงจาก Google Drive"):
        with st.spinner("กำลังเชื่อมต่อ Google Drive และดึงไฟล์ Word..."):
            docx_url = DRIVE_DOCX_LINKS[selected_media]
            paragraphs, images = parse_docx_from_url(docx_url)
            
            targets = [c for c in CLIENT_DATABASE if f"{c['company']} ({c['email']})" in selected_clients]
            
            st.session_state["targets"] = targets
            st.session_state["docx_paragraphs"] = paragraphs
            st.session_state["docx_images"] = images
            st.session_state["media_title"] = selected_media
            
            st.success(f"ดึงไฟล์ Word และรูปภาพจาก Google Drive สำเร็จ! เลือกไว้ {len(targets)} รายบริษัท ➔ ไปที่ STEP 02")

# --- STEP 02 ---
elif "02" in step:
    st.subheader("STEP 02 : พรีวิวข้อความและรูปภาพจริงจาก Google Drive")
    if "docx_paragraphs" in st.session_state:
        targets = st.session_state.get("targets", [])
        paragraphs = st.session_state.get("docx_paragraphs", [])
        images = st.session_state.get("docx_images", [])
        
        st.info(f"ดึงข้อมูลตรงจากไฟล์ Word ใน Drive เรียบร้อยแล้ว (จะระบุชื่อบริษัทลูกค้าให้อัตโนมัติ)")
        
        first_client = targets[0]
        body_content = f"<p style='margin-bottom: 15px;'><b>เรียน คุณ ทีมการตลาด {first_client['company']}</b></p>"
        for p in paragraphs:
            body_content += f"<p style='margin-bottom: 12px;'>{p}</p>"
            
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
    st.subheader("STEP 03 : ยืนยันการจัดส่ง Batch Email")
    if "docx_paragraphs" in st.session_state:
        targets = st.session_state.get("targets", [])
        paragraphs = st.session_state.get("docx_paragraphs", [])
        images = st.session_state.get("docx_images", [])
        
        col_a, col_b = st.columns(2)
        with col_a:
            sender = st.text_input("อีเมลผู้ส่ง:", value="wichayada.ph@planbmedia.co.th")
        with col_b:
            pwd = st.text_input("Google App Password:", value="szqfthyetnrmuulr", type="password")
            
        if st.button("🚀 ส่ง Email หาพร้อมกันทุกบริษัททันที", type="primary"):
            try:
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.login(sender, pwd)
                
                for client in targets:
                    msg = MIMEMultipart('related')
                    msg['From'] = sender
                    msg['To'] = client['email']
                    msg['Subject'] = f"[Plan B Media] เปิดตัวสื่อใหม่ล่าสุด {st.session_state.get('media_title')}"
                    
                    msg_alt = MIMEMultipart('alternative')
                    msg.attach(msg_alt)
                    
                    client_body = f"<p style='margin-bottom: 15px;'><b>เรียน คุณ ทีมการตลาด {client['company']}</b></p>"
                    for p in paragraphs:
                        client_body += f"<p style='margin-bottom: 12px;'>{p}</p>"
                        
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
                    
                    for idx, img_bytes in enumerate(images):
                        img_mime = MIMEImage(img_bytes)
                        img_mime.add_header('Content-ID', f'<word_img_{idx}>')
                        msg.attach(img_mime)
                        
                    server.sendmail(sender, client['email'], msg.as_string())
                    
                server.quit()
                st.balloons()
                st.success("🎉 ส่งอีเมลสำเร็จ! ดึงข้อมูลจาก Google Drive และ Database เรียบร้อย 100%")
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการส่ง: {str(e)}")
