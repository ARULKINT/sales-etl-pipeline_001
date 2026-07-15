"""
Generates a messy sales dataset on purpose — nulls, duplicates, mixed date
formats, inconsistent text case — so the pipeline has real problems to fix.
Run once: python generate_sample_data.py
"""
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

products = ["Laptop", "Mouse", "Keyboard", "Monitor", "Webcam", "Headset", "USB Cable", "Desk Chair"]
regions = ["North", "South", "East", "West"]
customers = [f"CUST{str(i).zfill(3)}" for i in range(1, 41)]

rows = []
start_date = datetime(2024, 1, 1)

for i in range(1, 501):
    order_id = f"ORD{str(i).zfill(4)}"
    product = random.choice(products)
    # inconsistent casing on purpose
    if random.random() < 0.2:
        product = product.upper()
    elif random.random() < 0.2:
        product = product.lower()

    qty = random.randint(1, 10)
    unit_price = round(random.uniform(5, 1200), 2)

    order_date = start_date + timedelta(days=random.randint(0, 365))
    # mixed date formats on purpose
    fmt = random.choice(["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y"])
    date_str = order_date.strftime(fmt)

    customer_id = random.choice(customers)
    region = random.choice(regions)

    rows.append([order_id, date_str, product, qty, unit_price, customer_id, region])

df = pd.DataFrame(rows, columns=[
    "order_id", "order_date", "product_name", "quantity", "unit_price", "customer_id", "region"
])

# inject nulls
null_idx = np.random.choice(df.index, size=15, replace=False)
df.loc[null_idx, "customer_id"] = np.nan

null_idx2 = np.random.choice(df.index, size=10, replace=False)
df.loc[null_idx2, "quantity"] = np.nan

# inject duplicates
dupes = df.sample(8, random_state=1)
df = pd.concat([df, dupes], ignore_index=True)

# inject a few negative/zero quantities (bad data)
bad_idx = np.random.choice(df.index, size=5, replace=False)
df.loc[bad_idx, "quantity"] = -1

df.to_csv("sales_data.csv", index=False)
print(f"Generated {len(df)} rows -> sales_data.csv")
