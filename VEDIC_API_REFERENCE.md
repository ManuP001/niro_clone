# 📚 Vedic Astro API - Complete Endpoint Reference

**Base URL:** `https://api.vedicastroapi.com/v3-json`  
**Total Endpoints:** 130 APIs

---

## 🔮 DASHAS (13 endpoints)
Planetary period calculations

| Endpoint | Description | Currently Used? |
|----------|-------------|-----------------|
| `/dashas/maha-dasha` | Mahadasha overview with planet sequence and dates | ❌ Replaced |
| `/dashas/current-mahadasha-full` | **Full dasha timeline with exact dates for all levels** | ✅ **YES** |
| `/dashas/current-mahadasha` | Current stacked dasha levels (5 levels deep) | ❌ |
| `/dashas/antar-dasha` | Antardasha sequences per mahadasha | ❌ |
| `/dashas/paryantar-dasha` | Sub-sub periods (Paryantardasha) | ❌ |
| `/dashas/specific-sub-dasha` | Drill down to any dasha level (up to 5) | ❌ |
| `/dashas/maha-dasha-predictions` | Narrative predictions for each mahadasha | ❌ **Potential** |
| `/dashas/char-dasha-current` | Jaimini Char Dasha current | ❌ |
| `/dashas/char-dasha-main` | Jaimini Char Dasha main sequence | ❌ |
| `/dashas/char-dasha-sub` | Jaimini Char Dasha sub periods | ❌ |
| `/dashas/yogini-dasha-main` | Yogini Dasha main cycle | ❌ |
| `/dashas/yogini-dasha-sub` | Yogini Dasha sub periods | ❌ |

---

## 🪐 HOROSCOPE (16 endpoints)
Birth chart and planetary data

| Endpoint | Description | Currently Used? |
|----------|-------------|-----------------|
| `/horoscope/planet-details` | **All planets with exact degrees, nakshatras, combust status** | ✅ **YES** |
| `/horoscope/planet-report` | Narrative report for a specific planet | ❌ Replaced |
| `/horoscope/ascendant-report` | Ascendant summary with lord, lucky gem, mantra | ❌ **Potential** |
| `/horoscope/personal-characteristics` | 12-house personalized predictions | ❌ **Potential** |
| `/horoscope/planets-in-houses` | House-wise planet placement with significations | ❌ |
| `/horoscope/planetary-aspects` | Which planets aspect each house | ❌ |
| `/horoscope/divisional-charts` | D1, D9, D10, etc. chart placements | ❌ **Potential** |
| `/horoscope/chart-image` | SVG chart image (North/South Indian style) | ❌ |
| `/horoscope/ashtakvarga` | Ashtakvarga points matrix | ❌ **Potential** |
| `/horoscope/ashtakvarga-chart-image` | Ashtakvarga grid image | ❌ |
| `/horoscope/binnashtakvarga` | Binna Ashtakvarga per planet | ❌ |
| `/horoscope/western-planets` | Western chart positions | ❌ |
| `/horoscope/ai-12-month-prediction` | **AI-generated 12-month forecast** | ❌ **HIGH POTENTIAL** |

---

## 📊 EXTENDED HOROSCOPE (17 endpoints)
Additional chart analysis

| Endpoint | Description | Currently Used? |
|----------|-------------|-----------------|
| `/extended-horoscope/extended-kundli-details` | Compact natal attributes (gana, yoni, nadi, etc.) | ❌ Replaced |
| `/extended-horoscope/yoga-list` | **Computed yogas with strength percentages** | ❌ **HIGH POTENTIAL** |
| `/extended-horoscope/find-moon-sign` | Moon sign finder with prediction | ❌ |
| `/extended-horoscope/find-sun-sign` | Sun sign finder with prediction | ❌ |
| `/extended-horoscope/find-ascendant` | Ascendant finder with prediction | ❌ |
| `/extended-horoscope/current-sade-sati` | Current Saturn period analysis | ❌ **Potential** |
| `/extended-horoscope/sade-sati-table` | Full Sade Sati timeline | ❌ |
| `/extended-horoscope/gem-suggestion` | Gem recommendation with wearing guidance | ❌ **Potential** |
| `/extended-horoscope/rudraksh-suggestion` | Rudraksha recommendation | ❌ |
| `/extended-horoscope/numero-table` | Numerology profile | ❌ |
| `/extended-horoscope/shad-bala` | Shadbala strength components | ❌ **Potential** |
| `/extended-horoscope/kp-planets` | KP system planet details | ❌ |
| `/extended-horoscope/kp-houses` | KP system house cusps | ❌ |
| `/extended-horoscope/arutha-padas` | Arudha Padas A1-A12 | ❌ |
| `/extended-horoscope/jaimini-karakas` | Jaimini Karakas (Atmakaraka, etc.) | ❌ |
| `/extended-horoscope/varshapal-details` | Annual chart (Varshaphal) highlights | ❌ |
| `/extended-horoscope/varshapal-year-chart` | Varshaphal year chart | ❌ |
| `/extended-horoscope/varshapal-month-chart` | Varshaphal monthly charts | ❌ |

