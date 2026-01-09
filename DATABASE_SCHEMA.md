# Air Tracker - Database Schema Documentation

## Overview
The Air Tracker database (`air_tracker`) contains 4 main tables that store flight, airport, aircraft, and delay data.

---

## Table Definitions

### 1. `airport` Table
Stores information about airports worldwide.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `airport_id` | INT | PRIMARY KEY, AUTO_INCREMENT | Unique airport identifier |
| `icao_code` | VARCHAR(4) | UNIQUE, NULL | International Civil Aviation Organization code |
| `iata_code` | VARCHAR(3) | UNIQUE, NULL | International Air Transport Association code |
| `name` | VARCHAR(150) | NULL | Full airport name |
| `city` | VARCHAR(100) | NULL | City where airport is located |
| `country` | VARCHAR(100) | NULL | Country name |
| `continent` | VARCHAR(50) | NULL | Continent name |
| `latitude` | DOUBLE | NULL | Geographic latitude |
| `longitude` | DOUBLE | NULL | Geographic longitude |
| `timezone` | VARCHAR(50) | NULL | Time zone identifier |

**Sample Query:**
```sql
SELECT * FROM airport WHERE country = 'India';
```

---

### 2. `aircraft` Table
Stores aircraft model and registration information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `aircraft_id` | INT | PRIMARY KEY, AUTO_INCREMENT | Unique aircraft identifier |
| `registration` | VARCHAR(10) | UNIQUE, NULL | Aircraft registration/tail number |
| `model` | VARCHAR(50) | NULL | Aircraft model name (e.g., Boeing 777) |
| `manufacturer` | VARCHAR(50) | NULL | Aircraft manufacturer |
| `icao_type_code` | VARCHAR(10) | NULL | ICAO type designator |
| `owner` | VARCHAR(100) | NULL | Airline or owner name |

**Sample Query:**
```sql
SELECT * FROM aircraft WHERE manufacturer = 'Boeing';
```

---

### 3. `flights` Table
Stores flight operation records.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `flight_id` | VARCHAR(50) | PRIMARY KEY | Unique flight identifier (UUID) |
| `flight_number` | VARCHAR(20) | NULL | Flight number (e.g., AI101) |
| `aircraft_registration` | VARCHAR(300) | NULL | Aircraft registration (FK to aircraft table) |
| `origin_iata` | VARCHAR(7) | NULL | Departure airport IATA code (FK to airport) |
| `destination_iata` | VARCHAR(7) | NULL | Arrival airport IATA code (FK to airport) |
| `scheduled_departure` | DATETIME | NULL | Scheduled departure time (UTC) |
| `actual_departure` | DATETIME | NULL | Actual departure time (local) |
| `scheduled_arrival` | DATETIME | NULL | Scheduled arrival time (local) |
| `actual_arrival` | DATETIME | NULL | Actual arrival time (UTC) |
| `status` | VARCHAR(20) | NULL | Flight status (On Time, Delayed, Cancelled) |
| `airline_code` | VARCHAR(50) | NULL | Airline IATA code |

**Sample Query:**
```sql
SELECT * FROM flights WHERE origin_iata = 'DEL' AND status = 'Delayed';
```

**Indexes (Recommended):**
```sql
CREATE INDEX idx_flights_origin ON flights(origin_iata);
CREATE INDEX idx_flights_destination ON flights(destination_iata);
CREATE INDEX idx_flights_status ON flights(status);
CREATE INDEX idx_flights_airline ON flights(airline_code);
```

---

### 4. `airport_delays` Table
Stores aggregated delay statistics for airports.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `delay_id` | INT | PRIMARY KEY, AUTO_INCREMENT | Unique delay record identifier |
| `airport_iata` | VARCHAR(5) | NULL | Airport IATA code |
| `delay_date` | DATE | NULL | Date of delay statistics |
| `total_flights` | INT | NULL | Total flights on this date |
| `delayed_flights` | INT | NULL | Number of delayed flights |
| `avg_delay_min` | INT | NULL | Average delay in minutes |
| `median_delay_min` | INT | NULL | Median delay in minutes |
| `canceled_flights` | INT | NULL | Number of cancelled flights |

**Sample Query:**
```sql
SELECT * FROM airport_delays 
WHERE airport_iata = 'DEL' 
AND delay_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY);
```

---

## Relationships

