# Impact Analysis: Household Composition & Housing Visualization Overhaul

## Files Requiring Updates

### **1. CAPSTONE_FINAL_REPORT.md** 🔴 CRITICAL
**Current content affected:**
- Section 6: Key Findings
  - Subsection: "Household Composition Impact: The Affordability Multiplier"
  - Line ~568-600: Current data tables for household composition
  
- Section 7: Visualization Interpretation Guide
  - Chart 05 interpretation (remaining budget)
  - Chart 02 interpretation (affordability cliff)
  - Thresholds explanation
  
**Changes needed:**
- [ ] Update household composition narrative to reference NEW "Family Squeeze" visualization
- [ ] Remove €0 threshold references
- [ ] Update housing cost discussion: change from single €14.4k to range/whisker concept
- [ ] Rewrite Chart 05 interpretation (currently "remaining budget" → change to "household composition impact")
- [ ] Add section on "Housing Burden by Income" whisker chart
- [ ] Update affordability cliff narrative to match Chart 02 (which stays same)

**Narrative impact:** MAJOR - affects central finding about household composition multiplier effect

---

### **2. PRESENTATION_GUIDE.md** 🔴 CRITICAL
**Current content affected:**
- SEGMENT 3: THE DATA STORY
  - Part C: Household Composition Crisis (2 minutes)
  - Lines describing cost impacts by member type
  
**Changes needed:**
- [ ] Update Segment 3C to reference NEW "Family Squeeze" visual
- [ ] Change from text descriptions to "See the squeeze in visualization X"
- [ ] Update numbers/percentages to match new chart data
- [ ] Add interpretation guidance for visualizing housing variation

**Narrative impact:** MAJOR - affects presentation flow and visual references

---

### **3. SPEAKER_NOTES_QUICK_REFERENCE.txt** 🟠 MEDIUM
**Current content affected:**
- SEGMENT 4C: THE DEMOGRAPHIC CONSEQUENCE (household composition section)
- Lines ~200-240: Numbers and thresholds

**Changes needed:**
- [ ] Update household composition numbers
- [ ] Change threshold references (remove €0, adjust €14.4k context)
- [ ] Add visual reference: "See Family Squeeze chart slide X"

**Narrative impact:** MEDIUM - affects talk track but not core structure

---

### **4. README_PRESENTATION_ASSETS.md** 🟠 MEDIUM
**Current content affected:**
- Section: Chart descriptions and placements
- Chart 05 description: "Remaining Budget After Food"

**Changes needed:**
- [ ] Update Chart 05 description: change from "Remaining Budget" to "Household Composition Impact"
- [ ] Update Chart placement instructions (which slide shows new charts)
- [ ] Add new whisker chart placement for "Housing Burden"

**Narrative impact:** MEDIUM - affects asset documentation

---

### **5. README_DIAGRAMS.md** 🟢 LOW
**Current content affected:**
- Integration checklist (if it references charts)

**Changes needed:**
- [ ] Check if any diagram references are affected
- [ ] Update if diagrams need new charts

**Narrative impact:** LOW - mostly technical documentation

---

### **6. Python Files (Generation Scripts)** 🟠 MEDIUM
**Files:**
- `capstone/synthetic_data/generate_basket_analysis.py`

**Current code affected:**
- `create_affordability_cliff_chart()` function (Chart 02) - KEEP AS-IS
- `create_healthy_cliff_chart()` function (Chart 05) - NEEDS REWRITE

**Changes needed:**
- [ ] **Chart 02**: Keep thresholds (10%, 15%, 20%, 30%, 50%) - NO CHANGES
- [ ] **Chart 05**: DELETE current "remaining budget" chart
- [ ] Create NEW `create_family_squeeze_chart()` for household composition impact
- [ ] Create NEW `create_housing_burden_chart()` for housing variation by income

**Narrative impact:** MEDIUM - affects visualization generation

---

