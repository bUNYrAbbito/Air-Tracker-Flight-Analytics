# Quick Start Guide - Air Tracker

Get up and running with Air Tracker in 5 minutes!

---

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies (1 min)
```bash
cd Air_tracker
pip install -r requirements.txt
```

### Step 2: Configure Database (1 min)
1. Start MySQL service
2. Edit connection in `Air_tracker.ipynb` and `ui.py`:
   - Replace `user="root"` with your username
   - Replace `password="12345678"` with your password

### Step 3: Get API Key (1 min)
1. Go to [RapidAPI](https://rapidapi.com/aeropropulsive/api/aerodatabox)
2. Sign up or log in
3. Copy your API key
4. Paste in `Air_tracker.ipynb` (cell 3):
   ```python
   API_KEY = "your_api_key_here"
   ```

### Step 4: Run Data Collection (1 min)
```bash
jupyter notebook Air_tracker.ipynb
# Run all cells in order (Kernel → Restart & Run All)
```

### Step 5: Launch Dashboard (1 min)
```bash
streamlit run ui.py
```

✅ **Done!** Open http://localhost:8501 in your browser

---

## 📁 File Overview

| File | Purpose |
|------|---------|
| `Air_tracker.ipynb` | Data collection & database setup |
| `ui.py` | Interactive Streamlit dashboard |
| `README.md` | Complete project documentation |
| `DATABASE_SCHEMA.md` | Database structure details |
| `NOTEBOOK_GUIDE.md` | Jupyter notebook guide |
| `requirements.txt` | Python dependencies |

---

## 🎯 Common Tasks

### View Dashboard
```bash
streamlit run ui.py
```
Then open browser to `http://localhost:8501`

### Update Flight Data
```bash
# Edit Air_tracker.ipynb, re-run flight collection cells
jupyter notebook Air_tracker.ipynb
```

### Check Database
```bash
mysql -u root -p
mysql> USE air_tracker;
mysql> SELECT * FROM flights LIMIT 5;
```

### Backup Database
```bash
mysqldump -u root -p air_tracker > backup.sql
```

---

## 🆘 Troubleshooting Quick Links

| Problem | Solution |
|---------|----------|
| MySQL won't connect | Start MySQL service first |
| API key error | Get key from RapidAPI, verify it's in code |
| Streamlit won't start | Run `pip install -r requirements.txt` |
| No data showing | Run all cells in Jupyter notebook |

See README.md for detailed troubleshooting.

---

## 📊 Dashboard Reports at a Glance

1. **Aircraft Models** - Which planes are used most?
2. **Aircraft Frequency** - Which specific planes fly most often?
3. **Hub Airports** - Where are flights originating?
4. **Top Destinations** - Most popular arrival airports?
5. **Flight Types** - Domestic vs International split?
6. **DEL Arrivals** - Recent flights to Delhi?
7. **Unused Airports** - Which airports have no flights?
8. **Airline Performance** - On-time rates by airline?
9. **Cancelled Flights** - Which flights were cancelled?
10. **Multi-Aircraft Routes** - Routes served by multiple aircraft?
11. **Delay Percentage** - Where are delays most common?

---

## 💡 Pro Tips

- 🔄 **Automation:** Schedule notebook to run daily
- 📈 **Scale:** Add more airports in the `iata_AIRPORTS` list
- 🔒 **Security:** Store API key in environment variable
- 📊 **Export:** Use Streamlit's download features
- 🚀 **Deploy:** Host dashboard on Streamlit Cloud (free)

---

## 📞 Support Resources

- **API Docs:** https://documenter.getpostman.com/view/4352470/aerodatabox-api/
- **Streamlit Docs:** https://docs.streamlit.io/
- **MySQL Docs:** https://dev.mysql.com/doc/
- **RapidAPI:** https://rapidapi.com/

---

**Need more details?** See the full README.md or NOTEBOOK_GUIDE.md
