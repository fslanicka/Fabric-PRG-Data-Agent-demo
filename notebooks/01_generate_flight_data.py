"""
Prague Airport Flight Data Generator for Microsoft Fabric
==========================================================

Usage in Fabric:
    Copy this script into a Fabric Notebook, splitting at each '# CELL N' marker.
    Each CELL comment denotes where to create a new notebook cell.
    CELL 1 should be a Markdown cell; all others are Code cells.
    Attach a Lakehouse before running — tables are written to the default Lakehouse.

Generates ~50,000 realistic flight records for Prague (PRG) airport across
2024-01-01 to 2025-12-31, plus supporting airlines, airports, and weather tables.
"""

# ============================================================================
# CELL 1 — Markdown Cell
# ============================================================================
# Create a **Markdown** cell in Fabric with the following content:
#
#   # Prague Airport Flight Data Generator
#   Generates ~50,000 realistic flight records for PRG airport (2024-2025)
#

# ============================================================================
# CELL 2 — Imports and Configuration
# ============================================================================

from pyspark.sql import SparkSession
from pyspark.sql.types import *
import pyspark.sql.functions as F
import builtins
import random
from datetime import datetime, timedelta, date
import math

# Fabric notebooks pre-import PySpark functions (round, max, min, abs, ...) into the
# global namespace, which shadows Python builtins.  Restore them explicitly so that
# the data-generation code below can use plain round() / max() / min().
round = builtins.round
max = builtins.max
min = builtins.min

spark = SparkSession.builder.getOrCreate()

# Configuration
START_DATE = date(2024, 1, 1)
END_DATE = date(2025, 12, 31)
TARGET_FLIGHTS = 50000
SEED = 42
random.seed(SEED)

# ============================================================================
# CELL 3 — Airlines Data
# ============================================================================
# ~40 airlines that actually fly to/from Prague

airlines_data = [
    ("OK", "Czech Airlines", "Czech Republic", "SkyTeam"),
    ("LH", "Lufthansa", "Germany", "Star Alliance"),
    ("FR", "Ryanair", "Ireland", "None"),
    ("W6", "Wizz Air", "Hungary", "None"),
    ("BA", "British Airways", "United Kingdom", "Oneworld"),
    ("AF", "Air France", "France", "SkyTeam"),
    ("KL", "KLM Royal Dutch Airlines", "Netherlands", "SkyTeam"),
    ("LX", "Swiss International Air Lines", "Switzerland", "Star Alliance"),
    ("OS", "Austrian Airlines", "Austria", "Star Alliance"),
    ("AZ", "ITA Airways", "Italy", "SkyTeam"),
    ("SK", "SAS Scandinavian Airlines", "Sweden", "Star Alliance"),
    ("AY", "Finnair", "Finland", "Oneworld"),
    ("IB", "Iberia", "Spain", "Oneworld"),
    ("VY", "Vueling", "Spain", "None"),
    ("U2", "easyJet", "United Kingdom", "None"),
    ("TK", "Turkish Airlines", "Turkey", "Star Alliance"),
    ("EK", "Emirates", "UAE", "None"),
    ("QR", "Qatar Airways", "Qatar", "Oneworld"),
    ("EY", "Etihad Airways", "UAE", "None"),
    ("KE", "Korean Air", "South Korea", "SkyTeam"),
    ("SU", "Aeroflot", "Russia", "SkyTeam"),
    ("EL", "Ellinair", "Greece", "None"),
    ("PC", "Pegasus Airlines", "Turkey", "None"),
    ("RO", "TAROM", "Romania", "SkyTeam"),
    ("FB", "Bulgaria Air", "Bulgaria", "None"),
    ("PS", "Ukraine International Airlines", "Ukraine", "None"),
    ("BT", "airBaltic", "Latvia", "None"),
    ("LO", "LOT Polish Airlines", "Poland", "Star Alliance"),
    ("TP", "TAP Air Portugal", "Portugal", "Star Alliance"),
    ("EI", "Aer Lingus", "Ireland", "None"),
    ("SN", "Brussels Airlines", "Belgium", "Star Alliance"),
    ("HV", "Transavia", "Netherlands", "None"),
    ("DE", "Condor", "Germany", "None"),
    ("XR", "Corendon Airlines Europe", "Malta", "None"),
    ("QS", "Smartwings", "Czech Republic", "None"),
    ("3Z", "Smartwings Poland", "Poland", "None"),
    ("TO", "Transavia France", "France", "None"),
    ("6E", "IndiGo", "India", "None"),
    ("CI", "China Airlines", "Taiwan", "SkyTeam"),
    ("ET", "Ethiopian Airlines", "Ethiopia", "Star Alliance"),
]

airlines_schema = StructType([
    StructField("airline_code", StringType(), False),
    StructField("airline_name", StringType(), False),
    StructField("country", StringType(), False),
    StructField("alliance", StringType(), False),
])

df_airlines = spark.createDataFrame(airlines_data, airlines_schema)
df_airlines.write.mode("overwrite").format("delta").saveAsTable("airlines")
print(f"Airlines table created: {df_airlines.count()} rows")

# ============================================================================
# CELL 4 — Airports Data
# ============================================================================
# ~100 airports connected to Prague with real IATA codes, cities, countries, coordinates