### **7. BASKET_ANALYSIS_REPORT.txt & CORRECTED.txt** 🟢 LOW
**Current content affected:**
- Threshold descriptions
- Housing cost explanations

**Changes needed:**
- [ ] Update threshold section if it explains €0, €14.4k, €9.6k
- [ ] Add section on housing cost variation concept

**Narrative impact:** LOW - more reference material

---

### **8. PowerPoint Presentation** 🔴 CRITICAL
**File:** `Snipper_Tool_Reality_vs_Official_Paris.pptx`

**Slides affected:**
- Slide with Chart 05 (Remaining Budget) - REPLACE with "Family Squeeze"
- Potentially slides showing household composition narrative
- Slide with Chart 02 (Affordability Cliff) - KEEP

**Changes needed:**
- [ ] Replace Chart 05 slide with new "Family Squeeze" visualization
- [ ] Add new slide for "Housing Burden by Income" whisker chart
- [ ] Update speaker notes on those slides
- [ ] Verify slide order and transitions still make sense

**Narrative impact:** MAJOR - presentation flow depends on these visuals

---

## Summary of Changes

### **Charts Being Changed:**
| Chart | Current | Status | New Name | Impact |
|-------|---------|--------|----------|--------|
| 02_affordability_cliffs.png | % of income on food | KEEP | Same | No change needed |
| 05_healthy_cliff.png | Remaining budget bars | **DELETE/REPLACE** | Family Squeeze | All 3 income brackets |
| NEW | - | CREATE | Housing Burden (Whisker) | Shows rent variation |

### **Thresholds Being Changed:**
| Current | Status | New Approach |
|---------|--------|--------------|
| €0 threshold | USELESS | Remove - no data intersects |
| €9.6k threshold | BORDERLINE | Keep but explain as "survival only" |
| €14.4k threshold | GOOD | Keep but add housing range context |
| 5 threshold lines (Chart 02) | GOOD | Keep as-is (10%, 15%, 20%, 30%, 50%) |

---

## Narrative Coherence Check

**Current narrative thread:**
1. Official statistics hide the real cost (gap: €234.98)
2. Real families spend much more (€303.65 vs €68.67)
3. This creates affordability cliffs by income
4. **Household composition MULTIPLIES the problem** ← KEY FINDING
5. Families rationally choose smaller families (demographic consequence)

**Risk of incoherence:**
- If we don't clearly visualize the "multiplier effect" in charts, the narrative breaks
- Current Chart 05 doesn't show this multiplication
- New "Family Squeeze" chart FIXES this

**Narrative flow with new charts:**
✅ Shows magnitude (existing charts)
✅ Shows distribution by income (existing charts)  
✅ Shows impact of family growth (NEW chart)
✅ Shows housing variation as context (NEW chart)

---

## Affected Narrative Sections

### In CAPSTONE_FINAL_REPORT.md:
- **Section 6.3** - Household Composition Impact
- **Section 7** - Visualization Guide
- **Appendix** - Data Summary

### In PRESENTATION_GUIDE.md:
- **Segment 3C** - The Household Composition Crisis
- **Segment 4C** - The Demographic Consequence

### In SPEAKER_NOTES.txt:
- **Segment 4B/4C** - Invisibility + Demographic sections

---

## Implementation Order

1. ✅ **Approve this impact analysis**
2. Create new Python functions for new charts
3. Update generate_basket_analysis.py
4. Regenerate all visualizations
5. Update CAPSTONE_FINAL_REPORT.md (Section 6.3, 7)
6. Update PRESENTATION_GUIDE.md (Segment 3C references)
7. Update SPEAKER_NOTES_QUICK_REFERENCE.txt
8. Update PowerPoint slides
9. Update README_PRESENTATION_ASSETS.md
10. Final narrative coherence review
11. Commit & push to GitHub

---

**Ready to proceed? Any files/sections you'd like adjusted before implementation?**
