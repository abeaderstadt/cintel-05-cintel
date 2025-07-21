# --------------------------------------------
# Imports at the top - PyShiny EXPRESS VERSION
# --------------------------------------------

from shiny import reactive, render
from shiny.express import ui
import random
from datetime import datetime
from collections import deque
import pandas as pd
import plotly.express as px
from shinywidgets import render_plotly
from scipy import stats
from faicons import icon_svg 

# --------------------------------------------
# Constants and reactive data setup
# --------------------------------------------

UPDATE_INTERVAL_SECS: int = 3
DEQUE_SIZE: int = 5
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

# --------------------------------------------
# --- reactive calculation (data logic) ---
# --------------------------------------------

@reactive.calc()
def reactive_calc_combined():
    # Invalidate this calculation every UPDATE_INTERVAL_SECS to trigger updates
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)

    # Data generation logic
    temperature = round(random.uniform(-18, -16), 1)
    humidity = round(random.uniform(60, 100), 1) 
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_dictionary_entry = {
        "temperature": temperature,
        "humidity": humidity,
        "timestamp": timestamp
    }

    # get the deque and append the new entry
    reactive_value_wrapper.get().append(new_dictionary_entry)

    # Get a snapshot of the current deque for any further processing
    deque_snapshot = reactive_value_wrapper.get()

    # For Display: Convert deque to DataFrame for display
    df = pd.DataFrame(deque_snapshot)

    # For Display: Get the latest dictionary entry
    latest_dictionary_entry = new_dictionary_entry

    # Return a tuple with everything we need
    return deque_snapshot, df, latest_dictionary_entry

# --------------------------------------------
# --- layout and sidebar section ---
# --------------------------------------------

ui.page_opts(title="Antarctic Lab: Temp + Humidity Dashboard", fillable=True, theme="minty",)
# Sidebar is typically used for user interaction/information
with ui.sidebar(open="open"):
    ui.h2("Polar Monitoring Lab ❄️", class_="text-center")
    ui.p("A demonstration of Real-time Antarctic climate conditions.", class_="text-center",)
    ui.hr()
    ui.h6("Links:")
    ui.a("GitHub Source", href="https://github.com/abeaderstadt/cintel-05-cintel", target="_blank",)
    # Uncomment when hosted
    # ui.a("GitHub App", href="https://abeaderstadt.github.io/cintel-05-cintel/", target="_blank")
    ui.a("PyShiny", href="https://shiny.posit.co/py/", target="_blank")
    ui.a(
        "PyShiny Express",
        href="https://shiny.posit.co/blog/posts/shiny-express/",
        target="_blank",
    )

# --------------------------------------------
# --- Value boxes and latest reading section ---
# --------------------------------------------

with ui.layout_columns():
    with ui.value_box(
        showcase=icon_svg("sun"),
        theme="bg-gradient-blue-purple",
    ):
        "Current Temperature"

        @render.text
        def display_temp():
            """Get the latest reading and return a temperature string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['temperature']} C"

        "Real-time Antarctic Temperature"


    with ui.value_box(
        showcase=icon_svg("droplet"),
        theme="bg-gradient-cyan-blue",
    ):
        "Current Humidity"
    
        @render.text
        def display_humidity():
            """Get the latest reading and return a humidity string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['humidity']} %"

        "Real-time Antarctic Humidity"

    with ui.card(full_screen=True):
        ui.card_header("Current Date and Time")

        @render.text
        def display_time():
            """Get the latest reading and return a timestamp string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['timestamp']}"

# --------------------------------------------
# --- DataFrame display section ---
# --------------------------------------------

#with ui.card(full_screen=True, min_height="40%"):
with ui.card(full_screen=True):
    ui.card_header("Most Recent Readings")

    @render.data_frame
    def display_df():
        """Get the latest reading and return a dataframe with current readings"""
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
        pd.set_option('display.width', None) 
        return render.DataGrid( df,width="100%")
    
# --------------------------------------------
# --- Charts section ---
# --------------------------------------------

with ui.card():
    ui.card_header("Temperature Over Time")

    @render_plotly
    def display_temp_plot():
        # Fetch from the reactive calc function
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()

        # Ensure the DataFrame is not empty before plotting
        if not df.empty:
            # Convert the 'timestamp' column to datetime for better plotting
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            sequence = range(len(df))
            x_vals = list(sequence)
            y_vals = df["temperature"]

            slope, intercept, _, _, _ = stats.linregress(x_vals, y_vals)
            df['temp_trend'] = [slope * x + intercept for x in x_vals]

            fig = px.line(df,
                x="timestamp",
                y="temperature",
                title="Temperature Over Time (°C)",
                markers=True,
                labels={"temperature": "Temperature (°C)", "timestamp": "Time"},
            )

            fig.add_scatter(
                x=df["timestamp"], y=df["temp_trend"],
                mode='lines',
                name='Temp Trend',
            )

            fig.update_layout(
                xaxis_title="Time",
                yaxis_title="Temperature (°C)",
                title_font=dict(size=20),
)
            return fig
        
with ui.card():
    ui.card_header("Humidity Over Time")

    @render_plotly
    def display_humidity_plot():
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()

        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            fig = px.line(df,
                          x="timestamp",
                          y="humidity",
                          title="Humidity Over Time (%)",
                          markers=True,
                          labels={"humidity": "Humidity (%)", "timestamp": "Time"})

            fig.update_layout(xaxis_title="Time", yaxis_title="Humidity (%)")
            return fig
