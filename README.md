# ✈️ Air Tracker - Flight Analytics Dashboard

A comprehensive flight data analytics platform that fetches real-time flight and airport data from the AeroDataBox API and stores it in a MySQL database. Includes an interactive Streamlit dashboard for analyzing flights, aircraft, and airport operations.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Database Schema](#database-schema)
- [API Reference](#api-reference)
- [Analytics Queries](#analytics-queries)
- [Troubleshooting](#troubleshooting)

---

## Overview

Air Tracker is a full-stack flight analytics solution that:
- Fetches real-time flight data from **AeroDataBox API**
- Collects airport and aircraft information
- Stores data in a **MySQL database**
- Provides interactive visualizations through a **Streamlit web dashboard**
- Performs complex analytics queries on flight operations

### Key Use Cases
- Monitor flight operations across multiple airports
- Track aircraft utilization rates
- Analyze flight delays and cancellations
- Identify route patterns and trends
- Compare domestic vs. international flights

---

## Features

### 📊 Dashboard Analytics (11 Reports)

1. **Total Flights per Aircraft Model** - Aircraft usage frequency
2. **High-Frequency Aircraft** - Aircraft used more than 5 times
3. **Busy Departure Airports** - Airports with >5 outbound flights
4. **Top Destination Airports** - Most popular arrival destinations
5. **Flight Classification** - Domestic vs. International breakdown
6. **Recent Arrivals at DEL** - 5 most recent flights to Delhi
7. **Underutilized Airports** - Airports with no incoming flights
8. **Flight Status by Airline** - On-time, delayed, and cancelled flights
9. **Cancelled Flights Log** - Details of all cancelled operations
10. **Multi-Aircraft Routes** - City pairs served by multiple aircraft
11. **Delay Analysis** - Percentage of delayed flights per destination

---

## Project Structure

```
Air_tracker/
├── Air_tracker.ipynb       # Jupyter notebook with data collection & analysis
├── ui.py                   # Streamlit dashboard application
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── DATABASE_SCHEMA.md     # Detailed database schema documentation
```

---

## Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **MySQL**: 8.0 or higher
- **RAM**: 2GB minimum
- **Internet**: Required for API calls

### API Credentials
- AeroDataBox RapidAPI key (obtain from [RapidAPI](https://rapidapi.com/aeropropulsive/api/aerodatabox))

---

## Installation & Setup

### Step 1: Clone/Setup Project
```bash
cd Air_tracker
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure MySQL Database

1. **Start MySQL Service**
   ```bash
   # Windows
   net start MySQL80
   
   # macOS
   brew services start mysql
   
   # Linux
   sudo systemctl start mysql
   ```

2. **Create Database User (optional)**
   ```sql
   CREATE USER 'air_tracker_user'@'localhost' IDENTIFIED BY 'secure_password';
   GRANT ALL PRIVILEGES ON air_tracker.* TO 'air_tracker_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

### Step 4: Update Configuration

Edit the connection details in `Air_tracker.ipynb` and `ui.py`:

```python
conn = mysql.connector.connect(
    host="localhost",
    user="root",                    # Change to your username
    password="12345678",            # Change to your password
    database="air_tracker"
)
```

### Step 5: Run Data Collection

1. Open `Air_tracker.ipynb` in Jupyter
2. Execute cells in order:
   - Database & table creation
   - Airport data fetch
   - Flight data fetch
   - Aircraft data fetch
   - Delay data fetch
   - Verification queries

```bash
jupyter notebook Air_tracker.ipynb
```

### Step 6: Launch Dashboard

```bash
streamlit run ui.py
```

The dashboard will open at `http://localhost:8501`

---

## Usage

### Running the Dashboard

```bash
streamlit run ui.py
```

**Dashboard Features:**
- Real-time data displays
- Sortable and filterable tables
- Auto-refresh on data updates
- Responsive design for desktop/tablet

### Updating Data

To refresh flight data:

1. Open `Air_tracker.ipynb`
2. Re-run the flight data collection cells
3. Dashboard automatically reflects new data on next page load

### Customizing Queries

Edit the SQL queries in `ui.py` to analyze specific airports or time periods:

```python
query_custom = """
SELECT * FROM flights
WHERE origin_iata = 'DEL'
AND scheduled_departure > DATE_SUB(NOW(), INTERVAL 7 DAY)
"""
st.dataframe(run_query(query_custom))
```

---

## Database Schema

### Tables

#### `airport`
Stores airport information
```sql
- airport_id (INT, PK)
- icao_code (VARCHAR)
- iata_code (VARCHAR, UNIQUE)
- name (VARCHAR)
- city (VARCHAR)
- country (VARCHAR)
- continent (VARCHAR)
- latitude (DOUBLE)
- longitude (DOUBLE)
- timezone (VARCHAR)
```

#### `aircraft`
Stores aircraft details
```sql
- aircraft_id (INT, PK)
- registration (VARCHAR, UNIQUE)
- model (VARCHAR)
- manufacturer (VARCHAR)
- icao_type_code (VARCHAR)
- owner (VARCHAR)
```

#### `flights`
Stores flight records
```sql
- flight_id (VARCHAR, PK)
- flight_number (VARCHAR)
- aircraft_registration (VARCHAR)
- origin_iata (VARCHAR)
- destination_iata (VARCHAR)
- scheduled_departure (DATETIME)
- actual_departure (DATETIME)
- scheduled_arrival (DATETIME)
- actual_arrival (DATETIME)
- status (VARCHAR)
- airline_code (VARCHAR)
```

#### `airport_delays`
Stores delay statistics
```sql
- delay_id (INT, PK)
- airport_iata (VARCHAR)
- delay_date (DATE)
- total_flights (INT)
- delayed_flights (INT)
- avg_delay_min (INT)
- median_delay_min (INT)
- canceled_flights (INT)
```

---

## API Reference

### AeroDataBox Endpoints Used

| Endpoint | Purpose |
|----------|---------|
| `/airports/iata/{iata}` | Fetch airport details |
| `/flights/airports/iata/{iata}` | Get flights for airport |
| `/aircrafts/reg/{registration}` | Get aircraft information |
| `/airports/iata/{iata}/delays` | Get airport delay statistics |

**Rate Limiting:** 100 requests/day (RapidAPI free tier)

---

## Analytics Queries

### Common Analysis Queries

**Top 5 Busiest Airports by Arrivals:**
```sql
SELECT ap.name, COUNT(*) AS arrivals
FROM flights f
JOIN airport ap ON f.destination_iata = ap.iata_code
GROUP BY ap.name
ORDER BY arrivals DESC
LIMIT 5;
```

**Flight Delay Rate by Airline:**
```sql
SELECT airline_code, 
    ROUND(SUM(CASE WHEN status='Delayed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS delay_rate
FROM flights
GROUP BY airline_code;
```

**Aircraft Utilization:**
```sql
SELECT a.registration, a.model, COUNT(*) AS total_flights
FROM flights f
JOIN aircraft a ON f.aircraft_registration = a.registration
GROUP BY a.registration, a.model
ORDER BY total_flights DESC;
```

---

## Troubleshooting

### Common Issues

**1. Database Connection Error**
```
Error: Can't connect to MySQL server on 'localhost'
```
**Solution:**
- Verify MySQL is running: `mysql -u root -p`
- Check credentials in code
- Ensure database `air_tracker` exists

**2. API Key Error**
```
Error: x-rapidapi-key not valid
```
**Solution:**
- Verify API key is correct in `Air_tracker.ipynb`
- Check API key hasn't expired
- Ensure RapidAPI account is active

**3. Streamlit Connection Error**
```
Error: ModuleNotFoundError: No module named 'streamlit'
```
**Solution:**
- Run: `pip install -r requirements.txt`
- Verify Python environment: `python --version`

**4. Missing Data in Dashboard**
**Solution:**
- Verify data collection completed in notebook
- Check database: `SELECT COUNT(*) FROM flights;`
- Re-run data collection cells if needed

### Debug Mode

Run Streamlit with verbose logging:
```bash
streamlit run ui.py --logger.level=debug
```

---

## Performance Tips

1. **Database Indexing**: Add indexes on frequently queried columns
   ```sql
   CREATE INDEX idx_flights_origin ON flights(origin_iata);
   CREATE INDEX idx_flights_destination ON flights(destination_iata);
   ```

2. **Query Optimization**: Use LIMIT clauses to reduce data transfer

3. **API Rate Limits**: Implement delays between API calls (already done with `time.sleep()`)

---

## Future Enhancements

- [ ] Real-time data streaming
- [ ] Predictive delay analysis using ML
- [ ] Weather data integration
- [ ] Email alerts for delays/cancellations
- [ ] Mobile app version
- [ ] Advanced filtering and custom reports
- [ ] Export to CSV/PDF reports

---

## License

This project is for educational and analytical purposes.

---

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review query syntax in analytics section
3. Verify MySQL and API configurations

---

**Last Updated**: January 2026
