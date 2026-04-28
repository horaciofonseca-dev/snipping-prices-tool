import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

# Complete monthly budget breakdown for SMIC and Median families
# SMIC: €21,000/year = €1,750/month
# Median: €42,000/year = €3,500/month

budget_categories = [
    'Housing',
    'Food (Real Basket)',
    'Utilities',
    'Childcare (1 child 0-3)',
    'Transport',
    'Clothing',
    'Healthcare',
    'Phone/Internet',
    'Insurance',
    'School Supplies',
    'Household Basics',
    'Personal Care'
]

# SMIC family (€1,750/month)
smic_costs = {
    'Housing': 725,  # Average of €600-850
    'Food (Real Basket)': 304,
    'Utilities': 150,
    'Childcare (1 child 0-3)': 200,
    'Transport': 100,
    'Clothing': 90,
    'Healthcare': 75,
    'Phone/Internet': 40,
    'Insurance': 45,
    'School Supplies': 30,
    'Household Basics': 40,
    'Personal Care': 25,
}

# Median family (€3,500/month)
median_costs = {
    'Housing': 1150,  # Average of €1,000-1,300
    'Food (Real Basket)': 304,
    'Utilities': 150,
    'Childcare (1 child 0-3)': 200,
    'Transport': 100,
    'Clothing': 90,
    'Healthcare': 75,
    'Phone/Internet': 40,
    'Insurance': 45,
    'School Supplies': 30,
    'Household Basics': 40,
    'Personal Care': 25,
}

monthly_income_smic = 1750
monthly_income_median = 3500

smic_total = sum(smic_costs.values())
median_total = sum(median_costs.values())

smic_remaining = monthly_income_smic - smic_total
median_remaining = monthly_income_median - median_total

# Create figure with two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 9))

# Color palette for categories
colors_budget = [
    '#1f77b4',  # Housing - blue
    '#ff7f0e',  # Food - orange
    '#2ca02c',  # Utilities - green
    '#d62728',  # Childcare - red
    '#9467bd',  # Transport - purple
    '#8c564b',  # Clothing - brown
    '#e377c2',  # Healthcare - pink
    '#7f7f7f',  # Phone - gray
    '#bcbd22',  # Insurance - olive
    '#17becf',  # School - cyan
    '#aec7e8',  # Household - light blue
    '#ffbb78',  # Personal - light orange
]

# ===== LEFT CHART: SMIC Family =====
categories = list(smic_costs.keys())
smic_values = list(smic_costs.values())

bottom = 0
rects = []
for i, (cat, val) in enumerate(zip(categories, smic_values)):
    rect = ax1.bar(0, val, bottom=bottom, color=colors_budget[i], edgecolor='black', linewidth=1)
    rects.append(rect)
    # Add label in the middle of each segment
    ax1.text(0, bottom + val/2, f'{cat}\n€{val}', ha='center', va='center',
            fontsize=9, fontweight='bold', color='white')
    bottom += val

# Add income line
ax1.axhline(y=monthly_income_smic, color='green', linestyle='--', linewidth=3, label=f'Monthly Income (€{monthly_income_smic})')

# Add deficit/surplus annotation
if smic_remaining < 0:
    ax1.fill_between([-0.3, 0.3], monthly_income_smic, smic_total, alpha=0.2, color='red')
    ax1.text(0, (monthly_income_smic + smic_total) / 2, f'DEFICIT\n€{abs(smic_remaining):.0f}/month',
            ha='center', va='center', fontsize=12, fontweight='bold', color='red',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
else:
    ax1.fill_between([-0.3, 0.3], smic_total, monthly_income_smic, alpha=0.2, color='green')
    ax1.text(0, (smic_total + monthly_income_smic) / 2, f'SURPLUS\n€{smic_remaining:.0f}/month',
            ha='center', va='center', fontsize=12, fontweight='bold', color='green',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))

ax1.set_ylim(0, max(monthly_income_smic, smic_total) * 1.1)
ax1.set_xlim(-0.5, 0.5)
ax1.set_ylabel('Monthly Cost (EUR)', fontsize=12, fontweight='bold')
ax1.set_title(f'SMIC FAMILY (€{monthly_income_smic}/month)\nTotal Essential Costs: €{smic_total:.0f}',
             fontsize=13, fontweight='bold', pad=15, color='darkred')
