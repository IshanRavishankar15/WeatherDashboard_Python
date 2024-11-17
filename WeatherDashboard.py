import streamlit as st
import requests
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# API Configuration
API_KEY = 'ec535cf3bfdd19f702ffed69ed6f7446'  # Your provided API key
BASE_URL = 'https://api.openweathermap.org/data/2.5'

# Load City Data
@st.cache_data
def load_city_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Fetch Current Weather
def get_weather(city_name):
    params = {
        'q': city_name,
        'appid': API_KEY,
        'units': 'metric'
    }
    response = requests.get(f"{BASE_URL}/weather", params=params)
    return response.json()

# Fetch 5-Day Forecast
def get_forecast(city_name):
    params = {
        'q': city_name,
        'appid': API_KEY,
        'units': 'metric'
    }
    response = requests.get(f"{BASE_URL}/forecast", params=params)
    return response.json()

# Plot Temperature Graph with annotations and adjusted y-axis limits
def plot_temperature_graph(times, temps, selected_day):
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2e2e2e')  # Set dark background for the graph

    # Convert times from string to datetime
    times = [datetime.strptime(time, '%Y-%m-%d %H:%M:%S') for time in times]

    # Plot temperature data with markers
    ax.plot(times, temps, marker='o', linestyle='-', color='tab:cyan', label=f"Temperature on {selected_day}")

    # Add a title to the graph
    ax.set_title(f"Temperature vs Time for {selected_day}", fontsize=14, color='white', ha='center')

    # Set labels and customize colors
    ax.set_xlabel("Time", fontsize=12, color='white', labelpad=20)
    ax.set_ylabel("Temperature (°C)", fontsize=12, color='white', labelpad=20)
    ax.tick_params(axis='y', labelcolor='white', colors='white')
    ax.tick_params(axis='x', labelcolor='white')

    # Add gridlines for better readability
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.5, color='white')

    # Format time axis (X-axis)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xticks(rotation=45)

    # Add annotations for each data point with better positioning and styling
    for i, (time, temp) in enumerate(zip(times, temps)):
        ax.annotate(
            f"{temp}°C", 
            (times[i], temps[i]), 
            textcoords="offset points", 
            xytext=(0, 15),  # Increase the vertical offset to avoid overlap
            ha='center', 
            fontsize=10,  # Set a smaller font size for clarity
            color='tab:cyan',  # Set the annotation color to match the graph
            fontweight='bold',  # Make the annotation text bold for better visibility
            bbox=dict(facecolor='black', edgecolor='none', boxstyle='round,pad=0.3')  # Add a contrasting background box
        )

    # Adjust the y-axis limits by adding 3 degrees to both ends
    min_temp = min(temps)
    max_temp = max(temps)
    buffer = 3
    ax.set_ylim(min_temp - buffer, max_temp + buffer)

    # Set the background color of the axes to dark
    ax.set_facecolor('#2e2e2e')

    # Improve layout
    plt.tight_layout()

    # Show the graph
    st.pyplot(fig)

# Streamlit App
def main():
    st.title("Weather Dashboard")
    st.write("🌤️ Get real-time weather updates and forecasts!")

    # Load city data
    city_data = load_city_data('city.list.json')  # Ensure 'city.list.json' is in the same directory
    city_names = [f"{city['name']}, {city['country']}" for city in city_data]

    # Initially, show a blank selectbox
    selected_city = st.selectbox("Search for a city", [""] + city_names)

    # If a city is selected and the button is clicked
    if selected_city and selected_city != "":
        city_name = selected_city.split(",")[0]  # Get city name without country

        # Fetch Data
        with st.spinner("Fetching weather data..."):
            current_weather = get_weather(city_name)
            forecast_data = get_forecast(city_name)
        
        if current_weather.get("cod") == 200:
            # Extract current weather data
            temperature = current_weather['main']['temp']
            temp_min = current_weather['main']['temp_min']
            temp_max = current_weather['main']['temp_max']
            humidity = current_weather['main']['humidity']
            wind_speed = current_weather['wind']['speed']
            description = current_weather['weather'][0]['description'].capitalize()
            icon_code = current_weather['weather'][0]['icon']
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

            # Display current weather in a styled card with larger font size
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
                <p style="text-align:center; color:white; font-size:20px;">🌬️ <strong>Wind Speed:</strong> {wind_speed} m/s</p>
            </div>
            """, unsafe_allow_html=True)

            # Process and Display Forecast Data
            if forecast_data.get("cod") == "200":
                st.subheader("Temperature vs Time")

                # Extract forecast information for the graph
                forecast_times = [item['dt_txt'] for item in forecast_data['list']]
                forecast_dates = [item['dt_txt'][:10] for item in forecast_data['list']]
                forecast_temps = [item['main']['temp'] for item in forecast_data['list']]
                
                # Get the current day and upcoming days
                current_day = datetime.now().strftime('%Y-%m-%d')
                upcoming_days = sorted(set(forecast_dates) - {current_day})

                # Create an empty container to update the graph
                graph_placeholder = st.empty()

                # Display the default graph for the current day
                selected_day = current_day
                selected_times = [forecast_times[i] for i in range(len(forecast_dates)) if forecast_dates[i] == selected_day]
                selected_temps = [forecast_temps[i] for i in range(len(forecast_dates)) if forecast_dates[i] == selected_day]
                
                # Initially plot the current day graph
                with graph_placeholder:
                    plot_temperature_graph(selected_times, selected_temps, selected_day)

                # Buttons to select upcoming days above the graph
                st.subheader("Select a Day to See Forecast")
                cols = st.columns(6)  # 6 columns for Today + 5 upcoming days

                # Button for Today
                with cols[0]:
                    if st.button('Today'):
                        selected_day = current_day
                        selected_times = [forecast_times[i] for i in range(len(forecast_dates)) if forecast_dates[i] == selected_day]
                        selected_temps = [forecast_temps[i] for i in range(len(forecast_dates)) if forecast_dates[i] == selected_day]
                        with graph_placeholder:
                            plot_temperature_graph(selected_times, selected_temps, selected_day)

                # Buttons for the next 5 days
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
