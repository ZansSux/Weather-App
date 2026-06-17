import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  
import requests
import sqlite3
from datetime import datetime

def init_database():
    connection = sqlite3.connect("weather_history.db")
    db_cursor = connection.cursor()
    db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            country TEXT,
            max_temp REAL,
            min_temp REAL,
            weather_condition TEXT,
            timestamp TEXT
        )
    """)
    
    missing_columns = [
        ("wind_speed", "REAL"),
        ("sunrise", "TEXT"),
        ("sunset", "TEXT"),
        ("humidity", "INTEGER")
    ]
    
    for col_name, col_type in missing_columns:
        try:
            db_cursor.execute(f"ALTER TABLE search_log ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            pass
            
    connection.commit()
    connection.close()

def save_search_to_log(city, country, max_t, min_t, condition, wind_speed, sunrise, sunset, humidity):
    connection = sqlite3.connect("weather_history.db")
    db_cursor = connection.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db_cursor.execute("""
        INSERT INTO search_log (city, country, max_temp, min_temp, weather_condition, wind_speed, sunrise, sunset, humidity, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (city, country, max_t, min_t, condition, wind_speed, sunrise, sunset, humidity, current_time))
    connection.commit()
    connection.close()

init_database()

def open_history_view():
    history_window = tk.Toplevel(app)
    history_window.title("Historical Search Records")
    history_window.geometry("920x380")
    
    header_lbl = tk.Label(history_window, text="Local Search History", font=("Arial", 12, "bold"))
    header_lbl.pack(pady=10)

    table_container = tk.Frame(history_window)
    table_container.pack(fill="both", expand=True, padx=15, pady=5)

    cols = ("id", "city", "country", "max", "min", "condition", "humidity", "wind_speed", "sunrise", "sunset", "time")
    data_table = ttk.Treeview(table_container, columns=cols, show="headings", height=10)
    
    data_table.heading("id", text="ID")
    data_table.heading("city", text="City")
    data_table.heading("country", text="Country")
    data_table.heading("max", text="Max Temp")
    data_table.heading("min", text="Min Temp")
    data_table.heading("condition", text="Condition")
    data_table.heading("humidity", text="Humidity")
    data_table.heading("wind_speed", text="Wind Speed")
    data_table.heading("sunrise", text="Sunrise")
    data_table.heading("sunset", text="Sunset")
    data_table.heading("time", text="Date & Time")

    data_table.column("id", width=40, anchor="center")
    data_table.column("city", width=100, anchor="w")
    data_table.column("country", width=70, anchor="center")
    data_table.column("max", width=80, anchor="center")
    data_table.column("min", width=80, anchor="center")
    data_table.column("condition", width=110, anchor="w")
    data_table.column("humidity", width=70, anchor="center")
    data_table.column("wind_speed", width=85, anchor="center")
    data_table.column("sunrise", width=70, anchor="center")
    data_table.column("sunset", width=70, anchor="center")
    data_table.column("time", width=130, anchor="center")

    v_scroll = ttk.Scrollbar(table_container, orient="vertical", command=data_table.yview)
    data_table.configure(yscrollcommand=v_scroll.set)
    
    data_table.pack(side="left", fill="both", expand=True)
    v_scroll.pack(side="right", fill="y")

    try:
        connection = sqlite3.connect("weather_history.db")
        db_cursor = connection.cursor()
        db_cursor.execute("SELECT id, city, country, max_temp, min_temp, weather_condition, humidity, wind_speed, sunrise, sunset, timestamp FROM search_log ORDER BY id DESC")
        saved_rows = db_cursor.fetchall()
        
        for record in saved_rows:
            data_table.insert("", tk.END, values=record)
            
        connection.close()
    except Exception as error:
        messagebox.showerror("Database Read Failure", f"Could not read historical records: {error}")

    exit_btn = tk.Button(history_window, text="Dismiss Log", command=history_window.destroy, font=("Arial", 10))
    exit_btn.pack(pady=10)

