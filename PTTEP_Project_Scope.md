# Enterprise Data Warehouse for Energy Operations Intelligence

**โปรเจกต์ personal — สร้าง Data Warehouse และ Dashboard สำหรับวิเคราะห์อุตสาหกรรมพลังงานไทย**

---

## 1. เป้าหมายโปรเจกต์

ทำความเข้าใจว่าผู้บริหารแต่ละฝ่ายต้องการมุมมองด้านไหนในการตัดสินใจ (Finance / Operations / Investor) แล้วออกแบบ Enterprise Data Warehouse ที่ consolidate ข้อมูลจากหลาย business function ให้เป็น common data model เดียว พร้อมสร้าง dashboard สื่อสาร insight เชิงกลยุทธ์

**เหตุผลที่เลือกทำโปรเจกต์นี้:**
อุตสาหกรรมพลังงานไทยกำลังลงทุนด้าน digital/data infrastructure ต่อเนื่อง สิ่งเหล่านี้ต้องพึ่งพาโครงสร้างข้อมูลที่มีคุณภาพเป็นฐานราก จึงเลือกทำโปรเจกต์ที่เน้นสร้าง Enterprise Data Warehouse/Data Mart ที่ถูกต้องตามหลักการ มากกว่าการทำ dashboard สวย ๆ เพียงอย่างเดียว

---

## 2. สถาปัตยกรรม

```
Annual Reports (56-1) ──┬── Finance ────────┐
                         └── Operations ─────┤
                                             │
SET Market Data ─────────────────────────────┼── ETL / Data Quality
Government Reference Data ───────────────────┘   (DMF / EPPO / DOEB)
                     │
                     ▼
      Enterprise Data Warehouse (BigQuery)
                     │
      ┌──────────────┼───────────────────┬──────────────┐
      │              │                   │              │
 Finance Mart   Operations Mart   Investor Perf. Mart  Reference Mart
                                                        (ไม่ใช่ business mart)
                     │
                     ▼
           Executive Dashboard (Looker Studio)
```

---

## 3. ขอบเขตบริษัท (Company Scope)

5 บริษัทพลังงานไทย ครอบคลุม value chain upstream–downstream:

| บริษัท | ตำแหน่งใน value chain |
|---|---|
| **PTTEP** | Upstream (E&P) |
| **PTT** | Integrated (upstream–downstream) |
| **TOP** | Downstream (Refining) |
| **BCP** | Integrated (small) |
| **OR** | Downstream (Retail/Marketing) |

---

## 4. Data Marts

### 4.1 Finance Mart
| Metric | สูตรคำนวณ | หมายเหตุ |
|---|---|---|
| Revenue | ตามรายงาน 56-1 | — |
| EBITDA | Net Income + Tax + Interest + D&A | มักไม่ report ตรง ๆ ต้องคำนวณเอง |
| EBITDA Margin | EBITDA / Revenue | — |
| CAPEX/Revenue Ratio | CAPEX / Revenue | อธิบายได้ว่าทำไม upstream (PTTEP) สูงกว่า downstream |

### 4.2 Operations Mart
| Metric | สูตรคำนวณ | หมายเหตุ |
|---|---|---|
| Production Volume | ตามรายงาน แปลงหน่วยเป็น BOE | ต้องมี unit conversion logic ชัดเจน (barrels/BOE/mmscfd) |
| Reserve Life Index | Reserves / Production | ต้องระวังเรื่อง reserve restatement ข้ามปี |

*Grain: รายปี/บริษัท (ไม่ใช่รายไตรมาส/รายโครงการ — ข้อจำกัดที่ต้องยอมรับเพราะดึงจาก annual report)*

### 4.3 Investor Performance Mart
| Metric | สูตรคำนวณ | หมายเหตุ |
|---|---|---|
| Dividend Yield | Dividend per Share / Price per Share | — |
| Market Cap | ตาม SET | — |
| P/E Ratio | ตาม SET | — |

### 4.4 Reference Mart (ไม่ใช่ business mart)
| ข้อมูล | แหล่ง | ใช้ทำอะไร |
|---|---|---|
| Thailand Total Production | DMF | คำนวณ Market Share ของแต่ละบริษัท |
| Energy Demand/Consumption | EPPO | เทียบ industry trend |
| Reference Crude Price | EIA | คำนวณ realized price |

