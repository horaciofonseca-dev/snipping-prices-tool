import pandas as pd
from datetime import datetime

# Base household (2 adults + 1 child age 7-10)
BASE_OFFICIAL = 68.67
BASE_REAL = 303.65
BASE_HEALTHY = 383.58

# Paris income levels
PARIS_INCOMES = {
    'SMIC (Minimum)': 21000,
    'Low Income': 28000,
    'Median': 42000,
    'Upper Middle': 65000,
}

# Consumption multipliers by member type
# Based on standard nutrition/consumption patterns
MEMBER_MULTIPLIERS = {
    'Baby (0-2)': {
        'description': 'Infant requiring formula, diapers, specialized creams',
        'official': 0.15,  # Small appetite, formula expensive
        'real': 0.25,      # Formula + diapers + creams = significant
        'healthy': 0.20,   # Quality formula, organic products
    },
    'Child (3-6)': {
        'description': 'Toddler/preschooler, still needs diapers/formula if under 3',
        'official': 0.25,
        'real': 0.40,      # Still needs diapers if under 5
        'healthy': 0.35,
    },
    'Child (7-12)': {
        'description': 'School-age child (typical in base household)',
        'official': 0.35,
        'real': 0.45,
        'healthy': 0.40,
    },
    'Teenager (13-18)': {
        'description': 'Teen with adult-size appetite',
        'official': 0.80,
        'real': 0.95,
        'healthy': 0.90,
    },
    'Adult': {
        'description': 'Additional working-age adult',
        'official': 1.0,
        'real': 1.0,
        'healthy': 1.0,
    },
    'Senior (65+)': {
        'description': 'Elderly with specialized dietary needs',
        'official': 0.85,
        'real': 1.10,      # Often needs softer foods, specialized items
        'healthy': 1.15,   # More medical/health food needs
    },
}

def calculate_household_cost(base_cost, members_list):
    """Calculate total household cost based on member composition"""
    total = base_cost
    for member_type in members_list:
        multiplier = MEMBER_MULTIPLIERS[member_type]['official' if base_cost == BASE_OFFICIAL else
                                                      'real' if base_cost == BASE_REAL else 'healthy']
        total += base_cost * multiplier
    return total

def analyze_composition(member_name, member_type):
    """Analyze impact of adding one household member"""

    print(f"\n{'='*90}")
    print(f"HOUSEHOLD COMPOSITION: Base (2 adults + 1 child) + 1 {member_name}")
    print(f"{'='*90}")
    print(f"Description: {MEMBER_MULTIPLIERS[member_type]['description']}\n")

    mult = MEMBER_MULTIPLIERS[member_type]

    # Calculate new costs
    new_official = BASE_OFFICIAL * (1 + mult['official'])
    new_real = BASE_REAL * (1 + mult['real'])
    new_healthy = BASE_HEALTHY * (1 + mult['healthy'])

    # Calculate increase
    inc_official = new_official - BASE_OFFICIAL
    inc_real = new_real - BASE_REAL
    inc_healthy = new_healthy - BASE_HEALTHY

    inc_pct_official = (inc_official / BASE_OFFICIAL) * 100
    inc_pct_real = (inc_real / BASE_REAL) * 100
    inc_pct_healthy = (inc_healthy / BASE_HEALTHY) * 100

    print(f"MONTHLY COST IMPACT:\n")
    print(f"  Official Basket:")
    print(f"    Base (2a+1c):     EUR {BASE_OFFICIAL:>8.2f}")
    print(f"    +1 {member_name:<13} EUR {new_official:>8.2f}  (+ EUR {inc_official:>6.2f}, +{inc_pct_official:>5.1f}%)")
    print()
    print(f"  Real Complete Basket:")
    print(f"    Base (2a+1c):     EUR {BASE_REAL:>8.2f}")
    print(f"    +1 {member_name:<13} EUR {new_real:>8.2f}  (+ EUR {inc_real:>6.2f}, +{inc_pct_real:>5.1f}%)")
    print()
    print(f"  Healthy Basket:")
    print(f"    Base (2a+1c):     EUR {BASE_HEALTHY:>8.2f}")
    print(f"    +1 {member_name:<13} EUR {new_healthy:>8.2f}  (+ EUR {inc_healthy:>6.2f}, +{inc_pct_healthy:>5.1f}%)")

    print(f"\n\nANNUAL COST IMPACT:\n")

    annual_official_base = BASE_OFFICIAL * 12
    annual_official_new = new_official * 12
    annual_real_base = BASE_REAL * 12
    annual_real_new = new_real * 12
    annual_healthy_base = BASE_HEALTHY * 12
    annual_healthy_new = new_healthy * 12

    print(f"  Official Basket:")
    print(f"    Base:    EUR {annual_official_base:>8,.0f}/year")
    print(f"    +1:      EUR {annual_official_new:>8,.0f}/year  (+ EUR {(annual_official_new - annual_official_base):>8,.0f})")
    print()
    print(f"  Real Complete:")
    print(f"    Base:    EUR {annual_real_base:>8,.0f}/year")
    print(f"    +1:      EUR {annual_real_new:>8,.0f}/year  (+ EUR {(annual_real_new - annual_real_base):>8,.0f})")
    print()
    print(f"  Healthy Basket:")
    print(f"    Base:    EUR {annual_healthy_base:>8,.0f}/year")
    print(f"    +1:      EUR {annual_healthy_new:>8,.0f}/year  (+ EUR {(annual_healthy_new - annual_healthy_base):>8,.0f})")

    # Income impact analysis
    print(f"\n\nINCOME IMPACT ANALYSIS (% of annual income):\n")
    print(f"{'Household Income':<25} | {'Official':<15} | {'Real Complete':<18} | {'Healthy':<15}")
    print(f"{'-'*90}")

    for income_name, annual_income in PARIS_INCOMES.items():
        pct_official_base = (annual_official_base / annual_income) * 100
        pct_official_new = (annual_official_new / annual_income) * 100

        pct_real_base = (annual_real_base / annual_income) * 100
        pct_real_new = (annual_real_new / annual_income) * 100

        pct_healthy_base = (annual_healthy_base / annual_income) * 100
        pct_healthy_new = (annual_healthy_new / annual_income) * 100

        official_str = f"{pct_official_base:.1f}% -> {pct_official_new:.1f}%"
        real_str = f"{pct_real_base:.1f}% -> {pct_real_new:.1f}%"
        healthy_str = f"{pct_healthy_base:.1f}% -> {pct_healthy_new:.1f}%"

        print(f"{income_name:<25} | {official_str:<15} | {real_str:<18} | {healthy_str:<15}")

    # Affordability status
    print(f"\n\nAFFORDABILITY STATUS CHANGE:\n")

    status_map = {
        0: "[OK] Excellent (0-10%)",
        1: "[OK] Good (10-15%)",
        2: "[!] Manageable (15-20%)",
        3: "[!] Difficult (20-30%)",
        4: "[X] Crisis (30-50%)",
        5: "[X] Impossible (50%+)",
    }

    def get_status(pct):
        if pct < 10:
            return 0
        elif pct < 15:
            return 1
        elif pct < 20:
            return 2
        elif pct < 30:
            return 3
        elif pct < 50:
            return 4
        else:
            return 5

    print("Real Complete Basket Status Changes:")
    print(f"{'Income Level':<25} | {'Base Household':<20} | {f'+1 {member_name}':<20} | {'Change':<20}")
    print("-" * 90)

    for income_name, annual_income in PARIS_INCOMES.items():
        pct_base = (annual_real_base / annual_income) * 100
        pct_new = (annual_real_new / annual_income) * 100

        status_base = get_status(pct_base)
        status_new = get_status(pct_new)

        change = "WORSENS" if status_new > status_base else "SAME" if status_new == status_base else "IMPROVES"

        print(f"{income_name:<25} | {status_map[status_base]:<20} | {status_map[status_new]:<20} | {change:<20}")

    return {
        'member': member_name,
        'official_inc': inc_official,
        'real_inc': inc_real,
        'healthy_inc': inc_healthy,
        'new_official': new_official,
        'new_real': new_real,
        'new_healthy': new_healthy,
    }

