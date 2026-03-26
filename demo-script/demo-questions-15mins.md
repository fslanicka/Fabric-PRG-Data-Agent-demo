
### Q1 — Total Flight Count
> **Demonstrates**: Simple COUNT query

- 🇨🇿 *"Kolik letů je celkem v databázi?"*
- 🇬🇧 *"How many flights are in the database?"*

**Expected**: ~100,000 flights total

---

### Q5 — Top Airlines
> **Demonstrates**: JOIN + ORDER BY + LIMIT

- 🇨🇿 *"Kterých 10 aerolinií má nejvíce letů?"*
- 🇬🇧 *"Which 10 airlines have the most flights?"*

**Expected**: A ranked list. Top airlines likely include Lufthansa (LH), Czech Airlines (OK), Ryanair (FR), Smartwings (QS), Austrian (OS), KLM (KL), Air France (AF).

---

### Q11 — Weather and Delays
> **Demonstrates**: Cross-table JOIN (flights ↔ weather)

- 🇨🇿 *"Jak ovlivňuje počasí zpoždění letů? Ukaž průměrné zpoždění a procento zpožděných letů pro každý typ počasí."*
- 🇬🇧 *"How does weather affect flight delays? Show average delay and percentage of delayed flights for each weather condition."*

**Expected**: Storm and fog should show highest delay rates (40-50%), clear weather lowest (~15%)

---

### Q14 — Monthly Trends
> **Demonstrates**: Time-series GROUP BY

- 🇨🇿 *"Ukaž měsíční trend počtu letů za celé období 2024-2025."*
- 🇬🇧 *"Show the monthly trend of flight counts for the entire 2024-2025 period."*

**Expected**: Chart-friendly data showing summer peaks (Jun-Aug) and winter dips (Dec-Feb)


### Q18 — Most Popular Destinations
> **Demonstrates**: JOIN flights ↔ airports

- 🇨🇿 *"Jakých 15 nejpopulárnějších destinací z Prahy? Uveď město, zemi a počet odletů."*
- 🇬🇧 *"What are the 15 most popular destinations from Prague? Show city, country, and departure count."*

**Expected**: London, Paris, Frankfurt, Amsterdam, Vienna among top destinations

---

### Q24 — Seasonal Cancellation Pattern
> **Demonstrates**: Multi-dimensional analysis (season × status)

- 🇨🇿 *"Jak se liší míra rušení letů podle ročního období? Ukaž procento zrušených letů na jaře, v létě, na podzim a v zimě."*
- 🇬🇧 *"How does the cancellation rate differ by season? Show the percentage of cancelled flights in spring, summer, autumn, and winter."*

**Expected**: Winter has highest cancellation rate (weather), summer has lowest

---

### Q27 — Weather-Driven Operational Summary
> **Demonstrates**: Complex multi-table query with conditional logic

- 🇨🇿 *"Pro dny s bouřkou ukaž: kolik letů bylo zpožděno, zrušeno, jaké bylo průměrné zpoždění a která aerolinka měla nejhorší výkon."*
- 🇬🇧 *"For stormy days, show: how many flights were delayed, cancelled, what was the average delay, and which airline performed worst."*

**Expected**: Multi-part answer combining weather filter with delay and airline analysis

---

### Q28 — Monthly Passenger Revenue Potential
> **Demonstrates**: Complex aggregation simulating business value

- 🇨🇿 *"Ukaž měsíční přehled: počet letů, celkový počet cestujících, průměrný počet cestujících na let a procento obsazenosti terminálu T1 vs T2."*
- 🇬🇧 *"Show a monthly summary: flight count, total passengers, average passengers per flight, and occupancy split between T1 and T2."*

**Expected**: Monthly table showing seasonal patterns in both traffic and passenger volumes

---

## 🚀 Fabric IQ Bonus (if time allows, +5 min)

If you have extra time, add these Fabric IQ questions to show multi-source capabilities:

### Q-A4 — Top Captains by Flights (Eventhouse/KQL)

- 🇬🇧 *"Which captains flew the most flights? Show top 10 with flight count."*

**Expected**: KQL query on crew_rosters table, showing captain names and flight counts.

---

### Q-B3 — Multi-Hop: Weather → Flight → Crew (Ontology/Graph)

- 🇬🇧 *"Which crew members were on flights that operated during storm conditions?"*

**Expected**: Graph traversal: WeatherObservation[storm] → Flight → CrewMember

---

### Q-D2 — Full Chain Traversal (Cross-Source)

- 🇬🇧 *"Trace: which airline had the most cancelled flights, what maintenance events affected those flights, and which crew members were assigned?"*

**Expected**: Combines Lakehouse (flights, airlines) + Eventhouse (maintenance, crew) through ontology.