```
airport ─────────┐
                 ├─── flights
aircraft ────────┘
                 └─── airport_delays

Key Relationships:
- flights.origin_iata → airport.iata_code
- flights.destination_iata → airport.iata_code
- flights.aircraft_registration → aircraft.registration
- airport_delays.airport_iata → airport.iata_code
```

---

## Data Types Reference

| Type | Usage | Max Size |
|------|-------|----------|
| INT | Numeric ID, counts | -2,147,483,648 to 2,147,483,647 |
| DOUBLE | Coordinates (lat/lon) | 15 decimal places |
| VARCHAR(n) | Text with limit | n characters |
| DATETIME | Date and time | YYYY-MM-DD HH:MM:SS |
| DATE | Date only | YYYY-MM-DD |

---

## Sample Data

### Airport Example
```
airport_id: 1
icao_code: VIDP
iata_code: DEL
name: Indira Gandhi International Airport
city: New Delhi
country: India
continent: Asia
latitude: 28.5665
longitude: 77.1197
timezone: Asia/Kolkata
```

### Aircraft Example
```
aircraft_id: 1
registration: VT-ALH
model: Boeing 777-300ER
manufacturer: Boeing
icao_type_code: B773
owner: Air India
```

### Flight Example
```
flight_id: 550e8400-e29b-41d4-a716-446655440001
flight_number: AI101
aircraft_registration: VT-ALH
origin_iata: DEL
destination_iata: BOM
scheduled_departure: 2026-01-09 08:00:00
actual_departure: 2026-01-09 08:15:00
scheduled_arrival: 2026-01-09 10:30:00
actual_arrival: 2026-01-09 10:45:00
status: Delayed
airline_code: AI
```

---

## Common Queries

### 1. Find all flights from specific airport
```sql
SELECT f.flight_number, a.name as aircraft, f.destination_iata, f.status
FROM flights f
JOIN aircraft a ON f.aircraft_registration = a.registration
WHERE f.origin_iata = 'DEL'
ORDER BY f.scheduled_departure DESC;
```

### 2. Aircraft utilization report
```sql
SELECT a.registration, a.model, COUNT(*) as total_flights, a.owner
FROM flights f
JOIN aircraft a ON f.aircraft_registration = a.registration
GROUP BY a.registration, a.model, a.owner
ORDER BY total_flights DESC;
```

### 3. On-time performance by airline
```sql
SELECT airline_code,
    COUNT(*) as total_flights,
    SUM(CASE WHEN status = 'On Time' THEN 1 ELSE 0 END) as on_time_flights,
    ROUND(100.0 * SUM(CASE WHEN status = 'On Time' THEN 1 ELSE 0 END) / COUNT(*), 2) as on_time_percentage
FROM flights
GROUP BY airline_code
ORDER BY on_time_percentage DESC;
```

### 4. Domestic vs International flights
```sql
SELECT 
    CASE WHEN ao.country = ad.country THEN 'Domestic' ELSE 'International' END as flight_type,
    COUNT(*) as flight_count
FROM flights f
JOIN airport ao ON f.origin_iata = ao.iata_code
JOIN airport ad ON f.destination_iata = ad.iata_code
GROUP BY flight_type;
```

### 5. Airport delay statistics
```sql
SELECT airport_iata, delay_date,
    total_flights,
    delayed_flights,
    ROUND(100.0 * delayed_flights / total_flights, 2) as delay_percentage,
    avg_delay_min,
    canceled_flights
FROM airport_delays
WHERE delay_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
ORDER BY delay_percentage DESC;
```

---

## Database Maintenance

### Backup Database
```bash
mysqldump -u root -p air_tracker > air_tracker_backup.sql
```

### Restore Database
```bash
mysql -u root -p air_tracker < air_tracker_backup.sql
```

### Check Database Size
```sql
SELECT 
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) as size_mb
FROM information_schema.tables
WHERE table_schema = 'air_tracker'
ORDER BY size_mb DESC;
```

### Optimize Tables
```sql
OPTIMIZE TABLE airport, aircraft, flights, airport_delays;
```

---

## Performance Considerations

1. **Indexing**: Add indexes on frequently queried columns
2. **Data Archival**: Archive old flight data to separate tables
3. **Query Optimization**: Use EXPLAIN to analyze slow queries
4. **Partitioning**: Consider partitioning flights table by date for large datasets

---

**Last Updated**: January 2026