# Main execution
print("\n" + "="*90)
print("HOUSEHOLD COMPOSITION IMPACT ANALYSIS")
print("Snipper Tool - Paris Food Affordability Study")
print("="*90)
print("\nBASE HOUSEHOLD: 2 adults + 1 child (age 7-10)")
print(f"  Official Monthly: EUR {BASE_OFFICIAL:.2f}")
print(f"  Real Complete Monthly: EUR {BASE_REAL:.2f}")
print(f"  Healthy Monthly: EUR {BASE_HEALTHY:.2f}")

results = {}

# Analyze each member type
for member_name, member_type in [
    ('Baby (0-2 years)', 'Baby (0-2)'),
    ('Child (3-6 years)', 'Child (3-6)'),
    ('Child (7-12 years)', 'Child (7-12)'),
    ('Teenager (13-18)', 'Teenager (13-18)'),
    ('Adult', 'Adult'),
    ('Senior (65+ years)', 'Senior (65+)'),
]:
    results[member_name] = analyze_composition(member_name, member_type)

# Summary comparison
print(f"\n\n{'='*90}")
print("QUICK COMPARISON: Impact Rank (Lowest to Highest Cost Increase)")
print(f"{'='*90}\n")

# Sort by impact on real basket
sorted_results = sorted(results.items(), key=lambda x: x[1]['real_inc'])

print("MONTHLY COST INCREASE (Real Complete Basket):\n")
for i, (member_name, data) in enumerate(sorted_results, 1):
    print(f"{i}. {member_name:<25} +EUR {data['real_inc']:>7.2f}/month  (New total: EUR {data['new_real']:>7.2f})")

print("\n\nCRITICAL INSIGHT - Most Expensive to Add:")
most_expensive = sorted_results[-1]
cheapest = sorted_results[0]

print(f"\nMost Expensive: {most_expensive[0]:<25} +EUR {most_expensive[1]['real_inc']:.2f}/month")
print(f"Least Expensive: {cheapest[0]:<25} +EUR {cheapest[1]['real_inc']:.2f}/month")
print(f"Difference: EUR {most_expensive[1]['real_inc'] - cheapest[1]['real_inc']:.2f}/month")

print(f"\n{'='*90}")
print("END OF ANALYSIS")
print(f"{'='*90}\n")
