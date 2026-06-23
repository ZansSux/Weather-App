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

# Global structure to hold full 3-day API payload metrics
cached_3day_metrics = []

def open_metrics_view():
    if not cached_3day_metrics:
        messagebox.showinfo("Info", "Please search for a city first to view detailed parameters.")
        return
        
    metrics_window = tk.Toplevel(app)
    metrics_window.title("3-Day Detailed Parameters")
    metrics_window.geometry("580x550")
    metrics_window.configure(bg="#FFFFFF")
    
    title_lbl = tk.Label(metrics_window, text="Comprehensive Forecast Overview".upper(), font=("Helvetica", 10, "bold"), bg="#FFFFFF", fg="#999999")
    title_lbl.pack(pady=(20, 15))
    
    main_frame = tk.Frame(metrics_window, bg="#FFFFFF")
    main_frame.pack(fill="both", expand=True, padx=20)

    for day_data in cached_3day_metrics:
        day_block = tk.LabelFrame(
            main_frame, 
            text=f"  {day_data['day_title']} — {day_data['emoji']} {day_data['condition']}  ", 
            font=("Helvetica", 11, "bold"), 
            bg="#FFFFFF", 
            fg="#111111",
            bd=1,
            relief="solid"
        )
        day_block.pack(fill="x", pady=10, ipady=10)
        
        inner_grid = tk.Frame(day_block, bg="#FFFFFF")
        inner_grid.pack(fill="x", padx=15, pady=5)
        
        # Configure columns weights so they distribute space evenly instead of breaking text lengths
        inner_grid.columnconfigure(0, weight=1)
        inner_grid.columnconfigure(1, weight=1)
        inner_grid.columnconfigure(2, weight=1)
        inner_grid.columnconfigure(3, weight=1)
        
        metrics_list = [
            ("Temp Range:", f"{day_data['max_t']}°C / {day_data['min_t']}°C", "Humidity:", f"{day_data['humidity']}%"),
            ("Wind Speed:", f"{day_data['wind']} km/h", "Sunrise:", day_data['sunrise']),
            ("Sunset:", day_data['sunset'], "", "")
        ]
        
        for r_idx, (k1, v1, k2, v2) in enumerate(metrics_list):
            # Left key-value pair
            tk.Label(inner_grid, text=k1, font=("Helvetica", 10), bg="#FFFFFF", fg="#666666", anchor="w").grid(row=r_idx, column=0, sticky="w", pady=4, padx=(0,5))
            tk.Label(inner_grid, text=v1, font=("Helvetica", 10, "bold"), bg="#FFFFFF", fg="#111111", anchor="w").grid(row=r_idx, column=1, sticky="w", pady=4, padx=(0,15))
            
            # Right key-value pair
            if k2:
                tk.Label(inner_grid, text=k2, font=("Helvetica", 10), bg="#FFFFFF", fg="#666666", anchor="w").grid(row=r_idx, column=2, sticky="w", pady=4, padx=(0,5))
                tk.Label(inner_grid, text=v2, font=("Helvetica", 10, "bold"), bg="#FFFFFF", fg="#111111", anchor="w").grid(row=r_idx, column=3, sticky="w", pady=4)

def open_history_view():
    history_window = tk.Toplevel(app)
    history_window.title("Historical Search Records")
    history_window.geometry("920x380")
    history_window.configure(bg="#FFFFFF")
    
    header_lbl = tk.Label(history_window, text="Local Search History", font=("Helvetica", 12, "bold"), bg="#FFFFFF", fg="#111111")
    header_lbl.pack(pady=15)

    table_container = tk.Frame(history_window, bg="#FFFFFF")
    table_container.pack(fill="both", expand=True, padx=20, pady=5)

    cols = ("id", "city", "country", "max", "min", "condition", "humidity", "wind_speed", "sunrise", "sunset", "time")
    data_table = ttk.Treeview(table_container, columns=cols, show="headings", height=10)
    
    for item in cols:
        data_table.heading(item, text=item.replace("_", " ").title())

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

    exit_btn = tk.Button(history_window, text="Dismiss Log", command=history_window.destroy, font=("Helvetica", 10), bg="#FFFFFF", fg="#111111", relief="flat", activebackground="#F5F5F5")
    exit_btn.pack(pady=15)

