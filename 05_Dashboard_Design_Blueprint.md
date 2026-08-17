# Deliverable #5: Dashboard Design Blueprint

**โปรเจกต์:** Enterprise Data Warehouse for Energy Operations Intelligence
**เครื่องมือ:** Looker Studio (เชื่อมกับ BigQuery)

---

## 1. Design System

### 1.1 Color Palette

**หลักการ:** ใช้สีแบรนด์จริงของ PTTEP เป็นฐาน (ตรวจสอบจากโลโก้บริษัท) — **น้ำเงินกรมท่าเข้มเป็นสีหลัก, แดงเป็น accent** (PTT บริษัทแม่ก็ใช้คู่สีนี้เช่นกัน) แล้วให้สีบริษัทแต่ละตัวไล่เฉดจากเย็น (upstream) ไปอุ่น (retail) ซ้อนอยู่ภายใต้ brand identity เดียวกัน

**Brand identity (มาจาก PTTEP โดยตรง):**

| การใช้งาน | Hex | ที่มา |
|---|---|---|
| Primary — Header/nav bar | `#0A2F5C` (deep navy) | สีตัวอักษร "PTTEP" บนโลโก้ |
| Accent — active state, highlight | `#C8102E` (red) | สีวงกลมใน droplet ของโลโก้ |
| Logo gradient (ใช้กับ hero/cover slide เท่านั้น) | `#1B4F8C` → `#0A2F5C` | ไล่เฉดตามหยดน้ำมันในโลโก้ |

**สีบริษัท (value chain gradient, เย็น→อุ่น):**

| บริษัท | Position | Hex | ใช้ยังไง |
|---|---|---|---|
| PTTEP | Upstream | `#0A2F5C` (navy, = brand primary) | เส้น/แท่งหลักทุกกราฟที่มี PTTEP — ใช้สีเดียวกับ header เพื่อเน้นว่าเป็นเจ้าของ dashboard |
| PTT | Integrated (ใหญ่) | `#3D6FA8` (mid blue) | |
| BCP | Integrated (เล็ก) | `#5DA88F` (teal-green) | |
| TOP | Downstream | `#E8A33D` (amber) | |
| OR | Retail | `#C8102E` (red, = brand accent) | ใช้สี accent ของแบรนด์กับจุดที่ margin ต่ำสุด — สร้าง contrast ที่จำง่าย |

**สีระบบ (ไม่ผูกกับบริษัท):**

| การใช้งาน | Hex | หมายเหตุ |
|---|---|---|
| Page background | `#F5F7FA` | เทาอมฟ้าอ่อนมาก โทนเย็นเข้ากับ navy |
| Card/panel background | `#FFFFFF` | |
| Card border | `#E2E8F0` | |
| Text primary | `#0F172A` | |
| Text secondary | `#64748B` | |
| Data quality — Pass | `#15803D` (green) | |
| Data quality — Warning | `#D97706` (amber) | ใช้กับ BCP tax anomaly |
| Data quality — Fail | `#C8102E` (= brand red — สื่อว่า "ต้องดูด่วน") | |
| Reference/context line | `#94A3B8` (gray, dashed) | |

**กฎการใช้สี:** สีแดง `#C8102E` มี 2 บทบาทซ้อนกัน (brand accent + data-quality-fail + สี OR) — ใช้ได้เพราะบริบทต่างหน้ากันชัดเจน (หน้า Overview ใช้เป็นสี OR, หน้า Data Quality ใช้เป็นสถานะ) แต่**ห้ามใช้ทั้งสองความหมายในกราฟเดียวกัน** เพื่อไม่ให้สับสน

### 1.2 Typography

| ระดับ | Font | Size | Weight |
|---|---|---|---|
| Page title (บนสุดของหน้า) | Inter / Roboto | 20px | Bold |
| Section header | Inter / Roboto | 13px, uppercase, letter-spacing 0.5px | Bold |
| KPI scorecard value | Inter / Roboto | 32px | Bold |
| KPI scorecard label | Inter / Roboto | 11px, uppercase | Medium |
| Chart axis/legend | Inter / Roboto | 10-11px | Regular |
| Body/caption | Inter / Roboto | 12px | Regular |

*(Looker Studio รองรับ Google Fonts ทั้งหมดนี้โดยตรงในตัว Theme settings)*

### 1.3 Layout Grid

