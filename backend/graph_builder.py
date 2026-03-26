import pandas as pd
import networkx as nx
import sqlite3
import os
import glob

class GraphDataManager:
    def __init__(self, data_dir="data/sap-o2c-data"):
        self.data_dir = data_dir
        self.G = nx.DiGraph()
        self.db_conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.dfs = {}
        
    def load_data(self):
        """Loads JSONL files into Pandas, NetworkX, and SQLite"""
        print("Loading sap-o2c-data into Pandas and SQLite...")
        if not os.path.exists(self.data_dir):
            print(f"Data directory {self.data_dir} not found.")
            return

        for folder in os.listdir(self.data_dir):
            folder_path = os.path.join(self.data_dir, folder)
            if os.path.isdir(folder_path):
                # find first jsonl file
                files = glob.glob(os.path.join(folder_path, "*.jsonl"))
                if files:
                    try:
                        df = pd.read_json(files[0], lines=True)
                        self.dfs[folder] = df
                        df.to_sql(folder, self.db_conn, index=False, if_exists="replace")
                        print(f"Loaded {folder} with {len(df)} rows.")
                    except Exception as e:
                        print(f"Failed to load {folder}: {e}")

        # Build Graph
        print("Building Network Graph...")
        self._build_graph()

    def _build_graph(self):
        """Specific modeling for SAP O2C items and headers"""
        # Limit to the first N nodes of each type so the browser doesn't freeze with huge datasets
        MAX_NODES = 50 
        
        # 1. Sales Orders
        if "sales_order_headers" in self.dfs:
            for _, r in self.dfs["sales_order_headers"].head(MAX_NODES).iterrows():
                so = str(r.get("salesOrder", ""))
                cust = str(r.get("soldToParty", ""))
                if so:
                    self.G.add_node(f"SO_{so}", label=f"Sales Order\n{so}", group="order", color="#a78bfa")
                if cust:
                    self.G.add_node(f"CUST_{cust}", label=f"Customer\n{cust}", group="customer", color="#facc15")
                if so and cust:
                    self.G.add_edge(f"CUST_{cust}", f"SO_{so}", label="places")
                
        # 2. Outbound Deliveries
        if "outbound_delivery_items" in self.dfs:
            for _, r in self.dfs["outbound_delivery_items"].head(MAX_NODES).iterrows():
                del_id = str(r.get("deliveryDocument", ""))
                so_id = str(r.get("referenceSDDocument", ""))
                if del_id:
                    self.G.add_node(f"DEL_{del_id}", label=f"Delivery\n{del_id}", group="delivery", color="#38bdf8")
                if so_id and del_id:
                    # we only connect if SO exists in graph to avoid floating nodes
                    if f"SO_{so_id}" in self.G.nodes:
                        self.G.add_edge(f"SO_{so_id}", f"DEL_{del_id}", label="fulfilled by")
                    
        # 3. Billing Documents
        if "billing_document_items" in self.dfs:
            for _, r in self.dfs["billing_document_items"].head(MAX_NODES).iterrows():
                bill_id = str(r.get("billingDocument", ""))
                del_id = str(r.get("referenceSDDocument", "")) 
                if bill_id:
                    self.G.add_node(f"INV_{bill_id}", label=f"Invoice\n{bill_id}", group="invoice", color="#f472b6")
                if bill_id and del_id:
                    if f"DEL_{del_id}" in self.G.nodes:
                        self.G.add_edge(f"DEL_{del_id}", f"INV_{bill_id}", label="invoiced by")
                        
        # 4. Payments (Journal Entries)
        if "journal_entry_items_accounts_receivable" in self.dfs:
            for _, r in self.dfs["journal_entry_items_accounts_receivable"].head(MAX_NODES).iterrows():
                je_id = str(r.get("accountingDocument", ""))
                ref_id = str(r.get("referenceDocument", "")) # usually invoice
                if je_id:
                    self.G.add_node(f"JE_{je_id}", label=f"Journal\n{je_id}", group="payment", color="#4ade80")
                if ref_id and je_id: 
                    # Ref id can be missing leading zeros, but we try direct match
                    if f"INV_{ref_id}" in self.G.nodes:
                        self.G.add_edge(f"INV_{ref_id}", f"JE_{je_id}", label="paid via")

    def get_graph_data(self):
        nodes = []
        for n, data in self.G.nodes(data=True):
            nodes.append({"id": n, "label": data.get("label", n), "color": data.get("color", "#ccc")})
            
        edges = []
        for u, v, data in self.G.edges(data=True):
            edges.append({"from": u, "to": v, "label": data.get("label", "")})
            
        return {"nodes": nodes, "edges": edges}

# Singleton instance
data_manager = GraphDataManager()
