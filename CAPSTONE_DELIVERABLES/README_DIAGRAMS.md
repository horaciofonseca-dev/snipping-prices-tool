# Snipper Tool Diagrams - Implementation Guide

## Overview

This folder contains Mermaid-based process diagrams showcasing the Snipper Tool architecture and data collection pipeline in two formats:

1. **DIAGRAMS_ARCHITECTURE.md** - Detailed technical diagrams (report-friendly)
2. **DIAGRAMS_PRESENTATION.md** - Simplified presentation diagrams (slide-friendly)

---

## Files & Locations

### Detailed Architecture (For Reports)
- **File:** `DIAGRAMS_ARCHITECTURE.md`
- **Contains:** 3 comprehensive flowcharts
  - Diagram 1: System Architecture (end-to-end, technical depth)
  - Diagram 2: Data Collection Pipeline (workflow stages)
  - Diagram 3: Affordability Analysis Logic (decision tree)
- **Best For:** 
  - CAPSTONE_FINAL_REPORT.md appendices
  - Technical documentation
  - Letter-size document embedding
  - Detailed explanation of system mechanics

### Presentation Version (For Slides)
- **File:** `DIAGRAMS_PRESENTATION.md`
- **Contains:** 5 simplified flowcharts
  - Slide Diagram 1: Receipt → Data (simple pipeline)
  - Slide Diagram 2: Three Baskets (visual comparison)
  - Slide Diagram 3: Income Impact (critical affordability)
  - Slide Diagram 4: Household Multiplier (the crisis factor)
  - Slide Diagram 5: Data to Decision (one-pager impact)
- **Best For:**
  - PowerPoint presentation slides
  - Quick visual communication
  - Executive summaries
  - Audience engagement (color-coded, simple)

---

## How to Use These Diagrams

### Option 1: GitHub Markdown Rendering (Recommended)
Mermaid diagrams render automatically on GitHub and in most modern markdown viewers:

1. Save the `.md` files to your repository
2. View on GitHub - diagrams render automatically
3. Reference in your capstone report with links

**In your CAPSTONE_FINAL_REPORT.md:**
```markdown
[See detailed architecture diagrams in DIAGRAMS_ARCHITECTURE.md]
[See presentation-ready diagrams in DIAGRAMS_PRESENTATION.md]
```

### Option 2: Convert to Images (PNG/SVG)

**Using Mermaid CLI:**
```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i DIAGRAMS_ARCHITECTURE.md -o diagrams_architecture.png
```

**Using Online Tool:**
1. Visit https://mermaid.live
2. Copy-paste diagram code from `.md` files
3. Export as PNG or SVG
4. Save to CAPSTONE_DELIVERABLES/diagrams/

### Option 3: Direct PowerPoint Integration

For Snipper_Tool_Reality_vs_Official_Paris.pptx:

1. Open https://mermaid.live
2. Copy each "Slide Diagram" code
3. Export as PNG (1920×1080 recommended)
4. Insert into PowerPoint slides
5. Place diagrams on:
   - Slide 2: Diagram 1 (Receipt → Data)
   - Slide 11: Diagram 2 (Three Baskets)
   - Slide 13: Diagram 3 (Income Impact)
   - Slide 15: Diagram 4 (Household Multiplier)
   - Slide 24: Diagram 5 (Data to Decision)

---

## Diagram Specifications

### For Letter-Size Documents (DIAGRAMS_ARCHITECTURE.md)

| Diagram | Height | Width | Use Case |
|---------|--------|-------|----------|
| System Architecture | 6 inches | 7 inches | Appendix A - Technical Overview |
| Data Pipeline | 5 inches | 8 inches | Section 3 - Data Collection |
| Affordability Logic | 6 inches | 7 inches | Section 6 - Analysis Methodology |

**Printing Tips:**
- Set page orientation: **Landscape** for pipeline diagrams
- Set page orientation: **Portrait** for architecture & logic diagrams
- Use print scaling: **Fit to Page**

### For Slide Presentations (DIAGRAMS_PRESENTATION.md)

| Diagram | Aspect | Complexity | Slide |
|---------|--------|-----------|-------|
| Receipt → Data | 16:9 | Very Simple | 2 |
| Three Baskets | 16:9 | Simple | 11 |
| Income Impact | 16:9 | Moderate | 13 |
| Household Multiplier | 16:9 | Moderate | 15 |
| Data to Decision | 16:9 | Simple | 24 (closing) |

**Presentation Tips:**
- Use **light background** (white/light gray)
- All diagrams are **color-coded** (red=crisis, yellow=caution, green=good)
- Audience can **quickly absorb** message through colors
- Each diagram fits comfortably on one slide with title

---

## Color Coding Legend

Used consistently across all diagrams:

