"""
Air Tracker Analytics Dashboard

A Streamlit-based web application for analyzing flight operations,
aircraft utilization, and airport statistics from the air_tracker
MySQL database.

Author: Air Tracker Team
Version: 1.0
Date: January 2026
"""

import streamlit as st
import mysql.connector
import pandas as pd
from typing import Optional

# ============================================================
# DATABASE CONNECTION
# ============================================================

# Database connection configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "12345678",
    "database": "air_tracker"
}

conn = mysql.connector.connect(**DB_CONFIG)


def run_query(query: str) -> pd.DataFrame:
    """
    Execute a SQL query and return results as a pandas DataFrame.
    
    Args:
        query (str): SQL query string to execute
        
    Returns:
        pd.DataFrame: Query results with column names as headers
        
    Raises:
        mysql.connector.Error: If database query fails
        
    Example:
        >>> query = "SELECT * FROM flights LIMIT 10"
        >>> df = run_query(query)
        >>> print(df.head())
    """
    return pd.read_sql(query, conn)

st.set_page_config(page_title="Air Tracker Analytics", layout="wide")
st.title("✈️ Air Tracker – Flight Analytics Dashboard")

# ============================================================
# 1️⃣ Flights per aircraft model
# ============================================================
st.header("1️⃣ Total Flights per Aircraft Model")

query1 = """
SELECT a.model AS aircraft_model, COUNT(f.flight_id) AS flight_count
FROM flights f
JOIN aircraft a ON f.aircraft_registration = a.registration
GROUP BY a.model
ORDER BY flight_count DESC;
"""
st.dataframe(run_query(query1))

# ============================================================
# 2️⃣ Aircraft used more than 5 times
# ============================================================
st.header("2️⃣ Aircraft Used More Than 5 Flights")

query2 = """
SELECT a.registration, a.model, COUNT(f.flight_id) AS flight_count
FROM flights f
JOIN aircraft a ON f.aircraft_registration = a.registration
GROUP BY a.registration, a.model
HAVING COUNT(f.flight_id) > 5;
"""
st.dataframe(run_query(query2))

# ============================================================
# 3️⃣ Airports with more than 5 outbound flights
# ============================================================
st.header("3️⃣ Airports with >5 Outbound Flights")

query3 = """
SELECT ap.name AS airport_name, COUNT(f.flight_id) AS outbound_flights
FROM flights f
JOIN airport ap ON ap.iata_code = f.origin_iata
GROUP BY ap.name
HAVING COUNT(f.flight_id) > 5;
"""
st.dataframe(run_query(query3))

# ============================================================
# 4️⃣ Top 3 destination airports
# ============================================================
st.header("4️⃣ Top 3 Destination Airports")

query4 = """
SELECT ap.name, ap.city, COUNT(f.flight_id) AS arrival_count
FROM flights f
JOIN airport ap ON ap.iata_code = f.destination_iata
GROUP BY ap.name, ap.city
ORDER BY arrival_count DESC
LIMIT 3;
"""
st.dataframe(run_query(query4))

# ============================================================
# 5️⃣ Domestic vs International flights
# ============================================================
st.header("5️⃣ Domestic vs International Flights")

query5 = """
SELECT
    f.flight_number,
    ao.name AS origin_airport,
    ad.name AS destination_airport,
    CASE
        WHEN ao.country = ad.country THEN 'Domestic'
        ELSE 'International'
    END AS flight_type
FROM flights f
JOIN airport ao ON ao.iata_code = f.origin_iata
JOIN airport ad ON ad.iata_code = f.destination_iata;
"""
st.dataframe(run_query(query5))

# ============================================================
# 6️⃣ 5 most recent arrivals at DEL
# ============================================================
st.header("6️⃣ Most Recent Arrivals at DEL")

query6 = """
SELECT
    f.flight_number,
    f.aircraft_registration AS aircraft,
    ao.name AS departure_airport,
    COALESCE(f.actual_arrival, f.scheduled_arrival) AS arrival_time
FROM flights f
JOIN airport ao ON ao.iata_code = f.origin_iata
WHERE f.destination_iata = 'DEL'
ORDER BY arrival_time DESC
LIMIT 5;
"""
st.dataframe(run_query(query6))

# ============================================================
# 7️⃣ Airports with no arrivals
# ============================================================
st.header("7️⃣ Airports With No Arriving Flights")

query7 = """
SELECT ap.iata_code, ap.name
FROM airport ap
LEFT JOIN flights f ON ap.iata_code = f.destination_iata
WHERE f.flight_id IS NULL;
"""
st.dataframe(run_query(query7))

# ============================================================
# 8️⃣ Flights by airline & status
# ============================================================
st.header("8️⃣ Flights by Airline and Status")

query8 = """
SELECT
    airline_code,
    SUM(CASE WHEN status = 'On Time' THEN 1 ELSE 0 END) AS on_time,
    SUM(CASE WHEN status = 'Delayed' THEN 1 ELSE 0 END) AS delayed_count,
    SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_count
FROM flights
GROUP BY airline_code;
"""
st.dataframe(run_query(query8))

# ============================================================
# 9️⃣ Cancelled flights
# ============================================================
st.header("9️⃣ Cancelled Flights")

query9 = """
SELECT
    f.flight_number,
    f.aircraft_registration,
    ao.name AS origin_airport,
    ad.name AS destination_airport,
    f.scheduled_departure
FROM flights f
JOIN airport ao ON ao.iata_code = f.origin_iata
JOIN airport ad ON ad.iata_code = f.destination_iata
WHERE f.status = 'Cancelled'
ORDER BY f.scheduled_departure DESC;
"""
st.dataframe(run_query(query9))

# ============================================================
# 🔟 City pairs with >2 aircraft models
# ============================================================
st.header("🔟 City Pairs with Multiple Aircraft Models")

query10 = """
SELECT
    ao.city AS origin_city,
    ad.city AS destination_city,
    COUNT(DISTINCT a.model) AS aircraft_models
FROM flights f
JOIN airport ao ON ao.iata_code = f.origin_iata
JOIN airport ad ON ad.iata_code = f.destination_iata
JOIN aircraft a ON a.registration = f.aircraft_registration
GROUP BY ao.city, ad.city
HAVING COUNT(DISTINCT a.model) > 2;
"""
st.dataframe(run_query(query10))

# ============================================================
# 1️⃣1️⃣ % of delayed flights per destination
# ============================================================
st.header("1️⃣1️⃣ % Delayed Flights per Destination Airport")

query11 = """
SELECT
    ap.name AS destination_airport,
    ROUND(
        SUM(CASE WHEN f.status = 'Delayed' THEN 1 ELSE 0 END) * 100.0
        / COUNT(f.flight_id),
        2
    ) AS delayed_percentage
FROM flights f
JOIN airport ap ON ap.iata_code = f.destination_iata
GROUP BY ap.name
ORDER BY delayed_percentage DESC;
"""
st.dataframe(run_query(query11))

st.success("✅ All 11 analytics loaded successfully")
