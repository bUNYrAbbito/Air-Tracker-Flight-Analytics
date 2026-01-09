# Air Tracker - Jupyter Notebook Documentation

## Overview

The `Air_tracker.ipynb` notebook contains the complete data collection and initial analysis pipeline for the Air Tracker project. It uses the AeroDataBox API to fetch real-time flight, airport, and aircraft data and stores it in a MySQL database.

---

## Notebook Structure

### Section 1: Setup & Configuration
**Purpose:** Install dependencies and configure API/database connections

**Steps:**
1. Install required packages: `requests`, `mysql-connector-python`
2. Import libraries: `requests`, `mysql.connector`, `pandas`, `datetime`, `time`
3. Configure AeroDataBox API credentials
4. Establish MySQL database connection

**Key Variables:**
```python
API_HOST = "aerodatabox.p.rapidapi.com"
API_KEY = "YOUR_API_KEY"  # Replace with your RapidAPI key
```

---

### Section 2: Database Creation
**Purpose:** Create the database structure

**Creates:**
- `air_tracker` database (if not exists)
- 4 tables with proper schema:
  - `airport` - Airport information
  - `aircraft` - Aircraft registration and details
  - `flights` - Flight records
  - `airport_delays` - Delay statistics

**SQL Operations:**
- CREATE DATABASE IF NOT EXISTS
- CREATE TABLE IF NOT EXISTS (prevents errors on re-run)

---

### Section 3: Airport Data Collection
**Purpose:** Fetch and store airport information

**Process:**
1. Define list of IATA codes: `["DEL","BOM","BLR","HYD","MAA","CCU","COK","DXB","LHR","JFK","SIN","CDG","HND","FRA","SYD"]`
2. Function `fetch_airport(iata)` - Calls `/airports/iata/{iata}` endpoint
3. Loop through each airport with 1-second delay (API rate limiting)
4. Extract data: ICAO code, IATA code, name, city, country, coordinates, timezone
5. Insert into `airport` table with ON DUPLICATE KEY UPDATE

**Important:**
- Rate limiting: `time.sleep(1)` prevents API blocking
- Duplicate handling: Uses INSERT ... ON DUPLICATE KEY UPDATE

---

### Section 4: Flight Data Collection
**Purpose:** Fetch departure flight data from airports

**Process:**
1. Function `fetch_flights(iata)` - Calls `/flights/airports/iata/{iata}` endpoint
2. Iterates through each airport
3. Extracts departure flights from API response
4. Filters flights with valid aircraft registration
5. Stores: flight number, aircraft, origin/destination, times, status

**Data Extracted:**
- Flight number and ID (UUID)
- Aircraft registration
- Origin/destination IATA codes
- Scheduled/actual departure times
- Scheduled/actual arrival times
- Flight status (On Time, Delayed, Cancelled)

**Helper Function:**
```python
def parse_dt(value):
    """Convert ISO 8601 datetime to Python datetime"""
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
```

---

### Section 5: Aircraft Data Collection
**Purpose:** Fetch detailed aircraft information

**Process:**
1. Extract unique aircraft registrations from flights
2. Function `fetch_aircraft(reg)` - Calls `/aircrafts/reg/{registration}` endpoint
3. Parse aircraft details: model, manufacturer, ICAO code, airline owner
4. Insert into `aircraft` table

**Data Extracted:**
- Aircraft registration/tail number
- Aircraft model (e.g., Boeing 777-300ER)
- Manufacturer
- ICAO type code
- Owner/airline name

**Error Handling:**
- Returns None if aircraft not found
- Continues processing remaining aircraft

---

### Section 6: Airport Delay Data Collection
**Purpose:** Fetch delay statistics for airports

**Process:**
1. Function `fetch_airport_delays(iata)` - Calls `/airports/iata/{iata}/delays` endpoint
2. Extracts delay information for departures and arrivals
3. Calculates metrics:
   - Total flights (departures + arrivals)
   - Delayed flights count
   - Cancelled flights count
   - Delay percentages

**Metrics Calculated:**
```python
total_flights = dep.numTotal + arr.numTotal
delayed_flights = dep.numQualifiedTotal + arr.numQualifiedTotal
delay_ratio = delayed_flights / total_flights
```

---

### Section 7: Data Analysis Queries
**Purpose:** Verify data and perform initial analysis

**11 Analysis Queries:**

1. **Query 1:** Aircraft model frequency
2. **Query 2:** High-utilization aircraft (>5 flights)
3. **Query 3:** Busy departure airports (>5 flights)
4. **Query 4:** Top destination airports
5. **Query 5:** Domestic vs international flights
6. **Query 6:** Recent arrivals at DEL
7. **Query 7:** Airports with no arrivals
8. **Query 8:** Flights by airline and status
9. **Query 9:** Cancelled flights
10. **Query 10:** City pairs with multiple aircraft types
11. **Query 11:** Delay percentage by destination

---

## Key Functions