| Color | Hex Code | Meaning | Status |
|-------|----------|---------|--------|
| 🔴 Red | #C62828 | Crisis/Critical | Impossible/Unaffordable |
| 🟡 Yellow | #F57F17 | Caution/Tight | Difficult/Manageable |
| 🟢 Green | #2E7D32 | Good/Acceptable | Manageable/Good/Excellent |
| Light Blue | #E3F2FD | Data Input | Collection Phase |
| Light Orange | #FFF3E0 | Processing | OCR/Validation |
| Light Purple | #F3E5F5 | Analysis | Calculation Phase |
| Light Pink | #FCE4EC | Output | Reports/Insights |

---

## Integration Checklist

- [ ] **DIAGRAMS_ARCHITECTURE.md** added to CAPSTONE_DELIVERABLES/
- [ ] **DIAGRAMS_PRESENTATION.md** added to CAPSTONE_DELIVERABLES/
- [ ] **README_DIAGRAMS.md** (this file) added to CAPSTONE_DELIVERABLES/
- [ ] Reference diagrams in CAPSTONE_FINAL_REPORT.md (Section 3 & Appendix)
- [ ] Add diagram slides to Snipper_Tool_Reality_vs_Official_Paris.pptx
  - [ ] Slide 2: Receipt → Data
  - [ ] Slide 11: Three Baskets
  - [ ] Slide 13: Income Impact
  - [ ] Slide 15: Household Multiplier
  - [ ] Slide 24: Data to Decision
- [ ] Commit all files to GitHub
- [ ] Verify diagrams render on GitHub web view

---

## Technical Notes

**Mermaid Syntax:**
- Diagrams use **Mermaid flowchart (graph)** syntax
- Compatible with: GitHub, GitLab, Notion, Obsidian, Hugo, Jekyll, etc.
- No installation required for GitHub rendering
- All diagrams are **plain text** - version control friendly

**Accessibility:**
- All nodes include **emoji + text labels** (not relying on color alone)
- Text descriptions work for screen readers
- High-contrast colors for visibility

**File Format:**
- Stored as `.md` (Markdown) files
- Mermaid code blocks: \`\`\`mermaid ... \`\`\`
- Easy to edit and version control

---

## Recommended Placement in Capstone Report

### CAPSTONE_FINAL_REPORT.md

```
Section 3: Data Collection Pipeline
├── Text explanation of process
└── [Insert DIAGRAMS_ARCHITECTURE.md - Diagram 2: Data Pipeline]

Section 6: Key Findings
├── Basket comparison
├── [Insert DIAGRAMS_PRESENTATION.md - Diagram 2: Three Baskets]
├── Income impact analysis
└── [Insert DIAGRAMS_PRESENTATION.md - Diagram 3: Income Impact]

APPENDIX A: System Architecture
├── Technical overview
├── [Insert DIAGRAMS_ARCHITECTURE.md - Diagram 1: System Architecture]
└── [Insert DIAGRAMS_ARCHITECTURE.md - Diagram 3: Analysis Logic]
```

### Snipper_Tool_Reality_vs_Official_Paris.pptx

```
Slide 2: The Tool
└── [Insert DIAGRAMS_PRESENTATION.md - Slide Diagram 1]

Slide 11: Three Baskets
└── [Insert DIAGRAMS_PRESENTATION.md - Slide Diagram 2]

Slide 13: Affordability Cliffs
└── [Insert DIAGRAMS_PRESENTATION.md - Slide Diagram 3]

Slide 15: Household Composition Impact
└── [Insert DIAGRAMS_PRESENTATION.md - Slide Diagram 4]

Slide 24: Closing / Data Summary
└── [Insert DIAGRAMS_PRESENTATION.md - Slide Diagram 5]
```

---

## Viewing & Editing

### View Diagrams Online (No Account Needed)
1. Go to https://mermaid.live
2. Copy entire `.md` file contents
3. Paste into editor
4. Diagrams render live
5. Export as PNG/SVG/PDF

### Edit Diagrams
1. Open `.md` file in any text editor
2. Modify Mermaid code (see syntax: https://mermaid.js.org)
3. Save
4. GitHub auto-renders updated version

### Generate High-Resolution Images
```bash
# Using mermaid-cli (optional, for PNG export)
npm install -g @mermaid-js/mermaid-cli
mmdc -i DIAGRAMS_PRESENTATION.md -o output/ --scale 2
```

---

## Questions & Support

For modifying diagrams:
- Mermaid Docs: https://mermaid.js.org
- Flowchart Tutorial: https://mermaid.js.org/syntax/flowchart.html
- Live Editor: https://mermaid.live

---

**Created:** April 27, 2026  
**For:** CAPSTONE Data Analytics Project  
**Author:** Horacio Fonseca  
**Professor:** Jobany Heredia Rico  
**Institution:** Miami Dade College
