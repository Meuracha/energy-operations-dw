# Deliverable #1: Requirement-Gathering Document

**โปรเจกต์:** Enterprise Data Warehouse for Energy Operations Intelligence

---

## วัตถุประสงค์

ก่อนออกแบบ data model ต้องเข้าใจก่อนว่า "ผู้บริหารแต่ละฝ่ายต้องการเห็นอะไร เพื่อตัดสินใจอะไร" เอกสารนี้จำลองการสัมภาษณ์ stakeholder 3 กลุ่ม แล้วแปลงเป็น business requirement และ data requirement ที่ใช้ออกแบบ schema ต่อได้จริง

---

## 1. สัมภาษณ์ Stakeholder (จำลอง)

### 1.1 CFO / Finance Team

**บทบาท:** ดูแลผลประกอบการ, การลงทุน, ต้นทุน

**สิ่งที่ต้องการเห็น:**
- แนวโน้ม Revenue, EBITDA Margin ย้อนหลังหลายปี เทียบกับคู่แข่งในอุตสาหกรรมเดียวกัน
- CAPEX/Revenue Ratio — ใช้ประเมินว่าการลงทุนหนักไปหรือเบาไปเทียบกับ peer
- คำถามเจาะจง: **"ปีที่ราคาน้ำมันดิบโลกผันผวนแรง กำไรของเราเปลี่ยนแปลงมากกว่าคู่แข่งกลุ่ม downstream แค่ไหน"**

**Pain point ที่ระบุ:** ตัวเลขจากรายงานประจำปีของแต่ละบริษัทเทียบกันตรง ๆ ไม่ได้ทันที เพราะ EBITDA ไม่ได้ report ตรงเสมอ ต้องคำนวณเองให้ method เดียวกันทุกบริษัท

### 1.2 Operations / Production Planning Team

**บทบาท:** ติดตามปริมาณการผลิต วางแผนกำลังผลิต

**สิ่งที่ต้องการเห็น:**
- ปริมาณผลิตรายปี แยกตามบริษัท เทียบสัดส่วนในภาพรวมอุตสาหกรรมไทย
- Reserve Life Index เพื่อประเมินความยั่งยืนของกำลังผลิตระยะยาว
- คำถามเจาะจง: **"ส่วนแบ่งการผลิตของบริษัทในประเทศเปลี่ยนไปยังไงในช่วง 5 ปีที่ผ่านมา"**

**Pain point ที่ระบุ:** ตัวเลขที่บริษัทรายงานเองกับตัวเลขที่หน่วยงานรัฐ (DMF) เก็บอาจไม่ตรงกันเป๊ะ ต้องมีขั้นตอนเทียบสอบก่อนเชื่อถือได้

### 1.3 Investor Relations Team

**บทบาท:** สื่อสารกับนักลงทุน/ผู้ถือหุ้น

**สิ่งที่ต้องการเห็น:**
- Dividend Yield, P/E เทียบกลุ่มอุตสาหกรรม เพื่อตอบคำถามนักลงทุนเรื่อง valuation
- แนวโน้มราคาหุ้นเทียบกับ fundamental (revenue, margin) เพื่อเช็คว่าตลาดตีราคาสอดคล้องกับผลประกอบการไหม
- คำถามเจาะจง: **"นักลงทุนควรมองบริษัทเราเป็น growth stock หรือ dividend stock เมื่อเทียบกับคู่แข่ง"**

**Pain point ที่ระบุ:** ข้อมูลราคาหุ้นเป็น real-time/daily แต่ข้อมูล fundamental เป็นรายปี — ต้อง align grain ให้เทียบกันได้อย่างมีความหมาย ไม่ใช่เอาข้อมูลคนละ frequency มาวางซ้อนกันตรง ๆ

---

## 2. สรุป Business Requirements

| Stakeholder | Business Function | คำถามหลักที่ต้องตอบได้ | ความถี่ที่ต้องการ |
|---|---|---|---|
| CFO | Finance | Margin/CAPEX เทียบ peer, sensitivity ต่อราคาน้ำมันโลก | รายปี |
| Operations | Operations | Market share, reserve sustainability | รายปี |
| Investor Relations | Investor Performance | Valuation เทียบ peer, price-fundamental alignment | รายปี (fundamental) + รายวัน (ราคาหุ้น) |

---

## 3. แปลงเป็น Data Requirements

