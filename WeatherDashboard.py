import streamlit as st
import requests
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

API_KEY = 'ec535cf3bfdd19f702ffed69ed6f7446' 
BASE_URL = 'https://api.openweathermap.org/data/2.5'

@st.cache_data
def load_city_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def get_weather(city_name):
    params = {
        'q': city_name,
        'appid': API_KEY,
        'units': 'metric'
    }
    response = requests.get(f"{BASE_URL}/weather", params=params)
    return response.json()

def get_forecast(city_name):
    params = {
        'q': city_name,
        'appid': API_KEY,
        'units': 'metric'
    }
    response = requests.get(f"{BASE_URL}/forecast", params=params)
    return response.json()

def plot_temperature_graph(times, temps, selected_day):
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2e2e2e') 

    times = [datetime.strptime(time, '%Y-%m-%d %H:%M:%S') for time in times]

    ax.plot(times, temps, marker='o', linestyle='-', color='tab:cyan', label=f"Temperature on {selected_day}")

    ax.set_title(f"Date : {selected_day}",  fontsize=19, color='white', ha='center',pad=20)

    ax.set_xlabel("Time",  fontsize=15, color='white', labelpad=20)
    ax.set_ylabel("Temperature (°C)",  fontsize=15, color='white', labelpad=20)
    ax.tick_params(axis='y', labelcolor='white', colors='white')
    ax.tick_params(axis='x', labelcolor='white')

    ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.5, color='white')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xticks(rotation=45)

    for i, (time, temp) in enumerate(zip(times, temps)):
        ax.annotate(
            f"{temp}°C", 
            (times[i], temps[i]), 
            textcoords="offset points", 
            xytext=(0, 15), 
            ha='center', 
            fontsize=10,
            color='tab:cyan', 
            fontweight='bold', 
            bbox=dict(facecolor='black', edgecolor='none', boxstyle='round,pad=0.3')
        )

    min_temp = min(temps)
    max_temp = max(temps)
    buffer = 3
    ax.set_ylim(min_temp - buffer, max_temp + buffer)
    ax.set_facecolor('#2e2e2e')
    plt.tight_layout()
    st.pyplot(fig)

def main():
    st.title("Weather Dashboard")
    st.write("🌤️ Get real-time weather updates and forecasts!")

    city_data = load_city_data('city.list.json') 
    city_names = [f"{city['name']}, {city['country']}" for city in city_data]

    selected_city = st.selectbox("Search for a city", [""] + city_names)

    if selected_city and selected_city != "":
        city_name = selected_city.split(",")[0] 

        with st.spinner("Fetching weather data..."):
            current_weather = get_weather(city_name)
            forecast_data = get_forecast(city_name)
        
        if current_weather.get("cod") == 200:
            temperature = current_weather['main']['temp']
            temp_min = current_weather['main']['temp_min']
            temp_max = current_weather['main']['temp_max']
            humidity = current_weather['main']['humidity']
            wind_speed = current_weather['wind']['speed']
            description = current_weather['weather'][0]['description'].capitalize()
            icon_code = current_weather['weather'][0]['icon']
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

            st.markdown(f"""
            <div style="border:1px solid #333; border-radius:10px; padding:20px; background-color:#222; width:100%; max-width: 600px; margin:auto;">
                <h2 style="text-align:center; color:white; font-size:24px;">Current Weather in {city_name}</h2>
                <div style="display:flex; align-items:center; justify-content:center;">
                    <img src="{icon_url}" alt="weather icon" width="80" height="80" style="margin-right:20px;">
                    <h3 style="color:#4bbbe; font-size:30px; color:white;">{temperature}°C</h3>
                </div>
                <p style="text-align:center; color:white; font-size:20px;">{description}</p>
                <p style="text-align:center; color:white; font-size:20px;">🌡️ <strong>Min Temp:</strong> {temp_min}°C | <strong>Max Temp:</strong> {temp_max}°C</p>
                <p style="text-align:center; color:white; font-size:20px;">💧 <strong>Humidity:</strong> {humidity}%</p>
                <p style="text-align:center; color:white; font-size:20px;">💨 <strong>Wind Speed:</strong> {wind_speed} m/s</p>
            </div>
            """, unsafe_allow_html=True)

            if forecast_data.get("cod") == "200":
                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("Forecast")

                forecast_times = [item['dt_txt'] for item in forecast_data['list']]
                forecast_dates = [item['dt_txt'][:10] for item in forecast_data['list']]
                forecast_temps = [item['main']['temp'] for item in forecast_data['list']]
                
                current_day = datetime.now().strftime('%Y-%m-%d')
                upcoming_days = sorted(set(forecast_dates) - {current_day})

                graph_placeholder = st.empty()

                selected_day = current_day
                selected_times = [forecast_times[i] for i in range(len(forecast_dates)) if forecast_dates[i] == selected_day]
                selected_temps = [forecast_temps[i] for i in range(len(forecast_dates)) if forecast_dates[i] == selected_day]
                
                with graph_placeholder:
                    plot_temperature_graph(selected_times, selected_temps, selected_day)

                st.subheader("Select a Day to View the Forecast")
                cols = st.columns(6)  # 6 columns for Today + 5 upcoming days

                with cols[0]:
                    if st.button('Today'):
                        selected_day = current_day
                        selected_times = [forecast_times[i] for i in range(len(forecast_dates)) if forecast_dates[i] == selected_day]
                        selected_temps = [forecast_temps[i] for i in range(len(forecast_dates)) if forecast_dates[i] == selected_day]
                        with graph_placeholder:
                            plot_temperature_graph(selected_times, selected_temps, selected_day)

                for i, day in enumerate(upcoming_days[:6]):
                    with cols[i+1]:
                        if st.button(day):
                            selected_day = day
                            selected_times = [forecast_times[i] for i in range(len(forecast_dates)) if forecast_dates[i] == selected_day]
                            selected_temps = [forecast_temps[i] for i in range(len(forecast_dates)) if forecast_dates[i] == selected_day]
                            with graph_placeholder:
                                plot_temperature_graph(selected_times, selected_temps, selected_day)

            else:
                st.error("Unable to fetch forecast data.")
        else:
            st.error("City not found. Please try another one.")

if __name__ == "__main__":
    main()
