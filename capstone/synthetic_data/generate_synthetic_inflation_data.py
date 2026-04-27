import os
import csv
from datetime import datetime, timedelta
from collections import defaultdict
import random
import math

import pandas as pd
import numpy as np

# Configuration
DATA_PATH = r"C:\Users\emman\p_Claude\capstone\datacollection"
OUTPUT_PATH = r"C:\Users\emman\p_Claude\devs\snipper_tool\synthetic_12month_inflation_data.csv"

# French monthly inflation rates (April 2025 - April 2026) - realistic scenario
# Based on French inflation trends, with seasonal adjustments
MONTHLY_INFLATION_RATES = {
    'Apr-2025': 0.022,   # 2.2% (spring baseline)
    'May-2025': 0.024,   # 2.4% (early summer)
    'Jun-2025': 0.025,   # 2.5% (summer start)
    'Jul-2025': 0.028,   # 2.8% (high summer, tourism season)
    'Aug-2025': 0.026,   # 2.6% (summer continuing)
    'Sep-2025': 0.020,   # 2.0% (back to school, slight dip)
    'Oct-2025': 0.019,   # 1.9% (fall stabilization)
    'Nov-2025': 0.021,   # 2.1% (pre-holiday)
    'Dec-2025': 0.032,   # 3.2% (Christmas peak, high demand)
    'Jan-2026': 0.015,   # 1.5% (post-holiday, lower demand)
    'Feb-2026': 0.017,   # 1.7% (winter stabilization)
    'Mar-2026': 0.020,   # 2.0% (spring season)
    'Apr-2026': 0.022,   # 2.2% (spring continuing)
}

# Seasonal multipliers by product category (varies throughout year)
SEASONAL_FACTORS = {
    'cafe': {'Dec': 1.15, 'Jan': 1.05, 'Apr': 1.0, 'Jul': 0.95},  # Coffee higher in winter
    'the': {'Dec': 1.12, 'Jan': 1.04, 'Apr': 1.0, 'Jul': 0.92},
    'chocolate': {'Dec': 1.20, 'Jan': 1.08, 'Apr': 1.0, 'Jul': 0.85},  # High for holidays
    'pain': {'Apr': 1.05, 'Dec': 1.10, 'Jan': 1.02, 'Jul': 0.98},  # Bread stable
    'beurre': {'Dec': 1.08, 'Jan': 1.06, 'Apr': 1.0, 'Jul': 0.95},  # Butter higher in winter
    'fromage': {'Dec': 1.12, 'Jan': 1.08, 'Apr': 1.0, 'Jul': 0.96},  # Cheese for holidays
    'lait': {'Apr': 1.0, 'Dec': 1.05, 'Jan': 1.03, 'Jul': 0.98},  # Milk stable
    'oeufs': {'Apr': 1.0, 'Dec': 1.08, 'Jan': 1.02, 'Jul': 1.0},  # Eggs for Easter/holidays
    'viande': {'Dec': 1.15, 'Jan': 1.10, 'Apr': 1.05, 'Jul': 0.92},  # Meat for holidays
    'jambon': {'Dec': 1.20, 'Jan': 1.08, 'Apr': 1.02, 'Jul': 0.90},  # Ham/deli for holidays
    'sardines': {'Jul': 1.08, 'Aug': 1.05, 'Apr': 1.0, 'Dec': 1.02},  # Summer canned goods
    'sauce': {'Apr': 1.0, 'Dec': 1.05, 'Jan': 1.02, 'Jul': 0.98},
    'bonbons': {'Dec': 1.30, 'Jan': 1.05, 'Apr': 1.10, 'Jul': 0.80},  # Candy high for holidays
    'biscuits': {'Dec': 1.15, 'Jan': 1.05, 'Apr': 1.0, 'Jul': 0.92},  # Biscuits for holidays
    'chips': {'Jul': 1.10, 'Aug': 1.08, 'Apr': 1.0, 'Dec': 1.05},  # Snacks in summer
    'ketchup': {'Jul': 1.08, 'Apr': 1.0, 'Dec': 1.02, 'Jan': 1.0},  # BBQ season (summer)
    'huile': {'Apr': 1.0, 'Jul': 1.05, 'Dec': 1.02, 'Jan': 1.02},  # Oil stable
    'farine': {'Apr': 1.0, 'Dec': 1.05, 'Jan': 1.02, 'Jul': 0.98},  # Flour for baking
    'ail': {'Apr': 1.08, 'Jul': 0.90, 'Dec': 1.10, 'Jan': 1.05},  # Garlic seasonal
    'carotte': {'Apr': 0.95, 'Jul': 1.08, 'Dec': 1.12, 'Jan': 1.05},  # Root veggies in winter
    'epinard': {'Apr': 1.05, 'Jul': 0.92, 'Dec': 1.10, 'Jan': 1.08},  # Greens seasonal
    'haricot': {'Apr': 1.02, 'Jul': 1.08, 'Dec': 1.05, 'Jan': 1.02},  # Beans seasonal
}

