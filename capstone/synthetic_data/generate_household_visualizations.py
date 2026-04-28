import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from datetime import datetime

# Household composition data (Real Complete Basket - Per-Capita Methodology)
# Base: 2 adults + 1 child = 303.65/month / 2.45 AE = 123.94/month per AE
percapita_cost = 123.94
members_data = {
    'Baby (0-2)': {'cost_inc': 30.98, 'pct_inc': 25.0, 'mult': 0.25},
    'Child (3-6)': {'cost_inc': 49.58, 'pct_inc': 40.0, 'mult': 0.40},
    'Child (7-12)': {'cost_inc': 55.77, 'pct_inc': 45.0, 'mult': 0.45},
    'Teenager': {'cost_inc': 117.74, 'pct_inc': 95.0, 'mult': 0.95},
    'Adult': {'cost_inc': 123.94, 'pct_inc': 100.0, 'mult': 1.0},
    'Senior (65+)': {'cost_inc': 136.33, 'pct_inc': 110.0, 'mult': 1.10},
}

base_cost = 303.65  # Real basket base

# Paris income levels (annual)
income_levels = {
    'SMIC': 21000,
    'Low Income': 28000,
    'Median': 42000,
    'Upper Middle': 65000,
}

# ===== VISUALIZATION 1: Cost Impact by Member Type =====
fig, ax = plt.subplots(figsize=(12, 7))

members = list(members_data.keys())
costs = [members_data[m]['cost_inc'] for m in members]
sorted_idx = np.argsort(costs)
members_sorted = [members[i] for i in sorted_idx]
costs_sorted = [costs[i] for i in sorted_idx]

colors = ['#2F4E79', '#4F81BD', '#70AD47', '#FFC000', '#FF6B6B', '#C5504A']
bars = ax.barh(members_sorted, costs_sorted, color=colors, edgecolor='black', linewidth=1.5)

# Add value labels
for i, (bar, cost) in enumerate(zip(bars, costs_sorted)):
    pct = (cost / base_cost) * 100
    ax.text(cost + 5, bar.get_y() + bar.get_height()/2,
            f'EUR {cost:.2f}/mo (+{pct:.0f}%)',
            va='center', fontsize=11, fontweight='bold')

