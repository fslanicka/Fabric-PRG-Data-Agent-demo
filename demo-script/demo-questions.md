# Demo Script — Prague Airport Flight Data Agent

> This script contains 25+ demo questions organized by category, from simple to advanced.
> Each question is provided in Czech 🇨🇿 and English 🇬🇧 with a description of the expected answer.
> Use these questions to showcase the Data Agent's capabilities during presentations.

---

## 🎯 How to Use This Script

1. Open the Data Agent chat interface
2. Follow the categories in order — they build from simple to complex
3. Each question shows what capability it demonstrates
4. Expected answers are approximate — actual values depend on the random seed

---

## Category 1: Basic Queries (Warm-up)

### Q1 — Total Flight Count
> **Demonstrates**: Simple COUNT query

🇨🇿 *"Kolik letů je celkem v databázi?"*
🇬🇧 *"How many flights are in the database?"*

**Expected**: ~100,000 flights total

---

### Q2 — Arrivals vs. Departures
> **Demonstrates**: GROUP BY with categorical column

🇨🇿 *"Kolik je příletů a kolik odletů?"*
🇬🇧 *"How many arrivals and how many departures are there?"*

**Expected**: Roughly 50/50 split between arrivals and departures

---

### Q3 — Flight Status Distribution
> **Demonstrates**: GROUP BY with percentage calculation

🇨🇿 *"Jaké je rozložení statusů letů? Kolik procent je včas, zpožděných, zrušených a odklonéných?"*
🇬🇧 *"What is the distribution of flight statuses? What percentage are on-time, delayed, cancelled, and diverted?"*

**Expected**: ~70% on_time, ~23% delayed, ~5% cancelled, ~2% diverted

---

### Q4 — Specific Date Query
> **Demonstrates**: Date filtering

🇨🇿 *"Kolik letů bylo 15. července 2024?"*
🇬🇧 *"How many flights were there on July 15, 2024?"*

**Expected**: A number (varies, typically 60-100 flights per day in summer)

---

## Category 2: Airline Analysis

### Q5 — Top Airlines
> **Demonstrates**: JOIN + ORDER BY + LIMIT

🇨🇿 *"Kterých 10 aerolinií má nejvíce letů?"*
🇬🇧 *"Which 10 airlines have the most flights?"*

**Expected**: A ranked list. Top airlines likely include Lufthansa (LH), Czech Airlines (OK), Ryanair (FR), Smartwings (QS), Austrian (OS), KLM (KL), Air France (AF).

---

### Q6 — Alliance Comparison
> **Demonstrates**: JOIN + GROUP BY on derived category

🇨🇿 *"Porovnej počet letů podle aliancí — Star Alliance, SkyTeam, Oneworld a nezávislé aerolinky."*
🇬🇧 *"Compare flight counts by alliance — Star Alliance, SkyTeam, Oneworld, and independent airlines."*

**Expected**: Table showing each alliance with flight count and percentage. "None" (independent/LCC) likely has a large share.

---

### Q7 — Airline On-Time Performance
> **Demonstrates**: Complex aggregation with CASE WHEN

🇨🇿 *"Která aerolinka má nejlepší a která nejhorší přesnost (on-time performance)? Ukaž top 5 a bottom 5."*
🇬🇧 *"Which airline has the best and worst on-time performance? Show top 5 and bottom 5."*

**Expected**: Two ranked lists with on-time percentages. Airlines with few flights may have extreme percentages.

---

## Category 3: Delay Analysis

### Q8 — Average Delay by Airline
> **Demonstrates**: AVG with filter

🇨🇿 *"Jaké je průměrné zpoždění v minutách pro každou aerolinku? Ukaž jen zpožděné lety."*
🇬🇧 *"What is the average delay in minutes for each airline? Only show delayed flights."*

**Expected**: Table with airline names and average delay minutes. Most airlines should show 25-40 min average delay.

---

### Q9 — Delay Reasons
> **Demonstrates**: GROUP BY with pie chart potential

🇨🇿 *"Jaké jsou nejčastější důvody zpoždění a kolik procent tvoří?"*
🇬🇧 *"What are the most common delay reasons and what percentage do they represent?"*

**Expected**: weather ~25%, air_traffic ~25%, technical ~20%, late_aircraft ~15%, crew ~10%, security ~5%

---

### Q10 — Longest Delays
> **Demonstrates**: ORDER BY DESC with details

