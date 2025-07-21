# --------------------------------------------
# Imports at the top - PyShiny EXPRESS VERSION
# --------------------------------------------

# From shiny, import just reactive and render
from shiny import reactive, render

# From shiny.express, import just ui and inputs if needed
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
# First, set a constant UPDATE INTERVAL for all live data
# --------------------------------------------

UPDATE_INTERVAL_SECS: int = 3

# --------------------------------------------
# Initialize a REACTIVE VALUE with a common data structure
# --------------------------------------------

DEQUE_SIZE: int = 5
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

# --------------------------------------------
# Initialize a REACTIVE CALC that all display components can call
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


# Define the Shiny UI Page layout
ui.page_opts(title="Antarctic Lab: Temp + Humidity Dashboard", fillable=True)

with ui.sidebar(open="open"):

    ui.h2("Polar Monitoring Lab ❄️", class_="text-center")
    ui.p(
        "A demonstration of Real-time Antarctic climate conditions.",
        class_="text-center",
    )
    ui.hr()
    ui.h6("Links:")
    ui.a(
    "GitHub Source",
    href="https://github.com/abeaderstadt/cintel-05-cintel",
    target="_blank",
)
# update or uncomment this once I host my app:
# ui.a(
#     "GitHub App",
#     href="https://abeaderstadt.github.io/cintel-05-cintel/",
#     target="_blank",
# )
    ui.a("PyShiny", href="https://shiny.posit.co/py/", target="_blank")
    ui.a(
        "PyShiny Express",
        href="https://shiny.posit.co/blog/posts/shiny-express/",
        target="_blank",
    )

# In Shiny Express, everything not in the sidebar is in the main panel

# ---------------------- Render Functions ----------------------

@render.plotly
def plot_temp_chart():
    deque_snapshot, df, _ = reactive_calc_combined()
    fig = px.line(df, x="timestamp", y="temperature", title="Temperature Over Time (\u00b0C)", markers=True)
    x_vals = list(range(len(df)))
    slope, intercept, _, _, _ = stats.linregress(x_vals, df["temperature"])
    df["temp_trend"] = [slope * x + intercept for x in x_vals]
    fig.add_scatter(x=df["timestamp"], y=df["temp_trend"], mode='lines', name='Trend')
    return fig

@render.plotly
def plot_humidity_chart():
    deque_snapshot, df, _ = reactive_calc_combined()
    fig = px.line(df, x="timestamp", y="humidity", title="Humidity Over Time (%)", markers=True)
    return fig

@render.text
def display_temp():
    _, _, latest = reactive_calc_combined()
    return f"{latest['temperature']} \u00b0C"

@render.text
def display_humidity():
    _, _, latest = reactive_calc_combined()
    return f"{latest['humidity']} %"

@render.text
def display_time():
    _, _, latest = reactive_calc_combined()
    return f"{latest['timestamp']}"

@render.data_frame
def display_df():
    _, df, _ = reactive_calc_combined()
    pd.set_option('display.width', None)
    return render.DataGrid(df, width="100%")

# ---------------------- UI Layout ----------------------

app_ui = ui.page_fluid(
    ui.h2("Live Antarctic Lab Readings"),

    ui.layout_columns(
        ui.card(
            ui.card_header("Temperature Over Time"),
            plot_temp_chart()
        ),
        ui.card(
            ui.card_header("Humidity Over Time"),
            plot_humidity_chart()
        ),
        col_widths=[6, 6]
    ),

    ui.layout_columns(
        ui.value_box(
            "Current Temperature",
            display_temp(),
            "Real-time Antarctic Temperature",
            showcase=icon_svg("sun"),
            theme="bg-gradient-blue-purple"
        ),
        ui.value_box(
            "Current Humidity",
            display_humidity(),
            "Real-time Antarctic Humidity",
            showcase=icon_svg("droplet"),
            theme="bg-gradient-cyan-blue"
        )
    ),

    ui.card(
        ui.card_header("Current Date and Time"),
        display_time(),
        full_screen=True
    ),

    ui.card(
        ui.card_header("Most Recent Readings"),
        display_df(),
        full_screen=True
    )
)

# ---------------------- Run App ----------------------

app = App(app_ui, server=None)