ax1.set_xticks([])
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['bottom'].set_visible(False)
ax1.grid(axis='y', alpha=0.3, linestyle='--')

# ===== RIGHT CHART: Median Family =====
median_values = list(median_costs.values())

bottom = 0
for i, (cat, val) in enumerate(zip(categories, median_values)):
    rect = ax2.bar(0, val, bottom=bottom, color=colors_budget[i], edgecolor='black', linewidth=1)
    # Add label
    ax2.text(0, bottom + val/2, f'{cat}\n€{val}', ha='center', va='center',
            fontsize=9, fontweight='bold', color='white')
    bottom += val

# Add income line
ax2.axhline(y=monthly_income_median, color='green', linestyle='--', linewidth=3, label=f'Monthly Income (€{monthly_income_median})')

# Add surplus annotation
ax2.fill_between([-0.3, 0.3], median_total, monthly_income_median, alpha=0.2, color='green')
ax2.text(0, (median_total + monthly_income_median) / 2, f'SURPLUS\n€{median_remaining:.0f}/month',
        ha='center', va='center', fontsize=12, fontweight='bold', color='darkgreen',
        bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))

ax2.set_ylim(0, max(monthly_income_median, median_total) * 1.1)
ax2.set_xlim(-0.5, 0.5)
ax2.set_ylabel('Monthly Cost (EUR)', fontsize=12, fontweight='bold')
ax2.set_title(f'MEDIAN FAMILY (€{monthly_income_median}/month)\nTotal Essential Costs: €{median_total:.0f}',
             fontsize=13, fontweight='bold', pad=15, color='darkgreen')
ax2.set_xticks([])
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['bottom'].set_visible(False)
ax2.grid(axis='y', alpha=0.3, linestyle='--')

# Overall title
fig.suptitle('Complete Family Budget Reality: All Essential Costs Included\nIncome vs. Actual Monthly Expenses',
            fontsize=15, fontweight='bold', y=0.98)

# Add professional note at bottom
fig.text(0.5, 0.02,
        'Note: SMIC family runs a monthly deficit of €' + f'{abs(smic_remaining):.0f} even before emergency savings, debt repayment, or discretionary spending.\n' +
        'Median family has €' + f'{median_remaining:.0f}/month remaining after all essential costs—a structural difference of €' + f'{median_remaining + abs(smic_remaining):.0f}/month.',
        ha='center', fontsize=10, style='italic', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout(rect=[0, 0.08, 1, 0.96])
plt.savefig(r'C:\Users\emman\p_Claude\devs\snipper_tool\CAPSTONE_DELIVERABLES\08_complete_budget_reality.png',
           dpi=300, bbox_inches='tight')
print("[OK] Saved: 08_complete_budget_reality.png")

# ===== Create summary data table =====
print("\n" + "="*80)
print("COMPLETE BUDGET BREAKDOWN")
print("="*80)

summary_df = pd.DataFrame({
    'Category': categories,
    'SMIC (€/month)': smic_values,
    'Median (€/month)': median_values,
    'Difference (€)': [median_costs[cat] - smic_costs[cat] for cat in categories]
})

print("\n" + summary_df.to_string(index=False))
print("\n" + "-"*80)
print(f"{'TOTAL EXPENSES':.<50} SMIC: €{smic_total:.2f}/month | Median: €{median_total:.2f}/month")
print(f"{'MONTHLY INCOME':.<50} SMIC: €{monthly_income_smic:.2f}/month | Median: €{monthly_income_median:.2f}/month")
print(f"{'REMAINING/DEFICIT':.<50} SMIC: €{smic_remaining:.2f}/month | Median: €{median_remaining:.2f}/month")
print("="*80)
print(f"\nSTRUCTURAL GAP: SMIC families face a €{abs(smic_remaining) + median_remaining:.0f}/month structural deficit")
print(f"compared to Median families.\n")

plt.show()
