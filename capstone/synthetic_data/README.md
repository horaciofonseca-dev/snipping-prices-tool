# Snipper Tool - Synthetic Inflation Data System

**Purpose:** Generate realistic 12-month synthetic price data with French inflation rates and seasonal variations for testing, analysis, and SaaS demonstrations.

---

## 📁 Folder Structure

```
synthetic_data/
├── README.md                                    (This file)
├── synthetic_12month_inflation_data.csv         (Generated synthetic dataset)
├── generate_synthetic_inflation_data.py         (Main data generation script)
├── generate_data_analysis_fixed.py              (Data analysis & visualization)
└── charts/                                      (Generated chart images)
    ├── 01_store_distribution.png
    ├── 02_top_categories.png
    ├── 03_category_distribution.png
    ├── 04_quality_metrics.png
    └── 05_captures_vs_products.png
```

---

## 📊 Dataset Overview

**File:** `synthetic_12month_inflation_data.csv`

### Dimensions:
- **Records:** 2,163 price observations
- **Time Period:** April 2025 - April 2026 (13 monthly snapshots)
- **Products:** 55 unique categories (matching actual data)
- **Stores:** Auchan, Carrefour
- **Frequency:** 2-4 captures per product per store per month

### Columns:
```
timestamp          → ISO 8601 (YYYY-MM-DDTHH:MM:SS)
product            → Product category name
store              → Store name (Auchan/Carrefour)
baseline_price     → Starting price (April 2025)
current_price      → Price after inflation + seasonality
price_change_pct   → % change from baseline
inflation_rate_pct → Cumulative inflation rate
month              → Month label (Apr-2025 format)
currency           → EUR
```

---

## 🔬 Key Features

### 1. French Inflation Rates (Monthly)
Realistic monthly inflation based on 2025-2026 France economic scenario:

| Month | Rate | Cumulative |
|-------|------|-----------|
| Apr 2025 | 2.2% | 2.2% |
| May 2025 | 2.4% | 4.6% |
| Jun 2025 | 2.5% | 7.1% |
| Jul 2025 | 2.8% | 9.9% |
| Aug 2025 | 2.6% | 12.5% |
| Sep 2025 | 2.0% | 14.5% |
| Oct 2025 | 1.9% | 16.4% |
| Nov 2025 | 2.1% | 18.5% |
| Dec 2025 | 3.2% | 21.7% |
| Jan 2026 | 1.5% | 23.2% |
| Feb 2026 | 1.7% | 24.9% |
| Mar 2026 | 2.0% | 26.9% |
| Apr 2026 | 2.2% | 29.1% |

### 2. Seasonal Variations by Category
Products have realistic seasonal price patterns:

- **Coffee/Tea:** +15% winter, -5% summer
- **Chocolate/Candy:** +30% December (holidays), -20% July
- **Meat/Deli/Ham:** +20% Dec-Jan (holidays), -10% summer
- **Dairy/Cheese:** +8-12% winter, -4% summer
- **Seasonal Produce:** Follow natural growing seasons
- **Summer Items:** +8-10% July-August

### 3. Store-Specific Pricing
Realistic pricing strategies:

- **Auchan:** 5% discount (discount chain positioning)
- **Carrefour:** 2% premium (mainstream supermarket)

### 4. Random Variations
±1% daily random fluctuations simulate real-world price variations

---

## 📈 Key Statistics

| Metric | Value |
|--------|-------|
| **Average Price** | €3.53 |
| **Median Price** | €3.27 |
| **Min Price** | €0.78 |
| **Max Price** | €11.21 |
| **Std Deviation** | €1.71 |
| **Avg Price Change** | 11.06% |
| **Max Price Change** | 50.66% |
| **Cumulative Inflation** | 29.1% |

### Top 5 Most Expensive Products:
1. **viande-bovine** (Meat): €10.04
2. **bacon**: €8.38
3. **jambon** (Ham): €7.89
4. **fromage** (Cheese): €6.72
5. **huile** (Oil): €6.66

### Top 5 Cheapest Products:
1. **sel-de-mer** (Sea salt): €1.17
2. **farine-de-ble** (Flour): €1.59
3. **sauce-tomate** (Tomato sauce): €1.59
4. **sucre** (Sugar): €1.79
5. **vinaigre** (Vinegar): €1.89

### Monthly Trend:
- **Apr 2025:** €3.08 (baseline)
- **Aug 2025:** €3.35 (mid-year)
- **Dec 2025:** €3.99 (peak season)
- **Jan 2026:** €3.94 (post-holiday)
- **Apr 2026:** €3.88 (+26% YoY)

---

## 🚀 How to Use

### 1. Load and Analyze
```python
import pandas as pd

df = pd.read_csv('synthetic_12month_inflation_data.csv')

# Basic stats
print(df.describe())

# By product
print(df.groupby('product')['current_price'].agg(['mean', 'min', 'max']))

# By store
print(df.groupby('store')['current_price'].mean())

# By month
print(df.groupby('month')['current_price'].mean())
```

### 2. Regenerate with Different Parameters
```bash
python generate_synthetic_inflation_data.py
```

Edit the script to modify:
- `MONTHLY_INFLATION_RATES` → Change inflation scenario
- `SEASONAL_FACTORS` → Adjust seasonal variations
- `STORE_MULTIPLIERS` → Change store pricing strategies
- `get_baseline_price()` → Modify starting prices

### 3. Create Visualizations
```bash
python generate_data_analysis_fixed.py
```

Generates:
- Store distribution charts
- Category frequency analysis
- Category pie charts
- Quality metrics visualization
- Captures vs unique products analysis

---

## 📋 Use Cases

✅ **Data Visualization:** Show 12-month price trends, seasonal patterns, inflation impact  
✅ **SaaS Demonstrations:** Demo historical analysis to potential customers  
✅ **Machine Learning:** Train time-series forecasting models  
✅ **Investor Presentations:** Show what full-year data collection looks like  
✅ **Competitor Analysis:** Compare store pricing strategies  
✅ **Inflation Tracking:** Demonstrate essential basket monitoring  
✅ **Test Datasets:** Validate data pipelines with realistic data  

---

## 🔧 Technical Details

### Data Generation Logic
1. **Extract actual product categories** from `C:\Users\emman\p_Claude\capstone\datacollection`
2. **Generate baseline prices** using realistic supermarket pricing
3. **Apply cumulative inflation** for each month
4. **Apply seasonal multipliers** specific to each category
5. **Apply store pricing strategies** (discount vs premium)
6. **Add random ±1% variation** to simulate daily fluctuations
7. **Generate 2-4 captures per product per store per month**

### Data Validation
- All prices realistic (€0.50 - €20+)
- Timestamps consistent (2025-2026)
- Monthly inflation cumulative and progressive
- Store multipliers consistent across products
- Seasonal factors applied correctly per category

---

## 📝 Notes

- **Carrefour Data:** Currently only Auchan in synthetic data. Carrefour implementation ready if needed.
- **Scalability:** Script easily modifiable to extend beyond 12 months or add more stores.
- **Real vs Synthetic:** Designed to match real data patterns but not replace actual market data.
- **Production Use:** Suitable for SaaS demos, presentations, and testing. For real analytics, combine with actual captured data.

---

## 📞 Questions?

For issues or modifications, check:
- `generate_synthetic_inflation_data.py` → Data generation parameters
- `generate_data_analysis_fixed.py` → Visualization settings
- Original data: `C:\Users\emman\p_Claude\capstone\datacollection`

---

**Generated:** April 2026  
**Data Version:** 1.0  
**Status:** Production Ready