airports_data = [
    # Prague itself
    ("PRG", "Václav Havel Airport Prague", "Prague", "Czech Republic", "Europe", 50.1008, 14.2600),
    # Major European hubs
    ("LHR", "Heathrow Airport", "London", "United Kingdom", "Europe", 51.4700, -0.4543),
    ("CDG", "Charles de Gaulle Airport", "Paris", "France", "Europe", 49.0097, 2.5479),
    ("FRA", "Frankfurt Airport", "Frankfurt", "Germany", "Europe", 50.0379, 8.5622),
    ("AMS", "Amsterdam Schiphol Airport", "Amsterdam", "Netherlands", "Europe", 52.3086, 4.7639),
    ("MUC", "Munich Airport", "Munich", "Germany", "Europe", 48.3538, 11.7861),
    ("FCO", "Leonardo da Vinci Airport", "Rome", "Italy", "Europe", 41.8003, 12.2389),
    ("MAD", "Adolfo Suárez Airport", "Madrid", "Spain", "Europe", 40.4936, -3.5668),
    ("BCN", "Barcelona–El Prat Airport", "Barcelona", "Spain", "Europe", 41.2971, 2.0785),
    ("VIE", "Vienna International Airport", "Vienna", "Austria", "Europe", 48.1103, 16.5697),
    ("ZRH", "Zurich Airport", "Zurich", "Switzerland", "Europe", 47.4647, 8.5492),
    ("BRU", "Brussels Airport", "Brussels", "Belgium", "Europe", 50.9014, 4.4844),
    ("CPH", "Copenhagen Airport", "Copenhagen", "Denmark", "Europe", 55.6180, 12.6561),
    ("HEL", "Helsinki Airport", "Helsinki", "Finland", "Europe", 60.3172, 24.9633),
    ("ARN", "Stockholm Arlanda Airport", "Stockholm", "Sweden", "Europe", 59.6519, 17.9186),
    ("OSL", "Oslo Gardermoen Airport", "Oslo", "Norway", "Europe", 60.1939, 11.1004),
    ("LIS", "Lisbon Airport", "Lisbon", "Portugal", "Europe", 38.7813, -9.1359),
    ("DUB", "Dublin Airport", "Dublin", "Ireland", "Europe", 53.4264, -6.2499),
    ("ATH", "Athens International Airport", "Athens", "Greece", "Europe", 37.9364, 23.9445),
    ("IST", "Istanbul Airport", "Istanbul", "Turkey", "Europe", 41.2608, 28.7419),
    ("SAW", "Sabiha Gökçen Airport", "Istanbul", "Turkey", "Europe", 40.8986, 29.3092),
    ("WAW", "Warsaw Chopin Airport", "Warsaw", "Poland", "Europe", 52.1657, 20.9671),
    ("BUD", "Budapest Ferenc Liszt Airport", "Budapest", "Hungary", "Europe", 47.4369, 19.2556),
    ("OTP", "Henri Coandă Airport", "Bucharest", "Romania", "Europe", 44.5711, 26.0850),
    ("SOF", "Sofia Airport", "Sofia", "Bulgaria", "Europe", 42.6952, 23.4064),
    ("BEG", "Belgrade Nikola Tesla Airport", "Belgrade", "Serbia", "Europe", 44.8184, 20.3091),
    ("ZAG", "Franjo Tuđman Airport", "Zagreb", "Croatia", "Europe", 45.7429, 16.0688),
    ("LJU", "Ljubljana Jože Pučnik Airport", "Ljubljana", "Slovenia", "Europe", 46.2237, 14.4576),
    ("BTS", "M. R. Štefánik Airport", "Bratislava", "Slovakia", "Europe", 48.1702, 17.2127),
    ("KRK", "John Paul II Airport", "Kraków", "Poland", "Europe", 50.0777, 19.7848),
    ("GDN", "Gdańsk Lech Wałęsa Airport", "Gdańsk", "Poland", "Europe", 54.3776, 18.4662),
    ("RIX", "Riga International Airport", "Riga", "Latvia", "Europe", 56.9236, 23.9711),
    ("TLL", "Tallinn Airport", "Tallinn", "Estonia", "Europe", 59.4133, 24.8328),
    ("VNO", "Vilnius Airport", "Vilnius", "Lithuania", "Europe", 54.6341, 25.2858),
    ("MXP", "Milan Malpensa Airport", "Milan", "Italy", "Europe", 45.6301, 8.7231),
    ("NAP", "Naples International Airport", "Naples", "Italy", "Europe", 40.8860, 14.2908),
    ("PMI", "Palma de Mallorca Airport", "Palma", "Spain", "Europe", 39.5517, 2.7388),
    ("AGP", "Málaga Airport", "Málaga", "Spain", "Europe", 36.6749, -4.4991),
    ("TFS", "Tenerife South Airport", "Tenerife", "Spain", "Europe", 28.0445, -16.5725),
    ("LPA", "Gran Canaria Airport", "Las Palmas", "Spain", "Europe", 27.9319, -15.3866),
    ("HER", "Heraklion Airport", "Heraklion", "Greece", "Europe", 35.3397, 25.1803),
    ("SKG", "Thessaloniki Airport", "Thessaloniki", "Greece", "Europe", 40.5197, 22.9709),
    ("CFU", "Corfu Airport", "Corfu", "Greece", "Europe", 39.6019, 19.9117),
    ("RHO", "Rhodes Diagoras Airport", "Rhodes", "Greece", "Europe", 36.4054, 28.0862),
    ("DBV", "Dubrovnik Airport", "Dubrovnik", "Croatia", "Europe", 42.5614, 18.2682),
    ("SPU", "Split Airport", "Split", "Croatia", "Europe", 43.5389, 16.2980),
    ("TIV", "Tivat Airport", "Tivat", "Montenegro", "Europe", 42.4047, 18.7233),
    ("BOJ", "Burgas Airport", "Burgas", "Bulgaria", "Europe", 42.5696, 27.5152),
    ("VAR", "Varna Airport", "Varna", "Bulgaria", "Europe", 43.2321, 27.8251),
    ("EDI", "Edinburgh Airport", "Edinburgh", "United Kingdom", "Europe", 55.9508, -3.3725),
    ("MAN", "Manchester Airport", "Manchester", "United Kingdom", "Europe", 53.3537, -2.2750),
    ("STN", "London Stansted Airport", "London", "United Kingdom", "Europe", 51.8850, 0.2350),
    ("LTN", "London Luton Airport", "London", "United Kingdom", "Europe", 51.8747, -0.3684),
    ("BER", "Berlin Brandenburg Airport", "Berlin", "Germany", "Europe", 52.3667, 13.5033),
    ("HAM", "Hamburg Airport", "Hamburg", "Germany", "Europe", 53.6304, 9.9882),
    ("DUS", "Düsseldorf Airport", "Düsseldorf", "Germany", "Europe", 51.2895, 6.7668),
    ("STR", "Stuttgart Airport", "Stuttgart", "Germany", "Europe", 48.6899, 9.2220),
    ("NUE", "Nuremberg Airport", "Nuremberg", "Germany", "Europe", 49.4987, 11.0669),
    ("ORY", "Paris Orly Airport", "Paris", "France", "Europe", 48.7233, 2.3794),
    ("NCE", "Nice Côte d'Azur Airport", "Nice", "France", "Europe", 43.6584, 7.2159),
    ("MRS", "Marseille Provence Airport", "Marseille", "France", "Europe", 43.4393, 5.2214),
    # Middle East
    ("DXB", "Dubai International Airport", "Dubai", "UAE", "Middle East", 25.2532, 55.3657),
    ("DOH", "Hamad International Airport", "Doha", "Qatar", "Middle East", 25.2731, 51.6082),
    ("AUH", "Abu Dhabi International Airport", "Abu Dhabi", "UAE", "Middle East", 24.4430, 54.6511),
    ("TLV", "Ben Gurion Airport", "Tel Aviv", "Israel", "Middle East", 32.0114, 34.8867),
    ("AMM", "Queen Alia Airport", "Amman", "Jordan", "Middle East", 31.7226, 35.9932),
    # Asia
    ("ICN", "Incheon International Airport", "Seoul", "South Korea", "Asia", 37.4602, 126.4407),
    ("PVG", "Shanghai Pudong Airport", "Shanghai", "China", "Asia", 31.1443, 121.8083),
    ("BKK", "Suvarnabhumi Airport", "Bangkok", "Thailand", "Asia", 13.6900, 100.7501),
    ("DEL", "Indira Gandhi Airport", "New Delhi", "India", "Asia", 28.5562, 77.1000),
    ("NRT", "Narita International Airport", "Tokyo", "Japan", "Asia", 35.7647, 140.3864),
    # North America
    ("JFK", "John F. Kennedy Airport", "New York", "USA", "North America", 40.6413, -73.7781),
    ("EWR", "Newark Liberty Airport", "Newark", "USA", "North America", 40.6895, -74.1745),
    ("ORD", "O'Hare International Airport", "Chicago", "USA", "North America", 41.9742, -87.9073),
    ("YYZ", "Toronto Pearson Airport", "Toronto", "Canada", "North America", 43.6777, -79.6248),
    ("ATL", "Hartsfield-Jackson Airport", "Atlanta", "USA", "North America", 33.6407, -84.4277),
    # Africa
    ("CAI", "Cairo International Airport", "Cairo", "Egypt", "Africa", 30.1219, 31.4056),
    ("CMN", "Mohammed V Airport", "Casablanca", "Morocco", "Africa", 33.3675, -7.5898),
    ("ADD", "Bole International Airport", "Addis Ababa", "Ethiopia", "Africa", 8.9778, 38.7994),
    ("HRG", "Hurghada Airport", "Hurghada", "Egypt", "Africa", 27.1784, 33.7994),
    ("SSH", "Sharm el-Sheikh Airport", "Sharm el-Sheikh", "Egypt", "Africa", 27.9773, 34.3951),
    # Seasonal / Charter
    ("AYT", "Antalya Airport", "Antalya", "Turkey", "Europe", 36.8987, 30.7925),
    ("DLM", "Dalaman Airport", "Dalaman", "Turkey", "Europe", 36.7131, 28.7925),
    ("PFO", "Paphos Airport", "Paphos", "Cyprus", "Europe", 34.7180, 32.4856),
    ("LCA", "Larnaca Airport", "Larnaca", "Cyprus", "Europe", 34.8751, 33.6249),
    ("TUN", "Tunis-Carthage Airport", "Tunis", "Tunisia", "Africa", 36.8510, 10.2272),
    ("RAK", "Marrakech Menara Airport", "Marrakech", "Morocco", "Africa", 31.6069, -8.0363),
    # More European
    ("GVA", "Geneva Airport", "Geneva", "Switzerland", "Europe", 46.2381, 6.1089),
    ("BSL", "EuroAirport Basel", "Basel", "Switzerland", "Europe", 47.5896, 7.5299),
    ("KTW", "Katowice Airport", "Katowice", "Poland", "Europe", 50.4743, 19.0800),
    ("WRO", "Copernicus Airport Wrocław", "Wrocław", "Poland", "Europe", 51.1027, 16.8858),
    ("POZ", "Poznań-Ławica Airport", "Poznań", "Poland", "Europe", 52.4211, 16.8263),
    ("PSA", "Pisa International Airport", "Pisa", "Italy", "Europe", 43.6839, 10.3927),
    ("BLQ", "Bologna Airport", "Bologna", "Italy", "Europe", 44.5354, 11.2887),
    ("CTA", "Catania-Fontanarossa Airport", "Catania", "Italy", "Europe", 37.4668, 15.0664),
    ("KEF", "Keflavík Airport", "Reykjavik", "Iceland", "Europe", 63.9850, -22.6056),
    ("BGY", "Milan Bergamo Airport", "Bergamo", "Italy", "Europe", 45.6739, 9.7042),
    ("EIN", "Eindhoven Airport", "Eindhoven", "Netherlands", "Europe", 51.4501, 5.3743),
    ("BRQ", "Brno-Tuřany Airport", "Brno", "Czech Republic", "Europe", 49.1513, 16.6944),
    ("KSC", "Košice Airport", "Košice", "Slovakia", "Europe", 48.6631, 21.2411),
]

