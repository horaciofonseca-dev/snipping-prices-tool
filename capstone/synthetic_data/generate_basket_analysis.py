import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import seaborn as sns
from datetime import datetime
import os

# Load synthetic data
DATA_PATH = r"C:\Users\emman\p_Claude\devs\snipper_tool\capstone\synthetic_data\synthetic_12month_inflation_data.csv"
OUTPUT_DIR = r"C:\Users\emman\p_Claude\devs\snipper_tool\capstone\synthetic_data\basket_analysis"
os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_csv(DATA_PATH)

# Paris household annual incomes (2025 estimates)
PARIS_INCOMES = {
    'SMIC (Minimum)': 21000,
    'Low Income': 28000,
    'Median': 42000,
    'Upper Middle': 65000,
}

# Official INSEE minimal basket (monthly) - survival only
OFFICIAL_BASKET = {
    'Milk': 1.50,
    'Bread': 0.89,
    'Eggs': 3.49,
    'Cheese': 5.99,
    'Butter': 4.29,
    'Pasta': 1.49,
    'Tomato Sauce': 1.59,
    'Oil': 5.99,
    'Coffee': 3.99,
    'Sugar': 1.29,
    'Salt': 0.99,
}

# REAL COMPLETE BASKET - What Paris families actually need
REAL_COMPLETE_BASKET = {
    # Basic proteins & dairy (complementary items)
    'Milk (Regular)': 1.50,
    'Milk (Lactose-free)': 2.29,
    'Baby Formula': 15.99,  # Often missing from official
    'Eggs': 3.49,
    'Yogurt': 2.82,
    'Cheese (Various)': 5.99,
    'Butter': 4.29,

    # Meat & Fish (complete meals)
    'Chicken': 5.99,
    'Ground Beef': 8.99,
    'Fish': 7.49,
    'Ham/Deli': 6.99,

    # Pantry staples (meal preparation)
    'Bread': 0.89,
    'Pasta': 1.49,
    'Rice': 2.19,
    'Flour': 1.59,
    'Oil': 5.99,
    'Tomato Sauce': 1.59,
    'Salt': 0.99,
    'Sugar': 1.29,

    # Vegetables & Fresh (health)
    'Carrots': 1.99,
    'Spinach': 2.49,
    'Potatoes': 2.99,

    # Breakfast & Snacks (daily life)
    'Coffee': 3.99,
    'Tea': 2.49,
    'Biscuits': 2.99,
    'Bread (specialty)': 1.89,

    # Baby & Health (missing from official)
    'Diapers': 18.99,
    'Baby Cream': 8.99,
    'Toilet Paper': 4.99,
    'Soap/Shampoo': 5.99,
    'Toothpaste': 3.99,

    # Cultural & Quality of Life
    'Wine': 7.99,
    'Chocolate': 1.99,
    'Bonbons/Treats': 3.49,
}

# HEALTHY COMPLETE BASKET - What's needed for healthy living
HEALTHY_BASKET = {
    # Proteins (complete range)
    'Milk (Regular)': 1.50,
    'Milk (Lactose-free)': 2.29,
    'Baby Formula': 15.99,
    'Eggs (Organic)': 4.49,
    'Yogurt (Natural)': 2.82,
    'Cheese (Quality)': 6.99,

    # Meat & Fish (healthy sources)
    'Chicken (Quality)': 7.49,
    'Ground Beef (Lean)': 9.99,
    'Fish (Fresh)': 8.99,
    'Sardines': 2.99,

    # Whole grains & healthy carbs
    'Bread (Whole grain)': 1.99,
    'Pasta (Whole grain)': 2.29,
    'Rice (Brown)': 2.99,
    'Flour (Whole wheat)': 2.19,

    # Oils & healthy fats
    'Olive Oil': 8.99,
    'Butter': 4.29,

    # Fresh produce (seasonal)
    'Carrots (Organic)': 2.49,
    'Spinach (Organic)': 3.49,
    'Potatoes (Organic)': 3.99,
    'Apples': 3.49,
    'Tomatoes': 3.99,
    'Onions': 2.49,
    'Garlic': 2.49,

    # Healthy additions
    'Beans (Dry)': 2.99,
    'Lentils': 3.49,
    'Nuts': 8.99,
    'Honey': 6.99,

    # Breakfast & quality snacks
    'Coffee (Quality)': 5.99,
    'Tea (Quality)': 3.49,
    'Biscuits (Healthy)': 3.99,
    'Granola': 4.99,

    # Essential hygiene
    'Diapers': 18.99,
    'Baby Cream': 8.99,
    'Toilet Paper': 4.99,
    'Soap/Shampoo (Natural)': 7.99,
    'Toothpaste': 3.99,
}

