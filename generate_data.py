"""
Generate a simulated e-commerce traffic dataset (2025) -> ecommerce_data.csv

Each row = one day x traffic channel x device with funnel counts:
visitors -> product_views -> add_to_cart -> purchases (+ revenue).
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(7)

dates = pd.date_range("2025-01-01", "2025-12-31", freq="D")
channels = {  # base daily visitors, view rate, cart rate, purchase rate (of carts)
    "Organic Search": (1200, 0.62, 0.20, 0.34),
    "Paid Ads":       (900,  0.55, 0.17, 0.28),
    "Social Media":   (1000, 0.50, 0.14, 0.24),
    "Email":          (350,  0.72, 0.28, 0.45),
    "Direct":         (600,  0.70, 0.26, 0.42),
}
devices = {  # traffic share, conversion multiplier
    "Mobile":  (0.62, 0.85),
    "Desktop": (0.31, 1.15),
    "Tablet":  (0.07, 1.00),
}
# month effect on traffic and purchase propensity (festive Oct-Dec, sale in Jan)
month_traffic = {1: 1.00, 2: 0.92, 3: 0.95, 4: 0.97, 5: 1.00, 6: 0.93,
                 7: 0.95, 8: 1.02, 9: 1.05, 10: 1.30, 11: 1.45, 12: 1.35}
month_conv = {1: 1.05, 2: 0.95, 3: 0.97, 4: 0.98, 5: 1.00, 6: 0.94,
              7: 0.95, 8: 1.00, 9: 1.03, 10: 1.18, 11: 1.28, 12: 1.20}

rows = []
for d in dates:
    wk = 1.12 if d.dayofweek >= 5 else 1.0          # weekend traffic bump
    for ch, (base, vr, cr, pr) in channels.items():
        for dev, (share, mult) in devices.items():
            lam = base * share * month_traffic[d.month] * wk
            visitors = max(int(rng.poisson(lam)), 1)
            views = rng.binomial(visitors, min(vr * rng.normal(1, .03), .95))
            carts = rng.binomial(views, min(cr * rng.normal(1, .05), .9))
            p = min(pr * mult * month_conv[d.month] * rng.normal(1, .05), .95)
            purchases = rng.binomial(carts, p)
            aov = rng.normal(2400 if dev != "Desktop" else 3100, 250)
            revenue = round(float(purchases * max(aov, 500)), 2)
            rows.append([d.date(), ch, dev, visitors, views, carts, purchases, revenue])

df = pd.DataFrame(rows, columns=["date", "channel", "device", "visitors",
                                 "product_views", "add_to_cart", "purchases", "revenue"])
df.to_csv("ecommerce_data.csv", index=False)
print(f"ecommerce_data.csv created: {df.shape[0]} rows")
print(df.head())
