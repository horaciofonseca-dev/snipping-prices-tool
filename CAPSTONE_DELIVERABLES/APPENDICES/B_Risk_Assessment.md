# Appendix B: Risk Assessment

**Snippet Tool - Technical, Business, and Legal Risk Analysis**  
**Date**: April 2026  

---

## Executive Summary

Snippet Tool faces **manageable risks** across three domains: technical (OCR accuracy, system stability), business (market adoption, competition), and legal (terms of service, data privacy). All identified risks have clear mitigation strategies.

**Overall Risk Level**: MEDIUM-LOW (typical for early-stage software product)

---

## Technical Risks

### 1. OCR Accuracy Degradation

**Risk**: EasyOCR confidence scores vary based on image quality, creating inconsistent price detection (85-95% accuracy)

**Severity**: MEDIUM  
**Likelihood**: HIGH (inherent to OCR technology)

**Impact**:
- User frustration with false positives
- Data quality issues (wrong prices in dataset)
- Customer churn if accuracy drops below 85%

**Mitigation Strategies**:
1. **Multi-price selection dialog**: User chooses correct price when multiple detected
2. **Confidence scoring**: Show confidence percentage to user
3. **Image preprocessing**: Crop region, optimize contrast before OCR
4. **Language-specific models**: French/English-specific training improves accuracy
5. **Fallback to manual entry**: User can override OCR result
6. **Quality metrics**: Track OCR accuracy per store/product (identify problem patterns)

**Monitoring Plan**:
- Log OCR confidence scores
- Quarterly accuracy reports
- Customer feedback on false positives
- Flag products with <80% average confidence

---

### 2. Dependency Stability (PyQt5, EasyOCR, torch)

**Risk**: Critical dependencies (torch 2.0.0, numpy 1.26.x) may have breaking updates or security vulnerabilities

**Severity**: MEDIUM-HIGH  
**Likelihood**: MEDIUM

**Historical Precedent**: torch 2.1+ broke Windows torch.lib.c10.dll compatibility

**Impact**:
- App crashes on new Windows setups
- Security vulnerabilities in old library versions
- Maintenance burden to update compatibility

**Mitigation Strategies**:
1. **Pin strict versions**: Keep requirements.txt locked (torch==2.0.0, numpy==1.26.4)
2. **Version monitoring**: Monthly check for critical security updates in pinned versions
3. **Testing regimen**: Test any updates in isolated environments before production
4. **Fallback strategy**: Maintain python 3.10 compatible backup if 3.11 breaks
5. **Documentation**: Record why specific versions chosen (for future maintainers)

**Long-term Plan**:
- Containerization (Docker) to freeze exact dependencies
- GitHub Actions for automated testing of new dependency versions

---

### 3. Cross-Platform Compatibility

**Risk**: Application tested primarily on Windows; Linux/Mac may have GUI issues

**Severity**: MEDIUM  
**Likelihood**: MEDIUM

**Potential Issues**:
- Qt library variations across platforms
- Path handling (forward vs. backslash)
- Keyboard capture (Alt+C shortcut) may fail on some Linux DMs
- Screenshot overlay may not appear on top of all windows

**Mitigation Strategies**:
1. **pathlib usage**: Already uses pathlib (platform-agnostic paths)
2. **Qt compatibility**: PyQt5 is inherently cross-platform
3. **Testing plan**: Test on Ubuntu 22.04 and macOS 12+
4. **CI/CD**: GitHub Actions for automated testing across platforms

---

### 4. Performance Scaling

**Risk**: OCR processing slows down with large image collections; gallery performance degrades

**Severity**: LOW-MEDIUM  
**Likelihood**: LOW (only when database >500 images)

**Impact**:
- Gallery navigation slows (>2 second load time)
- OCR inference times increase (>5 seconds per image)
- Memory usage bloats (large number of images in RAM)

**Mitigation Strategies**:
1. **Lazy loading**: Load gallery images on-demand, not all at startup
2. **Image caching**: Cache thumbnails separately from full resolution
3. **Pagination**: Display 50 images at a time, not infinite scroll
4. **Database migration**: Transition from JSON to SQLite when >1000 captures

---

## Business Risks

### 1. Market Adoption / Product-Market Fit

**Risk**: Customers may not adopt tool (unclear value proposition, wrong pricing model, better alternatives)

**Severity**: HIGH  
**Likelihood**: MEDIUM (common in new products)

**Impact**:
- Revenue fails to materialize
- Investor interest dies
- Pivoting required (cost, time)

