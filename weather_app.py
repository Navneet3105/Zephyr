import tkinter as tk
from tkinter import messagebox, Listbox
import requests
from weather_api import get_weather_data, get_weather_icon_url

# ------------------------------------------------------------
# PRELOADED CITY LIST FOR SEARCH SUGGESTIONS
# ------------------------------------------------------------
CITY_LIST = [
    "Delhi", "Mumbai", "Chennai", "Kolkata", "Hyderabad", "Bengaluru",
    "Pune", "Ahmedabad", "Surat", "Jaipur", "Lucknow", "Kanpur", "Nagpur",
    "Visakhapatnam", "Bhopal", "Patna", "Vadodara", "Ghaziabad", "Agra",
    "Noida", "Gurgaon", "New York", "Los Angeles", "London", "Paris",
    "Tokyo", "Singapore", "Sydney", "Toronto", "Berlin", "Dubai",
    "Hong Kong", "Bangkok", "Seoul"
]

# ------------------------------------------------------------
# COLOR UTILITIES
# ------------------------------------------------------------
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb

def fade_color(start_hex, end_hex, steps=30):
    start = hex_to_rgb(start_hex)
    end = hex_to_rgb(end_hex)
    for i in range(steps + 1):
        ratio = i / steps
        r = int(start[0] + (end[0] - start[0]) * ratio)
        g = int(start[1] + (end[1] - start[1]) * ratio)
        b = int(start[2] + (end[2] - start[2]) * ratio)
        yield rgb_to_hex((r, g, b))

# ------------------------------------------------------------
# MAP ICON CODE TO SOLID BACKGROUND COLOR
# ------------------------------------------------------------
def get_bg_color(icon_code):
    day = icon_code.endswith("d")
    mapping = {
        "01": ("#FFD54F", "#0A1A2F"),
        "02": ("#AEDFF7", "#1C3B57"),
        "03": ("#90A4AE", "#37474F"),
        "04": ("#78909C", "#263238"),
        "09": ("#4A76A8", "#1B2A41"),
        "10": ("#3F51B5", "#1A237E"),
        "11": ("#3E3E3E", "#1B1B1B"),
        "13": ("#E1F5FE", "#90CAF9"),
        "50": ("#B0BEC5", "#455A64"),
    }
    prefix = icon_code[:2]
    if prefix in mapping:
        return mapping[prefix][0] if day else mapping[prefix][1]
    return "#1E3A5F"