⚠️ Market Share ต้องคำนวณจาก production volume บริษัท ÷ total national production **ปีเดียวกัน** — ระวัง mismatch ปีบัญชี

---

## 5. Conformed Dimensions

- **dim_company** — บริษัท, sector, value chain position
- **dim_date** — ปี (มีผลต่อ fiscal year alignment ข้ามบริษัท)
- **dim_energy_segment** — แบ่งตาม upstream/midstream/downstream หรือ fuel type

---

## 6. แหล่งข้อมูล

| แหล่ง | ใช้สำหรับ | ประเภท |
|---|---|---|
| 56-1 One Report / Annual Report (แต่ละบริษัท) | Finance, Operations mart | Public PDF |
| SET (settrade.com) / yfinance | Investor Performance mart | Public |
| DMF (กรมเชื้อเพลิงธรรมชาติ) | Reference mart | Public |
| EPPO (สนพ.) | Reference mart | Public |
| EIA International | Reference mart (ราคาน้ำมันดิบอ้างอิง) | Public |

ทั้งหมดเป็นข้อมูลสาธารณะ ตัวเลขจริง — ไม่ใช้ synthetic data

---

## 7. Tech Stack

- **Data Warehouse:** BigQuery
- **BI/Dashboard:** Looker Studio
- เหตุผล: ฟรี, web-based ใช้ได้บน Mac ปกติ (เลี่ยงปัญหา Power BI/TIBCO Spotfire ที่เป็น Windows-only), GCP เข้าถึงง่าย

---

## 8. Deliverables (6 ส่วน)

1. **Requirement-gathering document** — จำลองการคุยกับ stakeholder (Finance, Operations, Investor Relations) → สรุปเป็น business requirement ก่อนออกแบบ data model
2. **Star schema + conformed dimensions** — เอกสาร data dictionary
3. **ETL pipeline** — ดึงข้อมูลจาก annual report (PDF) และตลาดหลักทรัพย์ → โหลดเข้า BigQuery
4. **Data quality assessment** — เทียบตัวเลขข้ามบริษัท/ข้ามปี (หน่วยไม่ตรงกัน, ปีบัญชีไม่ตรงกัน, ตัวเลข restate)
5. **Looker Studio dashboard** — พร้อม insight narrative (เช่น cost efficiency ranking, market share trend)
6. **Architecture/best-practice documentation**

---

## 9. สถานะปัจจุบัน

**ความคืบหน้า:**
- ✅ Deliverable #1-4 เสร็จสมบูรณ์ — รวมถึง ETL ที่มีข้อมูลจริง verify ครบ 5 บริษัท (PTTEP, PTT, TOP, BCP, OR) × 3 ปี (2023-2025) จากรายงาน 56-1 One Report จริงของแต่ละบริษัท, โหลดเข้า BigQuery จริงครบ 7 table
- ✅ Deliverable #5 (Looker Studio dashboard) เสร็จสมบูรณ์ 3 หน้า (Overview, Deep-dive, Data Quality) — เชื่อม BigQuery จริง ไม่มี placeholder
- ✅ Deliverable #6 (documentation) เสร็จสมบูรณ์

**ผลลัพธ์ที่ยืนยันแล้วจากข้อมูลจริง (ดูรายละเอียดใน 04_Data_Quality_Assessment.md):**
- Margin เรียงตาม value chain position ชัดเจน: PTTEP (upstream) 71.9% → PTT (integrated ใหญ่) 14.9% → TOP (downstream) 7.2% → BCP (integrated เล็ก) 5.7% → OR (retail) 3.4%
- ไม่พบ restatement เลยระหว่างรายงานปีต่อเนื่องของทั้ง 5 บริษัท (เช็คละเอียดถึงตัวเลขย่อยของ CAPEX) — บันทึกเป็น table `data_quality_restatement_checks` ใน BigQuery จริง (6/6 pass)
- พบ tax expense ผิดปกติของ BCP ปี 2024 (effective rate ~80.6%) — บันทึกเป็น known anomaly ไม่ได้พยายามหาเหตุผลมากลบ (table `data_quality_anomalies`)