import requests
import streamlit as st
 
def get_weather_data(city_name, api_key):
    """
    Fetches weather data for a given city.
    """
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city_name,
        'appid': api_key,
        'units': 'metric' # Or 'imperial' for Fahrenheit
    }
    try:
        response = requests.get(base_url, params=params, timeout=10) # 10 seconds timeout
        response.raise_for_status() # Raises an HTTPError for bad responses (4XX or 5XX)
        return response.json() # Return the JSON response on success
    # Let the caller handle the exceptions and display UI messages
    except requests.exceptions.RequestException as e:
        # Catch any request-related exception (HTTPError, ConnectionError, Timeout, etc.)
        # and re-raise it or return None, letting the caller handle the UI display.
        raise e # Re-raise the exception

def display_streamlit_weather(data, city_input_name):
    """Displays formatted weather data using Streamlit components."""
    try:
        actual_city_name = data.get('name', city_input_name)
        country = data.get('sys', {}).get('country', 'N/A')
        temp = data.get('main', {}).get('temp')
        feels_like = data.get('main', {}).get('feels_like')
        humidity = data.get('main', {}).get('humidity')
        weather_info = data.get('weather', [{}])[0]
        description = weather_info.get('description', 'N/A')
        wind_speed = data.get('wind', {}).get('speed')
        icon_code = weather_info.get('icon')
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png" if icon_code else None

        # Display results in a more structured way
        with st.container():
            st.subheader(f"Weather in {actual_city_name}, {country}")

            if icon_url:
                st.image(icon_url, caption=description.capitalize(), width=100)
            else:
                # Fallback if no icon, though OpenWeatherMap usually provides one
                st.markdown(f"**Conditions:** {description.capitalize()}")

            col1, col2 = st.columns(2)
            with col1:
                if temp is not None:
                    st.metric("Temperature", f"{temp}°C")
                if humidity is not None:
                    st.markdown(f"**Humidity:** {humidity}%")
            
            with col2:
                if feels_like is not None:
                    st.metric("Feels Like", f"{feels_like}°C")
                if wind_speed is not None:
                    st.markdown(f"**Wind Speed:** {wind_speed} m/s")
    except (IndexError, KeyError, TypeError) as e:
        st.error(f"Error parsing weather data: {e}. The received data might be incomplete or in an unexpected format.")

# --- Streamlit App UI ---
st.set_page_config(page_title="Weather App", layout="centered")
st.title("🌤️ Weather App")

API_KEY_PLACEHOLDER = "YOUR_ACTUAL_API_KEY"
API_KEY = API_KEY_PLACEHOLDER
API_KEY = "25fea628be91aa147881cd5b1c0c9044"

if API_KEY == API_KEY_PLACEHOLDER or API_KEY == "YOUR_ACTUAL_API_KEY" or not API_KEY:
    st.error("⚠️ API Key Not Configured!")
    st.warning("Please update the `API_KEY` variable in the `app.py` script with your actual OpenWeatherMap API key.")
    st.info("You can get a free API key from OpenWeatherMap.")
    st.stop() # Stop execution if API key is not set

# Use a form for better input handling
with st.form(key="weather_form"):
    city_name_input = st.text_input("Enter city name:", placeholder="e.g., London, New York, Tokyo")
    submit_button = st.form_submit_button(label="Get Weather 🌦️")

if submit_button:
    city_to_fetch = city_name_input.strip()
    if city_to_fetch:
        with st.spinner(f"Fetching weather for {city_to_fetch}..."):
            weather_data = None
            try:
                weather_data = get_weather_data(city_to_fetch, API_KEY)
            except requests.exceptions.HTTPError as http_err:
                if http_err.response.status_code == 401:
                    st.error("Error: Invalid API Key. Please check your API key.")
                elif http_err.response.status_code == 404:
                    st.error(f"Error: City '{city_to_fetch}' not found.")
                else:
                    st.error(f"HTTP error occurred: {http_err}")
            except requests.exceptions.ConnectionError:
                st.error("Error: Could not connect to the weather service. Check your internet connection.")
            except requests.exceptions.Timeout:
                st.error("Error: The request to the weather service timed out.")
            except Exception as err:
                st.error(f"An unexpected error occurred: {err}")
        
        st.divider() # Visual separator before showing results or errors from API
        if weather_data:
            display_streamlit_weather(weather_data, city_to_fetch)
    elif not city_to_fetch: # Only show warning if submit was pressed with empty input
        st.warning("Please enter a city name.")

st.divider()