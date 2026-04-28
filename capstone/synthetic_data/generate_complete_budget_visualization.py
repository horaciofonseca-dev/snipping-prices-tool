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
    'Childcare',
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
    'Housing': 725,
    'Food (Real Basket)': 304,
    'Utilities': 150,
    'Childcare': 200,
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
    'Housing': 1150,
    'Food (Real Basket)': 304,
    'Utilities': 150,
    'Childcare': 200,
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

# Create horizontal stacked bar chart
fig, ax = plt.subplots(figsize=(14, 6))

categories = list(smic_costs.keys())
smic_values = list(smic_costs.values())
median_values = list(median_costs.values())

# Y positions for bars
y_pos = [0, 1]
bar_height = 0.6

# ===== SMIC Bar =====
left = 0
for i, (cat, val) in enumerate(zip(categories, smic_values)):
    ax.barh(0, val, left=left, height=bar_height, color=colors_budget[i],
            edgecolor='black', linewidth=0.8, label=cat if i < len(categories) else "")
    # Add value label if segment is large enough
    if val > 40:
        ax.text(left + val/2, 0, f'€{val}', ha='center', va='center',
                fontsize=8, fontweight='bold', color='white')
    left += val

# Add income line for SMIC
ax.axvline(x=monthly_income_smic, color='green', linestyle='--', linewidth=2.5, alpha=0.8)
ax.text(monthly_income_smic, -0.5, f'Income\n€{monthly_income_smic}',
        ha='center', fontsize=9, fontweight='bold', color='green')

# Add deficit annotation for SMIC
deficit_text = f'DEFICIT\n€{abs(smic_remaining):.0f}/mo'
ax.text(smic_total + 50, 0, deficit_text, ha='left', va='center',
        fontsize=10, fontweight='bold', color='white',
        bbox=dict(boxstyle='round', facecolor='red', alpha=0.8))

# ===== MEDIAN Bar =====
left = 0
for i, (cat, val) in enumerate(zip(categories, median_values)):
    ax.barh(1, val, left=left, height=bar_height, color=colors_budget[i],
            edgecolor='black', linewidth=0.8)
    # Add value label if segment is large enough
    if val > 40:
        ax.text(left + val/2, 1, f'€{val}', ha='center', va='center',
                fontsize=8, fontweight='bold', color='white')
    left += val

# Add income line for Median
ax.axvline(x=monthly_income_median, color='green', linestyle='--', linewidth=2.5, alpha=0.8)
ax.text(monthly_income_median, 1.5, f'Income\n€{monthly_income_median}',
        ha='center', fontsize=9, fontweight='bold', color='green')

# Add surplus annotation for Median
surplus_text = f'SURPLUS\n€{median_remaining:.0f}/mo'
ax.text(median_total + 50, 1, surplus_text, ha='left', va='center',
        fontsize=10, fontweight='bold', color='white',
        bbox=dict(boxstyle='round', facecolor='darkgreen', alpha=0.8))

# Formatting
ax.set_yticks(y_pos)
ax.set_yticklabels(['SMIC\n(€1,750/mo)', 'MEDIAN\n(€3,500/mo)'], fontsize=11, fontweight='bold')
ax.set_xlabel('Monthly Cost (EUR)', fontsize=12, fontweight='bold')
ax.set_title('Complete Family Budget Reality: All Essential Costs\n' +
             f'SMIC: €{smic_total:.0f} costs vs €{monthly_income_smic} income = €{smic_remaining:.0f} deficit | ' +
             f'MEDIAN: €{median_total:.0f} costs vs €{monthly_income_median} income = €{median_remaining:.0f} surplus',
             fontsize=13, fontweight='bold', pad=15)

# Set x-axis limit to show all data comfortably
ax.set_xlim(0, max(monthly_income_median, median_total) * 1.15)

# Legend with category colors
legend_elements = [mpatches.Patch(facecolor=colors_budget[i], edgecolor='black', label=cat)
                   for i, cat in enumerate(categories)]
ax.legend(handles=legend_elements, loc='upper right', ncol=2, fontsize=9, title='Cost Categories', title_fontsize=10)

# Remove top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Grid
ax.grid(axis='x', alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig(r'C:\Users\emman\p_Claude\devs\snipper_tool\CAPSTONE_DELIVERABLES\08_complete_budget_reality.png',
           dpi=300, bbox_inches='tight')
print("[OK] Saved: 08_complete_budget_reality.png (Redesigned - horizontal layout)")

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
