# Dubai Property Market Dashboard (Looker Studio)

An interactive Looker Studio dashboard analysing ~3,400 Dubai residential sale listings: pricing, price per sq ft, and ready vs off-plan supply by area.

**Live dashboard:** _paste your Looker Studio share link here_
**Tools:** Looker Studio, Python (pandas) for cleaning, Google Sheets as data source
**Data:** Kaggle "UAE Real Estate / Housing" listings dataset (Dubai, sale listings, asking prices)

## Business questions
1. Where is the market most and least expensive per sq ft?
2. How does price scale with bedrooms and property type?
3. Do off-plan and furnished units carry a premium?
4. What does the delivery pipeline look like by handover year?

## KPI definitions (single source of truth)
| KPI | Definition | Looker Studio formula |
|---|---|---|
| Listings | Count of unique cleaned listings | `COUNT(listing_id)` |
| Median asking price (AED) | Median of `price_aed` | Use scorecard with Median aggregation, or `MEDIAN(price_aed)` |
| Median price per sq ft (AED) | Median of `price_aed / area_sqft`. Median, not mean, because a few AED 100M+ listings skew the mean | `MEDIAN(price_per_sqft)` |
| Median unit size (sq ft) | Median of `area_sqft` | `MEDIAN(area_sqft)` |
| Off-plan share % | Off-plan listings / all listings | `SUM(CASE WHEN completion_status="Off-Plan" THEN 1 ELSE 0 END)/COUNT(listing_id)` |
| Off-plan premium % | Off-plan median PSF / Ready median PSF - 1 | Compute in a blended scorecard or show both medians side by side |

Rule: KPIs are always **medians of asking prices**, never transaction prices. Locations with fewer than 30 listings are excluded from rankings (filter `Record Count >= 30` on the ranking table).

## Data governance
**Source & lineage:** Kaggle CSV (raw, never edited) -> `clean.py` -> `uae_housing_clean.csv` -> Google Sheets -> Looker Studio.

**Data quality log** (raw 5,380 rows -> 3,435 clean rows)
| Issue | Rows | Action |
|---|---|---|
| Exact duplicate rows across all columns | 1,942 | Removed (assumed repeat postings of one listing) |
| Column shift: `bathroom` contained an area value ("13,000 sqft") | 2 | Removed, cannot be repaired reliably |
| Impossible area: 13,149,888 sq ft (equal to the price) | 1 | Removed |
| Non-standard property types (Villa Compound, Residential Building) | 2 | Kept but flagged `non_standard_type`, excluded from KPIs |
| "Ready" units with handover year 2027 or later | see `dq_flag` | Kept but flagged `ready_but_future_handover`; handover field treated as unreliable for Ready units |

**Standardisation:** text numbers parsed ("1,800,000", "1,208 sqft", "3 beds"); Studio coded as 0 bedrooms; columns renamed (`propert_type` typo fixed, `area(sqft)` -> `area_sqft`).
**Constant columns** (`country`, `city`, `purpose`) dropped from the clean file because they carry no information (all UAE / Dubai / Sale).
**Known limitations:** asking prices not sale prices; single Dubai snapshot with no listing date, so no time trend; `handover` is the project's handover quarter.
**Access/ownership:** public data, no PII. Dashboard owner = you; viewers get view-only link.

## Data dictionary
See columns in `uae_housing_clean.csv`: `listing_id, price_aed, area_sqft, price_per_sqft, bedrooms, bedroom_label, bathrooms, property_type, location, project_name, furnishing, completion_status, handover, handover_year, handover_quarter, price_band, dq_flag`.

## Key findings
_Fill in after building the charts. Starting points from my analysis:_
- Median asking price is about AED 1.82M and median price per sq ft about AED 1,670.
- Dubai Harbour (~AED 4,300/sqft), Palm Jumeirah (~3,700) and Downtown (~3,200) are the most expensive areas with 30+ listings; International City (~790) is the cheapest.
- JVC has the most listings (372) with median ~AED 1,450/sqft; Business Bay is second with 311.
- Off-plan units carry a small premium (~5%) over ready units on price per sq ft; furnished about 8% over unfurnished.
- Off-plan deliveries peak in 2026-2027.