- Canvas ขนาด **1280 × 800px** (16:10, มาตรฐาน Looker Studio ที่ fit จอ presentation ได้พอดี)
- แบ่งเป็น grid 12 คอลัมน์ กว้างคอลัมน์ละ ~100px, gutter 16px
- Card ทุกใบ: `border-radius: 8px`, `padding: 16px`, ไม่มี drop shadow (ใช้ border บาง ๆ แทนเพื่อความ flat/clean)
- Header bar สูง 56px คงที่ทุกหน้า มีโลโก้/ชื่อโปรเจกต์ซ้าย + page navigation tabs ขวา

---

## 2. หน้า 1: Executive Overview — ✅ Built

**เป้าหมาย:** ให้ผู้บริหารเห็นภาพรวมภายใน 10 วินาทีแรก

```
┌─────────────────────────────────────────────────────────────┐
│ [Navy header bar] Energy Operations Intelligence    [Tabs]   │ 56px
├─────────────────────────────────────────────────────────────┤
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│ │ KPI Card │ │ KPI Card │ │ KPI Card │ │ KPI Card │         │ 120px
│ │ Highest  │ │ Lowest   │ │ Spread   │ │ Data     │         │
│ │ Margin   │ │ Margin   │ │ Ratio    │ │ Quality  │         │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
├───────────────────────────────┬───────────────────────────────┤
│  Card: EBITDA Margin Trend     │  Card: CAPEX/Revenue Trend     │
│  (line chart, 5 series,        │  (line chart, 5 series,        │
│   2023-2025, % axis)           │   2023-2025, % axis)           │  320px
│                                 │                                 │
├───────────────────────────────┴───────────────────────────────┤
│  Card: Company Filter (dropdown) + Value Chain Position Legend │  80px
└─────────────────────────────────────────────────────────────────┘
```

**รายละเอียด KPI Cards (4 ใบ):**
- ซ้าย: border-left 4px สีตามบริษัท (เช่น การ์ด "Highest Margin" มีแถบซ้ายสีน้ำเงิน `#1B3A5C` เพราะเป็น PTTEP)
- Layout ภายใน: label (บน, secondary text) → value ใหญ่ (กลาง) → sub-caption เทียบปีก่อน (ล่าง, ลูกศรขึ้น/ลงสีเขียว/แดง)

**Chart 1 — EBITDA Margin Trend:** line chart แบบที่ทำ mockup ไปแล้ว เส้นทึบ = PTTEP/BCP/OR (pure-play), เส้นประ = PTT/TOP (integrated) — ใช้ style เดียวกับ mockup ที่เห็นไปแล้ว

**Chart 2 — CAPEX/Revenue Trend:** เหมือน chart 1 แต่เป็นแกน CAPEX ratio — ใช้สีเดียวกันทุกบริษัท (สี company ต้อง**คงที่ทุกหน้า ทุกกราฟ**ในทั้ง dashboard)

---

## 3. หน้า 2: Company Deep-dive — ✅ Built

**เป้าหมาย:** วิเคราะห์บริษัทเดียวแบบละเอียด (มี filter ควบคุมทั้งหน้า)

```
┌─────────────────────────────────────────────────────────────┐
│ [Navy header]                              [Company Filter▾] │ 56px
├─────────────────────────────────────────────────────────────┤
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│ │ Revenue  │ │ Net Inc. │ │ EBITDA   │ │ CAPEX    │         │ 120px
│ │ 2025     │ │ 2025     │ │ Margin   │ │ /Revenue │         │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
├───────────────────────────────┬───────────────────────────────┤
│  Card: Revenue & Net Income    │  Card: Cost Structure          │
│  (combo chart — bar+line,      │  Breakdown (stacked bar:       │
│   3 years)                     │   Opex / D&A / Finance cost)   │  320px
├───────────────────────────────┴───────────────────────────────┤
│  Card: Source Document Links (table — ปี, ชื่อรายงาน, URL)     │  80px
└─────────────────────────────────────────────────────────────────┘
```

- KPI card สีแถบซ้าย**เปลี่ยนตามบริษัทที่ filter เลือก** (dynamic — ใช้ calculated field ผูกกับ CASE WHEN company_id)
- Combo chart: แท่ง = Revenue (สีบริษัท, opacity 100%), เส้น = Net Income (สีเดียวกัน แต่เป็นเส้นทึบสีเข้มกว่า)
- Cost structure stacked bar: ใช้สี**ระบบ**ไม่ใช่สีบริษัท (Opex=`#9CA3AF` เทา, D&A=`#6B7280` เทาเข้ม, Finance cost=`#D9695F` coral) เพราะเป็นการเทียบ component ภายในบริษัทเดียว ไม่ใช่เทียบข้ามบริษัท

