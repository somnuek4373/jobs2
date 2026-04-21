# 📋 ระบบแจกแจงงาน — Task Assignment System

> ระบบ web app สำหรับมอบหมายและแจกแจงงานให้พนักงาน สร้างด้วย Python + Streamlit

---

## ✨ ฟีเจอร์หลัก

| ฟีเจอร์ | รายละเอียด |
|---|---|
| 🔐 ระบบล็อกอิน | บัญชีผู้ใช้หลายคน รองรับสิทธิ์ admin / user |
| 👥 จัดการพนักงาน | เพิ่ม / แก้ไข / ลบ ค้นหาชื่อ-นามสกุล-ตำแหน่ง |
| 📝 จัดการงาน | เพิ่ม / แก้ไข / ลบ รายการงาน ค้นหาได้ |
| 🔀 แจกแจงงาน | มอบหมายงานทีละคนหรือทั้งหมด กรองด้วยชื่อหรืองาน |
| 🔄 สลับงาน | เลือกพนักงาน 2 คนสลับงานกันได้ทันที |
| 🖨️ พิมพ์ A4 | สร้างเอกสารพิมพ์ ปรับขนาดตัวอักษรอัตโนมัติ ดาวน์โหลด HTML |
| ⚙️ จัดการผู้ใช้ | เพิ่ม/ลบผู้ใช้ เปลี่ยนรหัสผ่าน |

---

## 🚀 วิธีติดตั้งและรัน

### รันบนเครื่อง Local

```bash
# 1. Clone repo
git clone https://github.com/<your-username>/task-assignment-app.git
cd task-assignment-app

# 2. ติดตั้ง dependencies
pip install -r requirements.txt

# 3. รันแอพ
streamlit run app.py
```

เปิด browser ที่ `http://localhost:8501`

---

### Deploy บน Streamlit Community Cloud (ฟรี)

1. Push โค้ดขึ้น GitHub
2. ไปที่ [share.streamlit.io](https://share.streamlit.io)
3. กด **New app** → เลือก repo → `app.py` → **Deploy!**

---

## 🔑 ข้อมูลเข้าสู่ระบบเริ่มต้น

```
Username : admin
Password : admin123
```

> ⚠️ **ควรเปลี่ยนรหัสผ่านหลัง deploy** ที่เมนู ⚙️ ตั้งค่าผู้ใช้

---

## 📁 โครงสร้างโปรเจกต์

```
task-assignment-app/
├── app.py              ← แอพหลัก (Streamlit)
├── requirements.txt    ← Python dependencies
├── README.md
├── .gitignore
└── data/               ← ไฟล์ข้อมูล (สร้างอัตโนมัติ)
    ├── users.json
    ├── employees.json
    ├── tasks.json
    └── assignments.json
```

---

## 🎨 ธีม

สีแดง-ขาว (`#8B0000` / `#C62828`) ออกแบบให้อ่านง่าย สบายตา  
ฟอนต์ **Sarabun** สำหรับภาษาไทย

---

## 📄 ฟีเจอร์พิมพ์ A4

- ปรับขนาดตัวอักษรอัตโนมัติตามจำนวนพนักงาน  
- เลือกแสดง: ตำแหน่ง / รายละเอียดงาน / วันที่ / ช่องเซ็น  
- เปิดพิมพ์ในแท็บใหม่ หรือดาวน์โหลดเป็น HTML  

---

## 🛠️ Tech Stack

- **Python 3.9+**
- **Streamlit** — UI framework  
- **Pandas** — ตารางข้อมูล  
- **JSON** — ฐานข้อมูล (ไม่ต้องติดตั้ง database)

---

*Made with ❤️ + Streamlit*