🇨🇿 *"Ukaž 10 letů s největším zpožděním. Uveď číslo letu, aerolinku, trasu a důvod."*
🇬🇧 *"Show the 10 flights with the longest delays. Include flight number, airline, route, and reason."*

**Expected**: Flights with 4-6 hour delays, various reasons

---

## Category 4: Weather Impact

### Q11 — Weather and Delays
> **Demonstrates**: Cross-table JOIN (flights ↔ weather)

🇨🇿 *"Jak ovlivňuje počasí zpoždění letů? Ukaž průměrné zpoždění a procento zpožděných letů pro každý typ počasí."*
🇬🇧 *"How does weather affect flight delays? Show average delay and percentage of delayed flights for each weather condition."*

**Expected**: Storm and fog should show highest delay rates (40-50%), clear weather lowest (~15%)

---

### Q12 — Snow Days
> **Demonstrates**: Filtered JOIN with specific condition

🇨🇿 *"Kolik letů bylo zrušeno ve dnech, kdy sněžilo?"*
🇬🇧 *"How many flights were cancelled on snowy days?"*

**Expected**: A specific count, higher cancellation rate than average

---

### Q13 — Temperature and Flight Volume
> **Demonstrates**: Correlation analysis

🇨🇿 *"Je souvislost mezi teplotou a počtem letů za den? Ukaž průměrný počet letů pro různé teplotní rozsahy."*
🇬🇧 *"Is there a correlation between temperature and daily flight volume? Show average flights per day for different temperature ranges."*

**Expected**: Higher flight counts in warm months (more seasonal routes active)

---

## Category 5: Time Analysis

### Q14 — Monthly Trends
> **Demonstrates**: Time-series GROUP BY

🇨🇿 *"Ukaž měsíční trend počtu letů za celé období 2024-2025."*
🇬🇧 *"Show the monthly trend of flight counts for the entire 2024-2025 period."*

**Expected**: Chart-friendly data showing summer peaks (Jun-Aug) and winter dips (Dec-Feb)

---

### Q15 — Peak Hours
> **Demonstrates**: Hourly distribution

🇨🇿 *"V kolik hodin je na letišti největší provoz? Ukaž počet letů po hodinách."*
🇬🇧 *"What are the peak hours at the airport? Show flight count by hour."*

**Expected**: Peaks around 8-10 AM and 4-6 PM, minimal traffic at night (midnight-5 AM)

---

### Q16 — Day of Week Analysis
> **Demonstrates**: DAYOFWEEK grouping

🇨🇿 *"Který den v týdnu má nejvíce letů?"*
🇬🇧 *"Which day of the week has the most flights?"*

**Expected**: Relatively even distribution with possible slight peaks on Mon/Fri (business travel)

---

### Q17 — Year-over-Year Comparison
> **Demonstrates**: YEAR comparison

🇨🇿 *"Porovnej celkový počet letů a cestujících v roce 2024 vs 2025."*
🇬🇧 *"Compare total flights and passengers in 2024 vs 2025."*

**Expected**: Similar numbers for both years (same generation parameters)

---

## Category 6: Route & Destination Analysis

### Q18 — Most Popular Destinations
> **Demonstrates**: JOIN flights ↔ airports

🇨🇿 *"Jakých 15 nejpopulárnějších destinací z Prahy? Uveď město, zemi a počet odletů."*
🇬🇧 *"What are the 15 most popular destinations from Prague? Show city, country, and departure count."*

**Expected**: London, Paris, Frankfurt, Amsterdam, Vienna among top destinations

---

### Q19 — Destinations by Region
> **Demonstrates**: GROUP BY region with JOIN

🇨🇿 *"Kolik letů míří do Evropy, Asie, Severní Ameriky, Blízkého východu a Afriky?"*
🇬🇧 *"How many flights go to Europe, Asia, North America, Middle East, and Africa?"*

**Expected**: Europe dominates (~90%+), followed by Middle East, then others

---

### Q20 — Routes with Worst Delays
> **Demonstrates**: Complex JOIN + aggregation

🇨🇿 *"Které trasy mají nejhorší průměrné zpoždění? Ukaž jen trasy s více než 50 lety."*
🇬🇧 *"Which routes have the worst average delays? Only show routes with more than 50 flights."*

**Expected**: Long-haul routes to weather-affected destinations may rank higher

---

## Category 7: Passenger & Terminal Analysis

### Q21 — Terminal Comparison
> **Demonstrates**: GROUP BY terminal