airports_schema = StructType([
    StructField("airport_code", StringType(), False),
    StructField("airport_name", StringType(), False),
    StructField("city", StringType(), False),
    StructField("country", StringType(), False),
    StructField("region", StringType(), False),
    StructField("latitude", DoubleType(), False),
    StructField("longitude", DoubleType(), False),
])

df_airports = spark.createDataFrame(airports_data, airports_schema)
df_airports.write.mode("overwrite").format("delta").saveAsTable("airports")
print(f"Airports table created: {df_airports.count()} rows")

# ============================================================================
# CELL 5 — Weather Data
# ============================================================================
# Generate realistic Prague weather for 2024-2025 based on actual climate patterns


def generate_weather(start_date, end_date):
    """Generate realistic daily weather data for Prague.

    Uses sinusoidal temperature curves and seasonal probability distributions
    for conditions like fog, snow, rain, and storms.
    """
    weather_rows = []
    current = start_date
    while current <= end_date:
        day_of_year = current.timetuple().tm_yday

        # Temperature: sinusoidal pattern peaking in July
        base_temp = 10 + 12 * math.sin((day_of_year - 90) * 2 * math.pi / 365)
        temp = round(base_temp + random.gauss(0, 3), 1)

        # Wind speed: slightly higher in winter
        base_wind = 12 + 4 * math.cos((day_of_year - 15) * 2 * math.pi / 365)
        wind = round(max(2.0, base_wind + random.gauss(0, 5)), 1)

        # Condition based on season and randomness
        month = current.month
        r = random.random()
        if month in (12, 1, 2):  # Winter
            if r < 0.15:
                condition = "snow"
            elif r < 0.30:
                condition = "fog"
            elif r < 0.55:
                condition = "cloudy"
            elif r < 0.70:
                condition = "rain"
            elif r < 0.75:
                condition = "storm"
            else:
                condition = "clear"
        elif month in (3, 4, 5):  # Spring
            if r < 0.25:
                condition = "rain"
            elif r < 0.45:
                condition = "cloudy"
            elif r < 0.50:
                condition = "fog"
            elif r < 0.55:
                condition = "storm"
            else:
                condition = "clear"
        elif month in (6, 7, 8):  # Summer
            if r < 0.10:
                condition = "rain"
            elif r < 0.12:
                condition = "storm"
            elif r < 0.25:
                condition = "cloudy"
            else:
                condition = "clear"
        else:  # Autumn
            if r < 0.20:
                condition = "rain"
            elif r < 0.35:
                condition = "fog"
            elif r < 0.50:
                condition = "cloudy"
            elif r < 0.55:
                condition = "storm"
            elif r < 0.60:
                condition = "snow"
            else:
                condition = "clear"

        # Precipitation (mm)
        if condition in ("rain", "storm"):
            precip = round(random.uniform(1, 25 if condition == "storm" else 15), 1)
        elif condition == "snow":
            precip = round(random.uniform(0.5, 10), 1)
        else:
            precip = 0.0

        # Visibility (km)
        if condition == "fog":
            vis = round(random.uniform(0.2, 3.0), 1)
        elif condition == "storm":
            vis = round(random.uniform(2, 6), 1)
        elif condition in ("rain", "snow"):
            vis = round(random.uniform(4, 8), 1)
        else:
            vis = round(random.uniform(8, 15), 1)

        weather_rows.append((
            current.isoformat(),
            temp,
            wind,
            vis,
            precip,
            condition,
        ))
        current += timedelta(days=1)
    return weather_rows


