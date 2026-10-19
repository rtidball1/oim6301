import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Mini Project 2: Outdoor Event Planner for Corporates Connect

    ## 1. The Question

    My tool will answer "what evening in the next seven days has the best weather for an outdoor Corporates Connect event in Vancouver, British Columbia, Canada?"

    As the founder of Corporates Connect (Cc), I will use this tool when deciding if I should host a small and last minute outdoor Cc event. If the weather is good (warm but not too hot, no rain, and light wind) I will host an event because I know more people are likely to come that week!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##2. My Plan Before AI

    My plan is to compare temperature, precipitation probability, and wind during the evening hours I want to host an event. I will use the open-meteo's geocoding API to identify Vancouver, British Columbia, Canada and then send the coordinates to the forecast API. One function will find the location and another will use coordinates to find the hourly weather and return a list. The output I want will be a table showing the coldest temperature, highest precipitation probability, and strongest wind for each evening, calculated acorss the event hours and whether each evening meets the limits that I set for my event.

    Which functions will your tool need? For each, what goes in and what comes out?

    My tool will need to be able to find the correct location and identify Vancouver, British Columbia, Canada. Inputs would be city, province, and country code to produce a list of matching locations. Another function would be hourly weather. The input would be coordinates, time zone, and number of days to get an output of a list of hourly records that include date and time, temperature, precipitation probability, and wind speed.

    Which addresses will they request?

    Location search: [https://geocoding-api.open-meteo.com/v1/search](https://geocoding-api.open-meteo.com/v1/search?name=Vancouver&count=10&language=en&format=json&countryCode=CA)
    Weather forecast: [https://api.open-meteo.com/v1/forecast](https://api.open-meteo.com/v1/forecast?latitude=49.24966&longitude=-123.11934&hourly=temperature_2m,precipitation_probability,wind_speed_10m&temperature_unit=celsius&wind_speed_unit=kmh&timezone=America%2FVancouver&forecast_days=7)

    How will you know you have every record?

    I will check that the returned timestamps and weather lists have matching lengths. Then, for each of the seven dates, I will check that every expected event-hour timestamp appears once and has temperature, precipitation probability, and wind values.

    Which check will you use in section 6, and which two numbers should agree?

    I will choose one evening and find the lowest temperature across the event hours in the API response. I will compare that number with the lowest temperature shown for the same evening in my results table. I will check that both numbers agree.

    Going further

    To go further I plan on comparing other nearby locations that I could move my event to if needed or changing the weather limits that I set.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##3. Inputs
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##4. The Work
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##5. The Answer
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. How I know These Numbers Are Right
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##7. Working With the Agent
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##8. Reading it Back
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##9. Going Further
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##10. Time Spent
    """)
    return


if __name__ == "__main__":
    app.run()