🇨🇿 *"Porovnej Terminal 1 a Terminal 2 — počet letů, cestujících a přesnost."*
🇬🇧 *"Compare Terminal 1 and Terminal 2 — flights, passengers, and on-time performance."*

**Expected**: T1 (Schengen) has more flights but smaller aircraft. T2 (non-Schengen) has fewer flights but bigger planes (wide-body).

---

### Q22 — Total Passengers
> **Demonstrates**: SUM aggregation

🇨🇿 *"Kolik cestujících celkem prošlo pražským letištěm v roce 2024?"*
🇬🇧 *"How many total passengers went through Prague Airport in 2024?"*

**Expected**: Several million (depends on generation, roughly ~4-6M)

---

### Q23 — Busiest Single Day
> **Demonstrates**: GROUP BY date + ORDER BY

🇨🇿 *"Který den měl nejvíce letů a kolik jich bylo?"*
🇬🇧 *"Which day had the most flights and how many were there?"*

**Expected**: A summer day with 100+ flights

---

## Category 8: Advanced / Business Insight Questions

### Q24 — Seasonal Cancellation Pattern
> **Demonstrates**: Multi-dimensional analysis (season × status)

🇨🇿 *"Jak se liší míra rušení letů podle ročního období? Ukaž procento zrušených letů na jaře, v létě, na podzim a v zimě."*
🇬🇧 *"How does the cancellation rate differ by season? Show the percentage of cancelled flights in spring, summer, autumn, and winter."*

**Expected**: Winter has highest cancellation rate (weather), summer has lowest

---

### Q25 — Low-Cost vs. Full-Service
> **Demonstrates**: Business categorization (alliance as proxy)

🇨🇿 *"Porovnej nízkonákladové aerolinky (bez aliance) s klasickými (v alianci) — průměrné zpoždění, míra zrušení a průměrný počet cestujících na let."*
🇬🇧 *"Compare low-cost carriers (no alliance) with full-service airlines (in an alliance) — average delay, cancellation rate, and average passengers per flight."*

**Expected**: LCCs may have slightly different delay profiles, typically smaller aircraft → fewer passengers

---

### Q26 — Aircraft Type Analysis
> **Demonstrates**: GROUP BY on aircraft_type

🇨🇿 *"Které typy letadel jsou nejčastější? Ukaž top 10 s počtem letů a průměrným počtem cestujících."*
🇬🇧 *"Which aircraft types are most common? Show top 10 with flight count and average passenger count."*

**Expected**: A320 family dominates, followed by B737-800. Wide-bodies (B777, A350) have higher passenger counts.

---

### Q27 — Weather-Driven Operational Summary
> **Demonstrates**: Complex multi-table query with conditional logic

🇨🇿 *"Pro dny s bouřkou ukaž: kolik letů bylo zpožděno, zrušeno, jaké bylo průměrné zpoždění a která aerolinka měla nejhorší výkon."*
🇬🇧 *"For stormy days, show: how many flights were delayed, cancelled, what was the average delay, and which airline performed worst."*

**Expected**: Multi-part answer combining weather filter with delay and airline analysis

---

### Q28 — Monthly Passenger Revenue Potential
> **Demonstrates**: Complex aggregation simulating business value

🇨🇿 *"Ukaž měsíční přehled: počet letů, celkový počet cestujících, průměrný počet cestujících na let a procento obsazenosti terminálu T1 vs T2."*
🇬🇧 *"Show a monthly summary: flight count, total passengers, average passengers per flight, and occupancy split between T1 and T2."*

**Expected**: Monthly table showing seasonal patterns in both traffic and passenger volumes

---

## 🎬 Recommended Demo Flow

For a **15-minute demo**, use this sequence:

1. **Start simple** (Q1) — show the agent understands the data
2. **Airline ranking** (Q5) — demonstrate JOIN capability
3. **Weather impact** (Q11) — showcase cross-table analysis
4. **Monthly trends** (Q14) — time-series intelligence
5. **Popular destinations** (Q18) — geographic dimension
6. **Czech language** (Q24 in Czech) — show bilingual capability
7. **Complex insight** (Q27) — grand finale with multi-table business question

For a **5-minute quick demo**, use: Q1 → Q5 → Q11 → Q18 → Q27

---

## 💡 Tips for Presenters

- **Start with the simple questions** to build confidence before moving to complex ones
- **Ask follow-up questions** naturally — e.g., after Q5, ask "A co Ryanair konkrétně?" / "What about Ryanair specifically?"
- **Show both languages** — ask the same question in Czech and English to demonstrate bilingual support
- **If the agent gives a wrong answer**, it's a great opportunity to show how adjusting instructions improves results
- **Have the example queries ready** in case you need to demonstrate the few-shot learning feature

