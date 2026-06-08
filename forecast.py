import tkinter as tk
from tkinter import messagebox
import requests


def search_weather():
    city_name = city.get().strip()

    if not city_name:
        messagebox.showerror("Error", "Please enter a city name")
        return

    try:
        geo_url = (
            "https://geocoding-api.open-meteo.com/v1/search"
            f"?name={city_name}&count=1"
        )

        geo_response = requests.get(geo_url, timeout=10)
        geo_data = geo_response.json()

        if "results" not in geo_data:
            messagebox.showerror("Error", "City not found")
            return

        place = geo_data["results"][0]

        latitude = place["latitude"]
        longitude = place["longitude"]
        city_found = place["name"]
        country = place.get("country", "")
        weather_url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}"
            f"&longitude={longitude}"
            "&daily=temperature_2m_max,temperature_2m_min"
            "&forecast_days=3"
            "&timezone=auto"
        )

        weather_response = requests.get(weather_url, timeout=10)
        weather_data = weather_response.json()

        dates = weather_data["daily"]["time"]
        max_temps = weather_data["daily"]["temperature_2m_max"]
        min_temps = weather_data["daily"]["temperature_2m_min"]

        result.delete("1.0", tk.END)

        result.insert(
            tk.END,
            f"3-Day Forecast for {city_found}, {country}\n\n"
        )

        for i in range(len(dates)):
            result.insert(
                tk.END,
                f"Date: {dates[i]}\n"
                f"Max Temp: {max_temps[i]}°C\n"
                f"Min Temp: {min_temps[i]}°C\n"
                f"{'-'*30}\n"
            )

    except Exception as e:
        messagebox.showerror("Error", str(e))
app = tk.Tk()
app.title("Weather Forecast")
app.geometry("500x400")

tk.Label(
    app,
    text="Enter City Name",
    font=("Arial", 12)
).pack(pady=10)

city = tk.Entry(
    app,
    width=30,
    font=("Arial", 12)
)
city.pack()

tk.Button(
    app,
    text="Search Forecast",
    command=search_weather
).pack(pady=10)

result = tk.Text(
    app,
    width=55,
    height=15
)
result.pack(pady=10)

app.mainloop()