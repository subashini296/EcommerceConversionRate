"""
E-COMMERCE CONVERSION RATE ANALYSIS
Funnel: Visitors -> Product Views -> Add to Cart -> Purchases

Run:  python generate_data.py   (once, creates ecommerce_data.csv)
      python ecommerce_analysis.py
Outputs: conversion_rate.png, monthly_conversion.png, Sales_Funnel.png, insights.txt
"""
import json
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")

# ------------------------------------------------------------------
# 1. LOAD + CLEAN
# ------------------------------------------------------------------
df = pd.read_csv("ecommerce_data.csv", parse_dates=["date"])
df = df.drop_duplicates().dropna()
# funnel sanity: each stage cannot exceed the previous one
df = df[(df.product_views <= df.visitors) & (df.add_to_cart <= df.product_views)
        & (df.purchases <= df.add_to_cart)]
df["month"] = df["date"].dt.to_period("M")
df["month_name"] = df["date"].dt.strftime("%b")
df["week"] = df["date"].dt.to_period("W").dt.start_time
df["dow"] = df["date"].dt.day_name()
print("Rows:", len(df), "|", df["date"].min().date(), "to", df["date"].max().date())


def agg(frame):
    """Aggregate funnel counts and compute rates (in %)."""
    g = frame[["visitors", "product_views", "add_to_cart", "purchases", "revenue"]].sum()
    return pd.Series({
        **g.to_dict(),
        "view_rate": g.product_views / g.visitors * 100,
        "cart_rate": g.add_to_cart / g.product_views * 100,
        "purchase_rate": g.purchases / g.add_to_cart * 100,
        "conversion": g.purchases / g.visitors * 100,
        "aov": g.revenue / g.purchases if g.purchases else 0,
    })


total = agg(df)
by_channel = df.groupby("channel").apply(agg, include_groups=False).sort_values("conversion", ascending=False)
by_device = df.groupby("device").apply(agg, include_groups=False).sort_values("conversion", ascending=False)
monthly = df.groupby("month").apply(agg, include_groups=False)
monthly.index = monthly.index.astype(str)
weekly = df.groupby("week").apply(agg, include_groups=False)
dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
by_dow = df.groupby("dow").apply(agg, include_groups=False).reindex(dow_order)

print("\nOVERALL FUNNEL\n", total.round(2))

# ------------------------------------------------------------------
# 2. CHART: SALES FUNNEL
# ------------------------------------------------------------------
stages = ["Visitors", "Product Views", "Add to Cart", "Purchases"]
vals = [total.visitors, total.product_views, total.add_to_cart, total.purchases]
colors = ["#4C78A8", "#72B7B2", "#F58518", "#54A24B"]
fig, ax = plt.subplots(figsize=(10, 5.5))
for i, (s, v, c) in enumerate(zip(stages, vals, colors)):
    ax.barh(i, v, color=c, height=0.65)
    pct = v / vals[0] * 100
    label = f"{v:,.0f}  ({pct:.1f}% of visitors)"
    if i > 0:
        label += f"   |   -{(1 - v / vals[i - 1]) * 100:.0f}% vs previous step"
    ax.text(v + vals[0] * 0.01, i, label, va="center", fontsize=10)
ax.set_yticks(range(4)); ax.set_yticklabels(stages, fontsize=11)
ax.invert_yaxis(); ax.set_xlim(0, vals[0] * 1.9); ax.set_xticks([])
ax.set_title("E-Commerce Sales Funnel (2025)", fontsize=14, fontweight="bold")
ax.grid(False)
plt.tight_layout(); plt.savefig("Sales_Funnel.png", dpi=150); plt.close()

# ------------------------------------------------------------------
# 3. CHART: MONTHLY CONVERSION (+ weekly trend)
# ------------------------------------------------------------------
fig, axes = plt.subplots(2, 1, figsize=(12, 9))
m_labels = pd.to_datetime(monthly.index).strftime("%b")
ax = axes[0]
ax.bar(m_labels, monthly.visitors / 1000, color="#BFD7EA", label="Visitors (thousands)")
ax.set_ylabel("Visitors (K)")
ax2 = ax.twinx()
ax2.plot(m_labels, monthly.conversion, color="#D1495B", marker="o", lw=2.5, label="Conversion %")
for x, y in zip(m_labels, monthly.conversion):
    ax2.text(x, y + 0.05, f"{y:.2f}", ha="center", fontsize=8, color="#D1495B")
ax2.set_ylabel("Conversion rate (%)"); ax2.grid(False)
ax.set_title("Monthly Visitors and Conversion Rate", fontsize=13, fontweight="bold")
ax = axes[1]
ax.plot(weekly.index, weekly.conversion, color="#2E86AB", lw=1.8)
ax.plot(weekly.index, weekly.conversion.rolling(4).mean(), color="#F18F01", lw=2.5,
        label="4-week moving average")
ax.set(title="Weekly Conversion Rate", ylabel="Conversion rate (%)")
ax.legend()
plt.tight_layout(); plt.savefig("monthly_conversion.png", dpi=150); plt.close()

# ------------------------------------------------------------------
# 4. CHART: CONVERSION RATE BREAKDOWN
# ------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(16, 5.2))
sns.barplot(x=by_channel.conversion.values, y=by_channel.index, hue=by_channel.index,
            palette="viridis", legend=False, ax=axes[0])
axes[0].set(title="Conversion by Channel", xlabel="Conversion rate (%)", ylabel="")
sns.barplot(x=by_device.index, y=by_device.conversion.values, hue=by_device.index,
            palette="mako", legend=False, ax=axes[1])
