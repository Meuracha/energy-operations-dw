# Deliverable #2: Star Schema + Conformed Dimensions

**โปรเจกต์:** Enterprise Data Warehouse for Energy Operations Intelligence

---

## หลักการออกแบบ

ใช้ **Kimball Bus Architecture** — สาม business mart (Finance, Operations, Investor Performance) ใช้ **conformed dimensions ชุดเดียวกัน** เพื่อให้ query ข้าม mart ได้โดยไม่ต้องแปลงข้อมูล ส่วน Reference data (DMF/EPPO/EIA) แยกเป็น fact ต่างหากที่เชื่อมผ่าน dimension เดียวกัน ไม่ใช่ mart เท่าเทียมกับ 3 mart หลัก

---

## 1. Conformed Dimensions

### dim_company
| Column | Type | หมายเหตุ |
|---|---|---|
| company_id (PK) | INT | |
| company_name | STRING | |
| ticker | STRING | เช่น PTTEP.BK — ใช้ join กับ yfinance |
| value_chain_position | STRING | Upstream / Downstream / Integrated |
| listing_market | STRING | SET |

### dim_date
| Column | Type | หมายเหตุ |
|---|---|---|
| date_id (PK) | DATE | ใช้ grain วันสำหรับราคาหุ้น |
| year | INT | ใช้ grain ปีสำหรับ fact การเงิน/operations |
| fiscal_year_flag | BOOL | เผื่อบริษัทที่ fiscal year ไม่ตรงปีปฏิทิน (ส่วนใหญ่ไทยใช้ปีปฏิทิน แต่ต้องเช็คทุกบริษัท) |

### dim_energy_segment
| Column | Type | หมายเหตุ |
|---|---|---|
| segment_id (PK) | INT | |
| segment_name | STRING | Crude Oil / Natural Gas / Refined Products |
| used_for | STRING | ระบุว่าใช้ในบริบท production หรือ consumption — ป้องกันความสับสนตามที่เคยพูดถึงเรื่องชื่อ mart กำกวม |

---

## 2. Fact Tables

### fact_finance_annual
*Grain: 1 แถว = 1 บริษัท × 1 ปี*

| Column | มาจาก | คำนวณ/ดิบ |
|---|---|---|
| company_id (FK) | dim_company | |
| year (FK) | dim_date | |
| revenue | 56-1 | ดิบ |
| net_income | 56-1 | ดิบ |
| tax_expense | 56-1 | ดิบ |
| interest_expense | 56-1 | ดิบ |
| depreciation_amortization | 56-1 | ดิบ |
| ebitda | คำนวณ | net_income + tax + interest + D&A |
| capex | 56-1 | ดิบ |
| opex | 56-1 | ดิบ |
| report_name | derived | เช่น "PTTEP 56-1 One Report 2024" — ใช้แสดงในตาราง Source Documents หน้า 2 |
| document_type | derived | เช่น "56-1 One Report" — คงที่ทุกแถวในโปรเจกต์นี้ |
| source | derived | ชื่อบริษัทผู้เผยแพร่รายงาน (= company_id) |
| report_url | 56-1 | URL ของรายงาน — สำหรับ PTTEP เป็น direct link ถึง PDF, สำหรับ PTT/TOP/BCP/OR เป็น URL หน้า investor relations (ยังไม่มี direct PDF link เพราะต้องกรอกอีเมล/nav ผ่านเมนู) |

### fact_operations_annual
*Grain: 1 แถว = 1 บริษัท × 1 ปี × 1 energy_segment*

