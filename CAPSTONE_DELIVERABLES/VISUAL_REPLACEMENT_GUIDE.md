# Manual Visualization Replacement Guide

**Date:** April 28, 2026  
**Status:** All visualizations regenerated with CORRECTED per-capita methodology  

---

## IMPORTANT: Correct Visualizations to Use

All visualizations have been regenerated with the **CORRECTED per-capita methodology** for household composition analysis. The files in `C:\Users\emman\p_Claude\devs\snipper_tool\CAPSTONE_DELIVERABLES\` are the authoritative versions.

### Slides That Need Visualization Updates

| Slide | Chart File | Current File | Description |
|-------|-----------|--------------|-------------|
| **4** | `01_basket_comparison.png` | Image in CAPSTONE_DELIVERABLES | The Gap: Official (€69) vs Real (€304) vs Healthy (€384) |
| **6** | `02_affordability_cliffs.png` | Image in CAPSTONE_DELIVERABLES | Affordability Cliffs by Income Level (color zones) |
| **9** | `03_gap_analysis.png` | Image in CAPSTONE_DELIVERABLES | Gap Analysis: What's Missing from official basket |
| **11** | `04_basket_composition.png` | Image in CAPSTONE_DELIVERABLES | Basket Composition: 13 vs 34 vs 41 items |
| **12** | `05_healthy_cliff.png` | Image in CAPSTONE_DELIVERABLES | Healthy Cliff: Remaining budget after health costs |
| **15** | `06_family_squeeze.png` | **[CORRECTED]** | Family Squeeze: Per-capita methodology (€117.74/month teenager) |
| **16** | `07_housing_burden.png` | Image in CAPSTONE_DELIVERABLES | Housing Burden: Cost variation by income |
| **25** | `08_complete_budget_reality.png` | **[CORRECTED]** | Complete Budget Reality: All 12 essential costs, SMIC €74 deficit |

---

## How to Manually Update in PowerPoint

### Step-by-Step Instructions

1. **Open Presentation**
   - File: `Snipper_Tool_Reality_vs_Official_Paris.pptx`
   - Location: `C:\Users\emman\p_Claude\devs\snipper_tool\CAPSTONE_DELIVERABLES\`

2. **For Each Slide (4, 6, 9, 11, 12, 15, 16, 25):**

   a. Navigate to the slide
   
   b. Click on the current chart/image to select it
   
   c. Delete it (Press Delete key)
   
   d. Click Insert → Pictures → This Device
   
   e. Navigate to: `C:\Users\emman\p_Claude\devs\snipper_tool\CAPSTONE_DELIVERABLES\`
   
   f. Select the corresponding PNG file from the table above
   
   g. Click Insert
   
   h. Resize to fit the slide (typically 9" wide × 5" tall, starting at 0.5" left, 1.5" top)

---

## Critical Corrections in Updated Visualizations

### Slide 15: Family Squeeze Chart (06_family_squeeze.png)

**What Changed:**
- **OLD (WRONG):** Teenager cost €288.47/month = €3,461/year
- **NEW (CORRECT):** Teenager cost €117.74/month = €1,413/year

**Why:**
- Per-capita decomposition: €303.65 base ÷ 2.45 adult-equivalents = €123.94/month per AE
- Teenager multiplier: 0.95 × €123.94 = €117.74/month
- This reflects realistic consumption patterns, not household multiplication

**Impact on Chart:**
- Remaining budgets for SMIC family: Base €17,356 → +Teen €15,943 (loss of €1,413, not €3,461)
- Remaining budgets for Median family: Base €38,356 → +Teen €36,943 (loss of €1,413, not €6,281)

### Slide 25: Complete Budget Reality (08_complete_budget_reality.png)

**What Changed:**
- All 12 essential cost categories shown side-by-side
- SMIC family: €1,824 total costs vs €1,750 income = **€74/month deficit**
- Median family: €2,249 total costs vs €3,500 income = **€1,251/month surplus**

**Critical Message:**
- SMIC families cannot survive on SMIC income alone
- Government transfers (CAF, housing allowance) are **structural necessity**, not supplemental help
- Structural deficit remains even after food cost correction

---

## All Member Costs (Corrected Per-Capita)

| Member Type | Multiplier | Monthly Cost | Annual Cost | Notes |
|---|---|---|---|---|
| Baby (0-2) | 0.25 | +€30.98 | +€372 | Infant formula, diapers |
| Child (3-6) | 0.40 | +€49.58 | +€595 | Toddler/preschool |
| Child (7-12) | 0.45 | +€55.77 | +€669 | School-age (base) |
| Teenager | 0.95 | +€117.74 | +€1,413 | Adult-size appetite |
| Adult | 1.0 | +€123.94 | +€1,487 | Additional adult |
| Senior | 1.10 | +€136.33 | +€1,636 | Specialized dietary needs |

**Base:** 2 adults + 1 child (age 7-12) = €303.65/month  
**Per-capita:** €123.94/month per adult-equivalent (2.45 total)

---

## Files in CAPSTONE_DELIVERABLES

All 11 visualizations are consolidated here:

```
CAPSTONE_DELIVERABLES/
├── 01_basket_comparison.png (70.5 KB)
├── 02_affordability_cliffs.png (116.6 KB)
├── 03_gap_analysis.png (77.7 KB)
├── 04_basket_composition.png (344.6 KB)
├── 05_healthy_cliff.png (130.1 KB)
├── 06_family_squeeze.png (192.7 KB) [CORRECTED]
├── 06_household_cost_impact.png (238.2 KB) [Alternative]
├── 07_affordability_by_composition.png (378.3 KB) [Alternative]
├── 07_housing_burden.png (142.5 KB)
├── 08_complete_budget_reality.png (295.5 KB) [CORRECTED]
├── 08_remaining_budget_composition.png (252.2 KB) [Alternative]
└── Snipper_Tool_Reality_vs_Official_Paris.pptx
```

---

## Verification Checklist

After updating visualizations, verify:

- [ ] Slide 4: Shows €69 vs €304 gap clearly
- [ ] Slide 6: Color zones visible (green/yellow/red affordability)
- [ ] Slide 9: Stacked bar showing gap breakdown
- [ ] Slide 11: Three pie charts (13, 34, 41 items)
- [ ] Slide 12: Remaining budget after healthy basket costs
- [ ] Slide 15: **Family Squeeze shows €117.74 for teenager** (corrected)
- [ ] Slide 16: Housing cost whisker chart
- [ ] Slide 25: **Complete budget shows SMIC €74 deficit** (corrected)

---

## Python Scripts (All Updated)

The following scripts have been updated with correct per-capita methodology:

| Script | Location | What It Does |
|--------|----------|--------------|
| `household_composition_impact.py` | `capstone/synthetic_data/` | Analyzes per-capita member costs |
| `generate_basket_analysis.py` | `capstone/synthetic_data/` | Generates all 8 core visualizations |
| `generate_complete_budget_visualization.py` | `capstone/synthetic_data/` | Generates complete budget reality chart |
| `generate_household_visualizations.py` | `capstone/synthetic_data/` | Generates household composition charts |

All scripts are committed to git with the per-capita corrections.

---

## Documentation (All Updated)

| Document | Updated Sections |
|----------|------------------|
| `CAPSTONE_FINAL_REPORT.md` | 6.3 - Member costs and family squeeze |
| `CAPSTONE_FINAL_REPORT_GOOGLE_DOCS_READY.md` | Same as above |
| `PRESENTATION_GUIDE.md` | Part C - Household composition speaking notes |
| `SPEAKER_NOTES_QUICK_REFERENCE.txt` | Segment 3C - All member cost references |

---

## Why Manual Update?

Due to library constraints with PPTX file manipulation on Windows, the visualizations must be manually updated in PowerPoint. This is a one-time operation that takes approximately 10-15 minutes for all 8 slides.

**All corrected visualization files are ready to use** - they just need to be inserted into the presentation slides listed above.

---

**Status:** Ready for final presentation with all corrections applied