def search_weather():
    global cached_3day_metrics
    city_name = city_input.get().strip()

    if not city_name:
        messagebox.showerror("Error", "Please enter a city name")
        return

    location_title_label.config(text="")
    temp_display_label.config(text="")
    condition_clickable_label.config(text="")
    emoji_display_label.config(text="")
    more_details_btn.pack_forget()
    
    for widget in forecast_container.winfo_children():
        widget.destroy()

    wmo_codes = {
        0: ("Clear Sky", "☀️"), 1: ("Mainly Clear", "🌤️"), 2: ("Partly Cloudy", "⛅"), 3: ("Overcast", "☁️"),
        45: ("Fog", "🌫️"), 48: ("Rime Fog", "🌫️"), 51: ("Light Drizzle", "🌦️"), 53: ("Moderate Drizzle", "🌦️"),
        55: ("Dense Drizzle", "🌧️"), 61: ("Slight Rain", "🌧️"), 63: ("Moderate Rain", "🌧️"), 65: ("Heavy Rain", "🌧️"),
        71: ("Slight Snow", "❄️"), 73: ("Moderate Snow", "❄️"), 75: ("Heavy Snow", "❄️"),
        80: ("Slight Rain Showers", "🌦️"), 81: ("Moderate Rain Showers", "🌧️"), 95: ("Thunderstorm", "⛈️")
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
            "&current=temperature_2m,weather_code"
            "&daily=temperature_2m_max,temperature_2m_min,weather_code,wind_speed_10m_max,sunrise,sunset,relative_humidity_2m_max"
            "&forecast_days=3"
            "&timezone=auto"
        )

        weather_response = requests.get(weather_url, timeout=10)
        weather_data = weather_response.json()

        current_temp = weather_data["current"]["temperature_2m"]
        current_wmo = weather_data["current"]["weather_code"]
        
        dates = weather_data["daily"]["time"]
        max_temps = weather_data["daily"]["temperature_2m_max"]
        min_temps = weather_data["daily"]["temperature_2m_min"]     
        current_codes = weather_data["daily"]["weather_code"]
        wind_speeds = weather_data["daily"]["wind_speed_10m_max"]
        sunrises = weather_data["daily"]["sunrise"]
        sunsets = weather_data["daily"]["sunset"]
        humidities = weather_data["daily"]["relative_humidity_2m_max"]

        resolved_condition, condition_emoji = wmo_codes.get(current_wmo, ("Unknown", "❓"))
        
        location_title_label.config(text=f"{city_found}, {country}".upper())
        emoji_display_label.config(text=condition_emoji)
        temp_display_label.config(text=f"{round(current_temp)}°")
        condition_clickable_label.config(text=f"{resolved_condition}\nClick to View History")
        
        cached_3day_metrics = []
        for idx in range(len(dates)):
            try:
                date_obj = datetime.strptime(dates[idx], "%Y-%m-%d")
                day_name = "TODAY" if idx == 0 else date_obj.strftime("%A").upper()
            except Exception:
                day_name = f"DAY {idx+1}"

            try:
                clean_srise = sunrises[idx].split("T")[-1] if "T" in sunrises[idx] else sunrises[idx]
                clean_sset = sunsets[idx].split("T")[-1] if "T" in sunsets[idx] else sunsets[idx]
            except Exception:
                clean_srise = "--:--"
                clean_sset = "--:--"

            f_code = current_codes[idx] if idx < len(current_codes) else -1
            f_cond, f_emoji = wmo_codes.get(f_code, ("Unknown", "❓"))

            cached_3day_metrics.append({
                "day_title": day_name,
                "emoji": f_emoji,
                "condition": f_cond,
                "max_t": round(max_temps[idx]) if idx < len(max_temps) else "--",
                "min_t": round(min_temps[idx]) if idx < len(min_temps) else "--",
                "humidity": humidities[idx] if idx < len(humidities) else "--",
                "wind": wind_speeds[idx] if idx < len(wind_speeds) else "--",
                "sunrise": clean_srise,
                "sunset": clean_sset
            })

        more_details_btn.pack(pady=(5, 20))

        save_search_to_log(
            city_found, country, max_temps[0], min_temps[0], resolved_condition, 
            wind_speeds[0], cached_3day_metrics[0]["sunrise"], cached_3day_metrics[0]["sunset"], humidities[0]
        )

        for i in range(len(dates)):
            column_frame = tk.Frame(forecast_container, bg="#FFFFFF")
            column_frame.pack(side="left", fill="both", expand=True, padx=15)

            try:
                date_obj = datetime.strptime(dates[i], "%Y-%m-%d")
                formatted_date = date_obj.strftime("%a").upper()
            except Exception:
                formatted_date = dates[i]

            day_lbl = tk.Label(column_frame, text=formatted_date, font=("Helvetica", 10, "bold"), bg="#FFFFFF", fg="#999999")
            day_lbl.pack(pady=(0, 4))

            cond_text, sub_emoji = wmo_codes.get(current_codes[i], ("Unknown", "❓"))
            cond_lbl = tk.Label(column_frame, text=f"{sub_emoji}\n{cond_text}", font=("Helvetica", 10), bg="#FFFFFF", fg="#666666", justify="center")
            cond_lbl.pack(pady=2)

            range_text = f"{round(max_temps[i])}° / {round(min_temps[i])}°"
            range_lbl = tk.Label(column_frame, text=range_text, font=("Helvetica", 11, "bold"), bg="#FFFFFF", fg="#111111")
            range_lbl.pack(pady=(4, 0))

    except Exception as e:
        messagebox.showerror("Error", str(e))