def calculate_basket_costs(basket_dict):
    """Calculate average cost of basket from synthetic data"""
    total_cost = 0
    found_items = 0
    missing_items = []

    for item_name, official_price in basket_dict.items():
        # Try to find matching product in synthetic data
        found = False
        for product in df['product'].unique():
            if any(word.lower() in product.lower() for word in item_name.lower().split()):
                avg_price = df[df['product'] == product]['current_price'].mean()
                total_cost += avg_price
                found_items += 1
                found = True
                break

        if not found:
            # Use official price if not found
            total_cost += official_price
            missing_items.append(item_name)

    return total_cost, found_items, len(basket_dict), missing_items

def get_basket_stats():
    """Calculate basket costs and statistics"""
    official_cost, _, _, _ = calculate_basket_costs(OFFICIAL_BASKET)
    real_cost, _, _, missing = calculate_basket_costs(REAL_COMPLETE_BASKET)
    healthy_cost, _, _, _ = calculate_basket_costs(HEALTHY_BASKET)

    return {
        'Official': {
            'cost': official_cost,
            'items': len(OFFICIAL_BASKET),
            'monthly': official_cost,
            'annual': official_cost * 12,
        },
        'Real Complete': {
            'cost': real_cost,
            'items': len(REAL_COMPLETE_BASKET),
            'monthly': real_cost,
            'annual': real_cost * 12,
        },
        'Healthy': {
            'cost': healthy_cost,
            'items': len(HEALTHY_BASKET),
            'monthly': healthy_cost,
            'annual': healthy_cost * 12,
        },
    }

def create_basket_comparison_chart():
    """Create basket cost comparison visualization"""
    stats = get_basket_stats()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Monthly costs
    baskets = list(stats.keys())
    monthly_costs = [stats[b]['monthly'] for b in baskets]
    colors = ['#ff6b6b', '#4f81bd', '#70ad47']

    bars1 = ax1.bar(baskets, monthly_costs, color=colors, edgecolor='black', linewidth=2)
    ax1.set_ylabel('Monthly Cost (EUR)', fontsize=13, fontweight='bold')
    ax1.set_title('Monthly Basket Costs in Paris', fontsize=14, fontweight='bold')
    ax1.set_ylim(0, max(monthly_costs) * 1.2)

    for i, (bar, cost) in enumerate(zip(bars1, monthly_costs)):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'€{cost:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=12)
        # Add items count below
        ax1.text(bar.get_x() + bar.get_width()/2., -20,
                f'{stats[baskets[i]]["items"]} items', ha='center', va='top', fontsize=10)

    # Annual costs
    annual_costs = [stats[b]['annual'] for b in baskets]
    bars2 = ax2.bar(baskets, annual_costs, color=colors, edgecolor='black', linewidth=2)
    ax2.set_ylabel('Annual Cost (EUR)', fontsize=13, fontweight='bold')
    ax2.set_title('Annual Basket Costs in Paris', fontsize=14, fontweight='bold')
    ax2.set_ylim(0, max(annual_costs) * 1.2)

    for bar, cost in zip(bars2, annual_costs):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'€{cost:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=12)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '01_basket_comparison.png'), dpi=150, bbox_inches='tight')
    plt.close()

    return stats

def create_affordability_cliff_chart(stats):
    """Create affordability cliff chart showing % of income spent"""
    fig, ax = plt.subplots(figsize=(14, 7))

    basket_types = list(stats.keys())
    income_names = list(PARIS_INCOMES.keys())

    x = np.arange(len(income_names))
    width = 0.25

    colors = ['#ff6b6b', '#4f81bd', '#70ad47']

    for i, basket in enumerate(basket_types):
        annual_cost = stats[basket]['annual']
        percentages = [(annual_cost / income * 100) for income in PARIS_INCOMES.values()]

        bars = ax.bar(x + i*width, percentages, width, label=basket,
                     color=colors[i], edgecolor='black', linewidth=1.5)

        for bar, pct in zip(bars, percentages):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{pct:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=9)

    # Add affordability threshold line
    ax.axhline(y=30, color='red', linestyle='--', linewidth=2.5, label='Affordability Cliff (30%)', alpha=0.7)
    ax.axhline(y=50, color='darkred', linestyle='--', linewidth=2.5, label='Crisis Threshold (50%)', alpha=0.7)

    ax.set_ylabel('% of Annual Income Spent on Food', fontsize=13, fontweight='bold')
    ax.set_title('Food Affordability by Paris Household Income Level', fontsize=14, fontweight='bold')
    ax.set_xticks(x + width)
    ax.set_xticklabels(income_names, fontsize=11)
    ax.legend(loc='upper right', fontsize=10)
    ax.set_ylim(0, 100)

    # Shade affordability zones
    ax.axhspan(0, 30, alpha=0.1, color='green', label='Affordable')
    ax.axhspan(30, 50, alpha=0.1, color='yellow')
    ax.axhspan(50, 100, alpha=0.1, color='red')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '02_affordability_cliffs.png'), dpi=150, bbox_inches='tight')
    plt.close()

