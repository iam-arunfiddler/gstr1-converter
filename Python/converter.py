import csv
import json
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def format_decimal(value):
    if value == 0:
        return 0
    return int(value.quantize(Decimal('1.'), rounding=ROUND_HALF_UP))

def get_pos_code(state_name):
    pos_mapping = {
        "UTTAR PRADESH": "09", "BIHAR": "10", "SIKKIM": "11", "ARUNACHAL PRADESH": "12",
        "NAGALAND": "13", "MANIPUR": "14", "MIZORAM": "15", "TRIPURA": "16",
        "MEGHALAYA": "17", "ASSAM": "18", "WEST BENGAL": "19", "JHARKHAND": "20",
        "ODISHA": "21", "CHHATTISGARH": "22", "MADHYA PRADESH": "23", "GUJARAT": "24",
        "DAMAN & DIU": "25", "DADRA & NAGAR HAVELI & DAMAN & DIU": "26", "MAHARASHTRA": "27",
        "KARNATAKA": "29", "GOA": "30", "LAKSHDWEEP": "31", "KERALA": "32",
        "TAMIL NADU": "33", "PUDUCHERRY": "34", "ANDAMAN & NICOBAR ISLANDS": "35",
        "TELANGANA": "36", "ANDHRA PRADESH": "37", "LADAKH": "38", "OTHER TERRITORY": "97"
    }
    return pos_mapping.get(state_name.upper(), "97")

def csv_to_json(csv_file_path, fp):
    data = {
        "gstin": "",
        "fp": fp,
        "version": "GST3.1.6",
        "hash": "hash",
        "b2cs": [],
        "supeco": {
            "clttx": []
        }
    }
    
    b2cs_data = defaultdict(lambda: defaultdict(Decimal))
    supeco_data = defaultdict(lambda: defaultdict(Decimal))
    
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            # Extract GSTIN
            data["gstin"] = row["Seller Gstin"]
            
            # Skip rows with zero or empty taxable value
            txval = Decimal(row["Tax Exclusive Gross"] or "0")
            if txval <= 0:
                continue
            
            # Process B2CS data
            pos = get_pos_code(row["Ship To State"])
            sply_ty = "INTRA" if pos == "33" else "INTER"
            
            # Calculate tax rate and skip if 0%
            if sply_ty == "INTER":
                igst_rate = Decimal(row["Igst Rate"] or "0")
                if igst_rate <= 0:
                    continue
                rt = int(igst_rate * 100)
            else:
                cgst_rate = Decimal(row["Cgst Rate"] or "0")
                if cgst_rate <= 0:
                    continue
                rt = int(cgst_rate * 200)  # CGST + SGST = Total rate
            
            key = (sply_ty, rt, "OE", pos)
            b2cs_data[key]["txval"] += txval
            
            if sply_ty == "INTER":
                iamt = Decimal(row["Igst Tax"] or "0") + Decimal(row["Shipping Igst Tax"] or "0")
                b2cs_data[key]["iamt"] += iamt
            else:
                camt = Decimal(row["Cgst Tax"] or "0") + Decimal(row["Shipping Cgst Tax"] or "0")
                samt = Decimal(row["Sgst Tax"] or "0") + Decimal(row["Shipping Sgst Tax"] or "0")
                b2cs_data[key]["camt"] += camt
                b2cs_data[key]["samt"] += samt
            
            b2cs_data[key]["csamt"] += Decimal(row.get("Compensatory Cess Tax", "0") or "0")
            
            # Process SUPECO data only if there's actual tax
            etin = "33AAICA3918J1C0"  # Static ETIN
            invoice_amount = Decimal(row["Invoice Amount"] or "0")
            
            if invoice_amount > 0:
                supeco_data[etin]["suppval"] += invoice_amount
                
                if sply_ty == "INTER":
                    supeco_data[etin]["igst"] += iamt
                else:
                    supeco_data[etin]["cgst"] += camt
                    supeco_data[etin]["sgst"] += samt
                
                supeco_data[etin]["cess"] += Decimal(row.get("Compensatory Cess Tax", "0") or "0")
    
    # Populate B2CS data - only include entries with meaningful values
    for key, value in b2cs_data.items():
        if value["txval"] <= 0:  # Skip entries with no taxable value
            continue
            
        entry = {
            "sply_ty": key[0],
            "rt": key[1],
            "typ": key[2],
            "pos": key[3],
            "txval": round(value["txval"], 2),
            "csamt": format_decimal(value["csamt"])
        }
        
        if key[0] == "INTER":
            entry["iamt"] = format_decimal(value["iamt"])
        else:
            entry["camt"] = format_decimal(value["camt"])
            entry["samt"] = format_decimal(value["samt"])
        
        data["b2cs"].append(entry)
    
    # Populate SUPECO data - only include entries with meaningful values
    for etin, value in supeco_data.items():
        if value["suppval"] <= 0:  # Skip entries with no supply value
            continue
            
        entry = {
            "etin": etin,
            "suppval": round(value["suppval"], 2),
            "igst": format_decimal(value["igst"]),
            "cgst": format_decimal(value["cgst"]),
            "sgst": format_decimal(value["sgst"]),
            "cess": format_decimal(value["cess"]),
            "flag": "N"
        }
        data["supeco"]["clttx"].append(entry)
    
    return data

# Get filing period from user
gstin = input("Enter your GSTIN: ")
fp = input("Enter the filing period (MMYYYY): ")

# Input and output file paths
input_file = "input.csv"
output_file = f"GSTR1_returns_{gstin}_monthly_{fp}.json"

try:
    # Convert CSV to JSON
    json_data = csv_to_json(input_file, fp)
    
    # Write JSON to file
    with open(output_file, "w") as json_file:
        json.dump(json_data, json_file, indent=2, default=decimal_default)
    
    print(f"Conversion complete. JSON file saved as {output_file}")
    
    # Display the contents of the output JSON file
    print("\nContents of output JSON file:")
    with open(output_file, 'r') as f:
        print(f.read())
        
except FileNotFoundError:
    print(f"Error: Could not find the input file '{input_file}'. Please make sure it exists in the same directory.")
except Exception as e:
    print(f"Error during conversion: {str(e)}")