weather_data = generate_weather(START_DATE, END_DATE)

weather_schema = StructType([
    StructField("date", StringType(), False),
    StructField("temperature_celsius", DoubleType(), False),
    StructField("wind_speed_kmh", DoubleType(), False),
    StructField("visibility_km", DoubleType(), False),
    StructField("precipitation_mm", DoubleType(), False),
    StructField("condition", StringType(), False),
])

df_weather = spark.createDataFrame(weather_data, weather_schema)
df_weather = df_weather.withColumn("date", F.col("date").cast("date"))
df_weather.write.mode("overwrite").format("delta").saveAsTable("weather")
print(f"Weather table created: {df_weather.count()} rows")

# ============================================================================
# CELL 6 — Flight Data Generation (Vectorized with NumPy/Pandas)
# ============================================================================
# Generates ~50K flights using vectorized NumPy operations (~10-30 seconds).
# All heavy work happens in NumPy arrays — no Python loops over individual flights.

import pandas as pd
import numpy as np

rng = np.random.default_rng(SEED)

# ---- Route definitions ----
# (airline, destination, base_weekly_freq, is_schengen, aircraft_types, avg_passengers)
routes = [
    ("OK", "CDG", 14, True, ["A320", "A319"], 145),
    ("OK", "AMS", 14, True, ["A320", "A319"], 140),
    ("OK", "FCO", 10, True, ["A320"], 155),
    ("OK", "MAD", 7, True, ["A320"], 150),
    ("OK", "LHR", 14, True, ["A320", "A321"], 160),
    ("OK", "BCN", 7, True, ["A320"], 155),
    ("OK", "ATH", 7, True, ["A320"], 150),
    ("OK", "BUD", 7, True, ["ATR 72"], 55),
    ("OK", "BEG", 5, True, ["ATR 72"], 50),
    ("OK", "ICN", 3, False, ["A330"], 250),
    ("LH", "FRA", 28, True, ["A320", "A319"], 145),
    ("LH", "MUC", 21, True, ["A320", "CRJ 900"], 120),
    ("FR", "STN", 14, True, ["B737-800"], 180),
    ("FR", "BGY", 10, True, ["B737-800"], 175),
    ("FR", "MAD", 7, True, ["B737-800"], 180),
    ("FR", "BCN", 7, True, ["B737-800"], 178),
    ("FR", "BER", 7, True, ["B737-800"], 172),
    ("FR", "DUB", 7, True, ["B737-800"], 170),
    ("FR", "AGP", 5, True, ["B737-800"], 180),
    ("FR", "PMI", 5, True, ["B737-800"], 178),
    ("W6", "LTN", 10, True, ["A321neo"], 200),
    ("W6", "BUD", 7, True, ["A320"], 170),
    ("W6", "SOF", 5, True, ["A320"], 165),
    ("W6", "OTP", 5, True, ["A320"], 168),
    ("W6", "TIV", 3, True, ["A320"], 170),
    ("BA", "LHR", 14, True, ["A320", "A321"], 160),
    ("AF", "CDG", 14, True, ["A320", "A319"], 145),
    ("KL", "AMS", 14, True, ["B737-800", "E190"], 135),
    ("LX", "ZRH", 14, True, ["A220-300", "A320"], 125),
    ("OS", "VIE", 21, True, ["A320", "E195"], 130),
    ("SK", "CPH", 10, True, ["A320neo", "CRJ 900"], 120),
    ("SK", "ARN", 7, True, ["A320neo"], 140),
    ("AY", "HEL", 7, True, ["A320", "E190"], 125),
    ("IB", "MAD", 7, True, ["A320"], 150),
    ("VY", "BCN", 7, True, ["A320"], 165),
    ("U2", "LTN", 7, True, ["A320"], 170),
    ("U2", "MAN", 5, True, ["A320"], 165),
    ("U2", "EDI", 3, True, ["A320"], 160),
    ("TK", "IST", 14, False, ["A321", "B737-800"], 170),
    ("EK", "DXB", 7, False, ["B777-300ER"], 340),
    ("QR", "DOH", 7, False, ["A350-900", "B787-8"], 280),
    ("EY", "AUH", 5, False, ["B787-9"], 260),
    ("KE", "ICN", 5, False, ["B787-9", "A330"], 270),
    ("QS", "AYT", 7, False, ["B737-800", "B737 MAX 8"], 180),
    ("QS", "HER", 5, True, ["B737-800"], 178),
    ("QS", "HRG", 3, False, ["B737-800"], 175),
    ("QS", "BOJ", 5, True, ["B737-800"], 170),
    ("QS", "CFU", 3, True, ["B737-800"], 172),
    ("QS", "RHO", 3, True, ["B737-800"], 168),
    ("QS", "PMI", 5, True, ["B737-800"], 178),
    ("QS", "TFS", 3, False, ["B737 MAX 8"], 182),
    ("QS", "LPA", 2, False, ["B737 MAX 8"], 180),
    ("QS", "SSH", 2, False, ["B737-800"], 176),
    ("LO", "WAW", 14, True, ["E195", "E175"], 85),
    ("BT", "RIX", 10, True, ["A220-300"], 120),
    ("TP", "LIS", 7, True, ["A320neo"], 155),
    ("EI", "DUB", 7, True, ["A320"], 160),
    ("SN", "BRU", 10, True, ["A319", "A320"], 130),
    ("PC", "SAW", 7, False, ["A320neo"], 175),
    ("RO", "OTP", 7, True, ["ATR 72", "B737-800"], 90),
    ("FB", "SOF", 7, True, ["A320", "E190"], 110),
    ("ET", "ADD", 3, False, ["B787-8"], 260),
    ("DE", "FRA", 7, True, ["A320"], 165),
    ("HV", "EIN", 5, True, ["B737-800"], 175),
    ("CI", "PVG", 2, False, ["A350-900"], 300),
]

