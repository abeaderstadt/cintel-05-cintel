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

    # Return a tuple with everything we need
    return deque_snapshot, df, new_dictionary_entry

# --------------------------------------------
# --- layout section ---
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

# In Shiny Express, everything not in the sidebar is in the main panel
# --------------------------------------------
# --- charts section ---
# --------------------------------------------
@render.plotly
def plot_temp_chart():
    """Line chart showing temperature over time with trend"""
    deque_snapshot, df, _ = reactive_calc_combined()
    fig = px.line(df, x="timestamp", y="temperature", title="Temperature Over Time (°C)", markers=True)

    # Add linear regression line
    x_vals = list(range(len(df)))
    y_vals = df["temperature"]
    slope, intercept, _, _, _ = stats.linregress(x_vals, y_vals)
    df["temp_trend"] = [slope * x + intercept for x in x_vals]

    fig.add_scatter(x=df["timestamp"], y=df["temp_trend"], mode="lines", name="Temp Trend")
    fig.update_layout(xaxis_title="Time", yaxis_title="Value (%) or °C")

    return fig

@render.plotly
def plot_humidity_chart():
    """Line chart showing humidity over time"""
    deque_snapshot, df, _ = reactive_calc_combined()
    fig = px.line(df, x="timestamp", y="humidity", title="Humidity Over Time (%)", markers=True)
    return fig

# --------------------------------------------
# --- main content layout ---
# --------------------------------------------

with ui.layout_columns(col_widths=[6, 6]):
    with ui.card():
        "Temperature Over Time"
        plot_temp_chart()

    with ui.card():
        "Humidity Over Time"
        plot_humidity_chart()
        "Current Temperature"

 # --- value box: temperature ---
        @render.text
        def display_temp():
            """Get the latest reading and return a temperature string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['temperature']} C"

        "Real-time Antarctic Temperature"

# --- value box: humidity ---
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

# --- value box: time ---
    with ui.card(full_screen=True):
        ui.card_header("Current Date and Time")

        @render.text
        def display_time():
            """Get the latest reading and return a timestamp string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['timestamp']}"

# --------------------------------------------
# --- dataframe section ---
# --------------------------------------------

#with ui.card(full_screen=True, min_height="40%"):
with ui.card(full_screen=True):
    ui.card_header("Most Recent Readings")

    @render.data_frame
    def display_df():
        """Get the latest reading and return a dataframe with current readings"""
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
        pd.set_option('display.width', None)        # Use maximum width
        return render.DataGrid( df,width="100%")