### Airport Data Collection
```python
def fetch_airport(iata):
    """
    Fetch airport information from AeroDataBox API.
    
    Args:
        iata (str): IATA airport code
        
    Returns:
        dict: Airport data including coordinates, timezone, etc.
    """
    url = f"https://aerodatabox.p.rapidapi.com/airports/iata/{iata}"
    response = requests.get(url, headers=HEADERS)
    return response.json()
```

### Flight Data Collection
```python
def fetch_flights(iata):
    """
    Fetch flight data for an airport.
    
    Args:
        iata (str): IATA airport code
        
    Returns:
        dict: Flight data with departures and arrivals
    """
    url = f"https://{API_HOST}/flights/airports/iata/{iata}"
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response.json()
```

### Aircraft Data Collection
```python
def fetch_aircraft(reg):
    """
    Fetch aircraft information by registration.
    
    Args:
        reg (str): Aircraft registration/tail number
        
    Returns:
        dict: Aircraft data or None if not found
    """
    url = f"https://aerodatabox.p.rapidapi.com/aircrafts/reg/{reg}"
    r = requests.get(url, headers=HEADERS, timeout=10)
    
    if r.status_code == 200:
        return r.json()
    else:
        print("Not found:", reg)
        return None
```

### DateTime Parsing
```python
def parse_dt(value):
    """
    Parse ISO 8601 datetime string to Python datetime.
    
    Args:
        value (str): ISO 8601 datetime string
        
    Returns:
        datetime: Parsed datetime object or None
    """
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
```

---

## Data Flow Diagram

```
AeroDataBox API
    ↓
    ├─→ Airport Data → airport table
    ├─→ Flight Data → flights table (with aircraft_registration FK)
    ├─→ Aircraft Data → aircraft table
    └─→ Delay Data → airport_delays table
    
MySQL air_tracker Database
    ↓
    └─→ Streamlit Dashboard (ui.py)
```

---

## Running the Notebook

### Method 1: Jupyter Notebook
```bash
jupyter notebook Air_tracker.ipynb
```
Then open in browser and run cells sequentially.

### Method 2: Jupyter Lab
```bash
jupyter lab Air_tracker.ipynb
```

### Method 3: Command Line
```bash
jupyter nbconvert --to notebook --execute Air_tracker.ipynb
```

---

## Important Notes

### API Rate Limiting
- Free tier: 100 requests/day
- The notebook includes `time.sleep(1)` between API calls
- Total airports: 15 → ~15 API calls minimum
- Add delays if running multiple times

### Database Considerations
- **First Run:** All tables created with IF NOT EXISTS
- **Subsequent Runs:** Data is upserted (duplicates updated)
- **Data Integrity:** Foreign key relationships recommended (add manually if needed)

### Error Handling
- Missing aircraft data: Silently skipped with print message
- API failures: Use try-catch for production
- Database errors: Will raise exceptions

### Performance Tips
1. Run airport data collection once (static data)
2. Re-run flight data collection daily/hourly
3. Aircraft data can be collected once per aircraft
4. Use appropriate LIMIT clauses in queries

---

## Customization Guide

### Add More Airports
```python
iata_AIRPORTS = [
    "DEL", "BOM", "BLR", "HYD",  # Original
    "PEK", "CTU", "CAN", "SHA"    # New Chinese airports
]
```

### Add Custom Analysis
```python
# Add to notebook after data collection
custom_query = """
SELECT your_columns
FROM your_tables
WHERE your_conditions
"""
cursor.execute(custom_query)
results = cursor.fetchall()
for row in results:
    print(row)
```

### Filter by Date Range
```python
query = """
SELECT * FROM flights
WHERE scheduled_departure >= '2026-01-01'
AND scheduled_departure < '2026-02-01'
"""
```

---

## Troubleshooting

### Issue: "API key not valid"
**Solution:**
- Get API key from RapidAPI dashboard
- Paste in `API_KEY` variable
- Ensure RapidAPI account is active

### Issue: "Can't connect to database"
**Solution:**
- Verify MySQL service is running
- Check credentials in connection config
- Ensure database `air_tracker` exists

### Issue: "rate limit exceeded"
**Solution:**
- Increase `time.sleep()` duration
- Run notebook at different times
- Use free trial credits from RapidAPI

### Issue: "KeyError in data extraction"
**Solution:**
- API response format may have changed
- Use `.get()` method with defaults
- Check API documentation for current schema

---

## Database Verification Queries

After running the notebook, verify data:

```sql
-- Check airports loaded
SELECT COUNT(*) FROM airport;  -- Should be ~15

-- Check flights loaded
SELECT COUNT(*) FROM flights;  -- Should be significant

-- Check aircraft loaded
SELECT COUNT(*) FROM aircraft;  -- Should match unique registrations

-- Check delays loaded
SELECT COUNT(*) FROM airport_delays;  -- Should match airports
```

---

## Next Steps

1. ✅ Run notebook to populate database
2. ✅ Verify data with queries above
3. ✅ Launch Streamlit dashboard: `streamlit run ui.py`
4. ✅ Explore analytics in dashboard
5. ✅ Schedule notebook runs for regular data updates

---

**Last Updated:** January 2026
**Version:** 1.0
