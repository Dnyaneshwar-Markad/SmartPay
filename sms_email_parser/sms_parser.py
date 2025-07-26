import re
import json
from datetime import datetime

def parse_sms(sms_text):
    patterns = [ r"debited with Rs.([\d,]+\.\d{2}) on (\d{1,2}-[A-Za-z]{3}-\d{4})", 
                r"charged Rs.([\d,]+\.\d{2}) for ([\w\s]+)\. Txn date: (\d{1,2}-[A-Za-z]{3}-\d{4})", 
                r"paid Rs.([\d,]+\.\d{2}) towards your monthly EMI on (\d{1,2}-[A-Za-z]{3}-\d{4})" 
                ]


    results = []

    for line in sms_text.split("\n"):
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                if "charged" in pattern:
                    amount, merchant, date = match.groups()
                elif "EMI" in pattern:
                    amount, date = match.groups()
                    merchant = "EMI Payment"
                else:
                    amount, date = match.groups()
                    merchant = "Bank Debit"
                
                results.append({
                    "amount": float(amount),
                    "merchant": merchant,
                    "date": datetime.strptime(date, "%d-%b-%Y").strftime("%Y-%m-%d")
                })

    return results

if __name__ == "__main__":
    with open("sample_sms.txt", "r") as file:
        sms_text = file.read()

    parsed_data = parse_sms(sms_text)

    with open("parsed_output.json", "w") as outfile:
        json.dump(parsed_data, outfile, indent=2)

    print("✅✅✅✅✅ SMS parsed successfully. Output saved to parsed_output.json")
