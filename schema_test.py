import json
import os
import glob

data_dir = "data/sap-o2c-data"
folders = ["sales_order_headers", "sales_order_items", "outbound_delivery_headers", "outbound_delivery_items", "billing_document_headers", "billing_document_items", "journal_entry_items_accounts_receivable"]

for f in folders:
    pat = os.path.join(data_dir, f, "*.jsonl")
    files = glob.glob(pat)
    if files:
        with open(files[0]) as file:
            line = file.readline()
            if line:
                print(f"{f}:", list(json.loads(line).keys()))
    else:
        print(f"{f}: NO FILES")