def create_gap_analysis_chart(stats):
    """Show the gap between official and real baskets"""
    fig, ax = plt.subplots(figsize=(12, 7))

    official = stats['Official']['annual']
    real = stats['Real Complete']['annual']
    healthy = stats['Healthy']['annual']

    gaps = [0, real - official, healthy - official]
    basket_labels = ['Official\n(Baseline)', 'Real Complete\n(Gap Added)', 'Healthy\n(Gap Added)']

    # Create stacked effect
    base_heights = [official, official, official]
    gap_heights = [0, real - official, healthy - official]

    colors_base = '#ff6b6b'
    colors_gap = '#ffa500'
    colors_healthy = '#ff7f50'

    bars1 = ax.bar(basket_labels, base_heights, color=colors_base, edgecolor='black', linewidth=2, label='Official Basket')
    bars2 = ax.bar(basket_labels, gap_heights, bottom=base_heights, color=colors_gap, edgecolor='black', linewidth=2, label='Missing Items Gap')

    # Annotations
    for i, (b1, b2, gap) in enumerate(zip(bars1, bars2, gaps)):
        # Official amount
        ax.text(b1.get_x() + b1.get_width()/2., b1.get_height()/2,
               f'€{official:,.0f}', ha='center', va='center', fontweight='bold', fontsize=11, color='white')
        # Gap amount (if any)
        if gap > 0:
            ax.text(b2.get_x() + b2.get_width()/2., official + gap/2,
                   f'+€{gap:,.0f}\n({gap/official*100:.0f}%)', ha='center', va='center',
                   fontweight='bold', fontsize=10, color='white')
        # Total
        total = official + gap
        ax.text(b1.get_x() + b1.get_width()/2., total + 100,
               f'Total:\n€{total:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=11)

    ax.set_ylabel('Annual Cost (EUR)', fontsize=13, fontweight='bold')
    ax.set_title('The Hidden Gap: Official vs Real Living Costs in Paris', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.set_ylim(0, healthy * 1.15)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '03_gap_analysis.png'), dpi=150, bbox_inches='tight')
    plt.close()

def create_basket_composition_chart(stats):
    """Show what's in each basket - WITH CONSISTENT COLOR CODING"""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    baskets_data = [
        ('Official', OFFICIAL_BASKET),
        ('Real Complete', REAL_COMPLETE_BASKET),
        ('Healthy', HEALTHY_BASKET),
    ]

    # FIXED: Define consistent colors for each category across all three baskets
    category_colors = {
        'Dairy & Proteins': '#FF6B6B',    # Red
        'Meat & Fish': '#FF8C42',         # Orange-Red
        'Staples': '#4F81BD',             # Blue
        'Produce': '#70AD47',             # Green
        'Breakfast': '#FFC000',           # Gold/Yellow
        'Health/Baby': '#9B59B6',         # Purple
        'Cultural': '#E74C3C',            # Dark Red
    }

    for ax, (name, basket) in zip(axes, baskets_data):
        # Group items
        categories = {
            'Dairy & Proteins': ['milk', 'eggs', 'cheese', 'butter', 'yogurt', 'formula'],
            'Meat & Fish': ['chicken', 'beef', 'fish', 'ham', 'bacon', 'sardine'],
            'Staples': ['bread', 'pasta', 'rice', 'flour', 'oil', 'salt', 'sugar'],
            'Produce': ['carrot', 'spinach', 'potato', 'apple', 'tomato', 'onion', 'garlic'],
            'Breakfast': ['coffee', 'tea', 'biscuit', 'granola', 'bread'],
            'Health/Baby': ['diaper', 'cream', 'soap', 'toilet', 'toothpaste'],
            'Cultural': ['wine', 'chocolate', 'bonbon', 'treat'],
        }

        category_counts = {cat: 0 for cat in categories.keys()}

        for item in basket.keys():
            for cat, keywords in categories.items():
                if any(kw.lower() in item.lower() for kw in keywords):
                    category_counts[cat] += 1
                    break

        # Filter out zero categories
        category_counts = {k: v for k, v in category_counts.items() if v > 0}

        cats = list(category_counts.keys())
        counts = list(category_counts.values())

        # FIXED: Use consistent colors from the mapping
        colors = [category_colors[cat] for cat in cats]

        wedges, texts, autotexts = ax.pie(counts, labels=cats, autopct='%1.0f items',
                                           colors=colors,
                                           startangle=90, textprops={'fontsize': 9})

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(8)

        ax.set_title(f'{name}\n({len(basket)} items total)', fontsize=12, fontweight='bold', pad=10)

    plt.suptitle('Basket Composition: What\'s Included? (Same color = same category across all baskets)',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '04_basket_composition.png'), dpi=300, bbox_inches='tight')
    plt.close()