⚠️ **แก้ไขจากดีไซน์เดิม (หลังตรวจสอบข้อมูล DMF จริง):** DMF เผยแพร่ข้อมูลระดับ **แหล่งผลิต (field)** เช่น เอราวัณ บงกช สิริกิติ์ อาทิตย์ — ไม่ใช่ระดับบริษัทโดยตรง และแทบทุกแหล่งผลิตหลักในไทยดำเนินการโดย **PTTEP บริษัทเดียว** (ดู `reference_data/field_to_company_mapping.csv`) ส่วน TOP/BCP/OR เป็นธุรกิจ downstream (กลั่น/ค้าปลีก) ไม่ได้ผลิตปิโตรเลียมในประเทศเอง — ดังนั้น `production_volume_dmf` จะมีค่าเฉพาะแถวของ **PTTEP** เท่านั้น บริษัทอื่นเป็น `NULL` โดยตั้งใจ ไม่ใช่ข้อมูลขาดหาย

| Column | มาจาก | หมายเหตุ |
|---|---|---|
| company_id (FK) | dim_company | |
| year (FK) | dim_date | |
| segment_id (FK) | dim_energy_segment | |
| production_volume_boe | 56-1 (แปลงหน่วย) | ใช้ assumption 1 BOE ≈ 6,000 scf ตามที่ระบุใน Deliverable #1 |
| production_volume_dmf | DMF (aggregate จากระดับ field ผ่าน field_to_company_mapping) | **มีค่าเฉพาะ PTTEP** — NULL สำหรับ TOP/BCP/OR โดยตั้งใจ |
| reserves_1p / 2p / 3p | 56-1 | |
| data_quality_flag | คำนวณ | มีค่าเฉพาะแถวที่มี production_volume_dmf ให้เทียบ (คือ PTTEP เท่านั้น) |

### fact_investor_daily
*Grain: 1 แถว = 1 บริษัท × 1 วัน*

| Column | มาจาก |
|---|---|
| company_id (FK) | dim_company |
| date_id (FK) | dim_date |
| close_price | yfinance |
| volume | yfinance |

### fact_investor_annual
*Grain: 1 แถว = 1 บริษัท × 1 ปี (สรุปจาก daily + ข้อมูลรายปี)*

| Column | มาจาก |
|---|---|
| company_id (FK) | dim_company |
| year (FK) | dim_date |
| dividend_per_share | 56-1 / yfinance |
| shares_outstanding | 56-1 |
| yearend_close_price | คำนวณจาก fact_investor_daily |
| market_cap | คำนวณ = shares_outstanding × yearend_close_price |
| pe_ratio | คำนวณ = yearend_close_price / (net_income / shares_outstanding) |

### fact_reference_annual (Reference Mart — ไม่ใช่ business mart)
*Grain: 1 แถว = 1 ปี × 1 energy_segment*

| Column | มาจาก |
|---|---|
| year (FK) | dim_date |
| segment_id (FK) | dim_energy_segment |
| national_production | DMF / EPPO |
| national_consumption | EPPO |
| reference_crude_price | EIA International |

---

## 3. ความสัมพันธ์ระหว่าง Mart (ตอบคำถาม "join กันยังไง" ที่เคยกังวลไว้)

```
                    dim_company ── dim_date ── dim_energy_segment
                       │              │               │
        ┌──────────────┼──────────────┼───────────────┤
        │              │              │               │
fact_finance    fact_operations  fact_investor   fact_reference
   _annual         _annual         (daily+annual)    _annual
```

**สำคัญ:** ไม่มี fact ไหน join ตรงกับ fact อื่นโดยตรง — ทุก fact เชื่อมกันผ่าน conformed dimension เท่านั้น เช่น การคำนวณ Market Share ทำโดย:
```
market_share = fact_operations_annual.production_volume_boe (company_id=PTTEP)
              ÷ fact_reference_annual.national_production (segment_id เดียวกัน, year เดียวกัน)
```
ไม่ใช่การ join fact ตรง ๆ แต่เป็นการ query สอง fact แยกกันแล้วหารในชั้น BI/analysis

---

## 4. Data Quality Design ที่ฝังอยู่ใน schema