def search_weather():
    city_name = city_input.get().strip()

    if not city_name:
        messagebox.showerror("Error", "Please enter a city name")
        return

    for widget in cards_container.winfo_children():
        widget.destroy()
    location_title_label.config(text="")

    wmo_details = {
        0: ("Clear sky", "☀️"),
        1: ("Mainly clear", "🌤️"), 2: ("Partly cloudy", "⛅"), 3: ("Overcast", "☁️"),
        45: ("Fog", "🌫️"), 48: ("Depositing rime fog", "🌫️"),
        51: ("Light drizzle", "🌦️"), 53: ("Moderate drizzle", "🌦️"), 55: ("Dense drizzle", "🌦️"),
        56: ("Light freezing drizzle", "🌨️"), 57: ("Dense freezing drizzle", "🌨️"),
        61: ("Slight rain", "🌧️"), 63: ("Moderate rain", "🌧️"), 65: ("Heavy rain", "🌧️"),
        66: ("Light freezing rain", "🌨️"), 67: ("Heavy freezing rain", "🌨️"),
        71: ("Slight snow fall", "❄️"), 73: ("Moderate snow fall", "❄️"), 75: ("Heavy snow fall", "❄️"),
        77: ("Snow grains", "❄️"),
        80: ("Slight rain showers", "🌦️"), 81: ("Moderate rain showers", "🌦️"), 82: ("Violent rain showers", "🌧️"),
        85: ("Slight snow showers", "❄️"), 86: ("Heavy snow showers", "❄️"),
        95: ("Thunderstorm", "⚡"), 96: ("Thunderstorm with slight hail", "⛈️"), 99: ("Thunderstorm with heavy hail", "⛈️")
    }

    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1"
        geo_response = requests.get(geo_url, timeout=10)
        geo_data = geo_response.json()

        if "results" not in geo_data or not geo_data["results"]:
            messagebox.showerror("Error", "City not found")
            return

        place = geo_data["results"][0]
        latitude = place["latitude"]
        longitude = place["longitude"]
        city_found = place["name"]
        country = place.get("country", "")
        
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}&longitude={longitude}"
            "&daily=temperature_2m_max,temperature_2m_min,weather_code,wind_speed_10m_max,sunrise,sunset,relative_humidity_2m_max"
            "&forecast_days=3"
            "&timezone=auto"
        )

        weather_response = requests.get(weather_url, timeout=10)
        weather_data = weather_response.json()

        dates = weather_data["daily"]["time"]
        max_temps = weather_data["daily"]["temperature_2m_max"]
        min_temps = weather_data["daily"]["temperature_2m_min"]     
        current_code = weather_data["daily"]["weather_code"]
        wind_speeds = weather_data["daily"]["wind_speed_10m_max"]
        sunrises = weather_data["daily"]["sunrise"]
        sunsets = weather_data["daily"]["sunset"]
        humidities = weather_data["daily"]["relative_humidity_2m_max"]

        location_title_label.config(text=f"📍 {city_found}, {country}")

        resolved_text, _ = wmo_details.get(current_code[0], ("Unknown", "❓"))
        save_search_to_log(city_found, country, max_temps[0], min_temps[0], resolved_text, wind_speeds[0], sunrises[0], sunsets[0], humidities[0])

        cards_container.columnconfigure((0, 1, 2), weight=1)

        for i in range(len(dates)):
            card = tk.Frame(cards_container, bd=1, relief="solid")
            card.grid(row=0, column=i, padx=8, pady=5, sticky="nsew")

            try:
                date_obj = datetime.strptime(dates[i], "%Y-%m-%d")
                formatted_date = date_obj.strftime("%a, %b %d")
            except Exception:
                formatted_date = dates[i]

            date_lbl = tk.Label(card, text=formatted_date, font=("Arial", 11, "bold"))
            date_lbl.pack(pady=(12, 8))

            divider = tk.Frame(card, height=1, bg="#CCCCCC") 
            divider.pack(fill="x", padx=15, pady=5)

            condition_text, condition_icon = wmo_details.get(current_code[i], ("Unknown", "❓"))

            weather = tk.Label(card, text=f"{condition_icon} {condition_text}", font=("Arial", 11), fg="#3498DB", wraplength=130)
            weather.pack(pady=6)

            max_lbl = tk.Label(card, text=f"🔺 Max: {max_temps[i]}°C", font=("Arial", 11), fg="#E74C3C")
            max_lbl.pack(pady=6)

            min_lbl = tk.Label(card, text=f"🔻 Min: {min_temps[i]}°C", font=("Arial", 11), fg="#3498DB")
            min_lbl.pack(pady=6)

            humidity_lbl = tk.Label(card, text=f"💧 Humidity: {humidities[i]}%", font=("Arial", 10), fg="#008080")
            humidity_lbl.pack(pady=6)

            wind_lbl = tk.Label(card, text=f"💨 Wind: {wind_speeds[i]} km/h", font=("Arial", 10), fg="#2E8B57")
            wind_lbl.pack(pady=6)

            clean_sunrise = sunrises[i].split("T")[-1] if "T" in sunrises[i] else sunrises[i]
            clean_sunset = sunsets[i].split("T")[-1] if "T" in sunsets[i] else sunsets[i]

            sunrise_lbl = tk.Label(card, text=f"🌅 Sunrise: {clean_sunrise}", font=("Arial", 10), fg="#F39C12")
            sunrise_lbl.pack(pady=6)

            sunset_lbl = tk.Label(card, text=f"🌇 Sunset: {clean_sunset}", font=("Arial", 10), fg="#8E44AD")
            sunset_lbl.pack(pady=6)

    except Exception as e:
        messagebox.showerror("Error", str(e))

app = tk.Tk()
app.title("Modern Weather Forecast")
app.geometry("780x580") 

try:
    app_icon = tk.PhotoImage(file='logo.png')
    app.iconphoto(False, app_icon)
except Exception:
    pass

app.columnconfigure(0, weight=1)

search_frame = tk.Frame(app)
search_frame.grid(row=0, column=0, padx=20, pady=(25, 10), sticky="ew")
search_frame.columnconfigure(1, weight=1)

title_lbl = tk.Label(search_frame, text="City Name:", font=("Arial", 11, "bold"))
title_lbl.grid(row=0, column=0, padx=(0, 10), sticky="w")

city_input = tk.Entry(search_frame, font=("Arial", 12), bd=1, relief="groove")
city_input.grid(row=0, column=1, padx=(0, 10), ipady=4, sticky="ew")
city_input.focus_set()

search_btn = tk.Button(
    search_frame, 
    text="Search Forecast", 
    command=search_weather, 
    font=("Arial", 10, "bold"),
    bd=1, 
    padx=12, 
    pady=4
)
search_btn.grid(row=0, column=2, padx=(0, 5), sticky="w")

history_btn = tk.Button(
    search_frame, 
    text="View History Log", 
    command=open_history_view, 
    font=("Arial", 10),
    bd=1, 
    padx=12, 
    pady=4
)
history_btn.grid(row=0, column=3, sticky="w")

location_title_label = tk.Label(app, text="", font=("Arial", 14, "bold"))
location_title_label.grid(row=1, column=0, pady=(15, 5), sticky="n")

cards_container = tk.Frame(app)
cards_container.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

app.rowconfigure(2, weight=1)

app.mainloop()