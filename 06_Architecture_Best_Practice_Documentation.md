# Deliverable #6: Architecture & Best-Practice Documentation

**โปรเจกต์:** Enterprise Data Warehouse for Energy Operations Intelligence
**วัตถุประสงค์ของเอกสารนี้:** สรุปภาพรวมสถาปัตยกรรมทั้งโปรเจกต์เป็นเอกสารเดียว ใช้เป็นจุดเริ่มต้นสำหรับคนที่ไม่เคยเห็นโปรเจกต์มาก่อน

---

## 1. End-to-End Architecture

```
                        ┌─────────────────────────────┐
                        │         DATA SOURCES         │
                        │                               │
   Company Filings ─────┤  56-1 One Report (5 บริษัท   │
   (semi-manual)         │  × 3 ปี) — PDF, verify ด้วยมือ │
                        │                               │
   Market Data ─────────┤  yfinance (ราคาหุ้นรายวัน)     │
   (automated)          │                               │
                        │                               │
   Government Data ─────┤  EIA (Brent price)            │
   (automated)          │  EPPO (national energy)       │
                        │  DMF (petroleum production)   │
                        └───────────────┬───────────────┘
                                        │
                        ┌───────────────▼───────────────┐
                        │      EXTRACT (Python/Docker)   │
                        │  extract_finance_operations.py │
                        │  extract_investor.py           │
                        │  extract_reference.py          │
                        └───────────────┬───────────────┘
                                        │
                        ┌───────────────▼───────────────┐
                        │   TRANSFORM (transform.py)     │
                        │  - EBITDA, margin, CAPEX ratio │
                        │  - FX normalization (THB→USD)  │
                        │  - Data quality flag (PTTEP)   │
                        └───────────────┬───────────────┘
                                        │
                        ┌───────────────▼───────────────┐
                        │   LOAD → BigQuery (7 tables)   │
                        │  fact_finance_operations_annual│
                        │  fact_investor_daily/annual    │
                        │  fact_reference_crude_price    │
                        │  data_quality_restatement_checks│
                        │  data_quality_anomalies        │
                        │  currency_conversion_rates     │
                        └───────────────┬───────────────┘
                                        │
                        ┌───────────────▼───────────────┐
                        │  VISUALIZE — Looker Studio     │
                        │  3 หน้า: Overview / Deep-dive /│
                        │           Data Quality          │
                        └─────────────────────────────────┘
```

**จุดที่ต่างจาก pipeline อัตโนมัติทั่วไป:** ขั้น Extract ของ finance/operations data เป็น **"semi-manual, human-in-the-loop"** โดยตั้งใจ ไม่ใช่ automate เต็มรูปแบบ เพราะ 56-1 One Report เป็นรายงานบรรยายยาว 300-500+ หน้า การ parse อัตโนมัติเสี่ยงผิดแบบเงียบ ๆ (silent error) มากกว่าการอ่าน+verify ด้วยคน — เป็นการตัดสินใจ trade-off ที่ตั้งใจ ไม่ใช่ข้อจำกัดทางเทคนิค

---

## 2. Technology Stack และเหตุผลที่เลือก

| Layer | เครื่องมือ | เหตุผล |
|---|---|---|
| Data Warehouse | Google BigQuery | ฟรี (free tier), ใช้งานง่าย |
| BI/Dashboard | Looker Studio | ฟรี, web-based (ใช้บน Mac ได้ปกติ ต่างจาก Power BI Desktop/TIBCO Spotfire ที่เป็น Windows-only) |
| ETL Runtime | Python + Docker | reproducible ข้าม environment, ไม่เจอปัญหา "รันได้ในเครื่องฉัน" |
| Version control ของข้อมูล | Single CSV source of truth (`manual_entry_verified.csv`) | ลด friction ระหว่าง extract/transform — เคยมี 2 ไฟล์ปนกันจนสับสน (`manual_entry_template.csv` vs `manual_entry_verified.csv`) แก้เป็นไฟล์เดียว |
| Market/reference data | yfinance, EIA API, EPPO/DMF open data | ทั้งหมดฟรี ไม่ต้องพึ่ง data vendor ที่มีค่าใช้จ่าย |

---

## 3. Key Architectural Decisions (Decision Log)

