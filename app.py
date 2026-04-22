import streamlit as st
import json
import os
import hashlib
import uuid
from datetime import datetime
import pandas as pd
import streamlit.components.v1 as components
import base64

# ─────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="ระบบแจกแจงงาน",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────
#  DATA LAYER
# ─────────────────────────────────────────
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

PATHS = {
    "users":       f"{DATA_DIR}/users.json",
    "employees":   f"{DATA_DIR}/employees.json",
    "tasks":       f"{DATA_DIR}/tasks.json",
    "assignments": f"{DATA_DIR}/assignments.json",
}

def _load(key):
    path = PATHS[key]
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(key, data):
    with open(PATHS[key], "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def new_id() -> str:
    return str(uuid.uuid4())[:8]

# ─────────────────────────────────────────
#  STYLING (CSS)
# ─────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Sarabun', sans-serif !important;
    }

    /* Background & Main Layout */
    .stApp {
        background-color: #f8f9fa;
    }

    /* Login Box */
    .login-outer {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 70vh;
    }
    .login-card {
        background: #ffffff;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        width: 100%;
        max-width: 400px;
        text-align: center;
        border-top: 5px solid #8B0000;
    }
    .login-card h2 {
        color: #8B0000;
        margin-bottom: 20px;
    }

    /* Fix: Inputs Text Visibility */
    .stTextInput > div > div > input {
        border-radius: 9px !important;
        border: 1.5px solid #FFCDD2 !important;
        background: #ffffff !important;
        color: #111111 !important; /* เปลี่ยนเป็นสีดำเข้ม */
        font-family: 'Sarabun', sans-serif !important;
    }
    
    /* ปรับให้ Placeholder และข้อความในช่องกรอกเห็นชัดขึ้น */
    input::placeholder {
        color: #666666 !important;
        opacity: 1;
    }

    /* Login Button */
    .stButton > button {
        width: 100%;
        border-radius: 9px !important;
        background-color: #8B0000 !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 10px !important;
        border: none !important;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background-color: #C62828 !important;
        box-shadow: 0 4px 12px rgba(139, 0, 0, 0.3);
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #eee;
    }
    .sidebar-title {
        color: #8B0000;
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 20px;
        text-align: center;
    }

    /* Data Cards */
    .data-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border-left: 5px solid #8B0000;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #8B0000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────
#  PAGES
# ─────────────────────────────────────────