leisure_destinations = {
    "AYT", "HER", "HRG", "BOJ", "CFU", "RHO", "PMI", "AGP",
    "TFS", "LPA", "SSH", "DLM", "PFO", "DBV", "SPU", "TIV",
    "RAK", "BKK",
}

SEASONAL_BASE = np.array(
    [0.0, 0.65, 0.70, 0.80, 0.90, 1.00, 1.20, 1.35, 1.30, 1.10, 0.95, 0.75, 0.80]
)  # index 0 unused; index 1-12 = Jan-Dec

HOUR_WEIGHTS = np.array([
    0.5, 0.2, 0.1, 0.1, 0.2, 0.5, 2, 4, 5, 5, 4, 3,
    3, 3, 3, 4, 5, 5, 4, 3, 2, 1.5, 1, 0.5,
])
HOUR_PROBS = HOUR_WEIGHTS / HOUR_WEIGHTS.sum()

MINUTE_OPTIONS = np.arange(0, 60, 5)

T1_GATES = np.array(
    [f"A{i}" for i in range(1, 16)]
    + [f"B{i}" for i in range(1, 21)]
    + [f"C{i}" for i in range(1, 11)]
)
T2_GATES = np.array(
    [f"D{i}" for i in range(1, 16)]
    + [f"E{i}" for i in range(1, 11)]
)