**Mitigation Strategies**:
1. **Early customer interviews**: Talk to 10-20 potential customers before scaling
2. **MVP pricing**: Start with low price (€50-100/month) to reduce adoption friction
3. **Free trial period**: 2-week free trial to demonstrate value
4. **Success metrics**: Track time-to-first-value (should be <30 min)
5. **Feedback loop**: Monthly customer interviews to iterate on features
6. **Multiple go-to-market channels**: Direct sales, partnerships, self-serve SaaS

**Validation Milestones**:
- Month 1-2: 3-5 paying customers (validate willingness to pay)
- Month 3-6: 10-15 customers, positive NPS (validate product-market fit)
- Month 6-12: 30+ customers, <5% monthly churn (sustained growth)

---

### 2. Competition & Market Entry

**Risk**: Larger competitors (Nielsen, Bright Data, web scraping platforms) could build similar products

**Severity**: MEDIUM  
**Likelihood**: LOW-MEDIUM (2-3 year timeframe)

**Why It Won't Happen Immediately**:
- Requires GUI/UX expertise (different skillset for data platform companies)
- Domain knowledge in retail/real estate/auto (requires market research)
- Low priority for existing competitors (fragmented market doesn't justify R&D)

**Long-term Risk**:
- Once market reaches €50M+ annually, larger players will enter
- Could reduce pricing power, increase churn

**Mitigation Strategies**:
1. **Move fast**: Establish market leadership before competition arrives
2. **Build network effects**: More users → better benchmarks → more valuable product
3. **Expand horizontally**: Cover multiple industries before large competitor enters
4. **Brand moat**: Become known as "the visual data capture standard"
5. **Customer lock-in**: Custom reports, integrations, workflows

---

### 3. Pricing Model Uncertainty

**Risk**: May have chosen wrong pricing tier (too high = no adoption, too low = low revenue)

**Severity**: MEDIUM  
**Likelihood**: MEDIUM

**Impact**:
- Revenue targets missed
- Inability to fund growth
- Customers switching to cheaper alternatives

**Mitigation Strategies**:
1. **Usage-based pricing**: Charge per data point captured (€0.01-0.05 per price)
2. **Tiered pricing**: Free tier (1 store, 10 captures/month) → Pro (€50) → Enterprise (custom)
3. **Testing**: Offer 3 different prices, see which customers convert best
4. **Grandfathering**: Early adopters get discounted rates (loyalty incentive)

---

### 4. Customer Support / Churn

**Risk**: Supporting diverse use cases (retail, real estate, auto) requires deep domain expertise

**Severity**: MEDIUM  
**Likelihood**: HIGH

**Impact**:
- Support costs exceed revenue (unsustainable unit economics)
- Customer frustration → churn
- Founder becomes support bottleneck

**Mitigation Strategies**:
1. **Self-service documentation**: Video tutorials, FAQ, knowledge base
2. **Community forum**: Users help each other (reduce support load)
3. **SLA tiers**: Free tier = community support only, Paid tiers = email support
4. **Automation**: Chatbot answers common questions
5. **Hiring**: Bring on support specialist at €500K annual revenue

---

## Legal & Compliance Risks

### 1. Terms of Service Violations

**Risk**: Capturing data from retail websites may violate their terms of service

**Severity**: MEDIUM-HIGH  
**Likelihood**: MEDIUM

**Current Approach**: Visual capture (screenshot) ≠ web scraping (automated data extraction)  
**Legal Gray Area**: TOS may prohibit any data capture, including screenshots

**Case Precedent**:
- **LinkedIn v. hiQ Labs** (2022): Courts ruled automated data collection illegal even from public pages
- **Zillow v. Redfin**: Real estate data scraping is litigious
- **Amazon v. Web Scrapers**: E-commerce sites aggressively pursue scrapers

**Mitigation Strategies**:
1. **User responsibility**: Include disclaimer: "User is responsible for complying with TOS of sites they capture from"
2. **License agreement**: Spell out that Snippet Tool is for price monitoring only (not commercial redistribution without permission)
3. **Terms of Service Review**: Have legal counsel review major retailer TOS
4. **Transparent positioning**: Market as "competitor price monitoring" (legitimate business purpose)
5. **Avoid automation**: Keep it manual (user-triggered screenshots), not bot-like

**Legal Counsel**: Budget €2-5K for initial TOS compliance review

---

### 2. Data Privacy & GDPR

**Risk**: Storing product data with location/timestamp could be considered personal data

**Severity**: MEDIUM  
**Likelihood**: LOW-MEDIUM

**GDPR Implications**:
- If data identifies individuals (e.g., "John's Coffee Auchan Paris"), it's personal data
- Requires explicit consent, privacy policies, data deletion rights
- EU regulatory penalties: €20-100M

**Current Data Model**: Product/price/store/timestamp (no personal data captured)  
**Safe**: Data does not identify individuals ✅

**Mitigation Strategies**:
1. **Privacy policy**: Clear statement on what data is collected and how it's used
2. **No personal data**: Ensure product data cannot identify individuals
3. **Data retention policy**: Delete captures older than 2 years (optional)
4. **Cookie consent**: If website has cookies, inform users
5. **Subprocessor agreements**: If using cloud storage, have DPA in place

**Legal Review**: Budget €1-2K for GDPR compliance audit

---

### 3. Intellectual Property

**Risk**: Similar tools could be built; no patent protection available

**Severity**: LOW  
**Likelihood**: HIGH (but acceptable risk)

**Why**: Process patents are weak; method of data collection (screenshot + OCR) is not unique

**Approach**: Rely on **execution speed** and **market timing**, not patents

**Mitigation Strategies**:
1. **Trade secrets**: Keep algorithm/preprocessing methods proprietary (don't open-source)
2. **Brand building**: Customer loyalty based on quality/service, not technology
3. **Network effects**: Build community/benchmarks competitors can't replicate
4. **Open-source strategy**: Open-source core (drives adoption) but keep premium features proprietary

---

### 4. Regulatory Changes

**Risk**: EU regulations (AI Act, Digital Markets Act) could restrict data collection methods

**Severity**: MEDIUM  
**Likelihood**: LOW (3-5 year timeframe)

**Potential Impact**:
- AI Act may restrict use of uncontrolled AI models (EasyOCR)
- Digital Markets Act may restrict collection from major platforms
- Data protection regulations may increase compliance costs

**Mitigation Strategies**:
1. **Compliance roadmap**: Monitor EU regulatory developments
2. **Flexibility**: Architecture allows switching OCR providers (if needed)
3. **Opt-in approach**: Users explicitly choose what data to capture (not forced)
4. **Transparency**: Document all data processing methods

---

## Risk Prioritization Matrix

| Risk | Severity | Likelihood | Mitigation Cost | Priority |
|------|----------|-----------|-----------------|----------|
| **OCR Accuracy** | MEDIUM | HIGH | €5-10K | HIGH |
| **Dependency Stability** | MEDIUM-HIGH | MEDIUM | €2-5K | HIGH |
| **Market Adoption** | HIGH | MEDIUM | €10-20K | CRITICAL |
| **Competition** | MEDIUM | LOW-MEDIUM | €5-15K | MEDIUM |
| **TOS Violations** | MEDIUM-HIGH | MEDIUM | €2-5K | HIGH |
| **Cross-platform** | MEDIUM | MEDIUM | €5-10K | MEDIUM |
| **Data Privacy** | MEDIUM | LOW-MEDIUM | €1-2K | LOW-MEDIUM |
| **Regulatory Changes** | MEDIUM | LOW | €0-5K | LOW |

---

## Recommended Risk Management Plan

### Immediate (Month 1-3)
1. ✅ Legal review of TOS compliance (€2-5K)
2. ✅ GDPR privacy policy (€1-2K)
3. ✅ OCR quality assurance testing
4. ✅ Early customer interviews (validate market fit)

### Short-term (Month 3-12)
1. ✅ Dependency vulnerability monitoring
2. ✅ Cross-platform testing (Linux/Mac)
3. ✅ Customer support infrastructure
4. ✅ Pricing optimization testing

### Long-term (Year 2+)
1. ✅ Insurance (E&O, D&O)
2. ✅ Ongoing regulatory monitoring
3. ✅ Competitive intelligence system
4. ✅ IP strategy (trade secrets + brand)

---

## Conclusion

**Risk Summary**: Snippet Tool faces typical early-stage software risks, all of which are manageable with clear mitigation strategies.

**No "Show-stopper" Risks**: None of the identified risks are insurmountable.

**Biggest Risk**: **Market adoption** (customers may not value the tool enough to pay)

**Mitigation**: **Talk to customers early and often** to validate product-market fit before scaling.

**Overall Assessment**: Ready to proceed with caution, with legal/compliance review before launch.
