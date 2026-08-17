# ETL Pipeline — Deliverable #3

## สถานะ

✅ **เสร็จสมบูรณ์** — ข้อมูลจริง verify ครบทั้ง 5 บริษัท × 3 ปี (2023-2025) = 15 data points ใน `data/raw/manual_entry_verified.csv`, โหลดเข้า BigQuery จริงครบ 7 table

| ส่วน | สถานะ |
|---|---|
| Investor data (yfinance) | ✅ ดึงจริงสำเร็จ 8,720 แถว |
| EIA crude price (Brent) | ✅ ดึงจริงสำเร็จ 2,047 แถว |
| EPPO national energy | ✅ ดึงไฟล์จริงสำเร็จ (ต้อง inspect encoding/columns ก่อนใช้คำนวณต่อ) |
| DMF company production | ✅ ดึงผ่าน CKAN API สำเร็จ |
| Finance/Operations (56-1) | ✅ verify ด้วยมือจากรายงาน 56-1 จริงของทุกบริษัท ครบทุกปี |
| Transform → BigQuery | ✅ โหลดครบ 7 table (`fact_finance_operations_annual`, `fact_investor_daily`, `fact_investor_annual_yf_supplement`, `fact_reference_crude_price`, `data_quality_restatement_checks`, `data_quality_anomalies`, `currency_conversion_rates`) |

`transform.py` อ่านจาก `manual_entry_verified.csv` โดยตรง (single source of truth — ไม่มีไฟล์ template แยกแล้ว)

## รันด้วย Docker

```bash
docker build -t pttep-dw-etl .

# รัน shell แบบ interactive เพื่อรันทีละสคริปต์และดู output
docker run -it --rm -v $(pwd)/data:/app/data --env-file .env pttep-dw-etl

# หรือรันสคริปต์เดียวตรง ๆ
docker run --rm -v $(pwd)/data:/app/data --env-file .env pttep-dw-etl python transform/transform.py
```

สร้างไฟล์ `.env` ก่อน:
```
EIA_API_KEY=your_key_here
```

## ลำดับการรันแบบเต็ม (extract → transform → load)

```bash
pip install -r requirements.txt

# 1. Investor data
python extract/extract_investor.py

# 2. Reference data (EIA/EPPO/DMF)
export EIA_API_KEY=your_key_here
python extract/extract_reference.py

# 3. Finance/Operations — โหลด 56-1 PDF มาก่อน แล้วรันหา candidate lines ช่วยหาตำแหน่งตัวเลข
python extract/extract_finance_operations.py path/to/report.pdf
# กรอกตัวเลขที่ verify แล้วลงใน data/raw/manual_entry_verified.csv โดยตรง

# 4. Transform
python transform/transform.py

# 5. Load เข้า BigQuery (ตั้ง PROJECT_ID ในไฟล์ load_bigquery.py และสร้าง BigQuery dataset ไว้ก่อน)
python load/load_bigquery.py
```

## ถ้าต้องการเพิ่ม/แก้ตัวเลขบริษัทในอนาคต

แก้ `data/raw/manual_entry_verified.csv` โดยตรง (เพิ่มแถวใหม่ตาม schema เดิม) แล้วรัน `python transform/transform.py` — ไม่ต้องทำอะไรเพิ่ม

## หมายเหตุ

- EIA ใช้ series **Brent (RBRTE)** ไม่ใช่ WTI — EIA ไม่มี series ราคา Dubai crude (เป็นข้อมูลของ Platts ที่เสียเงิน)
- EPPO/DMF ดึงไฟล์ raw สำเร็จแล้ว แต่การแปลงเป็น table structured (parse encoding, filter field ที่เกี่ยวข้อง) ยังไม่เสร็จสมบูรณ์ — ใช้ได้กับการดึงข้อมูลอัตโนมัติ แต่การแปลงเป็น metric สุดท้ายยังต้องทำต่อ