---

## 4. หน้า 3: Data Quality — ✅ Built

**เป้าหมาย:** โชว์ความน่าเชื่อถือของข้อมูล — หน้าที่ทำให้โปรเจกต์นี้ต่างจาก dashboard ทั่วไป

```
┌─────────────────────────────────────────────────────────────┐
│ [Navy header]                                                 │ 56px
├─────────────────────────────────────────────────────────────┤
│  Card: Restatement Check Summary                               │
│  (table: บริษัท | metric | unit | status | รายงาน A | รายงาน B) │ 200px
│  แถวที่ pass = พื้นเขียวอ่อน #E8F5E9, ตัวอักษร #2E7D32          │
├─────────────────────────────────────────────────────────────┤
│  Card: Flagged Anomalies                                       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ ⚠ BCP — Tax Expense 2024                    [amber card] │ │ 180px
│  │ Effective rate ~80.6%, ปกติ 20% — ไม่พบเหตุผลชัดเจนจาก    │ │
│  │ รายงาน บันทึกเป็น known anomaly                          │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  Card: Currency Conversion Methodology                         │
│  (ตาราง: ปี | เรทเฉลี่ย USD/THB | แหล่งอ้างอิง)                │ 140px
└─────────────────────────────────────────────────────────────────┘
```

- Anomaly card: พื้นหลัง `#FFF8E1` (amber tint) กรอบ `#F9A825` ซ้าย 4px, ไอคอนเตือนสีเดียวกับกรอบ
- ตาราง restatement: ใช้ conditional formatting สีพื้นตามสถานะ (เขียว = ตรงกัน, แดง = พบ discrepancy — ในโปรเจกต์นี้ควรเป็นเขียวทั้งหมดเพราะไม่พบ restatement เลย)
- **แต่ละ card query จาก table แยกกัน** (ไม่ได้ join เป็น table เดียว): `data_quality_restatement_checks`, `data_quality_anomalies`, `currency_conversion_rates` — ดู schema เต็มใน `02_Star_Schema_Design.md` ข้อ 6

### ⚠️ เปลี่ยนจาก design เดิม: "Data Quality Score" KPI card (อยู่หน้า 1 ไม่ใช่หน้านี้)

Design เดิมวางแผนให้หน้า 1 มี KPI card ชื่อ **"Data Quality Score"** แสดงเป็นตัวเลขเดียว (เช่น "100%" หรือ "5/5") — ระหว่างสร้างจริงพบว่า**ชื่อนี้ทำให้เข้าใจผิด** เพราะสื่อว่าเป็นคะแนนรวมของทุกมิติ data quality (รวม anomaly ด้วย) ทั้งที่จริง ๆ วัดแค่ restatement check เท่านั้น

**แก้เป็น:**
```
RESTATEMENT CHECK
6 / 6 PASS
No restatement found
```
- Label เปลี่ยนจาก "DATA QUALITY SCORE" → **"RESTATEMENT CHECK"** (บอกขอบเขตชัดเจนว่าวัดอะไร)
- Caption "No restatement found" — ข้อความคงที่ ไม่ต้องคำนวณ
- **Anomaly ไม่รวมอยู่ใน metric นี้** — โชว์แยกที่หน้า Data Quality เท่านั้น เพื่อไม่ให้ "6/6 pass" กลบข้อมูลว่ามี 1 anomaly ที่ยัง under review อยู่

**สูตร calculated field:**
```
CONCAT(CAST(SUM(CASE WHEN match_status="Pass" THEN 1 ELSE 0 END) AS TEXT), " / ", CAST(COUNT(match_status) AS TEXT), " PASS")
```

---

## 5. Global Elements (ใช้ทุกหน้า)

- **Footer:** ทุกหน้ามี footer บาง ๆ สูง 24px สี `#6B7280` บอก "Data as of [refresh date] · Source: 56-1 One Report, EIA, EPPO, DMF"
- **Navigation tabs:** มุมขวาบนของ header ทุกหน้า เป็น tab **3 อัน** (Overview / Deep-dive / Data Quality) ตัวอักษรขาว, tab ที่ active มีขีดเส้นใต้สีแดง accent `#C8102E`
- **Company legend:** แถบเล็กมุมล่างซ้ายของทุกหน้าที่มีกราฟหลายบริษัท (5 สีตามข้อ 1.1) เพื่อไม่ต้องเปิด page 1 ย้อนกลับไปดู