WX_BOOST_MAP = {
    "storm": 0.30, "fog": 0.20, "snow": 0.15,
    "rain": 0.05, "cloudy": 0.0, "clear": 0.0,
}

ALL_DELAY_REASONS = np.array(
    ["weather", "technical", "crew", "air_traffic", "security", "late_aircraft"]
)
DIVERT_REASONS = np.array(["weather", "technical", "air_traffic"])


# ---- Step 1: Flatten routes (expand aircraft variants) ----
flat_routes = []
for airline, dest, freq, schengen, acft_list, avg_pax in routes:
    for acft in acft_list:
        flat_routes.append({
            "airline": airline, "dest": dest,
            "weekly_freq": freq / len(acft_list),
            "schengen": schengen, "acft": acft,
            "avg_pax": avg_pax,
            "leisure": dest in leisure_destinations,
            "terminal": "T1" if schengen else "T2",
        })

n_routes = len(flat_routes)
r_airlines  = np.array([r["airline"]    for r in flat_routes])
r_dests     = np.array([r["dest"]       for r in flat_routes])
r_freqs     = np.array([r["weekly_freq"]for r in flat_routes])
r_schengen  = np.array([r["schengen"]   for r in flat_routes])
r_acft      = np.array([r["acft"]       for r in flat_routes])
r_avg_pax   = np.array([r["avg_pax"]    for r in flat_routes])
r_leisure   = np.array([r["leisure"]    for r in flat_routes])
r_terminals = np.array([r["terminal"]   for r in flat_routes])

# ---- Step 2: Date spine ----
dates = pd.date_range(START_DATE, END_DATE, freq="D")
n_days = len(dates)
print(f"{n_routes} route-aircraft variants × {n_days} days = {n_routes * n_days:,} slots")

# ---- Step 3: Cross-product indices ----
day_idx = np.repeat(np.arange(n_days), n_routes)
rte_idx = np.tile(np.arange(n_routes), n_days)

months = dates.month.values[day_idx]          # month for each slot
freqs  = r_freqs[rte_idx]                     # weekly freq for each slot
is_lsr = r_leisure[rte_idx]                   # leisure flag for each slot

# ---- Step 4: Seasonal multiplier ----
mult = SEASONAL_BASE[months].copy()
mult[is_lsr & np.isin(months, [6, 7, 8])]  *= 1.15
mult[is_lsr & np.isin(months, [12, 1, 2])] *= 0.60

# ---- Step 5: Poisson sample → flight count per slot ----
daily_lambda = freqs * mult / 7.0
flight_counts = rng.poisson(daily_lambda)

has_flights = flight_counts > 0
expand_idx = np.repeat(np.where(has_flights)[0], flight_counts[has_flights])
n = len(expand_idx)  # total individual flights (one direction)
print(f"Sampled {n:,} one-way flights → {n * 2:,} total (dep + arr)")