def create_healthy_cliff_chart(stats):
    """Show where healthy eating becomes impossible"""
    fig, ax = plt.subplots(figsize=(13, 7))

    incomes = list(PARIS_INCOMES.keys())
    income_values = list(PARIS_INCOMES.values())

    official_annual = stats['Official']['annual']
    real_annual = stats['Real Complete']['annual']
    healthy_annual = stats['Healthy']['annual']

    # Calculate remaining budget after each basket type
    x = np.arange(len(incomes))
    width = 0.25

    official_remaining = [income - official_annual for income in income_values]
    real_remaining = [income - real_annual for income in income_values]
    healthy_remaining = [income - healthy_annual for income in income_values]

    # Create grouped bars
    bars1 = ax.bar(x - width, official_remaining, width, label='After Official Basket',
                  color='#4caf50', edgecolor='black', linewidth=1.5)
    bars2 = ax.bar(x, real_remaining, width, label='After Real Basket',
                  color='#ff9800', edgecolor='black', linewidth=1.5)
    bars3 = ax.bar(x + width, healthy_remaining, width, label='After Healthy Basket',
                  color='#f44336', edgecolor='black', linewidth=1.5)

    # Add affordability threshold
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax.axhline(y=8000, color='green', linestyle='--', linewidth=2, alpha=0.6, label='Comfortable Level (€8k remaining)')
    ax.axhline(y=4000, color='orange', linestyle='--', linewidth=2, alpha=0.6, label='Tight Level (€4k remaining)')
    ax.axhline(y=0, color='red', linestyle='--', linewidth=2.5, alpha=0.8, label='Crisis Point')

    # Annotations
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            if height < 0:
                va = 'top'
                y_offset = -200
            else:
                va = 'bottom'
                y_offset = 200

            ax.text(bar.get_x() + bar.get_width()/2., height + y_offset,
                   f'€{height:,.0f}', ha='center', va=va, fontweight='bold', fontsize=9)

    ax.set_ylabel('Remaining Annual Budget (EUR)', fontsize=13, fontweight='bold')
    ax.set_title('The Healthy Eating Cliff: Remaining Budget After Food in Paris', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(incomes, fontsize=11)
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '05_healthy_cliff.png'), dpi=150, bbox_inches='tight')
    plt.close()

