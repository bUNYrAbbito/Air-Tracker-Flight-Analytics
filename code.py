# %%
!pip install requests mysql-connector-python 


# %%
import requests
import mysql.connector
import pandas as pd
from datetime import datetime
import time


# %%
API_HOST = "aerodatabox.p.rapidapi.com"
API_KEY = "71ff288c8emshc86261cd5e028edp170804jsnb6a70ef0a394"

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST
}


# %%
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345678",
    database="air_tracker",
)

cursor = conn.cursor(buffered=True)



# %%
cursor.execute("CREATE DATABASE IF NOT EXISTS air_tracker")

# %%
cursor.execute("""
CREATE TABLE IF NOT EXISTS airport (
    airport_id INT AUTO_INCREMENT PRIMARY KEY,
    icao_code VARCHAR(4) UNIQUE,
    iata_code VARCHAR(3) UNIQUE,
    name VARCHAR(150),
    city VARCHAR(100),
    country VARCHAR(100),
    continent VARCHAR(50),
    latitude DOUBLE,
    longitude DOUBLE,
    timezone VARCHAR(50)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS aircraft (
    aircraft_id INT AUTO_INCREMENT PRIMARY KEY,
    registration VARCHAR(10) UNIQUE,
    model VARCHAR(50),
    manufacturer VARCHAR(50),
    icao_type_code VARCHAR(10),
    owner VARCHAR(100)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS flights (
    flight_id VARCHAR(50) PRIMARY KEY,
    flight_number VARCHAR(20),
    aircraft_registration VARCHAR(300),
    origin_iata VARCHAR(7),
    destination_iata VARCHAR(7),
    scheduled_departure DATETIME,
    actual_departure DATETIME,
    scheduled_arrival DATETIME,
    actual_arrival DATETIME,
    status VARCHAR(20),
    airline_code VARCHAR(50)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS airport_delays (
    delay_id INT AUTO_INCREMENT PRIMARY KEY,
    airport_iata VARCHAR(5),
    delay_date DATE,
    total_flights INT,
    delayed_flights INT,
    avg_delay_min INT,
    median_delay_min INT,
    canceled_flights INT
)
""")

conn.commit()


# %%
import requests

iata_AIRPORTS = ["DEL","BOM","BLR","HYD","MAA","CCU","COK","DXB","LHR","JFK","SIN","CDG","HND","FRA","SYD"]
airport_data_list = []
def ferch_airport(iata):
    url = f"https://aerodatabox.p.rapidapi.com/airports/iata/{iata}"
    response = requests.get(url, headers = HEADERS)
    return response.json()

for iata in iata_AIRPORTS:
    airport_data = ferch_airport(iata)
    airport_data_list.append(airport_data)
    time.sleep(1)  # To avoid hitting the API rate limit


# %%
airport_data_list[0]

# %%
import time

for airport in airport_data_list:

    data = (
        airport.get("icao"),
        airport.get("iata"),
        airport.get("fullName"),
        airport.get("municipalityName"),
        airport.get("country" ,{}).get("name"),
        airport.get("continent",{}).get("name"),
        airport.get("location", {}).get("lat"),
        airport.get("location", {}).get("lon"),
        airport.get("timeZone")
    )

    cursor.execute(
        """
        INSERT INTO airport
        (icao_code, iata_code, name, city, country, continent, latitude, longitude, timezone)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            city = VALUES(city),
            country = VALUES(country),
            continent = VALUES(continent),
            latitude = VALUES(latitude),
            longitude = VALUES(longitude),
            timezone = VALUES(timezone)
        """,
        data
    )

    conn.commit()
    time.sleep(1)


# %%
for iata in airport_data_list:
    response_data = (iata["iata"])
    print(response_data)

# %%
import uuid
from datetime import datetime
import requests

def parse_dt(value):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

def fetch_flights(iata):
    url = f"https://{API_HOST}/flights/airports/iata/{iata}"
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response.json()

iata = ["DEL","BOM","BLR","HYD","MAA","CCU","COK","DXB","LHR","JFK","SIN","CDG","HND","FRA","SYD"]
all_flights = []

for airport in airport_data_list:
    iata = airport.get("iata")
    if not iata:
        continue

    response_data = fetch_flights(origin_iata)

    for flight in response_data.get("departures", []):

        aircraft = flight.get("aircraft", {})
        if not aircraft.get("reg"):
            continue

        # store flight with its origin airport
        all_flights.append({
            "origin_iata": iata,
            "flight": flight
        })


# %%
all_flights

# %%
import uuid

