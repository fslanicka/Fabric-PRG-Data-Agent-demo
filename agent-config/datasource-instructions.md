# Data Source Instructions

> **Copy the content below (between the --- markers) into the "Instructions" field for your Lakehouse data source in the Fabric Data Agent configuration.**

---

## General Knowledge

This Lakehouse contains flight operations data for Prague Václav Havel Airport (PRG) from January 2024 to December 2025. All flights either depart from or arrive at PRG. The data is synthetic but follows realistic patterns based on actual Prague Airport operations.

## Table Descriptions

### flights (~105,000 rows)
The main fact table. Each row is one flight event (arrival or departure).
- **flight_id** (INT): Primary key
- **flight_number** (STRING): IATA format, e.g. "OK 456", "LH 1402"
- **airline_code** (STRING): 2-letter IATA code, FK to airlines table
- **flight_type** (STRING): Either 'arrival' or 'departure'
- **origin_airport_code** (STRING): IATA code. For departures, always 'PRG'
- **destination_airport_code** (STRING): IATA code. For arrivals, always 'PRG'
- **scheduled_datetime** (TIMESTAMP): Scheduled time
- **actual_datetime** (TIMESTAMP): Actual time. NULL when status = 'cancelled'
- **status** (STRING): Values: 'on_time', 'delayed', 'cancelled', 'diverted'
- **delay_minutes** (INT): 0 for on_time, positive for delayed/diverted, NULL for cancelled
- **delay_reason** (STRING): Values: 'weather', 'technical', 'crew', 'air_traffic', 'security', 'late_aircraft'. NULL when on_time or cancelled
- **terminal** (STRING): 'T1' (Schengen) or 'T2' (non-Schengen)
- **gate** (STRING): Gate assignment, e.g. 'A1', 'B12', 'D5'
- **aircraft_type** (STRING): e.g. 'A320', 'B737-800', 'B777-300ER'
- **passenger_count** (INT): Number of passengers on the flight

### airlines (~40 rows)
Airline reference data.
- **airline_code** (STRING): Primary key, IATA 2-letter code
- **airline_name** (STRING): Full name, e.g. "Czech Airlines", "Ryanair"
- **country** (STRING): Home country
- **alliance** (STRING): 'Star Alliance', 'SkyTeam', 'Oneworld', or 'None'

### airports (~100 rows)
Airport reference data for all airports connected to Prague.
- **airport_code** (STRING): Primary key, IATA 3-letter code
- **airport_name** (STRING): Full name
- **city** (STRING): City name
- **country** (STRING): Country name
- **region** (STRING): 'Europe', 'Asia', 'North America', 'Middle East', 'Africa'
- **latitude** (DOUBLE): GPS latitude
- **longitude** (DOUBLE): GPS longitude

### weather (~730 rows)
Daily weather at Prague Airport.
- **date** (DATE): Primary key, one row per day
- **temperature_celsius** (DOUBLE): Average daily temperature
- **wind_speed_kmh** (DOUBLE): Average wind speed
- **visibility_km** (DOUBLE): Average visibility
- **precipitation_mm** (DOUBLE): Total daily precipitation
- **condition** (STRING): 'clear', 'cloudy', 'rain', 'snow', 'fog', 'storm'

## Query Logic

### Joins
- Always join flights → airlines ON flights.airline_code = airlines.airline_code
- Always join flights → airports ON flights.origin_airport_code = airports.airport_code OR flights.destination_airport_code = airports.airport_code (depending on context)
- Join flights → weather ON CAST(flights.scheduled_datetime AS DATE) = weather.date

### Filtering
- For arrivals only: WHERE flight_type = 'arrival'
- For departures only: WHERE flight_type = 'departure'
- When calculating delay averages, only include WHERE status = 'delayed' (exclude on_time and cancelled)
- When calculating on-time performance, use: COUNT(CASE WHEN status = 'on_time' THEN 1 END) * 100.0 / COUNT(CASE WHEN status != 'cancelled' THEN 1 END)
- For non-Schengen flights: WHERE terminal = 'T2'
- For Schengen flights: WHERE terminal = 'T1'

### Common Patterns
- Monthly trends: GROUP BY YEAR(scheduled_datetime), MONTH(scheduled_datetime)
- Hourly distribution: GROUP BY HOUR(scheduled_datetime)
- Airline ranking: JOIN airlines, GROUP BY airline_name, ORDER BY COUNT(*) DESC
- Route ranking: GROUP BY origin_airport_code, destination_airport_code with JOIN to airports for names
- Weather impact: JOIN weather, GROUP BY condition, calculate AVG(delay_minutes) and delay rate

### Value Formats
- airline_code: 2-letter uppercase, e.g. 'OK', 'LH', 'FR'
- airport_code: 3-letter uppercase, e.g. 'PRG', 'LHR', 'CDG'
- status: lowercase, one of: 'on_time', 'delayed', 'cancelled', 'diverted'
- flight_type: lowercase, 'arrival' or 'departure'
- terminal: 'T1' or 'T2'
- condition (weather): lowercase, one of: 'clear', 'cloudy', 'rain', 'snow', 'fog', 'storm'

---
