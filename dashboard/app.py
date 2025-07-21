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
import plotly.graph_objs as go

# --------------------------------------------
# Constants and reactive data setup
# --------------------------------------------

UPDATE_INTERVAL_SECS: int = 5
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

ui.page_opts(title="Antarctic Lab: Temp + Humidity Dashboard", fillable=True)
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

    with ui.value_box(
        showcase=icon_svg("clock"),
        theme="bg-gradient-purple-indigo",
    ):
        "Current Time"

        @render.text
        def display_time():
            """Get the latest reading and return a timestamp string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['timestamp']}"

    "Real-time Antarctic Timestamp"

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

            fig = go.Figure()
            # Temperature line
            fig.add_trace(go.Scatter(
                x=df["timestamp"],
                y=df["temperature"],
                mode="lines+markers",
                name="Temperature",
                line=dict(color="#FF5733"),
            ))

        # Trend line
        if len(df) >= 2:
            x_vals = list(range(len(df)))
            slope, intercept, *_ = stats.linregress(x_vals, df["temperature"])
            trend = [slope * x + intercept for x in x_vals]

            fig.add_trace(go.Scatter(
                x=df["timestamp"],
                y=trend,
                mode="lines",
                name="Temp Trend",
                line=dict(color="#900C3F", dash="dash")
            ))

            fig.update_layout(
                xaxis_title="Time",
                yaxis_title="Temperature (°C)",
                plot_bgcolor="#FDFEFE",
                paper_bgcolor="#FBFCFC",
                font=dict(color="#1B2631"),
                title_font=dict(size=20),
                transition=dict(duration=500)
            )

            return fig
        
with ui.card():
    ui.card_header("Humidity Over Time")

    @render_plotly
    def display_humidity_plot():
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()

        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=df["timestamp"],
                y=df["humidity"],
                mode="lines+markers",
                name="Humidity",
                line=dict(color="#3498DB"),
            ))

            fig.update_layout(
                xaxis_title="Time",
                yaxis_title="Humidity (%)",
                plot_bgcolor="#EBF5FB",
                paper_bgcolor="#EAF2F8",
                font=dict(color="#154360"),
                title_font=dict(size=20),
                transition=dict(duration=500) 
            )

            return fig