insert_sql = """
    INSERT INTO flights
    (flight_id, flight_number, aircraft_registration,
     origin_iata, destination_iata,
     scheduled_departure, actual_departure,
     scheduled_arrival, actual_arrival,
     status, airline_code)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

for t in all_flights:
    flight = t["flight"]
    origin_iata = t["origin_iata"]
    destination_iata = flight.get("movement",{}).get("airport", {}).get("iata")
    flight_id = str(uuid.uuid4())
    flight_number = flight.get("number")
    aircraft_registration = flight.get("aircraft", {}).get("reg")
    scheduled_departure = parse_dt(
        flight.get("movement", {})
              .get("scheduledTime", {})
              .get("utc")
    )

    actual_departure = parse_dt(flight.get("movement", {}).get("revisedTime", {}).get("local"))
    scheduled_arrival = parse_dt(flight.get("movement", {}).get("scheduledTime", {}).get("local"))
    actual_arrival = parse_dt(flight.get("movement", {}).get("revisedTime", {}).get("utc"))
    status = flight.get("status")
    airline_code = flight.get("airline", {}).get("iata")

    data_row = (
        flight_id,
        flight_number,
        aircraft_registration,
        origin_iata,
        destination_iata,
        scheduled_departure,
        actual_departure,
        scheduled_arrival,
        actual_arrival,
        status,
        airline_code
    )

    cursor.execute(insert_sql, data_row)

conn.commit()


# %%
for item in all_flights:
    flight = item.get("flight", {})
    reg = flight.get("aircraft", {}).get("reg")
    print(reg)


# %%
import requests
import time

def fetch_aircraft(reg):
    url = f"https://aerodatabox.p.rapidapi.com/aircrafts/reg/{reg}"
    r = requests.get(url, headers=HEADERS, timeout=10)

    if r.status_code == 200:
        return r.json()
    else:
        print("Not found:", reg)
        return None

aircraft_regs = []

for item in all_flights:
    flight = item.get("flight", {})
    reg = flight.get("aircraft", {}).get("reg")
    if reg:
        aircraft_regs.append(reg)


aircraft_regs = list(aircraft_regs)

print("Total aircraft:", len(aircraft_regs))


all_aircraft_data = []

for reg in aircraft_regs:
    data = fetch_aircraft(reg)
    if data:
        all_aircraft_data.append(data)
        print(data)

    time.sleep(1)   # prevent API blocking


# %%
all_aircraft_data

# %%
for fd in all_aircraft_data:

    registration = fd.get("reg") 
    model = fd.get("model") 
    manufacturer = fd.get("productionLine") 
    icao_type_code = fd.get("icaoCode") 
    owner = fd.get("airlineName") 

    data = (
        registration,
        model,
        manufacturer,
        icao_type_code,
        owner
    )

    cursor.execute("""
        INSERT IGNORE INTO aircraft
        (registration, model, manufacturer, icao_type_code, owner)
        VALUES (%s, %s, %s, %s, %s)
    """, data)

conn.commit()


# %%
iata_list = ["DEL","BOM","BLR","HYD","MAA","CCU","COK","DXB","LHR","JFK","SIN","CDG","HND","FRA","SYD"]

def fetch_airport_delays(iata):
    url = f"https://aerodatabox.p.rapidapi.com/airports/iata/{iata}/delays"
    return requests.get(url, headers=HEADERS).json()

delay_data = []

for code in iata_list:
    d = fetch_airport_delays(code)

    delay_data.append({
        "airport_iata": code,
        "delay": d
    })

print("Total airports:", len(delay_data))


# %%
delay_data

# %%
for item in delay_data:

    airport_iata = item.get("airport_iata")
    delay = item.get("delay", {})

    # ---------- DATE ----------
    utc_time = delay.get("from", {}).get("utc")
    if not utc_time:
        continue

    delay_date = utc_time[:10]

    # ---------- DELAY INFO ----------
    dep = delay.get("departuresDelayInformation", {})
    arr = delay.get("arrivalsDelayInformation", {})

    total_flights = (dep.get("numTotal") or 0) + (arr.get("numTotal") or 0)
    delayed_flights = (dep.get("numQualifiedTotal") or 0) + (arr.get("numQualifiedTotal") or 0)
    canceled_flights = (dep.get("numCancelled") or 0) + (arr.get("numCancelled") or 0)

    if total_flights == 0:
        continue

    # ---------- CALCULATIONS ----------
    delay_ratio = delayed_flights / total_flights

    # Optional: approximate delay minutes if API doesn't give it
    avg_delay_min = round(delay_ratio * 60, 2)
    median_delay_min = avg_delay_min

    data = (
        airport_iata,
        delay_date,
        total_flights,
        delayed_flights,
        avg_delay_min,
        median_delay_min,
        canceled_flights
    )

    cursor.execute(
        """
        INSERT INTO airport_delays
        (airport_iata, delay_date, total_flights,
         delayed_flights, avg_delay_min,
         median_delay_min, canceled_flights)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """,
        data
    )

conn.commit()


# %%
query1 = """SELECT a.model, COUNT(*) AS flight_count
FROM flights f
JOIN aircraft a 
ON f.aircraft_registration = a.registration
GROUP BY a.model;
"""

cursor.execute(query1)
for q1 in cursor:
    print(q1)

# %%
query2 =""" 
SELECT a.registration, a.model, COUNT(*) AS flight_count
FROM flights f
JOIN aircraft a ON f.aircraft_registration = a.registration
GROUP BY a.registration, a.model
HAVING COUNT(*) > 5;