---

## ⚠️ DOSHA (5 endpoints)
Affliction/dosha checks

| Endpoint | Description | Currently Used? |
|----------|-------------|-----------------|
| `/dosha/mangal-dosh` | Mangal dosh evaluation with cancellation | ❌ **Potential** |
| `/dosha/manglik-dosh` | Detailed Manglik breakdown | ❌ |
| `/dosha/kaalsarp-dosh` | Kaal Sarp dosha check with remedies | ❌ **Potential** |
| `/dosha/pitra-dosh` | Pitra dosha check | ❌ |
| `/dosha/papasamaya` | Papa points calculation | ❌ |

---

## 💑 MATCHING (10 endpoints)
Compatibility analysis

| Endpoint | Description | Currently Used? |
|----------|-------------|-----------------|
| `/matching/ashtakoot` | Ashtakoot matching (8 kootas) | ❌ **HIGH POTENTIAL** |
| `/matching/ashtakoot-with-astro-details` | Ashtakoot + planetary positions | ❌ |
| `/matching/dashakoot` | South Indian 10-koota matching | ❌ |
| `/matching/nakshatra-match` | Nakshatra-based compatibility | ❌ |
| `/matching/aggregate-match` | Combined compatibility score (0-100) | ❌ **Potential** |
| `/matching/papasamaya-match` | Papa points comparison | ❌ |
| `/matching/rajju-vedha-details` | Rajju/Vedha dosha check | ❌ |
| `/matching/western-match` | Western zodiac compatibility | ❌ |
| `/matching/bulk-north-match` | Bulk matching (multiple candidates) | ❌ |
| `/matching/bulk-south-match` | Bulk South Indian matching | ❌ |

---

## 📅 PANCHANG (14 endpoints)
Daily/monthly calendar

| Endpoint | Description | Currently Used? |
|----------|-------------|-----------------|
| `/panchang/panchang` | Full daily panchang | ❌ **Potential** |
| `/panchang/monthly-panchang` | Month-long panchang | ❌ |
| `/panchang/festivals` | Festival and yoga highlights | ❌ |
| `/panchang/choghadiya-muhurta` | Choghadiya auspicious times | ❌ **Potential** |
| `/panchang/hora-muhurta` | Hourly planet horas | ❌ |
| `/panchang/moon-calendar` | Moon phases for a period | ❌ |
| `/panchang/moon-phase` | Single day moon phase | ❌ |
| `/panchang/moonrise` | Moonrise time | ❌ |
| `/panchang/sunrise` | Sunrise time | ❌ |
| `/panchang/sunset` | Sunset time | ❌ |
| `/panchang/solarnoon` | Solar noon time | ❌ |
| `/panchang/retrogrades` | Planet retrograde status | ❌ |
| `/panchang/transit-dates` | **Planet transit periods for year** | ❌ **HIGH POTENTIAL** |

---

## 🔮 PREDICTION (9 endpoints)
Horoscope predictions

| Endpoint | Description | Currently Used? |
|----------|-------------|-----------------|
| `/prediction/daily-sun` | Daily Sun-sign horoscope | ❌ |
| `/prediction/daily-moon` | Daily Moon-sign horoscope | ❌ **Potential** |
| `/prediction/daily-nakshatra` | **Daily nakshatra horoscope** | ❌ **HIGH POTENTIAL** |
| `/prediction/weekly-sun` | Weekly Sun-sign horoscope | ❌ |
| `/prediction/weekly-moon` | Weekly Moon-sign horoscope | ❌ |
| `/prediction/yearly` | Yearly horoscope by phases | ❌ **Potential** |
| `/prediction/numerology` | Comprehensive numerology profile | ❌ |
| `/prediction/day-number` | Personal Day numerology | ❌ |
| `/prediction/biorhythm` | Biorhythm cycles | ❌ |

---

## 🃏 TAROT (12 endpoints)
Tarot card readings

| Endpoint | Description | Currently Used? |
|----------|-------------|-----------------|
| `/tarot/shuffle` | Shuffle deck | ❌ |
| `/tarot/daily` | Daily tarot guidance | ❌ |
| `/tarot/yes-no` | Yes/No reading | ❌ |
| `/tarot/career-select` | Career guidance | ❌ |
| `/tarot/in-depth-love` | Love reading | ❌ |
| `/tarot/love-triangle` | Relationship insights | ❌ |
| `/tarot/erotic-love` | Sensual guidance | ❌ |
| `/tarot/flirt-reading` | Flirting guidance | ❌ |
| `/tarot/romantic-breakup` | Breakup analysis | ❌ |
| `/tarot/business-breakup` | Business breakup analysis | ❌ |
| `/tarot/made-for-each-other-or-not` | Compatibility reading | ❌ |
| `/tarot/fortune-cookie` | Fortune message | ❌ |

