# Architectural & Technical Specification

## Core System Architecture
The application runs on a clean **functional execution pipeline** utilizing a non-blocking state model where live data payloads overwrite global dictionary targets (`cached_3day_metrics`), instantly modifying UI widgets without maintaining leaky state objects.

### Operational Lifecycle Design
1. **Boot Lifecycle:** Invokes `init_database()` to assert schema integrity -> Configures platform widget styles via `ttk.Style` primitives -> Spawns parent event-loop.
2. **Ingress Pipeline:** Intercepts `search_weather()` -> Queries Open-Meteo Geocoding REST endpoints -> Resolves WMO decimal indexes into semantic text mappings -> Commits properties to the local SQLite state log -> Spawns dynamic sub-frames.

## Database & Storage Schema
The underlying data layer leverages a zero-configuration storage approach via `sqlite3`. Upon first startup, a database file named `weather_history.db` is built or updated inline via an explicit schema migration script loop (`missing_columns` array).

### Table Schema: `search_log`
```sql
CREATE TABLE search_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT,
    country TEXT,
    max_temp REAL,
    min_temp REAL,
    weather_condition TEXT,
    wind_speed REAL,
    sunrise TEXT,
    sunset TEXT,
    humidity INTEGER,
    timestamp TEXT
);