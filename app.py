import streamlit as st
import smtplib
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

st.set_page_config(page_title="Plan B - Multi-Image Email Automation", page_icon="🏢", layout="wide")

CLIENT_DATABASE = [
    {"company": "บริษัท คอสเมคอน จำกัด", "email": "cosmecon.th@gmail.com"},
    {"company": "บริษัท บิวทีเอสเดอร์มา จำกัด (Mediheal)", "email": "beauteousderma@gmail.com"},
    {"company": "บริษัท บีดีเอ็มเอส เวลเนส คลินิก จำกัด", "email": "kunta.th@bdmswellness.com"},
    {"company": "บริษัท สตาร์ริชเชอร์ส กรุ๊ป จำกัด (MG)", "email": "warissara.benz@starrich.co.th"}
]

# ลิงก์ภาพสื่อ 2 ภาพคู่กันจาก Google Drive / Cloud
CENTRAL_PARK_IMG1 = "https://images.unsplash.com/photo-1519501025264-65ba15a82390?auto=format&fit=crop&w=600&q=80"
CENTRAL_PARK_IMG2 = "https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=600&q=80"

with st.sidebar:
    st.title("Plan B Media")
    st.caption("EXACT SALES NOTE ENGINE")
    step = st.radio("ขั้นตอน", ["01 เลือกลูกค้า & สื่อ", "02 พรีวิวข้อความและภาพคู่", "03 กดส่ง Email"])

st.markdown("## 🏢 PLAN B MEDIA • EMAIL AUTOMATION")

# --- STEP 01 ---
if "01" in step:
    st.subheader("STEP 01 : เลือกลูกค้า สื่อ และภาษา")
    col1, col2 = st.columns(2)
    with col1:
        all_clients = [f"{c['company']} ({c['email']})" for c in CLIENT_DATABASE]
        selected_raw = st.multiselect("เลือกลูกค้า (Multi-Select):", options=all_clients, default=[all_clients[0]])
        add_comp = st.text_input("ชื่อบริษัทเพิ่มเติม:")
        add_mail = st.text_input("อีเมลเพิ่มเติม:")
        
    with col2:
        media_choice = st.selectbox("เลือกสื่อ:", ["Central Park", "The 20"])
        lang_choice = st.radio("เลือกภาษา:", ["TH (ภาษาไทย)", "ENG (English)"], horizontal=True)

    if st.button("✨ ถอดแบบ Sales Note เป็น HTML"):
        targets = []
        for raw in selected_raw:
            for item in CLIENT_DATABASE:
                if item["company"] in raw:
                    targets.append(item)
                    break
        if add_comp and add_mail:
            targets.append({"company": add_comp, "email": add_mail})
            
        st.session_state["targets"] = targets
        st.session_state["media_choice"] = media_choice
        
        if "TH" in lang_choice:
            st.session_state["subject"] = "[Plan B Media] เปิดตัวจอ Signature ใหม่ล่าสุด! Central Park – สื่อดิจิทัลพรีเมียมใจกลางกรุงเทพฯ"
            st.session_state["body_html"] = """
            <p>สวัสดีค่ะ ทางเรามีความยินดีนำเสนอ <b>"Central Park"</b> จอดิจิทัลใหม่ล่าสุด บนโครงการมิกซ์ยูสระดับโลก Dusit Central Park<br>
            ซึ่งรวมโรงแรมดุสิตธานีโฉมใหม่ ศูนย์การค้า อาคารสำนักงานระดับลักชัวรี และสวนลอยฟ้าขนาด 7 ไร่ บนพื้นที่รวมกว่า 23 ไร่ บริเวณหัวมุมถนนสีลม – พระราม 4 เชื่อมต่อกับทั้ง BTS ศาลาแดง และ MRT สีลม</p>
            """
            st.session_state["bullets_html"] = """
            <p><b>จุดเด่นของสื่อ Central Park:</b></p>
            <ul style="padding-left: 20px;">
                <li style="margin-bottom: 6px;"><b>จอ LED Digital Curved ขนาดใหญ่กว่า 518 sq.m. บน facade ห้าง Central Park</b> ห้างลักชัวรี ที่รวบรวมแบรนด์ชั้นนำกว่า 230 แบรนด์ โดดเด่น สะดุดตา รองรับการมองเห็นจากหลายทิศทาง ทั้งพระราม 4, สีลม และสาทร</li>
                <li style="margin-bottom: 6px;">จอถูกออกแบบเพื่อรองรับงาน Creative Content โดยเฉพาะ 3D Visual</li>
                <li style="margin-bottom: 6px;">เข้าถึงผู้คนมากกว่า 8 ล้าน eyeballs/เดือน และ Reach กว่า 2.6 ล้านคน/เดือน</li>
                <li style="margin-bottom: 6px;">เข้าถึงกลุ่มเป้าหมายระดับบน ทั้งชาวต่างชาติ นักธุรกิจ และนักท่องเที่ยวคุณภาพ</li>
            </ul>
            <p>หากท่านสนใจข้อมูลเพิ่มเติม หรือต้องการสอบถามรายละเอียดเกี่ยวกับแพ็กเกจใดเพิ่มเติม สามารถติดต่อกลับได้ทางอีเมลนี้ ได้ตลอดเวลาค่ะ</p>
            """
        else:
            st.session_state["subject"] = "[Plan B Media] Introducing Central Park – Premium Digital Landmark in Bangkok"
            st.session_state["body_html"] = """
            <p>Greetings from Plan B.</p>
            <p>We are pleased to introduce <b>“Central Park”</b>, our latest premium digital screen located within Dusit Central Park — a world-class mixed-use development that combines the new Dusit Thani Hotel, a luxury shopping mall, Grade A office towers, and a 7-rai urban sky park, all situated on a 23-rai site at Silom and Rama IV intersection.</p>
            """
            st.session_state["bullets_html"] = """
            <p><b>Key Highlights of the Central Park Screen:</b></p>
            <ul style="padding-left: 20px;">
                <li style="margin-bottom: 6px;">A 518 sq.m curved LED digital screen on the facade of Central Park luxury mall</li>
                <li style="margin-bottom: 6px;">Designed specifically to support 3D creative content</li>
                <li style="margin-bottom: 6px;">Reaches over 8 million eyeballs per month and 2.6 million reach/month</li>
            </ul>
            <p>Should you be interested in more information, please feel free to reply to this email.</p>
            """
            
        st.success(f"เตรียมร่างสำหรับ {len(targets)} รายเรียบร้อย! กดไปที่ STEP 02")