# ------------------------------------------------------------
# WEATHER APP
# ------------------------------------------------------------
class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Zephyr")
        self.root.attributes('-fullscreen', True)
        self.default_bg = "#1E3A5F"
        self.root.configure(bg=self.default_bg)
        self.current_bg = self.default_bg

        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))

        # ------------------------------------------------------------
        # Search Entry
        # ------------------------------------------------------------
        self.city_entry = tk.Entry(
            root, font=("Arial", 20), bg="#D0E6FF",
            fg="#003366", justify="center"
        )
        self.city_entry.pack(pady=40, padx=40, fill="x")
        self.city_entry.bind("<KeyRelease>", self.show_suggestions)
        self.city_entry.bind("<Down>", self.focus_suggestion_list)

        # ------------------------------------------------------------
        # Suggestions Listbox
        # ------------------------------------------------------------
        self.suggestion_box = Listbox(
            root, font=("Arial", 16),
            bg=self.current_bg, fg="white",
            highlightthickness=0, bd=0,
            selectbackground="#3399FF",
            selectforeground="white"
        )
        self.suggestion_box.bind("<<ListboxSelect>>", self.fill_from_suggestions)
        self.suggestion_box.bind("<Return>", self.fill_from_suggestions)
        self.suggestion_box.place(x=0, y=0)
        self.suggestion_box.lower()

        # Search button
        self.search_button = tk.Button(
            root, text="Search", command=self.search_weather,
            bg="#3399FF", fg="white", font=("Arial", 16, "bold"), relief="flat"
        )
        self.search_button.pack(pady=10)

        # Logo
        try:
            self.logo_image = tk.PhotoImage(file="logo.png")
            self.logo_label = tk.Label(root, image=self.logo_image, bg=self.default_bg)
            self.logo_label.pack(pady=20)
        except:
            self.logo_label = tk.Label(root, text="Logo Missing", fg="white", bg=self.default_bg)
            self.logo_label.pack(pady=20)

        # Weather frame
        self.weather_frame = tk.Frame(root, bg=self.default_bg)
        self.weather_frame.pack(pady=20)
        self.icon_label = tk.Label(self.weather_frame, bg=self.default_bg)
        self.icon_label.pack()
        self.info_label = tk.Label(
            self.weather_frame, font=("Arial", 18), justify="center",
            bg=self.default_bg, fg="white"
        )
        self.info_label.pack()

    # ------------------------------------------------------------
    # Suggestion system
    # ------------------------------------------------------------
    def show_suggestions(self, event=None):
        text = self.city_entry.get().strip().lower()
        if not text:
            self.suggestion_box.lower()
            return

        matches = [city for city in CITY_LIST if text in city.lower()]
        if not matches:
            self.suggestion_box.lower()
            return

        # position listbox below entry
        x = self.city_entry.winfo_x()
        y = self.city_entry.winfo_y() + self.city_entry.winfo_height()
        self.suggestion_box.place(x=x, y=y, width=self.city_entry.winfo_width())
        self.suggestion_box.lift()

        self.suggestion_box.delete(0, tk.END)
        for m in matches:
            self.suggestion_box.insert(tk.END, m)

        # update suggestion box color to match current background
        self.suggestion_box.configure(bg=self.current_bg)

    def fill_from_suggestions(self, event=None):
        try:
            selection = self.suggestion_box.get(tk.ACTIVE)
        except:
            return
        self.city_entry.delete(0, tk.END)
        self.city_entry.insert(0, selection)
        self.suggestion_box.lower()
        self.search_weather()

    def focus_suggestion_list(self, event=None):
        self.suggestion_box.focus_set()
        self.suggestion_box.selection_set(0)

    # ------------------------------------------------------------
    # Background fade
    # ------------------------------------------------------------
    def apply_background(self, new_color):
        old_color = self.current_bg
        colors = list(fade_color(old_color, new_color, steps=30))
        self.current_bg = new_color

        def step(i=0):
            if i < len(colors):
                color = colors[i]
                self.root.configure(bg=color)
                self.weather_frame.configure(bg=color)
                self.icon_label.configure(bg=color)
                self.info_label.configure(bg=color)
                self.suggestion_box.configure(bg=color)
                try:
                    self.logo_label.configure(bg=color)
                except:
                    pass
                self.root.after(15, lambda: step(i + 1))

        step()

    # ------------------------------------------------------------
    # Search weather
    # ------------------------------------------------------------
    def search_weather(self):
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name.")
            return

        self.suggestion_box.lower()
        if self.logo_label.winfo_exists():
            self.logo_label.pack_forget()

        data = get_weather_data(city)
        if data:
            weather = data["weather"][0]["description"].title()
            temp = data["main"]["temp"]
            icon_code = data["weather"][0]["icon"]
            icon_url = get_weather_icon_url(icon_code)

            new_color = get_bg_color(icon_code)
            self.apply_background(new_color)
            self.display_weather(weather, temp, icon_url, city)
        else:
            messagebox.showerror("Error", "City not found or API error.")

    # ------------------------------------------------------------
    # Display weather
    # ------------------------------------------------------------
    def display_weather(self, weather, temp, icon_url, city):
        try:
            icon_response = requests.get(icon_url, stream=True)
            icon_data = icon_response.content
            with open("temp_icon.png", "wb") as f:
                f.write(icon_data)

            img = tk.PhotoImage(file="temp_icon.png")
            self.weather_icon = img.zoom(4, 4)
            self.icon_label.config(image=self.weather_icon)
            self.icon_label.image = self.weather_icon
            self.info_label.config(
                text=f"{city}\n{weather}\nTemperature: {temp}°C"
            )

        except Exception as e:
            messagebox.showerror("Image Error", f"Could not load weather icon.\n{e}")

# ------------------------------------------------------------
# RUN APP
# ------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