ax.set_xlabel('Monthly Cost Increase (EUR)', fontsize=13, fontweight='bold')
ax.set_title('Household Composition Impact on Food Costs\nBase Household: 2 Adults + 1 Child = EUR 303.65/month',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xlim(0, 380)
ax.grid(axis='x', alpha=0.3, linestyle='--')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Add base line
ax.axvline(x=base_cost, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Base cost')
ax.text(base_cost + 10, len(members_sorted) - 0.5, 'Base\ncost', fontsize=10, color='red', fontweight='bold')

plt.tight_layout()
plt.savefig(r'C:\Users\emman\p_Claude\devs\snipper_tool\capstone\synthetic_data\basket_analysis\06_household_cost_impact.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: 06_household_cost_impact.png")
plt.close()

# ===== VISUALIZATION 2: Affordability by Member Type & Income =====
fig, ax = plt.subplots(figsize=(13, 7))

# Calculate affordability for each member type at each income level
member_names = list(members_data.keys())
income_names = list(income_levels.keys())

# Matrix: rows=members, cols=incomes
affordability_pct = []
for member in member_names:
    new_cost = base_cost + members_data[member]['cost_inc']
    row = []
    for income in income_levels.values():
        monthly_income = income / 12
        pct = (new_cost / monthly_income) * 100
        row.append(pct)
    affordability_pct.append(row)

affordability_pct = np.array(affordability_pct)

# Create heatmap
im = ax.imshow(affordability_pct, cmap='RdYlGn_r', aspect='auto', vmin=5, vmax=40)

# Set ticks
ax.set_xticks(np.arange(len(income_names)))
ax.set_yticks(np.arange(len(member_names)))
ax.set_xticklabels(income_names, fontsize=11, fontweight='bold')
ax.set_yticklabels(member_names, fontsize=11)

# Rotate labels
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

# Add text annotations with affordability status
status_map = {
    0: 'Excellent',
    1: 'Good',
    2: 'Manageable',
    3: 'Difficult',
    4: 'Crisis',
    5: 'Impossible',
}

for i in range(len(member_names)):
    for j in range(len(income_names)):
        pct = affordability_pct[i, j]
        if pct < 10:
            status = 'Excellent'
        elif pct < 15:
            status = 'Good'
        elif pct < 20:
            status = 'Manageable'
        elif pct < 30:
            status = 'Difficult'
        elif pct < 50:
            status = 'Crisis'
        else:
            status = 'Impossible'

        text_color = 'white' if pct > 25 else 'black'
        ax.text(j, i, f'{pct:.1f}%\n{status}',
                ha='center', va='center', color=text_color, fontsize=9, fontweight='bold')

ax.set_title('Affordability Crisis Map: Food as % of Monthly Income\nAfter Adding One Family Member',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xlabel('Annual Household Income', fontsize=12, fontweight='bold')
ax.set_ylabel('Additional Family Member', fontsize=12, fontweight='bold')

# Colorbar
cbar = plt.colorbar(im, ax=ax)
cbar.set_label('% of Monthly Income Spent on Food', fontsize=11, fontweight='bold')

# Add reference lines
ax.axhline(y=-0.5, color='black', linewidth=0.5)
ax.axvline(x=-0.5, color='black', linewidth=0.5)

plt.tight_layout()
plt.savefig(r'C:\Users\emman\p_Claude\devs\snipper_tool\capstone\synthetic_data\basket_analysis\07_affordability_by_composition.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: 07_affordability_by_composition.png")
plt.close()

# ===== VISUALIZATION 3: Remaining Budget After Food =====
fig, ax = plt.subplots(figsize=(13, 7))

# Calculate remaining budget after food for SMIC and Median incomes
scenarios = ['SMIC\n(21,000/yr)', 'Median\n(42,000/yr)']
scenario_incomes = [21000, 42000]

x = np.arange(len(member_names))
width = 0.35

remaining_budgets = []
for annual_income in scenario_incomes:
    monthly_income = annual_income / 12
    row = []
    for member in member_names:
        new_cost = base_cost + members_data[member]['cost_inc']
        remaining = monthly_income - new_cost
        row.append(remaining)
    remaining_budgets.append(row)

colors_scenario = ['#FF6B6B', '#70AD47']
for idx, (scenario, remaining) in enumerate(zip(scenarios, remaining_budgets)):
    offset = width * (idx - 0.5)
    bars = ax.bar(x + offset, remaining, width, label=scenario, color=colors_scenario[idx],
                   edgecolor='black', linewidth=1.5)

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        if height < 0:
            va_pos = 'top'
            y_offset = -20
            color = 'darkred'
        else:
            va_pos = 'bottom'
            y_offset = 10
            color = 'darkgreen'
        ax.text(bar.get_x() + bar.get_width()/2, height + y_offset,
                f'EUR {height:.0f}', ha='center', va=va_pos, fontsize=10,
                fontweight='bold', color=color)

ax.set_ylabel('Remaining Monthly Budget (EUR)', fontsize=12, fontweight='bold')
ax.set_title('Remaining Monthly Budget After Food Costs\nBy Household Composition (Real Complete Basket)',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(member_names, fontsize=10)
ax.legend(fontsize=11, loc='upper right')
ax.axhline(y=0, color='red', linestyle='--', linewidth=2, alpha=0.7)
ax.text(len(member_names)-0.5, 50, 'CRISIS LINE', fontsize=10, color='red', fontweight='bold')
ax.grid(axis='y', alpha=0.3, linestyle='--')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Add rent reference line (approximate Paris rent for basic housing: 600 EUR)
ax.axhline(y=600, color='orange', linestyle=':', linewidth=2, alpha=0.6)
ax.text(0.5, 620, 'Basic Rent (~600 EUR)', fontsize=10, color='orange', fontweight='bold')

plt.tight_layout()
plt.savefig(r'C:\Users\emman\p_Claude\devs\snipper_tool\capstone\synthetic_data\basket_analysis\08_remaining_budget_composition.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: 08_remaining_budget_composition.png")
plt.close()

print("\n" + "="*80)
print("HOUSEHOLD COMPOSITION VISUALIZATIONS CREATED SUCCESSFULLY")
print("="*80)
print("\nGenerated visualizations:")
print("  1. 06_household_cost_impact.png - Cost increase ranking by member type")
print("  2. 07_affordability_by_composition.png - Affordability matrix (member × income)")
print("  3. 08_remaining_budget_composition.png - Remaining budget after food costs")
print("\nAll saved to: C:\\Users\\emman\\p_Claude\\devs\\snipper_tool\\capstone\\synthetic_data\\basket_analysis\\")