---

## 🚀 Extended Demo: Fabric IQ (Multi-Source)

The questions above use only the **Lakehouse** data source (SQL). For a more comprehensive demo showcasing **Eventhouse** (KQL) and **Ontology** (Graph) data sources, continue with:

→ **[demo-questions-fabric-iq.md](demo-questions-fabric-iq.md)** — 20 additional questions covering:
- **Operational data** (KQL): gate utilization, crew assignments, maintenance patterns
- **Graph traversals** (Ontology): multi-hop queries, cross-domain reasoning
- **Cross-source reasoning**: combining Lakehouse + Eventhouse through the ontology
- **Source comparison**: same question answered via SQL, KQL, and Graph

### Combined Demo Questions (Lakehouse + Eventhouse + Ontology)

These questions bridge the original Lakehouse demo with the new Fabric IQ capabilities:

### Q29 — Flight + Gate + Crew
> **Demonstrates**: Cross-source intelligence (Lakehouse + Eventhouse)

🇬🇧 *"For the top 5 most delayed airlines, what was their average gate turnaround time and how many unique crew members did they use?"*

**Expected**: Combines flight delay data (Lakehouse) with gate and crew data (Eventhouse). Requires ontology for cross-domain reasoning.

---

### Q30 — Weather + Maintenance + Cancellations
> **Demonstrates**: 3-way cross-source analysis

🇬🇧 *"On the 10 worst weather days (by delay rate), how many maintenance events occurred and what was the cancellation rate?"*

**Expected**: Weather and flights from Lakehouse, maintenance from Eventhouse, connected through ontology relationships.

---

### Q31 — Full Chain Traversal
> **Demonstrates**: End-to-end Fabric IQ power

🇬🇧 *"Trace the full operational chain for cancelled flights in January 2025: which airlines, what maintenance events, which crews were affected, and what were the weather conditions?"*

**Expected**: Multi-entity traversal through the ontology graph, pulling data from both Lakehouse and Eventhouse.

---

## Category 10: Fabric Maps (Geospatial Visualization)

> **Note**: These are not questions to ask the Data Agent — they are **visual demo scenarios** to showcase on the Fabric Map. Open the `PRG Airport Operations Map` item in your workspace.

### M1 — Flight Network Overview
> **Demonstrates**: Destination airport markers across 5 continents

**Action**: Open the map with the "Destination Airports" layer enabled. Zoom out to see all connected airports.

**What to show**: ~100 airports across Europe, Middle East, Asia, North America, and Africa — all connected to Prague. Point out the density in Europe vs. long-haul destinations.

---

### M2 — Crew Base Distribution
> **Demonstrates**: Operational crew data visualized geographically

**Action**: Toggle the "Crew Bases" layer. Zoom into Europe.

**What to show**: Bubble markers at crew base airports, sized by crew count. Highlight that Prague (PRG) has the most crew, followed by other European hubs. Click on a marker to see crew role breakdown (captains, first officers, pursers, cabin crew).

---

### M3 — Maintenance Hotspot
> **Demonstrates**: Maintenance data overlaid on map

**Action**: Toggle the "Maintenance Events" layer. Zoom to Prague.

**What to show**: All maintenance events clustered at PRG with breakdown by aircraft type. Click markers to see scheduled vs. unscheduled vs. AOG counts, average duration, and categories (engine, avionics, hydraulic, etc.).

---

### M4 — Regional Analysis
> **Demonstrates**: Interactive filtering on map

**Action**: Use the map filter controls to filter the "Destination Airports" layer by `region`.

**What to show**: Filter to "Middle East" — shows 5 airports (Dubai, Doha, Abu Dhabi, Tel Aviv, Amman). Switch to "Asia" — shows Seoul, Shanghai, Bangkok, Delhi, Tokyo. Demonstrate how filtering helps focus the story on specific regions.

---

### M5 — Combined Layer Demo
> **Demonstrates**: Multi-layer visual storytelling

**Action**: Enable all three layers simultaneously: Destination Airports (blue), Crew Bases (orange), Maintenance (red at PRG).

**What to show**: The complete operational picture — where Prague connects to, where crew are based, and where maintenance happens. This is the "geospatial intelligence" story that complements the Data Agent's natural language capabilities.