---

## 6. Lessons Learned จากการสร้างจริง — ปัญหาที่เจอและวิธีแก้

ส่วนนี้เขียนเพิ่มหลังสร้างจริงใน Looker Studio เสร็จ บันทึกปัญหาที่เจอระหว่างทำและวิธีแก้

| ปัญหาที่เจอ | สาเหตุ | วิธีแก้ |
|---|---|---|
| YoY delta (▲▼) แสดงค่าผิดพลาดรุนแรง (เช่น -96.6% ทั้งที่ควรเป็น +0.9pp) | `LAG()` window function ไม่ได้ `PARTITION BY company_id` — ปีก่อนหน้าที่ดึงมาเป็นของบริษัทอื่นที่ปีตรงกันแทน | เพิ่ม `PARTITION BY company_id` ใน `OVER()` clause ทุกจุดที่ใช้ LAG |
| `TO_TEXT` / `COUNTIF` ไม่ทำงานใน calculated field | Looker Studio มีชุดฟังก์ชันของตัวเอง แยกจาก syntax BigQuery SQL ที่คุ้นเคย | ใช้ `CAST(...AS TEXT)` แทน `TO_TEXT`, ใช้ `SUM(CASE WHEN...THEN 1 ELSE 0 END)` แทน `COUNTIF` |
| Chart เรียงปี 2025→2024→2023 (ผิดทิศ) ทั้งที่ตั้ง sort เป็น ascending แล้ว | Field `year` ที่ใช้ sort ติด aggregation type "CTD" (Count Distinct) โดยไม่ได้ตั้งใจ — sort ด้วยค่าคงที่ ไม่ใช่ปีจริง | เปลี่ยน aggregation ของ field ที่ใช้ sort จาก CTD → MIN หรือ MAX (ไม่มีตัวเลือก "None" ให้ใน Looker Studio) |
| Margin Spread แสดงเป็น "68.52%" ทำให้เข้าใจผิดว่าเป็นสัดส่วน relative | ผลต่างระหว่างสอง % ควรเป็น percentage point (pp) ไม่ใช่ % — สื่อความหมายคนละแบบ | ต่อท้าย suffix "pp" ในสูตร CONCAT แทนการพึ่ง built-in "%" formatting ของ scorecard (ซึ่งดันรีเซ็ตทศนิยมด้วย) |
| `load_bigquery.py` โหลดได้แค่ 3 table ทั้งที่ตั้งใจให้ได้ 4+ | Script ยังชี้ไปหาไฟล์เก่า (`manual_entry_template.csv`) ที่ถูกลบไปแล้วตอนรวมเป็น single-source-of-truth CSV — skip แบบไม่ error เลยไม่รู้ตัว | เช็ค output ของ script ทุกครั้งว่า "Loaded" ครบตามจำนวน table ที่ตั้งใจ ไม่ใช่แค่ดูว่า script รันจบไม่มี error |
| Auth error ตอนรัน `load_bigquery.py` ใน Docker container | Credentials (`gcloud auth`) อยู่บนเครื่อง host ไม่ได้ mount เข้า container | รันคำสั่งที่ต้องใช้ GCP auth บนเครื่องโดยตรง (นอก container) เพราะ volume mount ทำให้ไฟล์ที่ transform.py เขียนไว้ยังเข้าถึงได้จากนอก container อยู่แล้ว |

**บทเรียนภาพรวม:** ปัญหาส่วนใหญ่ไม่ใช่ "ไม่รู้ว่าต้องทำอะไร" แต่เป็น**รายละเอียดการ implement ที่ผิดพลาดเงียบ ๆ** (silent failure) — sort ที่ดูเหมือนตั้งถูกแต่ผลลัพธ์ผิด, script ที่รันจบแต่ skip table สำคัญไปเงียบ ๆ — บทเรียนคือต้อง**ตรวจสอบผลลัพธ์จริงเทียบกับที่คาดหวังเสมอ** ไม่ใช่แค่เช็คว่า "รันได้ไม่มี error"

---

## 7. Scope สุดท้าย

Dashboard นี้ตั้งใจไว้ 3 หน้า (Overview, Deep-dive, Data Quality) — ครบและใช้งานจริงได้แล้วทั้งหมด เชื่อม BigQuery จริง ไม่มี placeholder ถือว่า Deliverable #5 ปิดจบสมบูรณ์