- `fact_operations_annual` เก็บตัวเลขจาก **สองแหล่ง (56-1 vs DMF)** คู่กันในแถวเดียว พร้อม flag อัตโนมัติ — ทำให้ data quality assessment (Deliverable #4) ดึงมาใช้ได้ทันทีโดยไม่ต้องออกแบบ table เพิ่ม
- `source_document_url` ใน fact_finance_annual ทำให้ตรวจสอบย้อนกลับไปต้นฉบับได้เสมอ — ตอบโจทย์เรื่องการประเมินความถูกต้องและความน่าเชื่อถือของแหล่งข้อมูล

---

## 5. จุดที่ยังต้อง validate ตอนทำ ETL จริง

- ต้องเช็คว่าทุกบริษัทใช้ fiscal yearตรงกับปีปฏิทินจริงหรือไม่ (ไทยส่วนใหญ่ตรง แต่ต้องยืนยัน)
- Threshold สำหรับ `data_quality_flag` (เริ่มที่ 5% แล้วปรับตามข้อมูลจริงที่เจอ)

---

## 6. Dashboard Support Tables — เพิ่มหลัง Deliverable #5 (ไม่ได้อยู่ใน design เดิม)

ระหว่างสร้าง Looker Studio จริง พบว่าหน้า "Data Quality" ต้องการ table รองรับที่ไม่ได้ออกแบบไว้ตั้งแต่แรก (ตอนแรกวางแผนให้เป็น static/verify ด้วยมือ) — สร้างเป็น 3 table เล็กแยกจาก fact table หลัก เพราะเป็นข้อมูล static ที่ update ไม่บ่อย ไม่คุ้มจะรวมเข้า schema หลัก

### data_quality_restatement_checks
*Grain: 1 แถว = 1 การเปรียบเทียบตัวเลข 1 metric ระหว่างรายงาน 2 ฉบับ*

| Column | Type | หมายเหตุ |
|---|---|---|
| company_id | STRING | |
| metric_name | STRING | เช่น "Revenue 2024" |
| report_a_value | FLOAT | ค่าจากรายงานฉบับเก่ากว่า |
| report_b_value | FLOAT | ค่าจากรายงานฉบับใหม่กว่า |
| unit | STRING | "USD million" หรือ "THB" — จำเป็นเพราะแต่ละบริษัทรายงานหน่วยไม่เหมือนกัน |
| match_status | STRING | "Pass" / "Fail" |

### data_quality_anomalies
*Grain: 1 แถว = 1 anomaly ที่ flag ไว้*

| Column | Type | หมายเหตุ |
|---|---|---|
| company_id | STRING | |
| metric_name | STRING | |
| description | STRING | คำอธิบาย + ตัวเลขเปรียบเทียบกับค่าปกติ |
| severity | STRING | "Warning" / "Critical" |
| status | STRING | "Under review" / "Resolved" |

### currency_conversion_rates
*Grain: 1 แถว = 1 ปี*

| Column | Type | หมายเหตุ |
|---|---|---|
| year | INT | |
| usd_thb_rate | FLOAT | อัตราแลกเปลี่ยนเฉลี่ยรายปี |
| source | STRING | แหล่งอ้างอิง (ต้อง cross-verify อย่างน้อย 2 แหล่งก่อนใช้) |

**ทั้ง 3 table นี้เป็น static snapshot ที่ verify ด้วยมือ ไม่ใช่ automated pipeline** — ถ้าเพิ่มข้อมูลปีใหม่ในอนาคต ต้องทำ restatement check ซ้ำด้วยมือแล้วเติมแถวเอง ไม่มี job ที่รันตรวจสอบอัตโนมัติ (ยกเว้น PTTEP ที่มี `data_quality_flag` อัตโนมัติใน fact table หลักผ่าน DMF cross-check)

---

## 7. Next Step

→ เริ่ม **ETL Pipeline** (Deliverable #3): ดึงข้อมูลจริงจากแต่ละแหล่งตาม schema นี้ เริ่มจากแหล่งที่ง่ายสุดก่อน (yfinance → EPPO/DMF → 56-1 PDF)