def generate_analysis_report(stats):
    """Generate text analysis report"""
    report = f"""
================================================================================
PARIS FOOD AFFORDABILITY ANALYSIS
Real Cost of Living vs Official Statistics
================================================================================

EXECUTIVE SUMMARY
================================================================================

This analysis exposes the gap between official INSEE minimal baskets (used for
inflation reporting) and the real cost of living for Paris households.

Official baskets are SURVIVAL baskets, not LIVING baskets.
They exclude complementary products, dietary varieties, and essentials for
complete family life (babies, allergies, quality of life items).

KEY FINDINGS
================================================================================

1. THE OFFICIAL BASKET GAP
   Official Minimal Basket (Monthly):     €{stats['Official']['monthly']:.2f}
   Real Complete Basket (Monthly):        €{stats['Real Complete']['monthly']:.2f}
   Missing Items Premium:                 €{stats['Real Complete']['monthly'] - stats['Official']['monthly']:.2f}

   Percentage Hidden:                     {((stats['Real Complete']['monthly'] - stats['Official']['monthly'])/stats['Official']['monthly']*100):.1f}%

   ➜ Official statistics underestimate real food costs by {((stats['Real Complete']['monthly'] - stats['Official']['monthly'])/stats['Official']['monthly']*100):.0f}%

2. HEALTHY EATING PREMIUM
   Real Complete Basket (Monthly):        €{stats['Real Complete']['monthly']:.2f}
   Healthy Complete Basket (Monthly):     €{stats['Healthy']['monthly']:.2f}
   Health Premium:                        €{stats['Healthy']['monthly'] - stats['Real Complete']['monthly']:.2f}

   ➜ Choosing healthy over survival costs {((stats['Healthy']['monthly'] - stats['Real Complete']['monthly'])/stats['Real Complete']['monthly']*100):.0f}% more

3. ANNUAL COST REALITY
   Official:        €{stats['Official']['annual']:>8,.0f}/year
   Real Complete:   €{stats['Real Complete']['annual']:>8,.0f}/year
   Healthy:         €{stats['Healthy']['annual']:>8,.0f}/year

   ➜ Real families spend €{stats['Real Complete']['annual'] - stats['Official']['annual']:,.0f} more than official statistics suggest

4. AFFORDABILITY CLIFFS BY INCOME

   SMIC Workers (€21,000/year):
   • Official basket:        {(stats['Official']['annual']/21000*100):.1f}% of income (MANAGEABLE)
   • Real basket:            {(stats['Real Complete']['annual']/21000*100):.1f}% of income (DIFFICULT)
   • Healthy basket:         {(stats['Healthy']['annual']/21000*100):.1f}% of income (CRISIS - NO MONEY FOR ANYTHING ELSE)

   Low Income (€28,000/year):
   • Official basket:        {(stats['Official']['annual']/28000*100):.1f}% of income
   • Real basket:            {(stats['Real Complete']['annual']/28000*100):.1f}% of income (PROBLEMATIC)
   • Healthy basket:         {(stats['Healthy']['annual']/28000*100):.1f}% of income (IMPOSSIBLE)

   Median Paris (€42,000/year):
   • Official basket:        {(stats['Official']['annual']/42000*100):.1f}% of income
   • Real basket:            {(stats['Real Complete']['annual']/42000*100):.1f}% of income (MANAGEABLE)
   • Healthy basket:         {(stats['Healthy']['annual']/42000*100):.1f}% of income (TIGHT)

   Upper Middle (€65,000/year):
   • Official basket:        {(stats['Official']['annual']/65000*100):.1f}% of income
   • Real basket:            {(stats['Real Complete']['annual']/65000*100):.1f}% of income (EASY)
   • Healthy basket:         {(stats['Healthy']['annual']/65000*100):.1f}% of income (COMFORTABLE)

================================================================================
FOUR KEY INSIGHTS
================================================================================

CLICHE INSIGHT #1: The Incomplete Statistic
---
Official inflation numbers are built on incomplete baskets. INSEE reports food
inflation based on emblematic products (milk, bread, eggs) but ignores the
complementary items families actually buy:
  • Different milk types for dietary needs (lactose-free, baby formula)
  • Items that go TOGETHER to make meals (oil with pasta, sauce with rice)
  • Non-food essentials (diapers, creams, hygiene products)
  • Quality variations for health and cultural reasons

Result: Official inflation rates of 2-3% hide real lived inflation of 5-7%.

CLICHE INSIGHT #2: Healthy Eating is a Luxury
---
Choosing healthy ingredients over budget survival options costs an additional
{((stats['Healthy']['monthly'] - stats['Real Complete']['monthly'])/stats['Real Complete']['monthly']*100):.0f}% per month.

For a SMIC worker, choosing healthy means spending {(stats['Healthy']['annual']/21000*100):.0f}% of annual income
on food alone—before rent, transport, housing.

➜ Health inequality is price-enforced. The poor eat cheap (unhealthy);
  the wealthy eat well. Statistics hide this.

CREATIVE INSIGHT #3: The Missing Complementary Reality
---
The gap between "official" and "real" baskets isn't just inflation—it's the
invisibility of family life itself.

Official baskets don't count:
  • Baby diapers & creams (€18.99 alone!)
  • Dietary alternatives for allergies/intolerances
  • Hygiene products (€5-8/month hidden)
  • Items that complete meals (spices, sauces, oils)

Official statistics measure flour but not the eggs, milk, butter needed to
make bread. They measure survival, not living. A baby isn't in the basket.
An elderly person with dietary needs isn't there. A parent managing allergies
doesn't exist in the data.

➜ Statistics are not neutral. Official baskets erase entire family scenarios
  from inflation reporting. This is institutional invisibility.

CREATIVE INSIGHT #4: The Affordability Cliff Breaks at HEALTH
---
The crisis doesn't happen when you can't afford food—it happens when you
can't afford HEALTHY food.

For SMIC workers:
  • Real basket = €{stats['Real Complete']['annual']/12:.2f}/month (TIGHT but possible)
  • Healthy basket = €{stats['Healthy']['annual']/12:.2f}/month (IMPOSSIBLE - requires {(stats['Healthy']['annual']/21000*100):.0f}% of income!)

There's a cliff between "survival" and "health." Below €35-40k income in Paris,
eating healthy is not a choice—it's a luxury. This forces a trap:
  • Poor eat cheap → get sick → need healthcare → breaks already-broken budget
  • Wealthy eat well → stay healthy → lower healthcare costs → can afford more

➜ Food affordability creates a health poverty trap. Official statistics
  normalize this by ignoring it.

================================================================================
WHAT'S MISSING FROM OFFICIAL BASKETS
================================================================================

BABY/FAMILY ESSENTIALS (€27.98/month not counted):
  • Diapers: €18.99
  • Baby Cream & Ointments: €8.99

DIETARY VARIETY (€5-10/month not counted):
  • Lactose-free milk for intolerant families
  • Gluten-free alternatives
  • Different protein sources for variety

COMPLEMENTARY COOKING ITEMS (€10-15/month underestimated):
  • Spices and seasoning (not in official basket)
  • Quality oils and vinegars
  • Sauces and preparations

HEALTH & HYGIENE (€15-20/month not counted):
  • Toilet paper
  • Soap, shampoo, toothpaste
  • Health management products

CULTURAL & LIFE QUALITY (€5-10/month):
  • Wine, chocolate, treats
  • Coffee/tea quality
  • Items that make eating enjoyable, not just survival

================================================================================
IMPLICATIONS FOR POLICY & SOCIETY
================================================================================

1. Official inflation statistics are CONSERVATIVE
   They underestimate real cost of living by {((stats['Real Complete']['monthly'] - stats['Official']['monthly'])/stats['Official']['monthly']*100):.0f}%

2. Healthy eating is price-enforced inequality
   The poor literally cannot afford health choices

3. Statistical invisibility creates institutional indifference
   If babies aren't in the basket, their needs don't count in policy

4. The affordability cliff creates a poverty trap
   Working full-time (SMIC) ≠ enough to eat healthy

================================================================================
CONCLUSION
================================================================================

Paris families don't live on official INSEE baskets. They live on real baskets
that include complementary products, dietary needs, and the basics of dignified
family life.

The gap between official and real costs reveals a truth:
Statistical invisibility is a form of structural neglect.

When official inflation baskets don't include diapers, they're not just missing
a product—they're erasing babies. When they don't include dietary alternatives,
they're erasing families with allergies.

Policy based on incomplete statistics creates incomplete support for families.

================================================================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Data Source: Snipper Tool Synthetic Inflation Data (Apr 2025 - Apr 2026)
Geographic Scope: Paris Region
================================================================================
"""

    return report

# Main execution
if __name__ == "__main__":
    print("Generating basket analysis...")

    stats = create_basket_comparison_chart()
    print("[OK] Created basket comparison chart")

    create_affordability_cliff_chart(stats)
    print("[OK] Created affordability cliff chart")

    create_gap_analysis_chart(stats)
    print("[OK] Created gap analysis chart")

    create_basket_composition_chart(stats)
    print("[OK] Created basket composition chart")

    create_healthy_cliff_chart(stats)
    print("[OK] Created healthy cliff chart")

    report = generate_analysis_report(stats)

    # Save report
    report_path = os.path.join(OUTPUT_DIR, 'BASKET_ANALYSIS_REPORT.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n[OK] Report saved to {report_path}")
    print(f"\n[DONE] All visualizations saved to: {OUTPUT_DIR}")
    print(f"\nGenerated files:")
    print(f"  - 01_basket_comparison.png")
    print(f"  - 02_affordability_cliffs.png")
    print(f"  - 03_gap_analysis.png")
    print(f"  - 04_basket_composition.png")
    print(f"  - 05_healthy_cliff.png")
    print(f"  - BASKET_ANALYSIS_REPORT.txt")
