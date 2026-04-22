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

def now_str() -> str:
    return datetime.now().strftime("%d/%m/%Y %H:%M")

# Seed default admin on first run
if not os.path.exists(PATHS["users"]):
    _save("users", [{
        "username": "admin",
        "password": hash_pw("admin123"),
        "role": "admin",
        "display_name": "ผู้ดูแลระบบ",
    }])
for k in ("employees", "tasks", "assignments"):
    if not os.path.exists(PATHS[k]):
        _save(k, [])

# ─────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────
def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Sarabun', 'TH Sarabun New', sans-serif !important; }

/* App background */
.stApp { background: #FDF3F3; }

/* Sidebar */
section[data-testid="stSidebar"] > div:first-child {
    background: linear-gradient(180deg, #8B0000 0%, #B71C1C 40%, #C62828 100%);
    border-right: none;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div { color: #fff !important; }

/* All buttons → red theme */
.stButton > button {
    background: #C62828 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    padding: 9px 18px !important;
    transition: all 0.18s ease !important;
    box-shadow: 0 2px 6px rgba(198,40,40,.25) !important;
}
.stButton > button:hover {
    background: #8B0000 !important;
    box-shadow: 0 4px 14px rgba(139,0,0,.35) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* Sidebar buttons – ghost style */
section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.12) !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    text-align: left !important;
    justify-content: flex-start !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.25) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* Page header */
.page-header {
    background: linear-gradient(135deg, #8B0000, #C62828);
    color: #fff;
    padding: 22px 30px;
    border-radius: 16px;
    margin-bottom: 22px;
    box-shadow: 0 4px 18px rgba(139,0,0,.28);
}
.page-header h1 { color: #fff; margin: 0; font-size: 1.65rem; font-weight: 800; }
.page-header p  { color: rgba(255,255,255,.80); margin: 4px 0 0; font-size: .92rem; }

/* Metric cards */
.metric-card {
    background: #fff;
    border-radius: 14px;
    padding: 22px;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,.07);
    border-bottom: 4px solid #C62828;
}
.metric-num   { font-size: 2.4rem; font-weight: 800; color: #8B0000; line-height: 1; }
.metric-label { font-size: .88rem; color: #777; margin-top: 6px; }

/* Info / assignment row card */
.info-card {
    background: #fff;
    border-radius: 11px;
    padding: 16px 20px;
    box-shadow: 0 1px 8px rgba(0,0,0,.07);
    border-left: 4px solid #C62828;
    margin-bottom: 12px;
}

/* Inputs - FIX: เพิ่มสีตัวอักษรให้ชัดเจน */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    border-radius: 9px !important;
    border: 1.5px solid #FFCDD2 !important;
    background: #fff !important;
    color: #222 !important; /* ปรับสีตัวอักษรให้เข้มขึ้น */
    font-family: 'Sarabun', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #C62828 !important;
    box-shadow: 0 0 0 3px rgba(198,40,40,.12) !important;
}
.stSelectbox > div > div > div {
    border-radius: 9px !important;
    border: 1.5px solid #FFCDD2 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0 !important;
    background: #FFEBEE !important;
    color: #C62828 !important;
    font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
    background: #C62828 !important;
    color: #fff !important;
}

/* Dividers */
hr { border-color: #FFCDD2 !important; margin: 14px 0 !important; }

/* Login box - FIX: ปรับสีหัวข้อให้ชัดเจน */
.login-outer {
    max-width: 440px;
    margin: 40px auto 0;
    background: #fff;
    border-radius: 20px;
    padding: 42px 40px 36px;
    box-shadow: 0 8px 32px rgba(139,0,0,.13);
}
.login-outer h4 {
    color: #8B0000 !important; /* ปรับสี "🔐 เข้าสู่ระบบ" ให้เป็นสีแดงเข้ม */
    font-weight: 800 !important;
}

/* DataFrames */
.stDataFrame { border-radius: 10px !important; overflow: hidden !important; }

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  LOGIN PAGE
# ─────────────────────────────────────────
def login_page():
    inject_css()
    st.markdown("""
<div style="text-align:center; padding:48px 0 0;">
  <div style="font-size:3.2rem;">📋</div>
  <h1 style="color:#8B0000; font-size:1.9rem; font-weight:800; margin:10px 0 4px;">ระบบแจกแจงงาน</h1>
  <p style="color:#999; font-size:.92rem; margin:0;">Task Assignment System</p>
</div>
""", unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        st.markdown('<div class="login-outer">', unsafe_allow_html=True)
        st.markdown("#### 🔐 เข้าสู่ระบบ")
        username = st.text_input("ชื่อผู้ใช้", placeholder="กรอกชื่อผู้ใช้", key="login_user")
        password = st.text_input("รหัสผ่าน", type="password", placeholder="กรอกรหัสผ่าน", key="login_pw")
        st.markdown("")

        if st.button("เข้าสู่ระบบ →", use_container_width=True):
            users = _load("users")
            user = next((u for u in users if u["username"] == username and u["password"] == hash_pw(password)), None)
            if user:
                st.session_state.logged_in    = True
                st.session_state.current_user = user
                st.session_state.page         = "dashboard"
                st.rerun()
            else:
                st.error("❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

        # FIX: นำส่วนแสดงรหัสผ่านเริ่มต้นออกเพื่อความปลอดภัย
        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────
#  SIDEBAR NAV
# ─────────────────────────────────────────
def render_sidebar():
    user = st.session_state.current_user
    with st.sidebar:
        st.markdown(f"""
<div style="text-align:center; padding:20px 0 12px;">
  <div style="font-size:2.2rem;">📋</div>
  <div style="font-size:1.05rem; font-weight:700; margin:6px 0 2px;">ระบบแจกแจงงาน</div>
  <div style="font-size:.75rem; opacity:.75;">Task Assignment System</div>
</div>
<hr style="border-color:rgba(255,255,255,.25) !important; margin:0 0 12px !important;"/>
<div style="background:rgba(255,255,255,.15); border-radius:11px; padding:12px 14px; margin-bottom:14px; text-align:center;">
  <div style="font-size:1.35rem;">👤</div>
  <div style="font-weight:700; font-size:.9rem;">{user.get('display_name', user['username'])}</div>
  <div style="font-size:.72rem; opacity:.75;">{user.get('role','user')}</div>
</div>
""", unsafe_allow_html=True)

        pages = {
            "🏠  หน้าหลัก":          "dashboard",
            "👥  จัดการพนักงาน":      "employees",
            "📝  จัดการงาน":          "tasks",
            "🔀  แจกแจงงาน":          "assignments",
            "🖨️  พิมพ์รายการ A4":    "print_page",
            "⚙️  ตั้งค่าผู้ใช้":      "settings",
        }
        for label, key in pages.items():
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.page = key
                st.rerun()

        st.markdown("<hr style='border-color:rgba(255,255,255,.25) !important; margin:10px 0 !important;'/>", unsafe_allow_html=True)
        if st.button("🚪  ออกจากระบบ", use_container_width=True):
            st.session_state.logged_in    = False
            st.session_state.current_user = None
            st.rerun()

# ─────────────────────────────────────────
#  PAGE: DASHBOARD
# ─────────────────────────────────────────
def page_dashboard():
    employees   = _load("employees")
    tasks       = _load("tasks")
    assignments = _load("assignments")

    st.markdown("""<div class="page-header">
  <h1>🏠 หน้าหลัก</h1>
  <p>ภาพรวมระบบแจกแจงงาน</p>
</div>""", unsafe_allow_html=True)

    assigned_emp_ids = {a["employee_id"] for a in assignments if a.get("task_id")}
    unassigned_count = len(employees) - len(assigned_emp_ids)

    c1, c2, c3, c4 = st.columns(4)
    for col, num, label, color in [
        (c1, len(employees),       "พนักงานทั้งหมด",   "#8B0000"),
        (c2, len(tasks),           "งานทั้งหมด",       "#8B0000"),
        (c3, len(assigned_emp_ids),"มอบหมายแล้ว",      "#8B0000"),
        (c4, max(0,unassigned_count),"ยังไม่ได้มอบหมาย","#E65100"),
    ]:
        col.markdown(f"""<div class="metric-card">
  <div class="metric-num" style="color:{color};">{num}</div>
  <div class="metric-label">{label}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if assignments:
        emp_dict  = {e["id"]: f"{e['name']} {e['surname']}" for e in employees}
        task_dict = {t["id"]: t["name"] for t in tasks}
        rows = [{
            "ลำดับ":     i + 1,
            "พนักงาน":  emp_dict.get(a["employee_id"], "—"),
            "งาน":      task_dict.get(a.get("task_id",""), "ยังไม่มีงาน"),
            "วันที่":   a.get("assigned_date", "—"),
        } for i, a in enumerate(reversed(assignments[-20:]))]

        st.markdown("### 📊 รายการแจกแจงล่าสุด")
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("ยังไม่มีการแจกแจงงาน → ไปที่เมนู **🔀 แจกแจงงาน** เพื่อเริ่มต้น")

# ─────────────────────────────────────────
#  PAGE: EMPLOYEES
# ─────────────────────────────────────────
def page_employees():
    st.markdown("""<div class="page-header">
  <h1>👥 จัดการพนักงาน</h1>
  <p>เพิ่ม แก้ไข และลบข้อมูลพนักงาน</p>
</div>""", unsafe_allow_html=True)

    employees = _load("employees")
    tab_list, tab_add = st.tabs(["📋 รายชื่อพนักงาน", "➕ เพิ่มพนักงาน"])

    # ── TAB LIST ──
    with tab_list:
        search = st.text_input("🔍 ค้นหาพนักงาน", placeholder="พิมพ์ชื่อ / นามสกุล / ตำแหน่ง...")
        filtered = [e for e in employees if search.lower() in
                    f"{e['name']} {e['surname']} {e.get('position','')}".lower()] if search else employees

        st.markdown(f"**พบ {len(filtered)} / {len(employees)} คน**")
        st.markdown("<hr/>", unsafe_allow_html=True)

        if not filtered:
            st.info("ไม่พบพนักงาน")
        else:
            # Header row
            hc = st.columns([0.4, 2.2, 2.2, 2.6, 1.2])
            for h, t in zip(hc, ["#", "ชื่อ", "นามสกุล", "ตำแหน่ง", "จัดการ"]):
                h.markdown(f"**{t}**")
            st.markdown("<hr style='margin:4px 0;'/>", unsafe_allow_html=True)

            for i, emp in enumerate(filtered):
                c_no, c_name, c_sur, c_pos, c_act = st.columns([0.4, 2.2, 2.2, 2.6, 1.2])
                c_no.markdown(f"<div style='padding:8px 0; color:#aaa;'>{i+1}</div>", unsafe_allow_html=True)
                new_name = c_name.text_input("ชื่อ", value=emp["name"],                 key=f"en_{emp['id']}", label_visibility="collapsed")
                new_sur  = c_sur.text_input("นามสกุล", value=emp["surname"],             key=f"es_{emp['id']}", label_visibility="collapsed")
                new_pos  = c_pos.text_input("ตำแหน่ง", value=emp.get("position",""),    key=f"ep_{emp['id']}", label_visibility="collapsed")

                with c_act:
                    col_s, col_d = st.columns(2)
                    if col_s.button("💾", key=f"esave_{emp['id']}", help="บันทึก"):
                        for e in employees:
                            if e["id"] == emp["id"]:
                                e["name"]     = new_name.strip()
                                e["surname"]  = new_sur.strip()
                                e["position"] = new_pos.strip()
                        _save("employees", employees)
                        st.success("บันทึกแล้ว!")
                        st.rerun()
                    if col_d.button("🗑️", key=f"edel_{emp['id']}", help="ลบ"):
                        employees   = [e for e in employees if e["id"] != emp["id"]]
                        assignments = [a for a in _load("assignments") if a["employee_id"] != emp["id"]]
                        _save("employees", employees)
                        _save("assignments", assignments)
                        st.success("ลบเรียบร้อย!")
                        st.rerun()
                st.markdown("<hr style='margin:3px 0; border-color:#FFCDD2 !important;'/>", unsafe_allow_html=True)

    # ── TAB ADD ──
    with tab_add:
        st.markdown("#### เพิ่มพนักงานรายคน")
        c1, c2, c3 = st.columns(3)
        nm  = c1.text_input("ชื่อ *",        placeholder="ชื่อ")
        sur = c2.text_input("นามสกุล *",     placeholder="นามสกุล")
        pos = c3.text_input("ตำแหน่ง",       placeholder="ตำแหน่งงาน")

        st.markdown("---")
        st.markdown("#### หรือเพิ่มหลายคนพร้อมกัน")
        st.caption("รูปแบบแต่ละบรรทัด:  `ชื่อ  นามสกุล  ตำแหน่ง(ไม่บังคับ)`")
        bulk = st.text_area("", placeholder="สมชาย ใจดี ช่างไฟ\nสมหญิง รักงาน แม่บ้าน\nวิชัย สุขใจ", height=130)

        if st.button("➕ เพิ่มพนักงาน", use_container_width=True):
            added = 0
            if nm.strip() and sur.strip():
                employees.append({"id": new_id(), "name": nm.strip(), "surname": sur.strip(),
                                   "position": pos.strip(), "created_at": now_str()})
                added += 1
            for line in (bulk or "").strip().split("\n"):
                parts = line.strip().split()
                if len(parts) >= 2:
                    employees.append({"id": new_id(), "name": parts[0], "surname": parts[1],
                                       "position": " ".join(parts[2:]), "created_at": now_str()})
                    added += 1
            if added:
                _save("employees", employees)
                st.success(f"✅ เพิ่มพนักงาน {added} คน เรียบร้อยแล้ว!")
                st.rerun()
            else:
                st.error("กรุณากรอกชื่อและนามสกุลอย่างน้อย 1 คน")

# ─────────────────────────────────────────
#  PAGE: TASKS
# ─────────────────────────────────────────
def page_tasks():
    st.markdown("""<div class="page-header">
  <h1>📝 จัดการงาน</h1>
  <p>เพิ่ม แก้ไข และลบรายการงานที่จะแจกจ่าย</p>
</div>""", unsafe_allow_html=True)

    tasks = _load("tasks")
    tab_list, tab_add = st.tabs(["📋 รายการงาน", "➕ เพิ่มงาน"])

    # ── TAB LIST ──
    with tab_list:
        search = st.text_input("🔍 ค้นหางาน", placeholder="พิมพ์ชื่องาน / รายละเอียด...")
        filtered = [t for t in tasks if search.lower() in
                    f"{t['name']} {t.get('description','')}".lower()] if search else tasks

        st.markdown(f"**พบ {len(filtered)} / {len(tasks)} รายการ**")
        st.markdown("<hr/>", unsafe_allow_html=True)

        if not filtered:
            st.info("ไม่พบรายการงาน")
        else:
            hc = st.columns([0.4, 3, 4, 1.2])
            for h, t in zip(hc, ["#", "ชื่องาน", "รายละเอียด", "จัดการ"]):
                h.markdown(f"**{t}**")
            st.markdown("<hr style='margin:4px 0;'/>", unsafe_allow_html=True)

            for i, task in enumerate(filtered):
                c_no, c_nm, c_ds, c_act = st.columns([0.4, 3, 4, 1.2])
                c_no.markdown(f"<div style='padding:8px 0; color:#aaa;'>{i+1}</div>", unsafe_allow_html=True)
                new_name = c_nm.text_input("ชื่องาน",     value=task["name"],                    key=f"tn_{task['id']}", label_visibility="collapsed")
                new_desc = c_ds.text_input("รายละเอียด", value=task.get("description",""),        key=f"td_{task['id']}", label_visibility="collapsed")
                with c_act:
                    cs, cd = st.columns(2)
                    if cs.button("💾", key=f"tsave_{task['id']}", help="บันทึก"):
                        for t2 in tasks:
                            if t2["id"] == task["id"]:
                                t2["name"]        = new_name.strip()
                                t2["description"] = new_desc.strip()
                        _save("tasks", tasks)
                        st.success("บันทึกแล้ว!")
                        st.rerun()
                    if cd.button("🗑️", key=f"tdel_{task['id']}", help="ลบ"):
                        tasks = [t2 for t2 in tasks if t2["id"] != task["id"]]
                        _save("tasks", tasks)
                        st.success("ลบเรียบร้อย!")
                        st.rerun()
                st.markdown("<hr style='margin:3px 0; border-color:#FFCDD2 !important;'/>", unsafe_allow_html=True)

    # ── TAB ADD ──
    with tab_add:
        st.markdown("#### เพิ่มงานรายการ")
        c1, c2 = st.columns(2)
        tn = c1.text_input("ชื่องาน *",      placeholder="ชื่องาน")
        td = c2.text_input("รายละเอียด",     placeholder="รายละเอียดเพิ่มเติม (ถ้ามี)")

        st.markdown("---")
        st.markdown("#### หรือเพิ่มหลายงานพร้อมกัน")
        st.caption("รูปแบบแต่ละบรรทัด:  `ชื่องาน  รายละเอียด(ไม่บังคับ)`")
        bulk = st.text_area("", placeholder="ทำความสะอาด ห้องประชุม A\nส่งเอกสาร ชั้น 3\nตรวจสต็อกสินค้า", height=130)

        if st.button("➕ เพิ่มงาน", use_container_width=True):
            added = 0
            if tn.strip():
                tasks.append({"id": new_id(), "name": tn.strip(), "description": td.strip(), "created_at": now_str()})
                added += 1
            for line in (bulk or "").strip().split("\n"):
                parts = line.strip().split(None, 1)
                if parts:
                    tasks.append({"id": new_id(), "name": parts[0], "description": parts[1] if len(parts) > 1 else "", "created_at": now_str()})
                    added += 1
            if added:
                _save("tasks", tasks)
                st.success(f"✅ เพิ่มงาน {added} รายการ เรียบร้อยแล้ว!")
                st.rerun()
            else:
                st.error("กรุณากรอกชื่องานอย่างน้อย 1 รายการ")

# ─────────────────────────────────────────
#  PAGE: ASSIGNMENTS
# ─────────────────────────────────────────
def page_assignments():
    st.markdown("""<div class="page-header">
  <h1>🔀 แจกแจงงาน</h1>
  <p>มอบหมายงาน และสลับงานระหว่างพนักงาน</p>
</div>""", unsafe_allow_html=True)

    employees   = _load("employees")
    tasks       = _load("tasks")
    assignments = _load("assignments")

    if not employees:
        st.warning("⚠️ ยังไม่มีพนักงาน → กรุณาเพิ่มพนักงานก่อน")
        return
    if not tasks:
        st.warning("⚠️ ยังไม่มีรายการงาน → กรุณาเพิ่มงานก่อน")
        return

    emp_dict    = {e["id"]: e for e in employees}
    task_dict   = {t["id"]: t for t in tasks}
    assign_dict = {a["employee_id"]: a for a in assignments}
    task_opts   = ["— ยังไม่มีงาน —"] + [t["name"] for t in tasks]
    name_to_tid = {t["name"]: t["id"] for t in tasks}

    tab_assign, tab_swap = st.tabs(["📋 มอบหมายงาน", "🔄 สลับงาน"])

    # ── TAB ASSIGN ──
    with tab_assign:
        c1, c2 = st.columns(2)
        emp_q  = c1.text_input("🔍 ค้นหาพนักงาน", placeholder="ชื่อหรือนามสกุล...")
        task_f = c2.selectbox("🔍 กรองตามงาน", ["ทั้งหมด", "ยังไม่มีงาน"] + [t["name"] for t in tasks])

        filtered = employees
        if emp_q:
            filtered = [e for e in filtered if emp_q.lower() in f"{e['name']} {e['surname']}".lower()]
        if task_f == "ยังไม่มีงาน":
            filtered = [e for e in filtered if e["id"] not in assign_dict]
        elif task_f != "ทั้งหมด":
            tid = name_to_tid.get(task_f)
            filtered = [e for e in filtered if assign_dict.get(e["id"], {}).get("task_id") == tid]

        st.markdown(f"**แสดง {len(filtered)} / {len(employees)} คน**")
        st.markdown("<hr/>", unsafe_allow_html=True)

        pending_changes: dict[str, str] = {}

        hc = st.columns([0.4, 2.5, 3.5, 1.3])
        for h, t in zip(hc, ["#", "พนักงาน", "งานที่มอบหมาย", "บันทึก"]):
            h.markdown(f"**{t}**")
        st.markdown("<hr style='margin:4px 0;'/>", unsafe_allow_html=True)

        for i, emp in enumerate(filtered):
            cur_assign = assign_dict.get(emp["id"])
            cur_task_name = task_dict.get(cur_assign["task_id"], {}).get("name", "") if cur_assign and cur_assign.get("task_id") else ""
            cur_idx = task_opts.index(cur_task_name) if cur_task_name in task_opts else 0

            c_no, c_emp, c_task, c_btn = st.columns([0.4, 2.5, 3.5, 1.3])
            c_no.markdown(f"<div style='padding:10px 0; color:#aaa;'>{i+1}</div>", unsafe_allow_html=True)
            c_emp.markdown(
                f"<div style='padding:8px 0;'><b>{emp['name']} {emp['surname']}</b>"
                f"{'<br><small style=color:#aaa>' + emp.get('position','') + '</small>' if emp.get('position') else ''}"
                f"</div>",
                unsafe_allow_html=True
            )
            selected = c_task.selectbox("งาน", task_opts, index=cur_idx, key=f"asel_{emp['id']}", label_visibility="collapsed")
            pending_changes[emp["id"]] = selected

            if c_btn.button("💾 บันทึก", key=f"abtn_{emp['id']}"):
                new_tid = name_to_tid.get(selected)
                _upsert_assignment(assignments, emp["id"], new_tid)
                st.success(f"บันทึกงานของ {emp['name']} แล้ว!")
                st.rerun()
            st.markdown("<hr style='margin:3px 0; border-color:#FFCDD2 !important;'/>", unsafe_allow_html=True)

        st.markdown("")
        if st.button("💾 บันทึกทั้งหมดพร้อมกัน", use_container_width=True):
            for eid, sel in pending_changes.items():
                new_tid = name_to_tid.get(sel)
                _upsert_assignment(assignments, eid, new_tid)
            _save("assignments", assignments)
            st.success(f"✅ บันทึกทั้งหมด {len(pending_changes)} รายการ เรียบร้อย!")
            st.rerun()

    # ── TAB SWAP ──
    with tab_swap:
        st.markdown("#### 🔄 เลือกพนักงาน 2 คนเพื่อสลับงานกัน")
        emp_labels  = [f"{e['name']} {e['surname']}" for e in employees]
        label_to_id = {f"{e['name']} {e['surname']}": e["id"] for e in employees}

        sc1, sc2 = st.columns(2)
        sel1 = sc1.selectbox("พนักงานคนที่ 1", emp_labels, key="sw1")
        sel2 = sc2.selectbox("พนักงานคนที่ 2", emp_labels, key="sw2")

        id1, id2 = label_to_id[sel1], label_to_id[sel2]
        a1, a2   = assign_dict.get(id1), assign_dict.get(id2)
        t1_name  = task_dict.get(a1["task_id"], {}).get("name", "ยังไม่มีงาน") if a1 and a1.get("task_id") else "ยังไม่มีงาน"
        t2_name  = task_dict.get(a2["task_id"], {}).get("name", "ยังไม่มีงาน") if a2 and a2.get("task_id") else "ยังไม่มีงาน"

        sc1.markdown(f"<div class='info-card'>งานปัจจุบัน: <b>{t1_name}</b></div>", unsafe_allow_html=True)
        sc2.markdown(f"<div class='info-card'>งานปัจจุบัน: <b>{t2_name}</b></div>", unsafe_allow_html=True)

        st.markdown("")
        if st.button("🔄 สลับงานทันที", use_container_width=True):
            if id1 == id2:
                st.error("กรุณาเลือกพนักงานคนละคน")
            else:
                tid1 = a1["task_id"] if a1 else None
                tid2 = a2["task_id"] if a2 else None
                _upsert_assignment(assignments, id1, tid2)
                _upsert_assignment(assignments, id2, tid1)
                _save("assignments", assignments)
                st.success(f"✅ สลับงานระหว่าง **{sel1}** ↔ **{sel2}** เรียบร้อย!")
                st.rerun()

def _upsert_assignment(assignments: list, emp_id: str, task_id):
    for a in assignments:
        if a["employee_id"] == emp_id:
            a["task_id"]       = task_id
            a["assigned_date"] = now_str()
            return
    if task_id:
        assignments.append({
            "id": new_id(), "employee_id": emp_id,
            "task_id": task_id, "assigned_date": now_str(),
        })

# ─────────────────────────────────────────
#  PAGE: PRINT A4
# ─────────────────────────────────────────
def page_print():
    st.markdown("""<div class="page-header">
  <h1>🖨️ พิมพ์รายการ A4</h1>
  <p>สร้างเอกสารพร้อมพิมพ์ปรับขนาดอัตโนมัติตามจำนวนพนักงาน</p>
</div>""", unsafe_allow_html=True)

    employees   = _load("employees")
    tasks       = _load("tasks")
    assignments = _load("assignments")

    emp_dict    = {e["id"]: e for e in employees}
    task_dict   = {t["id"]: t for t in tasks}
    assign_dict = {a["employee_id"]: a for a in assignments}

    # ── Options ──
    co1, co2 = st.columns([2, 1])
    with co1:
        doc_title    = st.text_input("ชื่อเอกสาร",  value="รายการแจกแจงงาน")
        doc_subtitle = st.text_input("คำบรรยาย",    value=f"วันที่ {datetime.now().strftime('%d/%m/%Y')}")
        emp_filter   = st.text_input("🔍 เลือกพนักงานที่จะพิมพ์ (เว้นว่าง = ทั้งหมด)",
                                      placeholder="ค้นหาชื่อพนักงาน...")
    with co2:
        st.markdown("<br>", unsafe_allow_html=True)
        show_pos   = st.checkbox("แสดงตำแหน่ง",          value=True)
        show_desc  = st.checkbox("แสดงรายละเอียดงาน",    value=True)
        show_date  = st.checkbox("แสดงวันที่มอบหมาย",    value=False)
        show_sign  = st.checkbox("มีช่องเซ็นรับทราบ",    value=True)

    filtered_emp = [e for e in employees if not emp_filter or
                    emp_filter.lower() in f"{e['name']} {e['surname']}".lower()]

    count = len(filtered_emp)

    # Auto font size
    if   count <= 10: fs = "14pt"; row_h = "38px"
    elif count <= 20: fs = "12pt"; row_h = "32px"
    elif count <= 30: fs = "10pt"; row_h = "28px"
    elif count <= 40: fs = "9pt";  row_h = "24px"
    elif count <= 55: fs = "8pt";  row_h = "20px"
    else:             fs = "7pt";  row_h = "18px"

    st.info(f"📄 จำนวนพนักงานที่จะพิมพ์: **{count} คน** | ขนาดตัวอักษรอัตโนมัติ: **{fs}**")

    # Build rows HTML
    tbody = ""
    for i, emp in enumerate(filtered_emp):
        assign  = assign_dict.get(emp["id"])
        task    = task_dict.get(assign["task_id"], {}) if assign and assign.get("task_id") else {}
        t_name  = task.get("name", "—") or "—"
        t_desc  = f"<div class='sub'>{task.get('description','')}</div>" if show_desc and task.get("description") else ""
        pos_div = f"<div class='sub'>{emp.get('position','')}</div>"    if show_pos  and emp.get("position") else ""
        dt_div  = f"<div class='sub'>มอบหมาย: {assign.get('assigned_date','')}</div>" if show_date and assign else ""
        sign_td = "<td class='sign'></td>" if show_sign else ""

        row_cls = "odd" if i % 2 == 0 else "even"
        tbody += f"""
<tr class='{row_cls}'>
  <td class='num'>{i+1}</td>
  <td>{emp['name']} {emp['surname']}{pos_div}</td>
  <td>{t_name}{t_desc}{dt_div}</td>
  {sign_td}
</tr>"""

    sign_th = "<th class='sign'>ลายเซ็นรับทราบ</th>" if show_sign else ""
    sign_col = "<col style='width:20%'/>" if show_sign else ""

    print_html = f"""<!DOCTYPE html>
<html lang='th'>
<head>
<meta charset='UTF-8'>
<title>{doc_title}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;600;700;800&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{
  font-family:'Sarabun','TH Sarabun New',sans-serif;
  font-size:{fs};
  background:#fff;
  color:#111;
}}
@page{{
  size:A4 portrait;
  margin:12mm 14mm 12mm 14mm;
}}
@media print{{
  .no-print{{display:none!important;}}
  body{{margin:0;}}
  tr{{page-break-inside:avoid;}}
}}
.wrap{{width:182mm;margin:0 auto;padding:10mm 0;}}
.hdr{{text-align:center;padding-bottom:10px;border-bottom:3px solid #8B0000;margin-bottom:12px;}}
.hdr .sys{{font-size:.85em;color:#8B0000;font-weight:700;letter-spacing:1px;}}
.hdr .ttl{{font-size:1.4em;font-weight:800;margin:4px 0 2px;}}
.hdr .sub{{font-size:.88em;color:#555;}}
table{{width:100%;border-collapse:collapse;}}
colgroup col{{}}
thead tr{{background:#8B0000;color:#fff;}}
th{{padding:7px 9px;text-align:left;font-weight:700;}}
th.num{{width:6%;text-align:center;}}
th.sign{{width:20%;}}
td{{padding:4px 9px;border-bottom:.5px solid #FFCDD2;min-height:{row_h};vertical-align:middle;}}
td.num{{text-align:center;color:#8B0000;font-weight:700;}}
td.sign{{border-left:1px solid #FFCDD2;min-height:{row_h};}}
tr.even{{background:#FFF5F5;}}
tr.odd{{background:#fff;}}
.sub{{font-size:.82em;color:#666;margin-top:2px;}}
.ftr{{margin-top:14px;border-top:1px solid #FFCDD2;padding-top:8px;
      display:flex;justify-content:space-between;font-size:.78em;color:#999;}}
.print-btn{{
  position:fixed;top:16px;right:16px;
  background:#8B0000;color:#fff;border:none;
  padding:10px 22px;border-radius:8px;cursor:pointer;
  font-size:13pt;font-family:'Sarabun',sans-serif;font-weight:700;
  box-shadow:0 4px 14px rgba(139,0,0,.4);z-index:999;
}}
.print-btn:hover{{background:#B71C1C;}}
</style>
</head>
<body>
<button class='print-btn no-print' onclick='window.print()'>🖨️ พิมพ์เอกสาร</button>
<div class='wrap'>
  <div class='hdr'>
    <div class='sys'>📋 ระบบแจกแจงงาน</div>
    <div class='ttl'>{doc_title}</div>
    <div class='sub'>{doc_subtitle} &nbsp;|&nbsp; พนักงาน {count} คน</div>
  </div>
  <table>
    <colgroup>
      <col style='width:6%;'/>
      <col style='width:{"34%" if show_sign else "44%"};'/>
      <col style='width:{"40%" if show_sign else "50%"};'/>
      {sign_col}
    </colgroup>
    <thead>
      <tr>
        <th class='num'>#</th>
        <th>ชื่อ-นามสกุล{'&nbsp;/ ตำแหน่ง' if show_pos else ''}</th>
        <th>งานที่ได้รับมอบหมาย</th>
        {sign_th}
      </tr>
    </thead>
    <tbody>
      {tbody}
    </tbody>
  </table>
  <div class='ftr'>
    <span>ระบบแจกแจงงาน | พิมพ์เมื่อ {datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
    <span>รวม {count} รายการ</span>
  </div>
</div>
</body>
</html>"""

    # Encode & open
    b64 = base64.b64encode(print_html.encode("utf-8")).decode()

    if st.button("🖨️ เปิดหน้าพิมพ์ A4 (เปิดแท็บใหม่)", use_container_width=True):
        js = f"""
<script>
(function(){{
  var b = atob('{b64}');
  var ba = new Uint8Array(b.length);
  for(var i=0;i<b.length;i++) ba[i]=b.charCodeAt(i);
  var blob = new Blob([ba],{{type:'text/html;charset=utf-8'}});
  var url  = URL.createObjectURL(blob);
  window.open(url,'_blank');
}})();
</script>"""
        components.html(js, height=0)
        st.success("✅ กำลังเปิดหน้าพิมพ์ในแท็บใหม่…")

    # Download backup
    st.download_button(
        label="⬇️ ดาวน์โหลดเป็นไฟล์ HTML",
        data=print_html.encode("utf-8"),
        file_name=f"assignment_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
        mime="text/html",
        use_container_width=True,
    )

    # Preview table
    st.markdown("---")
    st.markdown("### 👁️ ตัวอย่างรายการ")
    prev = [{"#": i+1,
             "ชื่อ-นามสกุล": f"{e['name']} {e['surname']}",
             "ตำแหน่ง":      e.get("position",""),
             "งาน":          task_dict.get(assign_dict.get(e["id"],{}).get("task_id",""), {}).get("name","—") if assign_dict.get(e["id"]) else "—"}
            for i, e in enumerate(filtered_emp)]
    if prev:
        st.dataframe(pd.DataFrame(prev), use_container_width=True, hide_index=True)

# ─────────────────────────────────────────
#  PAGE: SETTINGS
# ─────────────────────────────────────────
def page_settings():
    st.markdown("""<div class="page-header">
  <h1>⚙️ ตั้งค่าผู้ใช้</h1>
  <p>จัดการบัญชีผู้ใช้งานระบบ</p>
</div>""", unsafe_allow_html=True)

    users        = _load("users")
    current_user = st.session_state.current_user
    tab_pw, tab_users = st.tabs(["🔑 เปลี่ยนรหัสผ่าน", "👤 จัดการผู้ใช้"])

    with tab_pw:
        old = st.text_input("รหัสผ่านเดิม",       type="password", key="s_old")
        nw  = st.text_input("รหัสผ่านใหม่",       type="password", key="s_new")
        cf  = st.text_input("ยืนยันรหัสผ่านใหม่", type="password", key="s_cf")
        if st.button("เปลี่ยนรหัสผ่าน"):
            user_obj = next((u for u in users if u["username"] == current_user["username"]), None)
            if user_obj and user_obj["password"] == hash_pw(old):
                if nw != cf:       st.error("รหัสผ่านไม่ตรงกัน")
                elif len(nw) < 6:  st.error("รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร")
                else:
                    user_obj["password"] = hash_pw(nw)
                    _save("users", users)
                    st.success("✅ เปลี่ยนรหัสผ่านเรียบร้อย!")
            else:
                st.error("รหัสผ่านเดิมไม่ถูกต้อง")

    with tab_users:
        if current_user.get("role") == "admin":
            for u in users:
                c1, c2, c3 = st.columns([2, 2, 1])
                c1.markdown(f"👤 **{u['username']}** ({u.get('display_name','')})")
                c2.markdown(f"`{u.get('role','user')}`")
                if u["username"] != "admin" and c3.button("🗑️", key=f"delu_{u['username']}"):
                    _save("users", [x for x in users if x["username"] != u["username"]])
                    st.rerun()
            st.markdown("---")
            st.markdown("#### ➕ เพิ่มผู้ใช้ใหม่")
            nc1, nc2, nc3 = st.columns(3)
            nu  = nc1.text_input("ชื่อผู้ใช้")
            np  = nc2.text_input("รหัสผ่าน", type="password")
            nr  = nc3.selectbox("สิทธิ์", ["user", "admin"])
            nd  = st.text_input("ชื่อที่แสดง")
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
        else:
            st.info("เฉพาะผู้ดูแลระบบเท่านั้นที่สามารถจัดการผู้ใช้ได้")

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
    PAGE_MAP.get(st.session_state.get("page", "dashboard"), page_dashboard)()

if __name__ == "__main__":
    main()