app = tk.Tk()
app.title("Weather")
app.geometry("480x690") 
app.configure(bg="#FFFFFF")

try:
    app_icon = tk.PhotoImage(file='logo.png')
    app.iconphoto(False, app_icon)
except Exception:
    pass

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background="#FFFFFF", fieldbackground="#FFFFFF", foreground="#111111", font=("Helvetica", 10))
style.configure("Treeview.Heading", background="#F5F5F5", foreground="#111111", font=("Helvetica", 10, "bold"), relief="flat")

search_frame = tk.Frame(app, bg="#FFFFFF")
search_frame.pack(pady=(35, 20))

city_input = tk.Entry(search_frame, width=22, font=("Helvetica", 14), bd=0, bg="#F2F2F7", fg="#111111", justify="center", insertbackground="#111111")
city_input.pack(side="left", padx=5, ipady=8)
city_input.focus_set()

search_btn = tk.Button(
    search_frame, 
    text="Search", 
    command=search_weather, 
    font=("Helvetica", 11, "bold"),
    bg="#111111", 
    fg="#FFFFFF",
    activebackground="#222222",
    activeforeground="#FFFFFF",
    bd=0, 
    padx=20, 
    pady=8,
    cursor="hand2"
)
search_btn.pack(side="left", padx=5)

display_container = tk.Frame(app, bg="#FFFFFF")
display_container.pack(fill="x", padx=30)

location_title_label = tk.Label(display_container, text="", font=("Helvetica", 11, "bold"), bg="#FFFFFF", fg="#999999")
location_title_label.pack(pady=(10, 0))

emoji_display_label = tk.Label(display_container, text="", font=("Segoe UI Emoji", 48), bg="#FFFFFF", fg="#111111")
emoji_display_label.pack(pady=(5, 0))

temp_display_label = tk.Label(display_container, text="", font=("Helvetica Light", 64), bg="#FFFFFF", fg="#111111")
temp_display_label.pack(pady=(0, 2))

condition_clickable_label = tk.Label(
    display_container, 
    text="", 
    font=("Helvetica", 11), 
    bg="#FFFFFF", 
    fg="#8E8E93", 
    cursor="hand2",
    justify="center"
)
condition_clickable_label.pack(pady=(0, 10))
condition_clickable_label.bind("<Button-1>", lambda e: open_history_view())

more_details_btn = tk.Button(
    display_container,
    text="More Details →",
    command=open_metrics_view,
    font=("Helvetica", 11, "bold"),
    bg="#FFFFFF",
    fg="#007AFF",
    activebackground="#FFFFFF",
    activeforeground="#0051A3",
    bd=0,
    cursor="hand2"
)

divider_line = tk.Frame(app, height=1, bg="#E5E5EA")
divider_line.pack(fill="x", padx=40, pady=(0, 25))

forecast_container = tk.Frame(app, bg="#FFFFFF")
forecast_container.pack(fill="x", padx=20)

app.mainloop()