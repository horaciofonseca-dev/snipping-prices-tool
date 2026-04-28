# Impact Analysis: Household Composition Annual Cost Correction

## THE ERROR

**Mixing monthly cost differences with annual budget aggregations**

### Example of Error:
- Baby costs €75.91/month
- I showed annual impact as: €17,356 - €17,280 = €76/year ❌
- Should be: €75.91 × 12 = €911/year ✅

---

## CORRECT CALCULATIONS

### SMIC (€21,000/year = €1,750/month)

**Base Household (2 adults + 1 child):**
- Monthly income: €1,750
- Monthly food cost: €303.65
- Monthly remaining: €1,446.35
- **Annual remaining: €17,356**

**+Baby (€75.91/month food cost):**
- Monthly remaining: €1,750 - €303.65 - €75.91 = €1,370.44
- **Annual remaining: €16,445**
- **Annual loss: €911** (NOT €76!)

**+Child 3-6 (€121.46/month food cost):**
- Monthly remaining: €1,750 - €303.65 - €121.46 = €1,324.89
- **Annual remaining: €15,899**
- **Annual loss: €1,457** (NOT €121!)

**+Child 7-12 (€136.64/month food cost):**
- Monthly remaining: €1,750 - €303.65 - €136.64 = €1,309.71
- **Annual remaining: €15,716**
- **Annual loss: €1,640** (NOT €136!)

**+Teenager (€288.47/month food cost):**
- Monthly remaining: €1,750 - €303.65 - €288.47 = €1,157.88
- **Annual remaining: €13,895**
- **Annual loss: €3,461** (NOT €288!)

**+Adult (€303.65/month food cost):**
- Monthly remaining: €1,750 - €303.65 - €303.65 = €1,142.70
- **Annual remaining: €13,712**
- **Annual loss: €3,644** (NOT €303!)

**+Senior (€334.01/month food cost):**
- Monthly remaining: €1,750 - €303.65 - €334.01 = €1,112.34
- **Annual remaining: €13,348**
- **Annual loss: €4,008** (NOT €334!)

---

### Median (€42,000/year = €3,500/month)

**Base Household:**
- **Annual remaining: €41,176**

**+Baby:**
- Monthly remaining: €3,500 - €303.65 - €75.91 = €3,120.44
- **Annual remaining: €37,445**
- **Annual loss: €3,731**

**+Teenager:**
- Monthly remaining: €3,500 - €303.65 - €288.47 = €2,907.88
- **Annual remaining: €34,895**
- **Annual loss: €6,281**

**+Senior:**
- Monthly remaining: €3,500 - €303.65 - €334.01 = €2,862.34
- **Annual remaining: €34,348**
- **Annual loss: €6,828**

---

## FILES REQUIRING UPDATES

### 1. **capstone/synthetic_data/generate_basket_analysis.py** 🔴 CRITICAL
**Function affected:** `create_family_squeeze_chart()`

**Current (WRONG):**
```python
smic_remaining = [17356, 17280, 17235, 17068]
median_remaining = [41176, 41100, 41055, 40888]
```

**Should be (CORRECT):**
```python
# Annual remaining budgets (correctly calculated)
smic_remaining = [17356, 16445, 15899, 13895]  # Base, +baby, +child(7-12), +teenager
median_remaining = [41176, 37445, 34895]        # Base, +baby, +teenager
```

**Change type:** Code logic correction

---

### 2. **CAPSTONE_FINAL_REPORT.md** 🔴 CRITICAL
**Sections affected:**
- Section 6.3: "Household Composition Multiplier Effect"
  - Table showing member costs and new totals
  - Narrative explaining the squeeze

**Current (EXAMPLE - WRONG):**
```
| Baby (0-2) | +€75.91 | +25% | €379.56 | 21.7% |
```

**Should be (CORRECT):**
```
The family squeeze shows annual impact:
- +Baby: -€911/year in remaining budget (not -€76)
- +Teenager: -€3,461/year in remaining budget (not -€288)
- +Senior: -€4,008/year in remaining budget (not -€334)
```

**Change type:** Data values and narrative clarification

---

### 3. **06_family_squeeze.png** 🔴 CRITICAL (VISUALIZATION)
**Current chart shows:** €17,356 → €17,280 → €17,068 (WRONG scale)

**Should show:** €17,356 → €16,445 → €15,899 → €13,895 (CORRECT annual values)

**Impact:** Chart currently makes crisis look minor (€288 loss); correct version shows real magnitude (€3,461 loss for teenager)

**Change type:** Regenerate visualization with correct data

---

### 4. **PRESENTATION_GUIDE.md** 🟠 MEDIUM
**Section affected:** Part C - Household Composition Crisis script

**Current example (WRONG):**
> "Add a teenager? Now it's €17,068 remaining."

**Should be (CORRECT):**
> "Add a teenager? Remaining budget drops from €17,356 to €13,895 annually. That's a loss of €3,461/year."

**Change type:** Update script narrative with correct annual values

---

### 5. **SPEAKER_NOTES_QUICK_REFERENCE.txt** 🟠 MEDIUM
**Section affected:** Segment 3C - Household Composition Crisis

**Current (WRONG):**
```
+Teenager: €17,068 remaining → Loss of €288/month margin
```

**Should be (CORRECT):**
```
+Teenager: €13,895 remaining → Annual loss of €3,461 (loss of €288/month × 12)
```

**Change type:** Update numerical values and clarify monthly-to-annual conversion

---

### 6. **README_PRESENTATION_ASSETS.md** 🟢 LOW
**Section affected:** Chart 06 description

**Current:** References the visualization but doesn't state values explicitly

**Should:** Update to note that chart shows correct annual impact magnitude

**Change type:** Minor clarification

---

## IMPACT SUMMARY

| File | Severity | Change Type | Impact |
|------|----------|-------------|--------|
| generate_basket_analysis.py | 🔴 CRITICAL | Code logic | Chart regeneration |
| CAPSTONE_FINAL_REPORT.md | 🔴 CRITICAL | Data values | Core findings accuracy |
| 06_family_squeeze.png | 🔴 CRITICAL | Visualization | Chart credibility |
| PRESENTATION_GUIDE.md | 🟠 MEDIUM | Script update | Presentation delivery |
| SPEAKER_NOTES.txt | 🟠 MEDIUM | Value update | Speaking points |
| README_PRESENTATION_ASSETS.md | 🟢 LOW | Clarification | Documentation |

---

## NARRATIVE IMPACT

**Critical issue:** The current chart makes household composition impact appear much smaller than reality.

**Current (WRONG):** "Adding a teenager reduces budget by €288/year"  
**Correct:** "Adding a teenager reduces budget by €3,461/year"

This affects:
- The emotional impact of the household composition section
- The credibility of the affordability crisis narrative
- The policy significance of family structure as a poverty multiplier

---

## IMPLEMENTATION STEPS

1. ✅ Create this impact analysis
2. Update generate_basket_analysis.py with correct calculations
3. Regenerate 06_family_squeeze.png visualization
4. Update CAPSTONE_FINAL_REPORT.md Section 6.3
5. Update PRESENTATION_GUIDE.md Part C
6. Update SPEAKER_NOTES_QUICK_REFERENCE.txt Segment 3C
7. Update README_PRESENTATION_ASSETS.md
8. Verify narrative coherence across all documents
9. Commit all changes to GitHub

---

**Ready to implement? Shall I proceed with all updates?**
