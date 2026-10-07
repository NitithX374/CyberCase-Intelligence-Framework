# Diagram verification — 2026-10-04

- Checkout HEAD: `5fdfb4d6`
- ตรวจ method/path ของ 21 HTTP operations กับ `http://localhost:8000/openapi.json`
- 7 ไฟล์ draw.io แยก และ 1 ไฟล์รวม 7 หน้า parse เป็น XML ได้
- cell IDs ไม่ซ้ำในแต่ละหน้า; มี root cells 0/1; ทุก edge มี geometry และ source/target ถูกต้อง
- source pointers ทุกไฟล์ใน diagram-specs.json มีอยู่ใน checkout
- PNG ทั้ง 7 รูป render แล้ว และตรวจภาพสำหรับข้อความไทย ลูกศร และพื้นที่แสดงผล
- `git diff --check` ผ่าน
- ผลนี้ตรวจเอกสารและ API surface; ไม่มีการเรียก provider หรือเขียนข้อมูลเคส

## HTTP operations

```text
POST   /api/v1/auth/register
POST   /api/v1/auth/login
GET    /api/v1/auth/session
POST   /api/v1/auth/logout
GET    /api/v1/cases
POST   /api/v1/cases
GET    /api/v1/cases/{case_id}
PATCH  /api/v1/cases/{case_id}
DELETE /api/v1/cases/{case_id}
GET    /api/v1/cases/{case_id}/sources
POST   /api/v1/cases/{case_id}/sources
POST   /api/v1/cases/{case_id}/documents
GET    /api/v1/cases/{case_id}/documents/{document_id}/content
POST   /api/v1/cases/{case_id}/analysis
GET    /api/v1/cases/{case_id}/analysis
GET    /api/v1/cases/{case_id}/chat
POST   /api/v1/cases/{case_id}/chat/messages
POST   /api/v1/cases/{case_id}/reports
GET    /api/v1/cases/{case_id}/reports
GET    /api/v1/cases/{case_id}/reports/{report_id}/pdf
GET    /api/v1/cases/{case_id}/reports/{report_id}/html
```