# ---- Step 6: Per-flight attribute arrays ----
fl_airlines  = r_airlines[rte_idx[expand_idx]]
fl_dests     = r_dests[rte_idx[expand_idx]]
fl_acft      = r_acft[rte_idx[expand_idx]]
fl_avg_pax   = r_avg_pax[rte_idx[expand_idx]].astype(float)
fl_terminals = r_terminals[rte_idx[expand_idx]]
fl_schengen  = r_schengen[rte_idx[expand_idx]]
fl_mult      = mult[expand_idx]
fl_dates     = dates[day_idx[expand_idx]]

# Flight numbers
fl_fn_nums = rng.integers(100, 10000, size=n)
fl_numbers = np.array([f"{a} {num}" for a, num in zip(fl_airlines, fl_fn_nums)])

# Scheduled hour (weighted) + minute
fl_hours   = rng.choice(24, size=n, p=HOUR_PROBS)
fl_minutes = rng.choice(MINUTE_OPTIONS, size=n)
dep_sched  = (
    pd.to_datetime(fl_dates)
    + pd.to_timedelta(fl_hours.astype(int), unit="h")
    + pd.to_timedelta(fl_minutes.astype(int), unit="m")
)

# Weather lookup (from CELL 5 output)
wx_lookup = {w[0]: w[5] for w in weather_data}  # date_str → condition
fl_date_strs = np.array([str(d.date()) for d in dep_sched])
fl_wx        = np.array([wx_lookup.get(d, "clear") for d in fl_date_strs])
fl_wx_boost  = np.array([WX_BOOST_MAP.get(c, 0.0) for c in fl_wx])

# Gate assignment
fl_gates = np.where(
    fl_schengen,
    rng.choice(T1_GATES, size=n),
    rng.choice(T2_GATES, size=n),
)

# Passenger count (Gaussian around avg × load factor, min 10)
fl_pax = np.maximum(
    10,
    (fl_avg_pax * (0.7 + 0.3 * fl_mult)
     + rng.standard_normal(n) * fl_avg_pax * 0.15
    ).astype(int),
)


def _status_block(size, wx_boost, wx_cond, rng_inst):
    """Vectorised status / delay_minutes / delay_reason / offset_minutes."""
    rolls = rng_inst.random(size)
    cancel_th = 0.03 + wx_boost * 0.3
    divert_th = cancel_th + 0.01
    delay_th  = divert_th + 0.18 + wx_boost

    status = np.full(size, "on_time", dtype=object)
    m_cn = rolls < cancel_th
    m_dv = (~m_cn) & (rolls < divert_th)
    m_dl = (~m_cn) & (~m_dv) & (rolls < delay_th)
    m_ot = ~(m_cn | m_dv | m_dl)

    status[m_cn] = "cancelled"
    status[m_dv] = "diverted"
    status[m_dl] = "delayed"

    # Delay minutes
    delay_min = np.full(size, np.nan)
    delay_min[m_ot] = 0.0
    if m_dl.any():
        delay_min[m_dl] = np.minimum(
            rng_inst.exponential(25, size=m_dl.sum()).astype(int) + 5, 360
        )
    if m_dv.any():
        delay_min[m_dv] = rng_inst.integers(30, 181, size=m_dv.sum())

    # Delay reason
    reason = np.full(size, None, dtype=object)
    if m_dl.any():
        n_dl = m_dl.sum()
        r_arr = rng_inst.choice(ALL_DELAY_REASONS, size=n_dl)
        bad_wx = np.isin(wx_cond[m_dl], ["storm", "fog", "snow"])
        wx_override = bad_wx & (rng_inst.random(n_dl) < 0.5)
        r_arr[wx_override] = "weather"
        reason[m_dl] = r_arr
    if m_dv.any():
        reason[m_dv] = rng_inst.choice(DIVERT_REASONS, size=m_dv.sum())

    # Actual-time offset (minutes from scheduled)
    offset = np.full(size, np.nan)
    if m_ot.any():
        offset[m_ot] = rng_inst.integers(-5, 6, size=m_ot.sum())
    offset[m_dl] = delay_min[m_dl]
    offset[m_dv] = delay_min[m_dv]
    # cancelled stays NaN → will become NaT

    return status, delay_min, reason, offset


# ---- Step 7: Build departures ----
dep_status, dep_delay, dep_reason, dep_offset = _status_block(n, fl_wx_boost, fl_wx, rng)

# Compute actual_datetime: scheduled + offset, or NaT for cancelled
dep_sched_s = dep_sched.to_series().reset_index(drop=True)
dep_actual = pd.Series(pd.NaT, index=dep_sched_s.index)
valid = ~np.isnan(dep_offset)
dep_actual[valid] = dep_sched_s[valid] + pd.to_timedelta(dep_offset[valid], unit="m")

pdf_dep = pd.DataFrame({
    "flight_number": fl_numbers,
    "airline_code": fl_airlines,
    "flight_type": "departure",
    "origin_airport_code": "PRG",
    "destination_airport_code": fl_dests,
    "scheduled_datetime": dep_sched,
    "actual_datetime": dep_actual,
    "status": dep_status,
    "delay_minutes": dep_delay,
    "delay_reason": dep_reason,
    "terminal": fl_terminals,
    "gate": fl_gates,
    "aircraft_type": fl_acft,
    "passenger_count": fl_pax,
})

