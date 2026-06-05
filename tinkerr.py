import tkinter as tk
import request_example

root = tk.Tk()
root.title("Weather App")
root.geometry("300x150")

label = tk.Label(root, text="Enter City to search: ", pady=10)
label.pack()

city_input = tk.Entry(root, font=("Arial", 14), width=20)
city_input.pack(pady=10)






def SecondaryWindow(weather_data, cityy):
    sec = tk.Toplevel()
    sec.title("Weather Details")
    sec.geometry("300x150")
    header_label = tk.Label(sec, text=f"{cityy}", font=("Arial", 16, "bold"))
    header_label.pack(pady=15)
    temp_label = tk.Label(sec, text=f"Temperature: {weather_data['temperature_2m']}°C", font=("Arial", 13))
    temp_label.pack(pady=5)
    wind_label = tk.Label(sec, text=f"Wind: {weather_data['wind_speed_10m']} km/h ({weather_data['wind_direction_10m']}°)", font=("Arial", 13))
    wind_label.pack(pady=5)
    close_btn = tk.Button(sec, text="Close", command=sec.destroy)
    close_btn.pack(pady=15)


def on_click():
    user_text = city_input.get().strip()
    label.config(text="Fetching details...")
    weather_data, cityy = request_example.weatherout(user_text)
    SecondaryWindow(weather_data, cityy)

button = tk.Button(root, text="Search", command=on_click)
button.pack(pady=10)
root.mainloop()