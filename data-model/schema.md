# Data Model — Prague Airport Flight Data

## Overview

This data model represents flight operations at Prague Václav Havel Airport (PRG) for 2024–2025. It consists of 4 tables optimized for analytical queries via Microsoft Fabric Data Agent.

## Entity Relationship Diagram

```
airports ──┐                    ┌── airports
(origin)   │    ┌──────────┐   │  (destination)
           └───→│ flights  │←──┘
airlines ──────→│          │
                └────┬─────┘
                     │ (date join)
                ┌────┴─────┐
                │ weather  │
                └──────────┘
```

## Table: flights

Primary table containing individual flight records.

| Column | Type | Nullable | Description | Example |
|--------|------|----------|-------------|---------|
| flight_id | INT | No | Primary key, auto-increment | 1, 2, 3 |
| flight_number | STRING | No | IATA flight number | "OK 456", "LH 1402" |
| airline_code | STRING | No | FK → airlines.airline_code | "OK", "LH", "FR" |
| flight_type | STRING | No | 'arrival' or 'departure' | "arrival" |
| origin_airport_code | STRING | No | FK → airports.airport_code. For departures, always 'PRG' | "PRG", "LHR" |
| destination_airport_code | STRING | No | FK → airports.airport_code. For arrivals, always 'PRG' | "CDG", "PRG" |
| scheduled_datetime | TIMESTAMP | No | Scheduled departure/arrival time | "2024-07-15 14:30:00" |
| actual_datetime | TIMESTAMP | Yes | Actual time. NULL if cancelled | "2024-07-15 14:55:00" |
| status | STRING | No | Flight status | "on_time", "delayed", "cancelled", "diverted" |
| delay_minutes | INT | Yes | Delay in minutes. 0 if on time, NULL if cancelled | 25, 0, NULL |
| delay_reason | STRING | Yes | Reason for delay. NULL if on_time or cancelled | "weather", "technical", "crew", "air_traffic", "security", "late_aircraft" |
| terminal | STRING | No | Terminal at PRG | "T1", "T2" |
| gate | STRING | Yes | Gate assignment | "A1", "B12", "C5" |
| aircraft_type | STRING | No | Aircraft model | "A320", "B737-800", "ATR 72" |
| passenger_count | INT | No | Number of passengers on the flight | 156 |

**Status distribution (approximate):**
- on_time: ~70%
- delayed: ~23%
- cancelled: ~5%
- diverted: ~2%

**Terminal assignment logic:**
- T1: Schengen flights (EU/EEA destinations)
- T2: Non-Schengen flights (rest of world)

## Table: airlines

Reference table for airlines operating at PRG.

| Column | Type | Nullable | Description | Example |
|--------|------|----------|-------------|---------|
| airline_code | STRING | No | PK, IATA 2-letter code | "OK", "LH" |
| airline_name | STRING | No | Full airline name | "Czech Airlines", "Lufthansa" |
| country | STRING | No | Airline's home country | "Czech Republic", "Germany" |
| alliance | STRING | No | Alliance membership | "SkyTeam", "Star Alliance", "Oneworld", "None" |

**Sample airlines:**
- OK — Czech Airlines (Czech Republic, SkyTeam)
- LH — Lufthansa (Germany, Star Alliance)
- FR — Ryanair (Ireland, None)
- W6 — Wizz Air (Hungary, None)
- BA — British Airways (United Kingdom, Oneworld)
- QR — Qatar Airways (Qatar, Oneworld)
- TK — Turkish Airlines (Turkey, Star Alliance)
- KE — Korean Air (South Korea, SkyTeam)
- EK — Emirates (UAE, None)
- AF — Air France (France, SkyTeam)

## Table: airports

Reference table for airports connected to PRG.

| Column | Type | Nullable | Description | Example |
|--------|------|----------|-------------|---------|
| airport_code | STRING | No | PK, IATA 3-letter code | "PRG", "LHR", "CDG" |
| airport_name | STRING | No | Full airport name | "Václav Havel Airport Prague" |
| city | STRING | No | City name | "Prague", "London" |
| country | STRING | No | Country name | "Czech Republic", "United Kingdom" |
| region | STRING | No | Geographic region | "Europe", "Asia", "North America", "Middle East", "Africa" |
| latitude | DOUBLE | No | GPS latitude | 50.1008 |
| longitude | DOUBLE | No | GPS longitude | 14.2600 |

**Sample airports by region:**
- Europe: LHR (London), CDG (Paris), FRA (Frankfurt), AMS (Amsterdam), FCO (Rome), BCN (Barcelona), VIE (Vienna)
- Asia: DXB (Dubai), DOH (Doha), ICN (Seoul), PVG (Shanghai), BKK (Bangkok)
- North America: JFK (New York), ORD (Chicago), YYZ (Toronto)
- Middle East: TLV (Tel Aviv), AMM (Amman)
- Africa: CAI (Cairo), CMN (Casablanca)

## Table: weather

Daily weather observations at Prague Airport.

| Column | Type | Nullable | Description | Example |
|--------|------|----------|-------------|---------|
| date | DATE | No | PK, observation date | "2024-07-15" |
| temperature_celsius | DOUBLE | No | Average daily temperature | 22.5, -3.2 |
| wind_speed_kmh | DOUBLE | No | Average wind speed | 15.3 |
| visibility_km | DOUBLE | No | Average visibility | 10.0, 2.5 |
| precipitation_mm | DOUBLE | No | Total daily precipitation | 0.0, 12.5 |
| condition | STRING | No | Primary weather condition | "clear", "cloudy", "rain", "snow", "fog", "storm" |

**Seasonal patterns (Prague climate):**
- Winter (Dec–Feb): temp -5 to 3°C, snow/fog common
- Spring (Mar–May): temp 5 to 18°C, rain periods
- Summer (Jun–Aug): temp 18 to 30°C, mostly clear, occasional storms
- Autumn (Sep–Nov): temp 3 to 15°C, fog increasing

## Relationships & Join Logic

1. **flights.airline_code → airlines.airline_code** (many-to-one)
2. **flights.origin_airport_code → airports.airport_code** (many-to-one)
3. **flights.destination_airport_code → airports.airport_code** (many-to-one)
4. **CAST(flights.scheduled_datetime AS DATE) → weather.date** (many-to-one, date-based join)

## Key Business Rules

- For **arrivals**: origin_airport_code is the departure airport, destination_airport_code = 'PRG'
- For **departures**: origin_airport_code = 'PRG', destination_airport_code is the arrival airport
- **delay_minutes** is only meaningful when status = 'delayed' (value > 0) or status = 'on_time' (value = 0)
- **actual_datetime** is NULL only when status = 'cancelled'
- **delay_reason** is NULL when status is 'on_time' or 'cancelled'
- **Weather joins** should use `CAST(flights.scheduled_datetime AS DATE) = weather.date`
