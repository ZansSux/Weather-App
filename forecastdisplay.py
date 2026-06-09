import tkinter as tk
from tkinter import messagebox
import requests

def search_weather():
    city_name = city_input.get().strip()

    if not city_name:
        messagebox.showerror("Error", "Please enter a city name")
        return

    for widget in cards_container.winfo_children():
        widget.destroy()
    location_title_label.config(text="")

    try:
        # Step 1: Get coordinates from city name
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

        # Step 2: Get 3-day forecast
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}&longitude={longitude}"
            "&daily=temperature_2m_max,temperature_2m_min"
            "&forecast_days=3"
            "&timezone=auto"
        )

        weather_response = requests.get(weather_url, timeout=10)
        weather_data = weather_response.json()

        dates = weather_data["daily"]["time"]
        max_temps = weather_data["daily"]["temperature_2m_max"]
        min_temps = weather_data["daily"]["temperature_2m_min"]

        location_title_label.config(text=f"📍 {city_found}, {country}")


        for i in range(len(dates)):
  
            card = tk.Frame(cards_container, bd=1, relief="solid")
            card.pack(side="left", padx=10, fill="both", expand=True)

            date_lbl = tk.Label(card, text=dates[i], font=("Arial", 11, "bold"))
            date_lbl.pack(pady=(12, 8))

            divider = tk.Frame(card, height=1)
            divider.pack(fill="x", padx=15, pady=5)


            max_lbl = tk.Label(card, text=f"🔺 Max: {max_temps[i]}°C", font=("Arial", 11), fg="#E74C3C")
            max_lbl.pack(pady=6)


            min_lbl = tk.Label(card, text=f"🔻 Min: {min_temps[i]}°C", font=("Arial", 11), fg="#3498DB")
            min_lbl.pack(pady=6)

    except Exception as e:
        messagebox.showerror("Error", str(e))



app = tk.Tk()
app.title("Modern Weather Forecast")
app.geometry("550x450")



title_lbl = tk.Label(app, text="Enter City Name", font=("Arial", 12, "bold"))
title_lbl.pack(pady=(20, 5))


city_input = tk.Entry(app, width=28, font=("Arial", 13), bd=1, relief="groove", justify="center")
city_input.pack(pady=5, ipady=4) 


search_btn = tk.Button(
    app, 
    text="Search Forecast", 
    command=search_weather, 
    font=("Arial", 11, "bold"),
    bd=0, 
    padx=15, 
    pady=6,
)
search_btn.pack(pady=15)

location_title_label = tk.Label(app, text="", font=("Arial", 14, "bold"))
location_title_label.pack(pady=(10, 5))

cards_container = tk.Frame(app)
cards_container.pack(fill="x", padx=20, pady=15)

app.mainloop()