def login_page():
    users = _load("users")
    # Initialize default admin if no users exist
    if not users:
        users.append({
            "username": "admin",
            "password": hash_pw("admin123"),
            "role": "admin",
            "display_name": "Administrator"
        })
        _save("users", users)

    st.markdown('<div class="login-outer">', unsafe_allow_html=True)
    with st.container():
        st.markdown(f"""
        <div class="login-card">
            <h2>📋 ระบบแจกแจงงาน</h2>
            <p style="color: #666; margin-bottom: 20px;">กรุณาลงชื่อเข้าใช้งาน</p>
        </div>
        """, unsafe_allow_html=True)
        
        user_input = st.text_input("ชื่อผู้ใช้", placeholder="Username")
        pass_input = st.text_input("รหัสผ่าน", type="password", placeholder="Password")
        
        if st.button("เข้าสู่ระบบ"):
            found = next((u for u in users if u["username"] == user_input and u["password"] == hash_pw(pass_input)), None)
            if found:
                st.session_state.logged_in = True
                st.session_state.current_user = found
                st.rerun()
            else:
                st.error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    st.markdown('</div>', unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.markdown(f'<div class="sidebar-title">📋 เมนูหลัก</div>', unsafe_allow_html=True)
        st.write(f"สวัสดี, **{st.session_state.current_user['display_name']}**")
        st.caption(f"สิทธิ์: {st.session_state.current_user['role']}")
        st.divider()
        
        if st.button("🏠 แดชบอร์ด", use_container_width=True):
            st.session_state.page = "dashboard"
        if st.button("👥 จัดการพนักงาน", use_container_width=True):
            st.session_state.page = "employees"
        if st.button("📝 จัดการรายการงาน", use_container_width=True):
            st.session_state.page = "tasks"
        if st.button("🔀 แจกแจงงาน", use_container_width=True):
            st.session_state.page = "assignments"
        if st.button("🖨️ พิมพ์รายการ (A4)", use_container_width=True):
            st.session_state.page = "print_page"
        
        st.divider()
        if st.button("⚙️ ตั้งค่าผู้ใช้", use_container_width=True):
            st.session_state.page = "settings"
        
        if st.button("🚪 ออกจากระบบ", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun()

def page_dashboard():
    st.title("🏠 แดชบอร์ด")
    emps = _load("employees")
    tasks = _load("tasks")
    assigns = _load("assignments")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("พนักงานทั้งหมด", len(emps))
    c2.metric("งานทั้งหมด", len(tasks))
    c3.metric("การมอบหมายงาน", len(assigns))
    
    st.subheader("📌 พนักงานและงานปัจจุบัน")
    if not assigns:
        st.info("ยังไม่มีการมอบหมายงานในขณะนี้")
    else:
        df = pd.DataFrame(assigns)
        st.table(df[["emp_name", "task_name", "timestamp"]])

def page_employees():
    st.title("👥 จัดการพนักงาน")
    emps = _load("employees")
    
    with st.expander("➕ เพิ่มพนักงานใหม่", expanded=True):
        name = st.text_input("ชื่อ-นามสกุล")
        dept = st.text_input("แผนก/ตำแหน่ง")
        if st.button("บันทึกพนักงาน"):
            if name:
                emps.append({"id": new_id(), "name": name, "dept": dept})
                _save("employees", emps)
                st.success("บันทึกสำเร็จ")
                st.rerun()

    st.subheader("รายชื่อพนักงาน")
    for i, e in enumerate(emps):
        cols = st.columns([3, 2, 1])
        cols[0].write(f"**{e['name']}**")
        cols[1].write(e['dept'])
        if cols[2].button("ลบ", key=f"del_emp_{e['id']}"):
            emps.pop(i)
            _save("employees", emps)
            st.rerun()

def page_tasks():
    st.title("📝 จัดการรายการงาน")
    tasks = _load("tasks")
    
    with st.expander("➕ เพิ่มงานใหม่", expanded=True):
        t_name = st.text_input("ชื่องาน / รายละเอียด")
        if st.button("บันทึกงาน"):
            if t_name:
                tasks.append({"id": new_id(), "name": t_name})
                _save("tasks", tasks)
                st.success("บันทึกสำเร็จ")
                st.rerun()

    st.subheader("รายการงาน")
    for i, t in enumerate(tasks):
        cols = st.columns([5, 1])
        cols[0].write(t['name'])
        if cols[1].button("ลบ", key=f"del_task_{t['id']}"):
            tasks.pop(i)
            _save("tasks", tasks)
            st.rerun()

def page_assignments():
    st.title("🔀 แจกแจงงาน")
    emps = _load("employees")
    tasks = _load("tasks")
    assigns = _load("assignments")
    
    if not emps or not tasks:
        st.warning("กรุณาเพิ่มพนักงานและรายการงานก่อน")
        return

    st.subheader("เลือกมอบหมายงาน")
    sel_emp = st.selectbox("เลือกพนักงาน", [e["name"] for e in emps])
    sel_task = st.selectbox("เลือกงาน", [t["name"] for t in tasks])
    
    if st.button("มอบหมายงาน"):
        assigns.append({
            "id": new_id(),
            "emp_name": sel_emp,
            "task_name": sel_task,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        _save("assignments", assigns)
        st.success(f"มอบหมายงานให้ {sel_emp} แล้ว")
        st.rerun()

    st.divider()
    if st.button("🗑️ ล้างการมอบหมายทั้งหมด", type="secondary"):
        _save("assignments", [])
        st.rerun()

def page_print():
    st.title("🖨️ เตรียมพิมพ์รายการ")
    assigns = _load("assignments")
    
    if not assigns:
        st.info("ไม่มีข้อมูลการมอบหมายงานให้พิมพ์")
        return

    # Calculate Font Size Auto
    count = len(assigns)
    fsize = "20px"
    if count > 15: fsize = "16px"
    if count > 25: fsize = "13px"

    html_content = f"""
    <div style="font-family: 'Sarabun', sans-serif; padding: 20px; background: white; color: black; border: 1px solid #ccc;">
        <h2 style="text-align: center; color: #8B0000;">รายการมอบหมายงานประจำวันที่ {datetime.now().strftime('%d/%m/%Y')}</h2>
        <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
            <thead>
                <tr style="background-color: #f2f2f2;">
                    <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">ชื่อพนักงาน</th>
                    <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">งานที่ได้รับมอบหมาย</th>
                </tr>
            </thead>
            <tbody>
    """
    for a in assigns:
        html_content += f"""
                <tr>
                    <td style="border: 1px solid #ddd; padding: 10px; font-size: {fsize};">{a['emp_name']}</td>
                    <td style="border: 1px solid #ddd; padding: 10px; font-size: {fsize};">{a['task_name']}</td>
                </tr>
        """
    html_content += "</tbody></table></div>"

    st.components.v1.html(html_content, height=600, scrolling=True)
    
    b64 = base64.b64encode(html_content.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="task_report.html" style="text-decoration: none;"><button style="padding: 10px 20px; background: #8B0000; color: white; border: none; border-radius: 5px; cursor: pointer;">📥 ดาวน์โหลดไฟล์สำหรับสั่งพิมพ์</button></a>'
    st.markdown(href, unsafe_allow_html=True)

def page_settings():
    st.title("⚙️ ตั้งค่าผู้ใช้")
    users = _load("users")
    curr = st.session_state.current_user
    
    with st.expander("🔑 เปลี่ยนรหัสผ่าน"):
        old_p = st.text_input("รหัสผ่านเดิม", type="password")
        new_p = st.text_input("รหัสผ่านใหม่", type="password")
        if st.button("อัปเดตรหัสผ่าน"):
            if hash_pw(old_p) == curr["password"]:
                for u in users:
                    if u["username"] == curr["username"]:
                        u["password"] = hash_pw(new_p)
                _save("users", users)
                st.success("เปลี่ยนรหัสผ่านสำเร็จ")
            else:
                st.error("รหัสผ่านเดิมไม่ถูกต้อง")

    if curr["role"] == "admin":
        st.divider()
        st.subheader("👨‍💼 จัดการบัญชีผู้ใช้ (Admin Only)")
        nu = st.text_input("ชื่อผู้ใช้ใหม่ (Username)")
        np = st.text_input("รหัสผ่านใหม่", type="password")
        nr = st.selectbox("สิทธิ์", ["user", "admin"])
        nd = st.text_input("ชื่อที่แสดง")
        if st.button("➕ เพิ่มผู้ใช้"):
            if nu and np:
                if any(x["username"] == nu for x in users):
                    st.error("ชื่อผู้ใช้นี้มีอยู่แล้ว")
                else:
                    users.append({"username": nu, "password": hash_pw(np),
                                   "role": nr, "display_name": nd or nu})
                    _save("users", users)
                    st.success(f"✅ เพิ่มผู้ใช้ {nu} แล้ว!")
                    st.rerun()

# ─────────────────────────────────────────
#  MAIN ROUTER
# ─────────────────────────────────────────
def main():
    inject_css()
    if "logged_in" not in st.session_state:
        st.session_state.logged_in    = False
        st.session_state.current_user = None
        st.session_state.page         = "dashboard"

    if not st.session_state.logged_in:
        login_page()
        return

    render_sidebar()

    PAGE_MAP = {
        "dashboard":  page_dashboard,
        "employees":  page_employees,
        "tasks":      page_tasks,
        "assignments": page_assignments,
        "print_page": page_print,
        "settings":   page_settings,
    }
    PAGE_MAP.get(st.session_state.get("page", "dashboard"))()

if __name__ == "__main__":
    main()