---

## 🌍 WESTERN (26 endpoints)
Western astrology

| Endpoint | Description | Currently Used? |
|----------|-------------|-----------------|
| `/western/natal-chart` | Western natal wheel SVG | ❌ |
| `/western/planet-details` | Western positions | ❌ |
| `/western/aspects` | Natal aspects | ❌ |
| `/western/transit-chart` | Transit overlay wheel | ❌ |
| `/western/transit-planets` | Current transit positions | ❌ **Potential** |
| `/western/daily-transits` | Daily transit aspects | ❌ **HIGH POTENTIAL** |
| `/western/weekly-transits` | Weekly transit aspects | ❌ |
| `/western/monthly-transits` | Monthly transit aspects | ❌ |
| `/western/daily-transit-prediction` | **Daily transit predictions by domain** | ❌ **HIGH POTENTIAL** |
| `/western/daily-horoscope` | Daily western horoscope | ❌ |
| `/western/weekly-horoscope` | Weekly western horoscope | ❌ |
| `/western/yearly-horoscope` | Yearly western horoscope | ❌ |
| `/western/synastry-chart` | Synastry bi-wheel | ❌ |
| `/western/synastry-aspects` | Synastry aspects | ❌ |
| `/western/synastry-aspect-predictions` | Synastry interpretations | ❌ |
| `/western/synastry-emotion-predictions` | Emotional dynamics | ❌ |
| `/western/synastry-career-predictions` | Career synergy | ❌ |
| `/western/synastry-finance-predictions` | Financial synergy | ❌ |
| `/western/synastry-health-predictions` | Health themes | ❌ |
| `/western/synastry-intimacy-predictions` | Intimacy/chemistry | ❌ |
| `/western/simple-compatibility` | Basic compatibility % | ❌ |
| `/western/planet-transit-dates` | Yearly transit map | ❌ |
| `/western/find-sun-sign` | Sun sign finder | ❌ |
| `/western/cusps-details` | House cusps | ❌ |
| `/western/detailed-planet-report` | Planet interpretation | ❌ |
| `/western/planet-position-report` | Planet position summary | ❌ |
| `/western/node-position-report` | Node interpretation | ❌ |
| `/western/ascendant-position-report` | Ascendant narrative | ❌ |

---

## 🛠️ UTILITIES (5 endpoints)
Helper functions

| Endpoint | Description | Currently Used? |
|----------|-------------|-----------------|
| `/utilities/geo-search` | City/location search | ❌ **Potential** |
| `/utilities/geo-search-advanced` | Advanced geo search with timezone | ❌ |
| `/utilities/gem-details` | Gem metadata | ❌ |
| `/utilities/radical-number-details` | Numerology content | ❌ |
| `/utilities/nakshatra-vastu-details` | Vastu by nakshatra | ❌ |

---

## 📄 PDF (2 endpoints)
PDF generation

| Endpoint | Description | Currently Used? |
|----------|-------------|-----------------|
| `/pdf/horoscope-queue` | Generate horoscope PDF | ❌ |
| `/pdf/matching-queue` | Generate matching PDF | ❌ |

---

# 🎯 HIGH POTENTIAL APIs FOR NIRO

Based on the current app functionality, these APIs could add significant value:

## 1. `/horoscope/ai-12-month-prediction` 
**AI-generated forecasts by domain** (career, relationship, health, finance)
- Returns probability, outcome, house scores
- Perfect for "what will 2025 bring?" questions

## 2. `/extended-horoscope/yoga-list`
**Computed yogas with strength percentages**
- Raja Yoga, Dhana Yoga, Daridra Yoga counts
- Would enhance chart analysis

## 3. `/prediction/daily-nakshatra`
**Daily nakshatra-based predictions**
- Category scores (career, relationship, health)
- Good for daily guidance feature

## 4. `/panchang/transit-dates`
**Planet transit calendar**
- Saturn, Jupiter transit timing with strength
- Essential for "when will things improve?" questions

## 5. `/western/daily-transit-prediction`
**Transit-based daily predictions**
- Domain-wise scores from current transits
- Could power a "today's energy" feature

## 6. `/matching/ashtakoot`
**Compatibility matching**
- 8-koota matching with scores
- Could enable partner compatibility feature

## 7. `/dosha/mangal-dosh` & `/dosha/kaalsarp-dosh`
**Dosha analysis**
- Common user questions about doshas
- Remedies included

---

# 📊 Current API Usage Summary

| Status | APIs |
|--------|------|
| ✅ Currently Used | `/horoscope/planet-details`, `/dashas/current-mahadasha-full` |
| ❌ Replaced | `/extended-horoscope/extended-kundli-details`, `/horoscope/planet-report` (×9), `/dashas/maha-dasha` |
| 🔄 Optimization | Reduced from 11+ calls to 2 calls |