axes[1].set(title="Conversion by Device", ylabel="Conversion rate (%)", xlabel="")
sns.barplot(x=[d[:3] for d in dow_order], y=by_dow.conversion.values, color="#6C8EBF", ax=axes[2])
axes[2].set(title="Conversion by Day of Week", ylabel="Conversion rate (%)", xlabel="")
for a in axes:
    for c in a.containers:
        a.bar_label(c, fmt="%.2f", padding=2, fontsize=9)
plt.suptitle(f"Overall conversion rate: {total.conversion:.2f}%", fontsize=14, fontweight="bold")
plt.tight_layout(); plt.savefig("conversion_rate.png", dpi=150); plt.close()

# ------------------------------------------------------------------
# 5. INSIGHTS (data-driven)
# ------------------------------------------------------------------
stage_drops = {
    "Visitor -> Product View": 100 - total.view_rate,
    "Product View -> Add to Cart": 100 - total.cart_rate,
    "Add to Cart -> Purchase": 100 - total.purchase_rate,
}
worst_stage = max(stage_drops, key=stage_drops.get)
best_m, worst_m = monthly.conversion.idxmax(), monthly.conversion.idxmin()
best_ch, worst_ch = by_channel.conversion.idxmax(), by_channel.conversion.idxmin()
best_dev, worst_dev = by_device.conversion.idxmax(), by_device.conversion.idxmin()
best_d, worst_d = by_dow.conversion.idxmax(), by_dow.conversion.idxmin()
top_rev_ch = by_channel.revenue.idxmax()
mob_share = by_device.loc["Mobile", "visitors"] / total.visitors * 100
fm = lambda s: pd.Period(s).strftime("%B")
cart_abandon = 100 - total.purchase_rate

dow_gap = by_dow.conversion.max() - by_dow.conversion.min()
dow_line = (f"Best day of week: {best_d} ({by_dow.conversion.max():.2f}%); weakest: {worst_d} ({by_dow.conversion.min():.2f}%)."
            if dow_gap >= 0.5 else
            f"Day of week has almost no effect (gap only {dow_gap:.2f} pts between {worst_d} and {best_d}); weekday vs weekend is not a lever.")

insights = f"""E-COMMERCE CONVERSION RATE - KEY INSIGHTS
=========================================
Period: {df['date'].min().date()} to {df['date'].max().date()}  |  Records: {len(df):,}

HEADLINE NUMBERS
- Total visitors      : {total.visitors:,.0f}
- Product views       : {total.product_views:,.0f}  ({total.view_rate:.1f}% of visitors)
- Add to cart         : {total.add_to_cart:,.0f}  ({total.cart_rate:.1f}% of views)
- Purchases           : {total.purchases:,.0f}  ({total.purchase_rate:.1f}% of carts)
- Overall conversion  : {total.conversion:.2f}%  (purchases / visitors)
- Revenue             : Rs. {total.revenue:,.0f}   |  Avg order value: Rs. {total.aov:,.0f}

FUNNEL
1. Biggest drop-off: {worst_stage} ({stage_drops[worst_stage]:.1f}% of users lost at this step).
2. Cart abandonment rate: {cart_abandon:.1f}% of carts never reach purchase.

TIME PATTERNS
3. Best month: {fm(best_m)} ({monthly.conversion.max():.2f}%); weakest month: {fm(worst_m)} ({monthly.conversion.min():.2f}%).
4. {dow_line}

SEGMENTS
5. Best channel: {best_ch} ({by_channel.conversion.max():.2f}%); weakest: {worst_ch} ({by_channel.conversion.min():.2f}%).
6. Highest revenue channel: {top_rev_ch} (Rs. {by_channel.revenue.max():,.0f}).
7. Best device: {best_dev} ({by_device.conversion.max():.2f}%); weakest: {worst_dev} ({by_device.conversion.min():.2f}%).
   Mobile brings {mob_share:.0f}% of visitors.

RECOMMENDATIONS
- Reduce cart abandonment: cart reminder emails, guest checkout, clear shipping cost early.
- Improve the {worst_dev.lower()} experience (faster pages, simpler checkout), as it converts lowest.
- Shift budget toward high-converting channels ({best_ch}); fix landing pages for {worst_ch}.
- Plan campaigns and stock around peak months ({fm(best_m)}) and keep offers running in slow months ({fm(worst_m)}).
- Run A/B tests on the {worst_stage} step, since it loses the most users.
"""
print("\n" + insights)
open("insights.txt", "w", encoding="utf-8").write(insights)

# optional metrics dump (used to build the Word report)
if os.environ.get("METRICS_OUT"):
    json.dump({
        "total": total.round(4).to_dict(),
        "channel": by_channel.round(4).reset_index().to_dict("records"),
        "device": by_device.round(4).reset_index().to_dict("records"),
        "monthly": monthly.round(4).reset_index().rename(columns={"month": "m"}).to_dict("records"),
        "dow": by_dow.round(4).reset_index().to_dict("records"),
        "period": [str(df["date"].min().date()), str(df["date"].max().date())],
        "rows": len(df), "worst_stage": worst_stage, "worst_drop": stage_drops[worst_stage],
        "cart_abandon": cart_abandon, "dow_line": dow_line, "mob_share": mob_share,
    }, open(os.environ["METRICS_OUT"], "w"), default=str)
print("Saved: Sales_Funnel.png, monthly_conversion.png, conversion_rate.png, insights.txt")
