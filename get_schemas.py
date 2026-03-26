import json
import os
import glob

data_dir = "data/sap-o2c-data"
folders = ["sales_order_headers", "outbound_delivery_headers", "billing_document_headers", "journal_entry_items_accounts_receivable"]

with open("schema_out.txt", "w") as out:
    for f in folders:
        pat = os.path.join(data_dir, f, "*.jsonl")
        files = glob.glob(pat)
        if files:
            with open(files[0]) as file:
                line = file.readline()
                if line:
                    out.write(f"{f}: {list(json.loads(line).keys())}\n")
