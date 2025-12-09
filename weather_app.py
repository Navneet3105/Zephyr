import tkinter as tk
from tkinter import messagebox
import requests
from weather_api import get_weather_data, get_weather_icon_url

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Zephyr")
        self.root.attributes('-fullscreen', True)  # Fullscreen mode
        self.root.configure(bg="#1E3A5F")

        # Escape key to exit fullscreen
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))

        self.city_entry = tk.Entry(root, font=("Arial", 20), bg="#D0E6FF", fg="#003366", justify="center")
        self.city_entry.pack(pady=40, padx=40, fill="x")

        self.search_button = tk.Button(
            root, text="Search", command=self.search_weather,
            bg="#3399FF", fg="white", font=("Arial", 16, "bold"), relief="flat"
        )
        self.search_button.pack(pady=10)

        # Display logo below search bar
        try:
            self.logo_image = tk.PhotoImage(file="logo.png").subsample(1)  # Load original
            self.logo_image = self.logo_image.zoom(1).subsample(max(self.logo_image.width() // 400, 1))
            self.logo_label = tk.Label(root, image=self.logo_image, bg="#1E3A5F")
            self.logo_label.pack(pady=20)
        except Exception as e:
            self.logo_label = tk.Label(root, text=f"Logo error:\n{e}", fg="white", bg="#1E3A5F")
            self.logo_label.pack(pady=20)

        self.weather_frame = tk.Frame(root, bg="#1E3A5F")
        self.weather_frame.pack(pady=20)

        self.icon_label = tk.Label(self.weather_frame, bg="#1E3A5F")
        self.icon_label.pack()

        self.info_label = tk.Label(
            self.weather_frame, font=("Arial", 18), justify="center",
            bg="#1E3A5F", fg="white"
        )
        self.info_label.pack()

    def search_weather(self):
        city = self.city_entry.get()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name.")
            return

        data = get_weather_data(city)
        if data:
            weather = data["weather"][0]["description"].title()
            temp = data["main"]["temp"]
            icon_code = data["weather"][0]["icon"]
            icon_url = get_weather_icon_url(icon_code)

            self.display_weather(weather, temp, icon_url, city)
        else:
            messagebox.showerror("Error", "City not found or API error.")

    def display_weather(self, weather, temp, icon_url, city):
        try:
            icon_response = requests.get(icon_url, stream=True)
            icon_data = icon_response.content

            with open("temp_icon.png", "wb") as f:
                f.write(icon_data)

            self.weather_icon = tk.PhotoImage(file="temp_icon.png")
            self.icon_label.config(image=self.weather_icon)
            self.icon_label.image = self.weather_icon

            self.info_label.config(
                text=f"{city}\n{weather}\nTemperature: {temp}°C"
            )
        except Exception as e:
            messagebox.showerror("Image Error", f"Could not load weather icon.\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
