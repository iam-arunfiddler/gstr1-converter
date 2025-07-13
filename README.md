### GSTR1 Converter for Amazon Sellers. 

GSTR1 Converter is a command-line Python tool that converts invoice data from a CSV file into a GST-compliant JSON file, ready for upload to the GST Portal. It is specifically designed for sellers filing GSTR-1 returns in India.

Prerequisites : 
* Download the MTR of Filing month (Supports only B2C)
---------------------------

🚀 Features
----
✅ Command-line interface for easy input
✅ Reads seller invoice data from .csv
✅ Auto-detects intra/inter-state transactions
✅ Handles B2CS and SUPECO sections of GSTR-1
✅ Outputs structured .json file ready for upload
✅ Compliant with GST JSON schema GST3.1.6

-----------------

🛠 Requirements
----
Python 3.6 or higher
(Only standard libraries are used: csv, json, decimal, collections)

----------

## 📁 CSV Input Format

Make sure your input.csv contains the following headers:

  ```text
  Seller Gstin, Ship To State, Igst Rate, Cgst Rate,
  Tax Exclusive Gross, Igst Tax, Shipping Igst Tax,
  Cgst Tax, Shipping Cgst Tax, Sgst Tax, Shipping Sgst Tax,
  Compensatory Cess Tax, Invoice Amount
```
Example row:

| Seller Gstin     | Ship To State | Igst Rate | Cgst Rate | Tax Exclusive Gross | Igst Tax | Invoice Amount |
|------------------|---------------|-----------|-----------|---------------------|----------|----------------|
| 33ABCDE1234F1Z5  | Karnataka     | 0.18      | 0.09      | 10000.00            | 1800.00  | 11800.00       |

## 💻 How to Run
1. Ensure your invoice data is saved in input.csv
2. Run the script:
```bash
python gstr1_converter.py
```
3. Enter:
    * GSTIN (e.g., 33ABCDE1234F1Z5)
    * Filing period (e.g., 072024 for July 2024)
4. Output file will be generated as:
```bash
  GSTR1_returns_<GSTIN>_monthly_<MMYYYY>.json
```

⭐ Feel free to fork and submit issue if there's any improvement or bug identified.  🙌