# --- STEP 02 ---
elif "02" in step:
    st.subheader("STEP 02 : พรีวิวอีเมล (ภาพคู่เหมือนไฟล์ Word เป๊ะๆ)")
    if "targets" in st.session_state:
        targets = st.session_state.get("targets", [])
        subj = st.text_input("หัวข้ออีเมล:", value=st.session_state.get("subject"))
        st.session_state["subject"] = subj
        
        # จัดโครงสร้างตารางวางรูปคู่ 2 รูปเคียงข้างกันเหมือนในเอกสาร
        preview_html = f"""
        <div style="background-color: #ffffff; color: #333333; padding: 25px; border-radius: 8px; font-family: Arial, sans-serif; line-height: 1.6; max-width: 680px; border: 1px solid #dddddd;">
            <p>เรียน คุณ ทีมการตลาด ({targets[0]['company']})</p>
            {st.session_state.get('body_html')}
            
            <!-- ตารางแสดงรูปคู่ 2 รูปเคียงข้างกัน -->
            <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin: 20px 0;">
                <tr>
                    <td width="49%" align="center" style="padding-right: 2%;">
                        <img src="{CENTRAL_PARK_IMG1}" style="width: 100%; max-width: 300px; border-radius: 4px;">
                    </td>
                    <td width="49%" align="center" style="padding-left: 2%;">
                        <img src="{CENTRAL_PARK_IMG2}" style="width: 100%; max-width: 300px; border-radius: 4px;">
                    </td>
                </tr>
            </table>
            
            {st.session_state.get('bullets_html')}
            <p>ขอแสดงความนับถือ,<br><b>ทีมงาน Plan B Media</b></p>
        </div>
        """
        st.components.v1.html(preview_html, height=550, scrolling=True)

# --- STEP 03 ---
elif "03" in step:
    st.subheader("STEP 03 : จัดส่ง Auto Batch Mail (ฝังรูปภาพแก้ปัญหากากบาท [x])")
    if "targets" in st.session_state:
        targets = st.session_state.get("targets", [])
        subj = st.session_state.get("subject", "")
        
        col_a, col_b = st.columns(2)
        with col_a:
            sender = st.text_input("อีเมลผู้ส่ง:", value="wichayada.ph@planbmedia.co.th")
        with col_b:
            pwd = st.text_input("Google App Password:", value="szqfthyetnrmuulr", type="password")
            
        if st.button("🚀 กดส่ง HTML Email พร้อมรูปภาพคู่ทันที", type="primary"):
            try:
                # ดาวน์โหลดรูปภาพมาเตรียมฝังเข้าอีเมลแบบ CID
                img1_data = urllib.request.urlopen(CENTRAL_PARK_IMG1).read()
                img2_data = urllib.request.urlopen(CENTRAL_PARK_IMG2).read()
                
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.login(sender, pwd)
                
                for client in targets:
                    msg = MIMEMultipart('related')
                    msg['From'] = sender
                    msg['To'] = client['email']
                    msg['Subject'] = subj
                    
                    msg_alternative = MIMEMultipart('alternative')
                    msg.attach(msg_alternative)
                    
                    # โครงสร้าง HTML อ้างอิงรูปฝังภายใน cid:image1 และ cid:image2
                    email_html = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; color: #333333; line-height: 1.6; background-color: #ffffff; padding: 20px;">
                        <div style="max-width: 650px; margin: 0 auto;">
                            <p>เรียน คุณ ทีมการตลาด <b>{client['company']}</b></p>
                            {st.session_state.get('body_html')}
                            
                            <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin: 20px 0;">
                                <tr>
                                    <td width="49%" align="center"><img src="cid:image1" style="width:100%; border-radius:4px;"></td>
                                    <td width="2%"></td>
                                    <td width="49%" align="center"><img src="cid:image2" style="width:100%; border-radius:4px;"></td>
                                </tr>
                            </table>
                            
                            {st.session_state.get('bullets_html')}
                            <p>ขอแสดงความนับถือ,<br><b>ทีมงาน Plan B Media</b></p>
                        </div>
                    </body>
                    </html>
                    """
                    msg_alternative.attach(MIMEText(email_html, 'html', 'utf-8'))
                    
                    # ฝังไฟล์รูปภาพ
                    img1 = MIMEImage(img1_data)
                    img1.add_header('Content-ID', '<image1>')
                    msg.attach(img1)
                    
                    img2 = MIMEImage(img2_data)
                    img2.add_header('Content-ID', '<image2>')
                    msg.attach(img2)
                    
                    server.sendmail(sender, client['email'], msg.as_string())
                    
                server.quit()
                st.balloons()
                st.success(f"🎉 จัดส่งอีเมลพร้อมภาพคู่ตรงตามเอกสารเรียบร้อยแล้ว!")
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {str(e)}")
