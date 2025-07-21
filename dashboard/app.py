# --------------------------------------------
# Imports at the top - PyShiny EXPRESS VERSION
# --------------------------------------------

from shiny import reactive, render
from shiny.express import ui
import random
from datetime import datetime
from faicons import icon_svg

# --------------------------------------------
# FOR OPTIONAL LOCAL DEVELOPMENT
# --------------------------------------------

# Add all packages not in the Std Library
# to requirements.txt ONLY when working locally:
#
# faicons
# shiny
# shinylive
# 
# And install them into an active project virtual environment (usually in .venv)

# --------------------------------------------
# SET UP THE REACTIVE CONTENT
# --------------------------------------------

UPDATE_INTERVAL_SECS: int = 1

# Initialize a REACTIVE CALC that our display components can call

@reactive.calc()
def lab_temp_sensor():

    # Invalidate this calculation every UPDATE_INTERVAL_SECS to trigger updates
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)

    # Data generation logic. Get random between 20.0 and 23.0 C
    temp = round(random.uniform(20.0, 23.0), 1)

    # Get a timestamp for "now" and use string format strftime() method to format it
    lab_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    latest_dictionary_entry = {"temp": temp, "lab_time": lab_time}

    # Return everything we need
    return latest_dictionary_entry

# ------------------------------------------------
# Define the Shiny UI Page layout - Page Options
# ------------------------------------------------

ui.page_opts(title="Alissa's Lab Temperature Monitor", fillable=True)

# ------------------------------------------------
# Define the Shiny UI Page layout - Sidebar
# ------------------------------------------------

with ui.sidebar(open="open"):
    ui.h2("Lab Sensor Dashboard", class_="text-center")
    ui.p(
        "A demonstration of real-time temperature readings inside a controlled lab environment.",
        class_="text-center",
    )

#---------------------------------------------------------------------
# In Shiny Express, everything not in the sidebar is in the main panel
#---------------------------------------------------------------------

ui.h2("Current Lab Temperature")

@render.text
def display_temp():
    """Get the latest reading and return a temperature string"""
    latest_dictionary_entry = lab_temp_sensor()
    return f"{latest_dictionary_entry['temp']} C"

ui.p("Within controlled range.")

ui.p("🧪")

ui.hr()

ui.h2("Current Date and Time")

@render.text
def display_time():
    """Get the latest reading and return a timestamp string"""
    latest_dictionary_entry = lab_temp_sensor()
    return f"{latest_dictionary_entry['lab_time']}"
