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
            wind_speed REAL,
            sunrise TEXT,
            sunset TEXT,
            timestamp TEXT
                      
        )
    """)
    connection.commit()
    connection.close()

def save_search_to_log(city, country, max_t, min_t, condition, wind_speed, sunrise, sunset):
    connection = sqlite3.connect("weather_history.db")
    db_cursor = connection.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db_cursor.execute("""
        INSERT INTO search_log (city, country, max_temp, min_temp, weather_condition, wind_speed, sunrise, sunset, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (city, country, max_t, min_t, condition, wind_speed, sunrise, sunset, current_time))
    connection.commit()
    connection.close()

init_database()

def open_history_view():
    history_window = tk.Toplevel(app)
    history_window.title("Historical Search Records")
    history_window.geometry("680x360")
    
    header_lbl = tk.Label(history_window, text="Local Search History", font=("Arial", 12, "bold"))
    header_lbl.pack(pady=10)

    table_container = tk.Frame(history_window)
    table_container.pack(fill="both", expand=True, padx=15, pady=5)

    cols = ("id", "city", "country", "max", "min", "condition", "wind_speed", "sunrise", "sunset", "time")
    data_table = ttk.Treeview(table_container, columns=cols, show="headings", height=10)
    
    data_table.heading("id", text="ID")
    data_table.heading("city", text="City")
    data_table.heading("country", text="Country")
    data_table.heading("max", text="Max Temp")
    data_table.heading("min", text="Min Temp")
    data_table.heading("condition", text="Condition")
    data_table.heading("time", text="Date & Time")
    data_table.heading("wind_speed", text="Wind Speed")
    data_table.heading("sunrise", text="Sunrise")
    data_table.heading("sunset", text="Sunset")

    data_table.column("id", width=45, anchor="center")
    data_table.column("city", width=110, anchor="w")
    data_table.column("country", width=80, anchor="center")
    data_table.column("max", width=85, anchor="center")
    data_table.column("min", width=85, anchor="center")
    data_table.column("condition", width=125, anchor="w")
    data_table.column("time", width=140, anchor="center")
    data_table.column("wind_speed", width=100, anchor="center")
    data_table.column("sunrise", width=120, anchor="center")
    data_table.column("sunset", width=120, anchor="center")

    v_scroll = ttk.Scrollbar(table_container, orient="vertical", command=data_table.yview)
    data_table.configure(yscrollcommand=v_scroll.set)
    
    data_table.pack(side="left", fill="both", expand=True)
    v_scroll.pack(side="right", fill="y")

    try:
        connection = sqlite3.connect("weather_history.db")
        db_cursor = connection.cursor()
        db_cursor.execute("SELECT id, city, country, max_temp, min_temp, weather_condition, wind_speed, sunrise, sunset, timestamp FROM search_log ORDER BY id DESC")
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

    wmo_codes = {
        0: "Clear sky",
        1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast (Cloudy)",
        45: "Fog", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        56: "Light freezing drizzle", 57: "Dense freezing drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain (Rainy)",
        66: "Light freezing rain", 67: "Heavy freezing rain",
        71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        85: "Slight snow showers", 86: "Heavy snow showers",
        95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
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
            "&daily=temperature_2m_max,temperature_2m_min,weather_code,wind_speed_10m_max,sunrise,sunset"
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

        location_title_label.config(text=f"📍 {city_found}, {country}")

        current_resolved_condition = wmo_codes.get(current_code[0], "Unknown")
        save_search_to_log(city_found, country, max_temps[0], min_temps[0], current_resolved_condition, wind_speeds[0], sunrises[0], sunsets[0])

        for i in range(len(dates)):
            card = tk.Frame(cards_container, bd=1, relief="solid")
            card.pack(side="left", padx=10, fill="both", expand=True)

            date_lbl = tk.Label(card, text=dates[i], font=("Arial", 11, "bold"))
            date_lbl.pack(pady=(12, 8))

            divider = tk.Frame(card, height=1, bg="#CCCCCC") 
            divider.pack(fill="x", padx=15, pady=5)

            weather = tk.Label(card, text=f"🌦️ Current Condition: \n {wmo_codes.get(current_code[i], 'Error')}", font=("Arial", 11), fg="#3498DB")
            weather.pack(pady=6)

            max_lbl = tk.Label(card, text=f"🔺 Max: {max_temps[i]}°C", font=("Arial", 11), fg="#E74C3C")
            max_lbl.pack(pady=6)

            min_lbl = tk.Label(card, text=f"🔻 Min: {min_temps[i]}°C", font=("Arial", 11), fg="#3498DB")
            min_lbl.pack(pady=6)

            wind_lbl = tk.Label(card, text=f"💨 Wind: {wind_speeds[i]} km/h", font=("Arial", 11), fg="#2E8B57")
            wind_lbl.pack(pady=6)

            sunrise_lbl = tk.Label(card, text=f"🌅 Sunrise: {sunrises[i]}", font=("Arial", 11), fg="#F39C12")
            sunrise_lbl.pack(pady=6)

            sunset_lbl = tk.Label(card, text=f"🌇 Sunset: {sunsets[i]}", font=("Arial", 11), fg="#8E44AD")
            sunset_lbl.pack(pady=6)

    except Exception as e:
        messagebox.showerror("Error", str(e))

app = tk.Tk()
app.title("Modern Weather Forecast")
app.geometry("550x500") 

try:
    app_icon = tk.PhotoImage(file='logo.png')
    app.iconphoto(False, app_icon)
except Exception:
    pass

title_lbl = tk.Label(app, text="Enter City Name", font=("Arial", 12, "bold"))
title_lbl.pack(pady=(20, 5))

city_input = tk.Entry(app, width=28, font=("Arial", 13), bd=1, relief="groove", justify="center")
city_input.pack(pady=5, ipady=4) 

button_container_row = tk.Frame(app)
button_container_row.pack(pady=15)

search_btn = tk.Button(
    button_container_row, 
    text="Search Forecast", 
    command=search_weather, 
    font=("Arial", 11, "bold"),
    bd=1, 
    padx=15, 
    pady=6,
)
search_btn.pack(side="left", padx=5)

history_btn = tk.Button(
    button_container_row, 
    text="View History Log", 
    command=open_history_view, 
    font=("Arial", 11),
    bd=1, 
    padx=15, 
    pady=6,
)
history_btn.pack(side="left", padx=5)

location_title_label = tk.Label(app, text="", font=("Arial", 14, "bold"))
location_title_label.pack(pady=(10, 5))

cards_container = tk.Frame(app)
cards_container.pack(fill="x", padx=20, pady=15)

app.mainloop()