# ---- Step 8: Build arrivals (separate random draws) ----
arr_offset_h = rng.integers(2, 7, size=n)
arr_sched = dep_sched + pd.to_timedelta(arr_offset_h, unit="h")

arr_status, arr_delay, arr_reason, arr_off = _status_block(n, fl_wx_boost, fl_wx, rng)

arr_sched_s = arr_sched.to_series().reset_index(drop=True)
arr_actual = pd.Series(pd.NaT, index=arr_sched_s.index)
valid_a = ~np.isnan(arr_off)
arr_actual[valid_a] = arr_sched_s[valid_a] + pd.to_timedelta(arr_off[valid_a], unit="m")

arr_fn_nums = rng.integers(100, 10000, size=n)
arr_numbers = np.array([f"{a} {num}" for a, num in zip(fl_airlines, arr_fn_nums)])
arr_gates = np.where(fl_schengen, rng.choice(T1_GATES, size=n), rng.choice(T2_GATES, size=n))
arr_pax = np.maximum(
    10,
    (fl_avg_pax * (0.7 + 0.3 * fl_mult)
     + rng.standard_normal(n) * fl_avg_pax * 0.15
    ).astype(int),
)

pdf_arr = pd.DataFrame({
    "flight_number": arr_numbers,
    "airline_code": fl_airlines,
    "flight_type": "arrival",
    "origin_airport_code": fl_dests,
    "destination_airport_code": "PRG",
    "scheduled_datetime": arr_sched,
    "actual_datetime": arr_actual,
    "status": arr_status,
    "delay_minutes": arr_delay,
    "delay_reason": arr_reason,
    "terminal": fl_terminals,
    "gate": arr_gates,
    "aircraft_type": fl_acft,
    "passenger_count": arr_pax,
})

# Drop arrivals that land after the date range
pdf_arr = pdf_arr[pdf_arr["scheduled_datetime"] <= pd.Timestamp(END_DATE) + pd.Timedelta(days=1)]

# ---- Step 9: Combine departures + arrivals ----
pdf_all = pd.concat([pdf_dep, pdf_arr], ignore_index=True)
pdf_all.insert(0, "flight_id", range(1, len(pdf_all) + 1))

# Convert delay_minutes: NaN → None-compatible nullable integer
pdf_all["delay_minutes"] = pdf_all["delay_minutes"].astype("Int64")

print(f"Generated {len(pdf_all):,} total flights")
print(f"  Departures : {(pdf_all.flight_type == 'departure').sum():,}")
print(f"  Arrivals   : {(pdf_all.flight_type == 'arrival').sum():,}")
print(f"  Status mix : {pdf_all.status.value_counts().to_dict()}")

# ============================================================================
# CELL 7 — Write Flights to Delta Table
# ============================================================================

flights_schema = StructType([
    StructField("flight_id", IntegerType(), False),
    StructField("flight_number", StringType(), False),
    StructField("airline_code", StringType(), False),
    StructField("flight_type", StringType(), False),
    StructField("origin_airport_code", StringType(), False),
    StructField("destination_airport_code", StringType(), False),
    StructField("scheduled_datetime", TimestampType(), False),
    StructField("actual_datetime", TimestampType(), True),
    StructField("status", StringType(), False),
    StructField("delay_minutes", IntegerType(), True),
    StructField("delay_reason", StringType(), True),
    StructField("terminal", StringType(), False),
    StructField("gate", StringType(), True),
    StructField("aircraft_type", StringType(), False),
    StructField("passenger_count", IntegerType(), False),
])

df_flights = spark.createDataFrame(pdf_all, schema=flights_schema)
df_flights.write.mode("overwrite").format("delta").saveAsTable("flights")
print(f"Flights table created: {df_flights.count():,} rows")

# ============================================================================
# CELL 8 — Verification & Summary
# ============================================================================

print("=" * 60)
print("DATA GENERATION COMPLETE")
print("=" * 60)

tables = ["airlines", "airports", "weather", "flights"]
for t in tables:
    count = spark.sql(f"SELECT COUNT(*) as cnt FROM {t}").first()["cnt"]
    print(f"  {t}: {count:,} rows")

print("\n--- Flight Statistics ---")
spark.sql("""
    SELECT
        flight_type,
        status,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY flight_type), 1) as pct
    FROM flights
    GROUP BY flight_type, status
    ORDER BY flight_type, status
""").show()

print("\n--- Top 10 Airlines by Flight Count ---")
spark.sql("""
    SELECT f.airline_code, a.airline_name, COUNT(*) as flight_count
    FROM flights f JOIN airlines a ON f.airline_code = a.airline_code
    GROUP BY f.airline_code, a.airline_name
    ORDER BY flight_count DESC
    LIMIT 10
""").show(truncate=False)

print("\n--- Monthly Flight Distribution ---")
spark.sql("""
    SELECT
        YEAR(scheduled_datetime) as year,
        MONTH(scheduled_datetime) as month,
        COUNT(*) as flights
    FROM flights
    GROUP BY YEAR(scheduled_datetime), MONTH(scheduled_datetime)
    ORDER BY year, month
""").show(24)

print("\nAll tables are ready in your Lakehouse!")
