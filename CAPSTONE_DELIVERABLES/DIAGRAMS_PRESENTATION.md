# Snipper Tool - Presentation-Friendly Diagrams

## Slide Diagram 1: From Receipt to Data (Simple Pipeline)

```mermaid
graph LR
    A["📸<br/>Receipt<br/>Photo"] -->|OCR| B["🤖<br/>Extract<br/>Data"]
    B -->|Validate| C["✓<br/>Clean<br/>Data"]
    C -->|Aggregate| D["📊<br/>2,163<br/>Points"]
    D -->|Analyze| E["💡<br/>Real Cost<br/>vs Official"]
    
    style A fill:#E3F2FD,stroke:#1976D2,stroke-width:3px
    style B fill:#FFF3E0,stroke:#F57C00,stroke-width:3px
    style C fill:#E8F5E9,stroke:#388E3C,stroke-width:3px
    style D fill:#F3E5F5,stroke:#7B1FA2,stroke-width:3px
    style E fill:#FCE4EC,stroke:#C2185B,stroke-width:3px
```

---

## Slide Diagram 2: The Three Baskets (Visual Comparison)

```mermaid
graph TB
    A["Official<br/>INSEE Basket"] --> B1["€68.67<br/>monthly"]
    A --> B2["13 items<br/>Survival only"]
    
    C["Real Complete<br/>Family Basket"] --> D1["€303.65<br/>monthly"]
    C --> D2["34 items<br/>Reality check"]
    
    E["Healthy<br/>Quality Basket"] --> F1["€383.58<br/>monthly"]
    E --> F2["41 items<br/>Health focus"]
    
    B1 --> X["The Gap:<br/>€234.98 more<br/>+342%"]
    D1 --> X
    
    X --> Y["Problem:<br/>Official stats<br/>are blind"]
    
    style A fill:#FFCDD2,stroke:#C62828
    style C fill:#FFF9C4,stroke:#F57F17
    style E fill:#C8E6C9,stroke:#2E7D32
    style X fill:#FFCCBC,stroke:#E64A19,stroke-width:3px
    style Y fill:#FCE4EC,stroke:#C2185B,stroke-width:3px
```

---

## Slide Diagram 3: Income Impact (Critical Insight)

```mermaid
graph TB
    subgraph Income["Income Levels in Paris"]
        A["SMIC<br/>€21k/year"]
        B["Low Income<br/>€28k/year"]
        C["Median<br/>€42k/year"]
        D["Upper<br/>€65k/year"]
    end
    
    subgraph Status["Affordability Status"]
        E["🔴 CRISIS<br/>17% of income"]
        F["🟡 TIGHT<br/>13% of income"]
        G["🟢 GOOD<br/>9% of income"]
        H["🟢 EXCELLENT<br/>6% of income"]
    end
    
    A -->|Real Basket| E
    B -->|Real Basket| F
    C -->|Real Basket| G
    D -->|Real Basket| H
    
    E --> I["Cannot afford<br/>housing +<br/>food together"]
    F --> J["Manageable<br/>but tight"]
    G --> K["Healthy<br/>eating<br/>possible"]
    H --> K
    
    style A fill:#FFCDD2
    style B fill:#FFE0B2
    style C fill:#C8E6C9
    style D fill:#C8E6C9
    style E fill:#C62828,color:#fff,stroke-width:3px
    style F fill:#F57F17,color:#fff,stroke-width:3px
    style G fill:#2E7D32,color:#fff,stroke-width:3px
    style H fill:#1B5E20,color:#fff,stroke-width:3px
    style I fill:#FFCDD2,stroke:#C62828,stroke-width:2px
    style J fill:#FFE0B2,stroke:#F57F17,stroke-width:2px
    style K fill:#C8E6C9,stroke:#2E7D32,stroke-width:2px
```

---

## Slide Diagram 4: Household Composition Multiplier (The Crisis Factor)

```mermaid
graph TB
    A["Base Family<br/>2 adults + 1 child<br/>€303.65/month"]
    
    A --> B1["+ Baby<br/>€75.91"]
    A --> B2["+ Teenager<br/>€288.47"]
    A --> B3["+ Senior<br/>€334.01"]
    
    B1 --> C1["New total:<br/>€379.56<br/>21.7% SMIC<br/>income"]
    B2 --> C2["New total:<br/>€592.12<br/>33.8% SMIC<br/>income"]
    B3 --> C3["New total:<br/>€637.66<br/>36.4% SMIC<br/>income"]
    
    C1 --> D["Still Tight<br/>but possible"]
    C2 --> D
    C3 --> E["🔴 IMPOSSIBLE<br/>Must choose:<br/>Food OR Rent"]
    
    style A fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px
    style B1 fill:#C8E6C9
    style B2 fill:#FFE0B2
    style B3 fill:#FFCDD2
    style C1 fill:#C8E6C9
    style C2 fill:#FFE0B2
    style C3 fill:#FFCDD2
    style D fill:#FFF9C4,stroke:#F57F17,stroke-width:2px
    style E fill:#FFCDD2,stroke:#C62828,stroke-width:3px
```

---

## Slide Diagram 5: From Data to Decision (One-Pager Impact)

```mermaid
graph LR
    A["📊 Data<br/>Collection"] --> B["🔍 Analysis"]
    B --> C["💡 Insight"]
    C --> D["🎯 Action"]
    
    A --> A1["2,163 prices<br/>55 categories<br/>12 months"]
    B --> B1["€234.98 gap<br/>Official vs Real<br/>342% difference"]
    C --> C1["Official statistics<br/>are incomplete<br/>Policy is blind"]
    D --> D1["Need higher wages<br/>Need better policy<br/>Based on real data"]
    
    style A fill:#E3F2FD,stroke:#1976D2,stroke-width:3px
    style B fill:#FFF3E0,stroke:#F57C00,stroke-width:3px
    style C fill:#F3E5F5,stroke:#7B1FA2,stroke-width:3px
    style D fill:#FCE4EC,stroke:#C2185B,stroke-width:3px
```

---

## Usage Notes

**For Presentations:**
- Use **Slide Diagrams 1-5** (simplified, colorful, easy to read)
- Each diagram fits well on one slide with title and callouts
- Color coding helps audience follow logic quickly

**For Reports:**
- Use **DIAGRAMS_ARCHITECTURE.md** detailed diagrams
- Diagrams 1-3 provide technical depth
- Can be embedded in documentation or appendices

**Diagram Meanings:**
- 🔴 Red = Crisis/Problem
- 🟡 Yellow = Caution/Difficult
- 🟢 Green = Good/Manageable
- Color intensity = severity level
