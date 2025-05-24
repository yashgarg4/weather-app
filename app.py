import requests
import streamlit as st
import google.generativeai as genai
import os 
 
def get_weather_data(city_name, api_key):
    """
    Fetches weather data for a given city.
    """
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city_name,
        'appid': api_key,
        'units': 'metric'
    }
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
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

def call_google_llm(prompt_text, api_key):
    """
    Calls the Google LLM with the given prompt.
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt_text)
        return response.text
    except Exception as e:
        st.error(f"Error calling Google LLM: {e}")
        return None

# --- Streamlit App UI ---
st.set_page_config(page_title="Weather App", layout="centered")
st.title("🌤️ Weather App")

OWM_API_KEY_PLACEHOLDER = "YOUR_OPENWEATHER_API_KEY_PLACEHOLDER"
# OWM_API_KEY = "25fea628be91aa147881cd5b1c0c9044" # For locl environment testing before deployment
OWM_API_KEY = st.secrets.get("OPENWEATHER_API_KEY", OWM_API_KEY_PLACEHOLDER)

if OWM_API_KEY == OWM_API_KEY_PLACEHOLDER or not OWM_API_KEY:
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
                weather_data = get_weather_data(city_to_fetch, OWM_API_KEY)
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

# --- Google LLM Interaction ---
st.header("💬 Ask Google LLM")

GOOGLE_API_KEY_PLACEHOLDER = "YOUR_GOOGLE_API_KEY_PLACEHOLDER"
# GOOGLE_API_KEY = "AIzaSyAjYWTyf6kxcxn6wfPT_Ln1WEvdFhjqC9w" # For local testing before deployment
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", GOOGLE_API_KEY_PLACEHOLDER)

if GOOGLE_API_KEY == GOOGLE_API_KEY_PLACEHOLDER or not GOOGLE_API_KEY:
    st.warning("⚠️ Google API Key Not Configured for LLM feature.")
    st.info(
        "To use this feature, please set your Google API Key. "
        "You can get one from Google AI Studio. "
        "It's recommended to set it as an environment variable `GOOGLE_API_KEY` or use Streamlit secrets."
    )
else:
    with st.form(key="llm_form"):
        llm_prompt = st.text_area("Enter your question for the LLM:", placeholder="e.g., Explain quantum computing in simple terms.", height=150)
        llm_submit_button = st.form_submit_button(label="Ask LLM 🤖")

    if llm_submit_button:
        if llm_prompt:
            with st.spinner("The LLM is thinking... 🤔"):
                llm_response = call_google_llm(llm_prompt, GOOGLE_API_KEY)
                if llm_response:
                    st.markdown("### LLM Response:")
                    st.markdown(llm_response)
        else: # Only show warning if submit was pressed with empty input
            st.warning("Please enter a question for the LLM.")