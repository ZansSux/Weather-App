# Minimalist Dark-Theme Weather Station

A sleek, lightweight desktop weather application built in Python using **Tkinter** and powered by the **Open-Meteo API**. It features asynchronous-style UI updates, a 3-day multi-metric parameter grid forecast, local query caching via an **SQLite** relational database, and an adaptive layout engine that matches system-default scaling rules.

![License](https://img.shields.io/badge/license-MIT-black)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Tkinter](https://img.shields.io/badge/UI-Tkinter%20%2F%20ttk-orange)

## Key Features
* 🌓 **Dark Theme:** Deep dark-mode color palette made using custom styling structures to prevent native OS canvas bleeding.
* 📊 **Comprehensive 3-Day Forecast:** Extracts real-time daily aggregates including high/low temperature metrics, relative humidity caps, peak wind speeds, and precise sunset/sunrise ranges.
* 💾 **Local Relational Caching:** Automatically provisions an SQLite schema to cache incoming geolocation payloads, timestamping lookups for instant offline auditing.
* 🔍 **System-Safe Layout:** Implements dynamic column weights over rigid text-wrapping limits, resolving visual component clipping across diverse resolution scaling settings.

## Quick Start

### Prerequisites
Ensure you have Python 3.8 or higher installed. The application utilizes the native standard library (`tkinter`, `sqlite3`, `datetime`) alongside the third-party requests engine.

### Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/ZansSux/Weather-App.git]
   cd Weather-App
2. Install the necessary network wrapper dependency:
    pip install requests
3. Execute the dashboard instance:
    python weather.py