"""
cursor.execute(query2)
for q2 in cursor:
    print(q2)

# %%
query3 = """
SELECT ap.name, COUNT(*) AS outbound_flights
FROM flights f
JOIN airport ap
ON f.origin_iata = ap.iata_code
GROUP BY ap.name
HAVING COUNT(*) > 5;
"""
cursor.execute(query3)
results = cursor.fetchall()
for q3 in results:
    print("Airport:", q3[0], "| Outbound Flights:", q3[1])

# %%
query4 = """
SELECT ap.name, ap.city, COUNT(*) AS arrivals
FROM flights f
JOIN airport ap
ON f.destination_iata = ap.iata_code
GROUP BY ap.name, ap.city
ORDER BY arrivals DESC
LIMIT 1;
"""

cursor.execute(query4)

results = cursor.fetchall()

for row in results:
    print(
        "Airport:", row[0],
        "| City:", row[1],
        "| Arrivals:", row[2]
    )


# %%
query5 = """
SELECT 
    f.flight_number,
    o.iata_code AS origin,
    d.iata_code AS destination,
    CASE
        WHEN o.country = d.country THEN 'Domestic'
        ELSE 'International'
    END AS flight_type
FROM flights f
JOIN airport o ON f.origin_iata = o.iata_code
JOIN airport d ON f.destination_iata = d.iata_code;
"""

cursor.execute(query5)

results = cursor.fetchall()

for row in results:
    print(
        "Flight:", row[0],
        "| From:", row[1],
        "| To:", row[2],
        "| Type:", row[3]
    )


# %%

query6 = """
SELECT
    f.flight_number,
    f.aircraft_registration AS aircraft,
    ao.name AS departure_airport,
    COALESCE(f.actual_arrival, f.scheduled_arrival) AS arrival_time
FROM flights f
JOIN airport ao
    ON ao.iata_code = f.origin_iata
WHERE f.destination_iata = 'DEL'
ORDER BY arrival_time DESC
LIMIT 5;


"""
cursor.execute(query6)
results = cursor.fetchall()

for row in results:
    print(
        "Flight:", row[0],
        "| Aircraft Model:", row[1],
        "| Departure Airport:", row[2],
        "| Actual Arrival:", row[3]
    )


# %%
query7= """ SELECT
    ap.iata_code,
    ap.name
FROM airport ap
LEFT JOIN flights f
    ON ap.iata_code = f.destination_iata
WHERE f.flight_id IS NULL;
"""
cursor.execute(query7)
results = cursor.fetchall()
for row in results:
    print(
        "IATA Code:", row[0],
        "| Airport Name:", row[1]
    )

# %%
query8 = """
SELECT
    airline_code,
    SUM(CASE WHEN status = 'On Time' THEN 1 ELSE 0 END) AS on_time,
    SUM(CASE WHEN status = 'Delayed' THEN 1 ELSE 0 END) AS `delayed`,
    SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled
FROM flights
GROUP BY airline_code;


"""
cursor.execute(query8)
results = cursor.fetchall()
for row in results:
    print(
        "Airline Code:", row[0],
        "| On Time:", row[1],
        "| Delayed:", row[2],
        "| Cancelled:", row[3]
    )

# %%
query9="""
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
cursor.execute(query9)
results = cursor.fetchall()
for row in results:
    print(
        "Flight:", row[0],
        "| Aircraft Registration:", row[1],
        "| Origin Airport:", row[2],
        "| Destination Airport:", row[3],
        "| Scheduled Departure:", row[4]
    )

# %%
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
cursor.execute(query10)
results = cursor.fetchall()
for row in results:
    print(
        "From:", row[0],
        "| To:", row[1],
        "| Aircraft Models:", row[2]
    )
    

# %%
query11 = """ SELECT
    ap.name AS destination_airport,
    ROUND(
        SUM(CASE WHEN f.status = 'Delayed' THEN 1 ELSE 0 END) * 100.0
        / COUNT(f.flight_id),
        2
    ) AS delayed_percentage
FROM flights f
JOIN airport ap
    ON ap.iata_code = f.destination_iata
GROUP BY ap.name
ORDER BY delayed_percentage DESC;
"""
cursor.execute(query11)
results = cursor.fetchall()
for row in results:
    print(
        "Airport:", row[0],
        "| Delayed Percentage:", row[1], "%"
    )


