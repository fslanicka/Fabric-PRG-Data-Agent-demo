-- ============================================================
-- Example Queries for Microsoft Fabric Data Agent (Few-Shot)
-- ============================================================
-- Copy these into the "Example Queries" section of your
-- Lakehouse data source configuration in the Data Agent.
-- Each query has a natural language question and the SQL answer.
-- ============================================================

-- Question: How many flights were there in 2024?
SELECT COUNT(*) AS total_flights
FROM flights
WHERE YEAR(scheduled_datetime) = 2024;

-- Question: What is the total number of arrivals and departures?
SELECT flight_type, COUNT(*) AS flight_count
FROM flights
GROUP BY flight_type
ORDER BY flight_type;

-- Question: Which airlines have the most flights?
SELECT TOP 10 a.airline_name, a.airline_code, COUNT(*) AS flight_count
FROM flights f
JOIN airlines a ON f.airline_code = a.airline_code
GROUP BY a.airline_name, a.airline_code
ORDER BY flight_count DESC;


-- Question: What is the average delay by airline?
SELECT TOP 10 a.airline_name, a.airline_code,
       COUNT(*) AS delayed_flights,
       ROUND(AVG(f.delay_minutes), 1) AS avg_delay_minutes
FROM flights f
JOIN airlines a ON f.airline_code = a.airline_code
WHERE f.status = 'delayed'
GROUP BY a.airline_name, a.airline_code
ORDER BY avg_delay_minutes DESC;


-- Question: How does weather affect flight delays?
SELECT w.condition AS weather_condition,
       COUNT(*) AS total_flights,
       SUM(CASE WHEN f.status = 'delayed' THEN 1 ELSE 0 END) AS delayed_flights,
       ROUND(SUM(CASE WHEN f.status = 'delayed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS delay_rate_pct,
       ROUND(AVG(CASE WHEN f.status = 'delayed' THEN f.delay_minutes END), 1) AS avg_delay_minutes
FROM flights f
JOIN weather w ON CAST(f.scheduled_datetime AS DATE) = w.date
GROUP BY w.condition
ORDER BY delay_rate_pct DESC;

-- Question: What are the busiest months?
SELECT YEAR(scheduled_datetime) AS year,
       MONTH(scheduled_datetime) AS month,
       COUNT(*) AS flight_count,
       SUM(passenger_count) AS total_passengers
FROM flights
GROUP BY YEAR(scheduled_datetime), MONTH(scheduled_datetime)
ORDER BY year, month;

-- Question: What are the most popular destinations from Prague?
SELECT TOP 15 ap.city, ap.country, ap.airport_code,
       COUNT(*) AS departures
FROM flights f
JOIN airports ap ON f.destination_airport_code = ap.airport_code
WHERE f.flight_type = 'departure'
GROUP BY ap.city, ap.country, ap.airport_code
ORDER BY departures DESC;


-- Question: What is the on-time performance by terminal?
SELECT terminal,
       COUNT(*) AS total_flights,
       SUM(CASE WHEN status = 'on_time' THEN 1 ELSE 0 END) AS on_time_flights,
       ROUND(SUM(CASE WHEN status = 'on_time' THEN 1 ELSE 0 END) * 100.0 / 
             NULLIF(SUM(CASE WHEN status != 'cancelled' THEN 1 ELSE 0 END), 0), 1) AS on_time_pct
FROM flights
GROUP BY terminal;

-- Question: What are the peak hours at the airport?
SELECT
    DATEPART(HOUR, [scheduled_datetime]) AS [hour_of_day],
    COUNT(*) AS [flight_count],
    SUM(CASE WHEN [flight_type] = 'departure' THEN 1 ELSE 0 END) AS [departures],
    SUM(CASE WHEN [flight_type] = 'arrival' THEN 1 ELSE 0 END) AS [arrivals]
FROM
    [dbo].[flights]
GROUP BY
    DATEPART(HOUR, [scheduled_datetime])
ORDER BY
    [hour_of_day];

-- Question: Which routes have the worst delays?
SELECT TOP 10
    CASE WHEN f.flight_type = 'departure' 
         THEN CONCAT('PRG → ', ap.city)
         ELSE CONCAT(ap.city, ' → PRG') 
    END AS route,
    COUNT(*) AS total_flights,
    ROUND(AVG(CASE WHEN f.status = 'delayed' THEN f.delay_minutes END), 1) AS avg_delay_min,
    ROUND(SUM(CASE WHEN f.status = 'cancelled' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS cancel_rate_pct
FROM flights f
JOIN airports ap ON (
    CASE WHEN f.flight_type = 'departure' THEN f.destination_airport_code 
         ELSE f.origin_airport_code END) = ap.airport_code
GROUP BY 
    CASE WHEN f.flight_type = 'departure' 
         THEN CONCAT('PRG → ', ap.city)
         ELSE CONCAT(ap.city, ' → PRG') END
HAVING COUNT(*) > 50
ORDER BY avg_delay_min DESC;


-- Question: How many passengers traveled through each terminal in 2024?
SELECT terminal,
       SUM(passenger_count) AS total_passengers,
       COUNT(DISTINCT airline_code) AS airlines_count
FROM flights
WHERE YEAR(scheduled_datetime) = 2024
GROUP BY terminal;

-- Question: What is the cancellation rate by delay reason and season?
SELECT 
    CASE 
        WHEN MONTH(scheduled_datetime) IN (12, 1, 2) THEN 'Winter'
        WHEN MONTH(scheduled_datetime) IN (3, 4, 5) THEN 'Spring'
        WHEN MONTH(scheduled_datetime) IN (6, 7, 8) THEN 'Summer'
        ELSE 'Autumn'
    END AS season,
    status,
    COUNT(*) AS flight_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (
        PARTITION BY CASE 
            WHEN MONTH(scheduled_datetime) IN (12, 1, 2) THEN 'Winter'
            WHEN MONTH(scheduled_datetime) IN (3, 4, 5) THEN 'Spring'
            WHEN MONTH(scheduled_datetime) IN (6, 7, 8) THEN 'Summer'
            ELSE 'Autumn' END
    ), 1) AS pct_of_season
FROM flights
GROUP BY 
    CASE 
        WHEN MONTH(scheduled_datetime) IN (12, 1, 2) THEN 'Winter'
        WHEN MONTH(scheduled_datetime) IN (3, 4, 5) THEN 'Spring'
        WHEN MONTH(scheduled_datetime) IN (6, 7, 8) THEN 'Summer'
        ELSE 'Autumn'
    END,
    status
ORDER BY season, status;

-- Question: Compare alliance performance
SELECT a.alliance,
       COUNT(*) AS total_flights,
       ROUND(AVG(CASE WHEN f.status = 'delayed' THEN f.delay_minutes END), 1) AS avg_delay_min,
       ROUND(SUM(CASE WHEN f.status = 'on_time' THEN 1 ELSE 0 END) * 100.0 / 
             NULLIF(SUM(CASE WHEN f.status != 'cancelled' THEN 1 ELSE 0 END), 0), 1) AS on_time_pct,
       SUM(f.passenger_count) AS total_passengers
FROM flights f
JOIN airlines a ON f.airline_code = a.airline_code
GROUP BY a.alliance
ORDER BY total_flights DESC;