# Default seasonal factor if category not listed
DEFAULT_SEASONAL = {'Apr': 1.0, 'Dec': 1.08, 'Jan': 1.03, 'Jul': 0.95}

# Store pricing multipliers (Auchan = discount, Carrefour = mainstream)
STORE_MULTIPLIERS = {
    'Auchan': 0.95,      # 5% discount vs baseline
    'Carrefour': 1.02,   # 2% premium vs baseline
}

def extract_products_from_data():
    """Extract all product categories from current data"""
    products = defaultdict(lambda: {'stores': set(), 'count': 0})

    for store_dir in os.listdir(DATA_PATH):
        store_path = os.path.join(DATA_PATH, store_dir)
        if not os.path.isdir(store_path):
            continue

        for product_dir in os.listdir(store_path):
            product_path = os.path.join(store_path, product_dir)
            if not os.path.isdir(product_path):
                continue

            files = [f for f in os.listdir(product_path) if f.endswith('.png')]
            count = len(files)

            if count > 0:
                # Extract category from product name
                category = product_dir.rsplit('_', 1)[0] if '_' in product_dir else product_dir
                products[category]['stores'].add(store_dir)
                products[category]['count'] += count

    return products

def get_baseline_price(category):
    """Generate realistic baseline prices for French supermarket products"""
    baseline_prices = {
        'cafe': 3.99,
        'the': 2.49,
        'infusion': 3.50,
        'chocolate': 1.99,
        'pain': 1.29,
        'baguette': 0.89,
        'beurre': 4.29,
        'fromage': 5.99,
        'lait': 1.49,
        'creme': 2.99,
        'oeufs': 3.49,
        'viande': 8.99,
        'jambon': 6.99,
        'bacon': 7.49,
        'sardines': 2.49,
        'thon': 2.99,
        'sauce': 1.59,
        'ketchup': 2.19,
        'vinaigre': 1.99,
        'huile': 5.99,
        'farine': 1.49,
        'sel': 0.99,
        'sucre': 1.29,
        'bonbons': 3.49,
        'biscuits': 2.99,
        'chips': 2.49,
        'cacahuete': 3.99,
        'saucisse': 4.99,
        'jus': 3.49,
        'carrots': 1.99,
        'epinards': 2.49,
        'haricot': 2.99,
        'ail': 2.49,
    }

    # Find matching category
    for key, price in baseline_prices.items():
        if key.lower() in category.lower():
            return price + random.uniform(-0.30, 0.30)  # Slight variation

    # Default price if not found
    return 2.99 + random.uniform(-0.50, 0.50)

def get_seasonal_factor(category, month):
    """Get seasonal price multiplier for category and month"""
    # Extract month abbreviation
    month_abbr = month.split('-')[0]

    # Get seasonal factors for this category
    if category.lower() in SEASONAL_FACTORS:
        factors = SEASONAL_FACTORS[category.lower()]
    else:
        factors = DEFAULT_SEASONAL

    # Get factor for this month, or interpolate
    if month_abbr in factors:
        return factors[month_abbr]

    # Default seasonal factor
    if month_abbr in DEFAULT_SEASONAL:
        return DEFAULT_SEASONAL[month_abbr]

    return 1.0

def calculate_price(baseline_price, category, month_key, store, cumulative_inflation):
    """Calculate price with inflation and seasonal variations"""
    # Apply cumulative inflation
    inflated_price = baseline_price * (1 + cumulative_inflation)

    # Apply seasonal variation
    seasonal = get_seasonal_factor(category, month_key)
    seasonal_price = inflated_price * seasonal

    # Apply store multiplier
    store_mult = STORE_MULTIPLIERS.get(store, 1.0)
    final_price = seasonal_price * store_mult

    # Add small random variation (±1%)
    final_price *= (1 + random.uniform(-0.01, 0.01))

    return round(final_price, 2)