| Business Requirement | ข้อมูลที่ต้องใช้ | แหล่ง | Grain | สถานะ |
|---|---|---|---|---|
| Margin/CAPEX เทียบ peer | Revenue, Net Income, Tax, Interest, D&A, CAPEX | 56-1 One Report | บริษัท × ปี | ✅ execute แล้ว — มีครบ 5 บริษัท × 3 ปีใน BigQuery |
| Sensitivity ต่อราคาน้ำมันโลก | Revenue/EBITDA รายปี + ราคาน้ำมันดิบอ้างอิง | 56-1 + EIA International | บริษัท × ปี | ⬜ ยังไม่ execute — ดึงราคา Brent มาได้แล้ว (2,047 แถว) แต่ยังไม่ได้ join กับ EBITDA จริง |
| Market share การผลิต | ปริมาณผลิตบริษัท + ปริมาณผลิตรวมประเทศ | 56-1 + DMF | บริษัท × ปี | ⬜ ยังไม่ execute — DMF ดึงไฟล์ raw ได้แล้วแต่ยังไม่ parse เป็นตัวเลขใช้งานได้ |
| Cross-check ความถูกต้องปริมาณผลิต | ปริมาณผลิตที่บริษัทรายงานเอง vs DMF | 56-1 + DMF | บริษัท × ปี | ⬜ ยังไม่ execute — `production_volume_dmf` ใน fact table ยังเป็น NULL ทั้งหมด |
| Valuation เทียบ peer | Dividend, Share Price, P/E | yfinance (Yahoo Finance) | บริษัท × วัน (aggregate เป็นรายปีตอนวิเคราะห์) | ✅ ดึงข้อมูลจริงสำเร็จ (8,720 แถว) แต่ยังไม่ได้ทำ dashboard หรือ analysis ต่อ |
| Reserve sustainability | Reserves (1P/2P/3P รวม), Production | 56-1 | บริษัท × ปี | ✅ มี reserves 1P ครบ PTTEP 3 ปี — 2P/3P และบริษัทอื่นยังไม่มี (นอกเหนือขอบเขต เพราะมีแค่ PTTEP ที่เป็น E&P) |

---

## 4. Insight Hypotheses ที่จะทดสอบ (จาก pain point ของแต่ละฝ่าย)

ตั้งเป็นสมมติฐานล่วงหน้า เพื่อให้ dashboard มีจุดยืนชัดเจน ไม่ใช่แค่โชว์ตัวเลข:

1. **H1 (Finance):** บริษัท upstream (PTTEP) มี earnings volatility สูงกว่าบริษัท downstream (TOP, BCP) เมื่อราคาน้ำมันดิบโลกผันผวน
   *สถานะ:* ⬜ ยังไม่ทดสอบ — ต้อง join margin กับราคา Brent ก่อน (ยังไม่ execute) พบ insight อื่นแทนระหว่างทาง คือ margin ไล่ระดับชัดตาม value chain position (PTTEP 71.9% → OR 3.4%) ซึ่งเป็นแกนหลักของ dashboard ที่ทำเสร็จแล้ว
2. **H2 (Operations):** ส่วนแบ่งการผลิตในประเทศของ PTTEP มีแนวโน้มเปลี่ยนแปลงตามการหมดอายุสัมปทานแหล่งเดิม (เช่น เอราวัณ)
   *สถานะ:* ⬜ ยังไม่ทดสอบ — ต้องมี market share data จาก DMF ที่ parse เสร็จก่อน
3. **H3 (Investor):** ราคาหุ้นกลุ่มพลังงานไทยมี correlation กับ fundamental margin ต่ำกว่าที่คาด (ตลาดอาจตีราคาจาก sentiment มากกว่าตัวเลขจริง)
   *สถานะ:* ⬜ ยังไม่ทดสอบ — มีข้อมูลราคาหุ้นแล้ว (yfinance) แต่ยังไม่ได้ทำ correlation analysis กับ margin

*หมายเหตุ: เป็นสมมติฐานตั้งต้น ต้องทดสอบกับข้อมูลจริงหลังทำ ETL แล้ว — ถ้าผลไม่ตรงสมมติฐาน ก็เป็น insight ที่น่าสนใจเหมือนกัน*

---

## 5. Assumption ที่ต้องระบุให้ชัด (จากการตรวจสอบ feasibility ก่อนหน้า)

- EBITDA คำนวณด้วยสูตรเดียวกันทุกบริษัท (Net Income + Tax + Interest + D&A) แม้บางบริษัทจะ report EBITDA เองมาให้แล้วก็ตาม — เพื่อความสอดคล้องกัน
- Production volume แปลงหน่วยเป็น BOE ด้วยอัตราแปลงมาตรฐานเดียว (1 BOE ≈ 6,000 scf) และระบุไว้ใน documentation ว่าอาจต่างจากที่แต่ละบริษัทใช้เอง
- ราคาหุ้นใช้ราคาปิดสิ้นปี (year-end close) เป็นตัวแทนเวลาเทียบกับ fundamental รายปี ไม่ใช่ราคาเฉลี่ยทั้งปี (ระบุเหตุผล + ข้อจำกัดไว้)
- Market share คำนวณจากปีปฏิทินเดียวกันระหว่างตัวเลขบริษัทกับ DMF เท่านั้น

---

## 6. Next Step

→ นำ Data Requirements ในข้อ 3 ไปออกแบบ **Star Schema + Conformed Dimensions** (Deliverable #2)