import tkinter as tk
from tkinter import ttk
import requests
from PIL import Image, ImageTk
from io import BytesIO

API_KEY = "51ccfee7da29ca63a135782b2fe57e66"

CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


class WeatherApp:

    def __init__(self, root):

        self.root = root
        self.root.title("Advanced Weather Application")
        self.root.geometry("900x700")

        self.unit = "metric"

        title = tk.Label(root,
                         text="Advanced Weather App",
                         font=("Arial",20,"bold"))
        title.pack(pady=10)

        top = tk.Frame(root)
        top.pack()

        self.city_entry = tk.Entry(top,width=30,font=("Arial",12))
        self.city_entry.pack(side=tk.LEFT,padx=5)

        tk.Button(top,
                  text="Get Weather",
                  command=self.get_weather).pack(side=tk.LEFT)

        tk.Button(top,
                  text="Use My Location",
                  command=self.detect_location).pack(side=tk.LEFT,padx=5)

        self.toggle_btn = tk.Button(
            top,
            text="Switch to °F",
            command=self.toggle_units
        )
        self.toggle_btn.pack(side=tk.LEFT)

        self.error_label = tk.Label(root,
                                    fg="red",
                                    font=("Arial",11))
        self.error_label.pack()

        self.result = tk.Label(root,
                               font=("Arial",12),
                               justify=tk.LEFT)
        self.result.pack()

        self.icon_label = tk.Label(root)
        self.icon_label.pack()

        tk.Label(root,
                 text="Next 6 Hours",
                 font=("Arial",14,"bold")).pack()

        self.hour_frame = tk.Frame(root)
        self.hour_frame.pack()

        tk.Label(root,
                 text="Next 5 Days",
                 font=("Arial",14,"bold")).pack()

        self.day_frame = tk.Frame(root)
        self.day_frame.pack()

    def toggle_units(self):
        if self.unit == "metric":
            self.unit = "imperial"
            self.toggle_btn.config(text="Switch to °C")
        else:
            self.unit = "metric"
            self.toggle_btn.config(text="Switch to °F")
        if self.city_entry.get().strip():
            self.get_weather()

    def detect_location(self):

        try:
            r=requests.get("https://ipinfo.io/json",timeout=5)

            city=r.json()["city"]

            self.city_entry.delete(0,tk.END)
            self.city_entry.insert(0,city)

            self.get_weather()

        except:
            self.error_label.config(text="Could not detect location.")

    def get_weather(self):

        city=self.city_entry.get().strip()

        if city=="":
            self.error_label.config(text="Please enter a city.")
            return

        self.error_label.config(text="")

        params={
            "q":city,
            "appid":API_KEY,
            "units":self.unit
        }

        try:

            weather=requests.get(CURRENT_URL,
                                 params=params,
                                 timeout=10)

            if weather.status_code==401:
                self.error_label.config(text="Invalid API Key.")
                return

            if weather.status_code==404:
                self.error_label.config(text="City not found.")
                return

            weather=weather.json()

            temp=weather["main"]["temp"]

            humidity=weather["main"]["humidity"]

            wind=weather["wind"]["speed"]

            desc=weather["weather"][0]["description"].title()

            icon=weather["weather"][0]["icon"]

            if self.unit=="metric":
                c=temp
                f=(temp*9/5)+32
            else:
                f=temp
                c=(temp-32)*5/9

            text=f"""
City : {city}

Temperature :
{c:.1f} °C
{f:.1f} °F

Humidity : {humidity} %

Wind Speed : {wind}

Condition : {desc}
"""

            self.result.config(text=text)

            self.load_icon(icon)

            self.load_forecast(city)

        except requests.exceptions.Timeout:
            self.error_label.config(text="Network Timeout")

        except requests.exceptions.ConnectionError:
            self.error_label.config(text="No Internet Connection")

        except Exception as e:
            self.error_label.config(text=str(e))

    def load_icon(self,icon):

        url=f"https://openweathermap.org/img/wn/{icon}@2x.png"

        img=requests.get(url)

        image=Image.open(BytesIO(img.content))

        photo=ImageTk.PhotoImage(image)

        self.icon_label.config(image=photo)

        self.icon_label.image=photo

    def load_forecast(self,city):

        for widget in self.hour_frame.winfo_children():
            widget.destroy()

        for widget in self.day_frame.winfo_children():
            widget.destroy()
        params={"q":city,"appid":API_KEY,"units":self.unit}
        response = requests.get(FORECAST_URL,params=params,timeout=10)
        if response.status_code != 200:
            self.error_label.config(text="Forecast unavailable.")
            return
        forecast = response.json()["list"]
        tk.Label(self.hour_frame,text="Time        Temp").pack(anchor="w")

        for item in forecast[:6]:

            time=item["dt_txt"][11:16]

            temp=item["main"]["temp"]

            label=f"{time}      {temp}°"

            tk.Label(self.hour_frame,
                     text=label).pack(anchor="w")

        days=[]

        used=set()

        for item in forecast:

            day=item["dt_txt"][:10]

            if day not in used:

                used.add(day)

                days.append(item)

            if len(days)==5:
                break

        for d in days:

            date=d["dt_txt"][:10]

            temp=d["main"]["temp"]

            desc=d["weather"][0]["description"]

            text=f"{date}   {temp}°   {desc}"

            tk.Label(self.day_frame,
                     text=text).pack(anchor="w")


root=tk.Tk()

app=WeatherApp(root)

root.mainloop()
