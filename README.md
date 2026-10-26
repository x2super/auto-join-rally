# AnyJoin ⚡

> **High-Performance Direct-API Activity & Club Sniper for EnrollJoin (Pawano Enroll V.7)**  
> สคริปต์ลงทะเบียนกิจกรรมชุมนุมอัตโนมัติความเร็วสูง ยิงตรงผ่าน Direct AJAX API ระดับมิลลิวินาที พร้อมระบบตั้งเวลาล่วงหน้าและกู้คืนเซสชันเมื่อเว็บล่ม

---

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg?style=for-the-badge&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg?style=for-the-badge)](#)
[![Speed](https://img.shields.io/badge/Latency-Sub--100ms-orange.svg?style=for-the-badge)](#)

---

## ✨ Features (จุดเด่น)

- ⚡ **Direct REST/AJAX Endpoint**: ยิง payload ตรงเข้าสู่ `POST /1509/7401/{category_id}` โดยข้ามหน้าเว็บ UI, การโหลดรูปภาพ และ ASP.NET WebForms Postback หน่วงๆ ตอบสนองในระดับ sub-100ms
- 🎯 **Smart Code Resolver**: รองรับทั้งรหัสชุมนุมสั้น (เช่น `2217`, `H2217`) หรือรหัสภายใน 8 หลัก (`61718395`) แปลงรหัสและหมวดหมู่อัตโนมัติใน 0ms ผ่านฐานข้อมูลออฟไลน์ `quick_dump.json`
- ⏱️ **Precision Countdown Timer**: ตั้งเวลาเปิดระบบล่วงหน้าได้แบบวินาทีต่อวินาที (เช่น `14:00:00`) พร้อม Ticker นับถอยหลัง และจะเริ่มยิงทันที ณ จุดตัดของเวลาโดยไม่มี latency เสียเปล่า
- 🛡️ **Crash & Rate-Limit Resilience**: รับมือเว็บล่มช่วงคนแย่งกันเปิดระบบ (500, 502 Bad Gateway, 503, Connection Dropped, Timeout) โดยวนลูปยิงซ้ำอัตโนมัติต่อเนื่องจนกว่าจะสำเร็จ
- 🔄 **Auto Re-Authentication**: ตรวจจับกรณีเซสชันหลุด (Server ส่ง 302 Redirect กลับหน้า Login) แล้วทำ ViewState login ใหม่ให้ทันทีกลางอากาศโดยไม่ต้องเริ่มสคริปต์ใหม่
- 👥 **Multi-Account Concurrent Concurrency**: รองรับการลงทะเบียนพร้อมกันหลายคนผ่าน `ThreadPoolExecutor` แยก thread และแยก session cookies ของแต่ละคนอย่างสมบูรณ์
- 🔔 **Clean Console & Audio Alert**: ตัด log รกๆ ทิ้ง แสดงเฉพาะสถานะสำคัญ และมีเสียงเตือน `\a` (Terminal Bell) ทันทีที่ลงทะเบียนสำเร็จ

---

## 📁 Project Structure

```text
anyjoin/
├── auto_join.py       # Core sniper engine & CLI controller
├── config.json        # การตั้งค่าบัญชี, รหัสชุมนุม และเวลาเริ่มต้น
├── quick_dump.json    # ฐานข้อมูลรหัสกิจกรรม/หมวดหมู่ออฟไลน์ (0ms lookup)
├── requirements.txt   # รายการ dependencies ที่ต้องใช้
└── .gitignore         # ป้องกันการเผลอ commit ข้อมูลเซสชันส่วนตัว
```

---

## 🚀 Quick Start (เริ่มต้นใช้งาน)

### 1. ติดตั้ง Dependencies
ตรวจสอบว่าติดตั้ง Python 3.9 ขึ้นไป จากนั้นรัน:

```bash
pip install -r requirements.txt
```

### 2. ตั้งค่า `config.json`

เปิดไฟล์ `config.json` แล้วกรอกข้อมูลของคุณ:

#### แบบคนเดียว (Single Account):
```json
{
  "student_id": "31820",
  "citizen_id": "175990053xxxx",
  "club_id": "2217",
  "start_time": "14:00"
}
```

#### แบบหลายคนพร้อมกัน (Multi-Account Concurrency):
```json
[
  {
    "student_id": "31820",
    "citizen_id": "175990053xxxx",
    "club_id": "2217",
    "start_time": "14:00"
  },
  {
    "student_id": "31819",
    "citizen_id": "170990186xxxx",
    "club_id": "2217",
    "start_time": "14:00"
  }
]
```

### 3. รันระบบ

```bash
python auto_join.py
```

> **หมายเหตุ:** หากเว้นว่างค่าใน `config.json` ไว้ ตัวโปรแกรมจะสลับเป็นโหมด Interactive ถามข้อมูลสั้นๆ 4 บรรทัดผ่าน Terminal ให้อัตโนมัติ

---

## ⚙️ Configuration Reference

| Field | Type | Required | Description |
| :--- | :---: | :---: | :--- |
| `student_id` | `string` | **Yes** | รหัสนักเรียน (เช่น `31820`) |
| `citizen_id` | `string` | **Yes** | เลขประจำตัวประชาชน 13 หลัก |
| `club_id` | `string` | **Yes** | รหัสชุมนุม เช่น `2217`, `H2217` หรือรหัสตรง 8 หลัก `61718395` |
| `start_time` | `string` | No | เวลาที่ต้องการให้เริ่มยิง (`HH:MM` หรือ `HH:MM:SS`) เว้นว่างเพื่อยิงทันที |
| `interval` | `float` | No | ความถี่ในการวนลูปยิงซ้ำเมื่อเซิร์ฟเวอร์ยังไม่เปิด (ค่าเริ่มต้น: `0.2` วินาที) |

---

## 🔬 Technical Architecture (Reverse Engineering)

EnrollJoin ทำงานบน ASP.NET WebForms V.7 ซึ่งมี flow การลงทะเบียน 2 ชั้น:

1. **Authentication Flow**:
   - `GET /login?q={cat_id}` เพื่อดึง `__VIEWSTATE`, `__VIEWSTATEGENERATOR` และ `__EVENTVALIDATION`
   - `POST /login?q={cat_id}` พร้อมส่ง `txtstudent_stdCode` และ `txtstudent_stdCard`
   - ระบบจะได้รับ Authentication Cookies เก็บไว้ใน `session_{student_id}.json` เพื่อนำกลับมาใช้ซ้ำโดยไม่ต้องล็อกอินใหม่ทุกครั้ง
2. **Direct Join Payload**:
   - URL: `POST https://sattha.enrolljoin.com/1509/7401/{category_id}`
   - Header: `Content-Type: application/json; charset=UTF-8`, `X-Requested-With: XMLHttpRequest`
   - Body:
     ```json
     {
       "_mActivities_Code": "61718395"
     }
     ```
   - Server Response:
     ```json
     [
       {
         "status": "1",
         "alert_text": "ลงทะเบียนสำเร็จ",
         "message": "..."
       }
     ]
     ```

---

## ⚠️ Disclaimer

- ซอฟต์แวร์นี้จัดทำขึ้นเพื่อการศึกษาการทำงานของโครงสร้าง Web Protocol (REST/AJAX Reverse Engineering) และการทดสอบ Performance การรองรับโหลดของระบบเท่านั้น
- ผู้ใช้งานต้องยอมรับความรับผิดชอบในการใช้งานด้วยตนเองตามกฎและข้อกำหนดของสถาบันการศึกษา

---

## 📄 License

This project is open-sourced under the [MIT License](LICENSE).