def generate_synthetic_data():
    """Generate 12 months of synthetic price data"""
    print("Extracting product categories from current data...")
    products = extract_products_from_data()
    print(f"Found {len(products)} product categories")

    # Generate CSV data
    rows = []
    months = list(MONTHLY_INFLATION_RATES.keys())

    print(f"\nGenerating synthetic data for {len(months)} months...")

    cumulative_inflation = 0

    for month_idx, month_key in enumerate(months):
        # Add monthly inflation to cumulative
        monthly_rate = MONTHLY_INFLATION_RATES[month_key]
        cumulative_inflation += monthly_rate

        # Generate data for each product
        for category, info in sorted(products.items()):
            baseline_price = get_baseline_price(category)

            # Generate for each store in original data
            for store in info['stores']:
                # Generate 2-4 captures per product per month per store
                num_captures = random.randint(2, 4)

                for capture_num in range(num_captures):
                    # Generate timestamp
                    day = random.randint(1, 28)
                    time = f"{random.randint(8, 20):02d}:{random.randint(0, 59):02d}"

                    month_num = list(MONTHLY_INFLATION_RATES.keys()).index(month_key) + 1

                    timestamp = f"2025-{month_num:02d}-{day:02d}T{time}:00"
                    if month_num > 12:  # Handle 2026
                        timestamp = f"2026-{month_num-12:02d}-{day:02d}T{time}:00"

                    # Calculate price
                    price = calculate_price(baseline_price, category, month_key, store, cumulative_inflation)

                    rows.append({
                        'timestamp': timestamp,
                        'product': category,
                        'store': store,
                        'baseline_price': round(baseline_price, 2),
                        'current_price': price,
                        'price_change_pct': round(((price - baseline_price) / baseline_price) * 100, 2),
                        'inflation_rate_pct': round(cumulative_inflation * 100, 2),
                        'month': month_key,
                        'currency': 'EUR'
                    })

    print(f"Generated {len(rows)} price observations")

    # Create DataFrame
    df = pd.DataFrame(rows)

    # Save to CSV
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nData saved to: {OUTPUT_PATH}")

    return df

def generate_analysis_report(df):
    """Generate analysis report from synthetic data"""
    print("\n" + "="*80)
    print("SYNTHETIC INFLATION DATA ANALYSIS")
    print("="*80)

    print(f"\nDataset Overview:")
    print(f"  Total records: {len(df)}")
    print(f"  Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"  Unique products: {df['product'].nunique()}")
    print(f"  Stores: {', '.join(df['store'].unique())}")
    print(f"  Months: {df['month'].nunique()}")

    print(f"\nPrice Statistics:")
    print(f"  Average price: €{df['current_price'].mean():.2f}")
    print(f"  Median price: €{df['current_price'].median():.2f}")
    print(f"  Min price: €{df['current_price'].min():.2f}")
    print(f"  Max price: €{df['current_price'].max():.2f}")
    print(f"  Std Dev: €{df['current_price'].std():.2f}")

    print(f"\nInflation Impact:")
    print(f"  Average price change: {df['price_change_pct'].mean():.2f}%")
    print(f"  Max price change: {df['price_change_pct'].max():.2f}%")
    print(f"  Cumulative inflation: {df['inflation_rate_pct'].max():.2f}%")

    print(f"\nStore Comparison:")
    for store in sorted(df['store'].unique()):
        store_df = df[df['store'] == store]
        print(f"  {store}: €{store_df['current_price'].mean():.2f} avg (n={len(store_df)})")

    print(f"\nTop 5 Most Expensive Products:")
    top_products = df.groupby('product')['current_price'].mean().nlargest(5)
    for idx, (prod, price) in enumerate(top_products.items(), 1):
        print(f"  {idx}. {prod}: €{price:.2f}")

    print(f"\nTop 5 Cheapest Products:")
    cheap_products = df.groupby('product')['current_price'].mean().nsmallest(5)
    for idx, (prod, price) in enumerate(cheap_products.items(), 1):
        print(f"  {idx}. {prod}: €{price:.2f}")

    print(f"\nMonthly Price Trends:")
    monthly_avg = df.groupby('month')['current_price'].mean()
    for month, price in monthly_avg.items():
        print(f"  {month}: €{price:.2f}")

    print("\n" + "="*80)

# Main execution
if __name__ == "__main__":
    print("Generating synthetic 12-month inflation data for Snipper Tool...\n")

    df = generate_synthetic_data()
    generate_analysis_report(df)

    print(f"\nFiles created:")
    print(f"  - {OUTPUT_PATH}")
    print(f"\nNext steps:")
    print(f"  - Use this CSV for data visualization")
    print(f"  - Compare with real pricing data")
    print(f"  - Train ML models on inflation trends")
    print(f"  - Demo to SaaS customers")