| การตัดสินใจ | ทางเลือกอื่นที่พิจารณา | เหตุผลที่เลือก |
|---|---|---|
| Cross-company benchmarking (5 บริษัท) แทน PTTEP-only deep-dive | PTTEP Upstream Portfolio DW (project-level, เจาะลึก reserves/working interest) | ลดความเสี่ยง domain (petroleum engineering ลึก), ให้ business function (Finance/Operations/Market) เป็นหน่วยวิเคราะห์ที่ตรงกับแผนกจริงในองค์กรมากกว่า |
| Star schema (Kimball bus architecture) | Single wide denormalized table | Conformed dimensions ทำให้ query ข้าม mart ได้โดยไม่ต้องแปลงข้อมูล เป็นมาตรฐานอุตสาหกรรม |
| DMF cross-check จำกัดแค่ PTTEP | ทำ cross-check ให้ทุกบริษัท | ตรวจสอบข้อมูลจริงแล้วพบว่า DMF เป็นข้อมูลระดับ field (upstream) เท่านั้น — TOP/BCP/OR เป็น downstream ไม่มี production data ให้เทียบตามธรรมชาติของธุรกิจ ไม่ใช่ข้อจำกัดของ pipeline |
| CAPEX นิยามเดียวกันทุกบริษัท (PP&E + E&E + Intangible, ไม่รวม short-term investments) | ใช้ตัวเลข "Net cash used in investing activities" ตรง ๆ | ตัวเลข investing activities ปนกิจกรรมบริหารสภาพคล่อง (short-term investments, loans) ที่ไม่ใช่ CAPEX จริง — ต้อง filter ให้เหลือแค่การลงทุนสินทรัพย์ถาวร เพื่อเทียบข้ามบริษัทได้อย่างมีความหมาย |
| Currency: ใช้ average annual FX rate (cross-verified 2 แหล่ง) | ใช้ point-in-time rate หรือ rate จากรายงานเอง | มีแค่ PTTEP ที่รายงานคู่ USD/THB ในตัว บริษัทอื่นรายงาน THB อย่างเดียว — average annual เป็นมาตรฐานที่ยอมรับได้และ verify ได้จากแหล่งอิสระ |
| Data quality tables (`data_quality_*`) แยกจาก fact table หลัก | รวม data quality logic เข้า fact table เดียว | เป็น static snapshot ที่ verify ด้วยมือ อัปเดตไม่บ่อย — แยก table ทำให้ fact table หลักไม่ปนกับ metadata ที่มี grain ต่างกัน |

---

## 4. Best Practices ที่ใช้ในโปรเจกต์

**Data Governance**
- Conformed dimensions (`dim_company`, `dim_date`, `dim_energy_segment`) ให้ metric definition ตรงกันทุก mart
- ทุก assumption ที่ใช้ (BOE conversion factor, FX rate, นิยาม CAPEX) บันทึกไว้เป็นลายลักษณ์อักษร ไม่ใช่ implicit ในโค้ด

**Data Quality**
- Cross-source validation จริง (restatement check ระหว่างรายงาน 2 ฉบับติดกัน ไม่ใช่แค่ trust ตัวเลขจากแหล่งเดียว)
- Anomaly ที่เจอ (BCP tax expense) บันทึกไว้ตรง ๆ ไม่พยายามหาเหตุผลมากลบ

**Traceability**
- ทุก fact row มี `report_name`, `document_type`, `source`, `report_url` ย้อนกลับไปยังต้นฉบับได้เสมอ

**Reproducibility**
- Dockerized pipeline — build ที่ไหนก็ได้ผลเหมือนกัน (พิสูจน์จริงตอน build ผ่าน Google Cloud Build แล้วรันได้ในเครื่อง local เหมือนกัน)
- Single source of truth CSV — ไม่มี "ไฟล์ไหนคือตัวจริง" ให้สับสน

---

## 5. ข้อจำกัดที่รู้ตัว (Known Limitations)

- **Data quality checks เป็น static/manual** ไม่ใช่ automated job ที่รันตรวจสอบเองตามรอบ — ถ้าเพิ่มข้อมูลปีใหม่ต้อง verify ซ้ำด้วยมือ
- **DMF cross-check ใช้ได้กับ PTTEP เท่านั้น** ตามธรรมชาติของ business model แต่ละบริษัท
- **Currency conversion เป็น annual average** ไม่ใช่ point-in-time — เพียงพอสำหรับ trend analysis แต่ไม่เหมาะกับการวิเคราะห์ที่ต้องการความละเอียดระดับวัน
- **Reference/Industry Benchmark page ถูกตัดออกจาก scope** (ไม่ใช่แค่ยังไม่เสร็จ) — 3 หน้าที่มีเพียงพอต่อการเล่า core insight ของโปรเจกต์

---

## 6. สรุปสถานะโปรเจกต์

**Deliverable ทั้ง 6 ข้อเสร็จสมบูรณ์:**

| # | Deliverable | ไฟล์ |
|---|---|---|
| 1 | Requirement Gathering | `01_Requirement_Gathering.md` |
| 2 | Star Schema Design | `02_Star_Schema_Design.md` |
| 3 | ETL Pipeline | `03_ETL_Pipeline/` |
| 4 | Data Quality Assessment | `04_Data_Quality_Assessment.md` |
| 5 | Dashboard | `05_Dashboard_Design_Blueprint.md` + Looker Studio (live) |
| 6 | Architecture & Best Practice | เอกสารนี้ |