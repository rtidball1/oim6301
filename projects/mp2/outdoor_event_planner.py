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

    As the founder of Corporates Connect (Cc), I will use this tool when deciding if I should host a small and last minute outdoor Cc event. If the weather is good (at or above my minimum temperature, with lower precipitation probability and wind preferred) I will host an event because I know more people are likely to come that week!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##2. My Plan Before AI

    My plan is to compare temperature, precipitation probability, and wind during the evening hours I want to host an event. I will use Open-Meteo's geocoding API to identify Vancouver, British Columbia, Canada and then send the coordinates to the forecast API. One function will find the location and another will use coordinates to find the hourly weather and return a list. The output I want will be a table showing the coldest temperature, highest precipitation probability, and strongest wind for each evening, calculated across the event hours and whether each evening meets the limits that I set for my event.

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


@app.cell
def _():
    city = "Vancouver"
    province = "British Columbia"
    country_code = "CA"

    forecast_days = 7
    event_start_hour = 18
    event_end_hour = 21
    minimum_temperature_c = 10

    location_api_url = "https://geocoding-api.open-meteo.com/v1/search"
    forecast_api_url = "https://api.open-meteo.com/v1/forecast"

    location_search_limit = 100
    request_timeout_seconds = 30

    event_time_options = [
        {"name": "5–8 p.m.", "start_hour": 17, "end_hour": 20},
        {"name": "6–9 p.m.", "start_hour": 18, "end_hour": 21},
        {"name": "7–10 p.m.", "start_hour": 19, "end_hour": 22},
    ]
    return (
        city,
        country_code,
        event_end_hour,
        event_start_hour,
        event_time_options,
        forecast_api_url,
        forecast_days,
        location_api_url,
        location_search_limit,
        minimum_temperature_c,
        province,
        request_timeout_seconds,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##4. The Work
    """)
    return


@app.cell
def _():
    import requests
    import json
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo

    return ZoneInfo, datetime, json, requests, timedelta


@app.cell
def _(requests):
    def find_location(city_name, province_name, country, api_url,
                      search_limit, timeout_seconds):
        response = requests.get(
            api_url,
            params={
                "name": city_name,
                "countryCode": country,
                "count": search_limit,
                "language": "en",
                "format": "json",
            },
            timeout=timeout_seconds,
        )

        response.raise_for_status()
        data = response.json()

        matches = []

        for _place in data.get("results", []):
            if (
                _place["name"].casefold() == city_name.casefold()
                and _place.get("admin1", "").casefold() == province_name.casefold()
                and _place["country_code"] == country
            ):
                matches.append({
                    "name": _place["name"],
                    "province": _place["admin1"],
                    "country": _place["country"],
                    "latitude": _place["latitude"],
                    "longitude": _place["longitude"],
                    "timezone": _place["timezone"],
                })

        if len(matches) != 1:
            raise ValueError(
                "The search did not find exactly one matching location. "
                "Check the city, province, and country."
            )

        return matches

    return (find_location,)


@app.cell
def _(requests, timedelta):
    def fetch_hourly_weather(latitude, longitude, timezone_name,
                             first_date, number_of_days,
                             api_url, timeout_seconds):
        last_date = first_date + timedelta(days=number_of_days - 1)

        response = requests.get(
            api_url,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "timezone": timezone_name,
                "start_date": str(first_date),
                "end_date": str(last_date),
                "hourly": (
                    "temperature_2m,"
                    "precipitation_probability,"
                    "wind_speed_10m"
                ),
                "temperature_unit": "celsius",
                "wind_speed_unit": "kmh",
            },
            timeout=timeout_seconds,
        )

        response.raise_for_status()
        data = response.json()

        hourly = data["hourly"]
        times = hourly["time"]
        temperatures = hourly["temperature_2m"]
        precipitation = hourly["precipitation_probability"]
        wind = hourly["wind_speed_10m"]

        if (
            len(times) != len(temperatures)
            or len(times) != len(precipitation)
            or len(times) != len(wind)
        ):
            raise ValueError("The API returned weather lists of different lengths.")

        records = []

        for _index in range(len(times)):
            records.append({
                "time": times[_index],
                "temperature_c": temperatures[_index],
                "precipitation_probability": precipitation[_index],
                "wind_kmh": wind[_index],
            })

        return records

    return (fetch_hourly_weather,)


@app.cell
def _(
    ZoneInfo,
    city,
    country_code,
    datetime,
    event_end_hour,
    event_start_hour,
    fetch_hourly_weather,
    find_location,
    forecast_api_url,
    forecast_days,
    location_api_url,
    location_search_limit,
    province,
    request_timeout_seconds,
):
    if not 0 <= event_start_hour <= event_end_hour <= 23:
        raise ValueError("Use whole-hour event times within the same day.")

    if not 1 <= forecast_days <= 7:
        raise ValueError("For this project, choose between one and seven days.")

    locations = find_location(
        city,
        province,
        country_code,
        location_api_url,
        location_search_limit,
        request_timeout_seconds,
    )

    selected_location = locations[0]

    local_now = datetime.now(ZoneInfo(selected_location["timezone"]))
    first_forecast_date = local_now.date()

    weather_records = fetch_hourly_weather(
        selected_location["latitude"],
        selected_location["longitude"],
        selected_location["timezone"],
        first_forecast_date,
        forecast_days,
        forecast_api_url,
        request_timeout_seconds,
    )

    print(
        f"Location: {selected_location['name']}, "
        f"{selected_location['province']}, "
        f"{selected_location['country']}"
    )
    print(f"Fetched {len(weather_records)} hourly records.")
    return first_forecast_date, local_now, selected_location, weather_records


@app.cell
def _(
    event_end_hour,
    event_start_hour,
    first_forecast_date,
    forecast_days,
    local_now,
    minimum_temperature_c,
    timedelta,
    weather_records,
):
    # Group records by timestamp so missing or duplicate hours can be detected.
    weather_by_time = {}

    for _record in weather_records:
        _timestamp = _record["time"]

        if _timestamp not in weather_by_time:
            weather_by_time[_timestamp] = []

        weather_by_time[_timestamp].append(_record)

    evening_results = []
    best_evening = None

    for _day_offset in range(forecast_days):
        _date = first_forecast_date + timedelta(days=_day_offset)
        _evening_records = []

        for _hour in range(event_start_hour, event_end_hour + 1):
            _expected_time = f"{_date}T{_hour:02d}:00"
            _matches = weather_by_time.get(_expected_time, [])

            if len(_matches) != 1:
                raise ValueError(
                    f"Expected exactly one weather record for {_expected_time}."
                )

            _hour_record = _matches[0]

            if (
                _hour_record["temperature_c"] is None
                or _hour_record["precipitation_probability"] is None
                or _hour_record["wind_kmh"] is None
            ):
                raise ValueError(f"Missing weather values for {_expected_time}.")

            _evening_records.append(_hour_record)

        # Start with the first hour, then compare every event hour.
        _lowest_temperature = _evening_records[0]["temperature_c"]
        _highest_precipitation = _evening_records[0]["precipitation_probability"]
        _strongest_wind = _evening_records[0]["wind_kmh"]

        for _hour_record in _evening_records:
            if _hour_record["temperature_c"] < _lowest_temperature:
                _lowest_temperature = _hour_record["temperature_c"]

            if _hour_record["precipitation_probability"] > _highest_precipitation:
                _highest_precipitation = _hour_record["precipitation_probability"]

            if _hour_record["wind_kmh"] > _strongest_wind:
                _strongest_wind = _hour_record["wind_kmh"]

        _temperature_passes = _lowest_temperature >= minimum_temperature_c

        # Do not recommend an event window that has already started.
        _already_started = (
            _date == local_now.date()
            and local_now.hour >= event_start_hour
        )

        if _already_started:
            _status = "Already started"
        elif _temperature_passes:
            _status = "Qualifies"
        else:
            _status = "Too cold"

        _evening = {
            "date": str(_date),
            "lowest_temperature_c": _lowest_temperature,
            "highest_precipitation_probability": _highest_precipitation,
            "strongest_wind_kmh": _strongest_wind,
            "status": _status,
        }

        evening_results.append(_evening)

        if _status == "Qualifies":
            if best_evening is None:
                best_evening = _evening
            elif (
                _highest_precipitation
                < best_evening["highest_precipitation_probability"]
            ):
                best_evening = _evening
            elif (
                _highest_precipitation
                == best_evening["highest_precipitation_probability"]
                and _strongest_wind < best_evening["strongest_wind_kmh"]
            ):
                best_evening = _evening
    return best_evening, evening_results, weather_by_time


@app.cell
def _(json, local_now, mo, weather_records):
    snapshot_folder = mo.notebook_location() / "data"
    snapshot_folder.mkdir(parents=True, exist_ok=True)

    snapshot_stamp = local_now.strftime("%Y%m%d_%H%M%S_%f")
    snapshot_path = snapshot_folder / f"weather_{snapshot_stamp}.json"

    with snapshot_path.open("w", encoding="utf-8") as _snapshot_file:
        json.dump(weather_records, _snapshot_file, indent=2)

    print(f"Saved {len(weather_records)} records to {snapshot_path.name}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##5. The Answer
    """)
    return


@app.cell
def _(
    best_evening,
    evening_results,
    event_end_hour,
    event_start_hour,
    forecast_days,
    minimum_temperature_c,
    selected_location,
):
    print(
        f"Location: {selected_location['name']}, "
        f"{selected_location['province']}, {selected_location['country']}"
    )
    print(
        f"Hours checked: {event_start_hour:02d}:00–"
        f"{event_end_hour:02d}:00, including both endpoints, "
        f"in {selected_location['timezone']}."
    )
    print()

    print(
        f"{'Date':<12} {'Min temp °C':>12} "
        f"{'Max precip %':>13} {'Max wind km/h':>14} {'Result':>18}"
    )

    for _answer in evening_results:
        print(
            f"{_answer['date']:<12} "
            f"{_answer['lowest_temperature_c']:>12.1f} "
            f"{_answer['highest_precipitation_probability']:>13.0f} "
            f"{_answer['strongest_wind_kmh']:>14.1f} "
            f"{_answer['status']:>18}"
        )

    print()

    if best_evening is None:
        print(
            f"No remaining evening in the {forecast_days}-day period stays "
            f"at least {minimum_temperature_c}°C at every checked event hour."
        )
    else:
        print(
            f"The best qualifying evening is {best_evening['date']}: "
            f"its lowest event-hour temperature is "
            f"{best_evening['lowest_temperature_c']:.1f}°C, "
            f"its highest hourly precipitation probability is "
            f"{best_evening['highest_precipitation_probability']:.0f}%, "
            f"and its strongest hourly wind is "
            f"{best_evening['strongest_wind_kmh']:.1f} km/h; "
            f"it ranks first by precipitation probability, then wind, "
            f"then earliest date."
        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. How I know These Numbers Are Right
    """)
    return


@app.cell
def _(
    datetime,
    evening_results,
    event_end_hour,
    event_start_hour,
    weather_records,
):
    check_date = evening_results[0]["date"]
    check_temperatures = []

    print(f"Checking event-hour temperatures for {check_date}:")

    for _check_record in weather_records:
        _check_time = datetime.fromisoformat(_check_record["time"])

        if (
            str(_check_time.date()) == check_date
            and event_start_hour <= _check_time.hour <= event_end_hour
        ):
            check_temperatures.append(_check_record["temperature_c"])
            print(
                f"{_check_time:%H:%M}: "
                f"{_check_record['temperature_c']:.1f}°C"
            )

    if len(check_temperatures) != event_end_hour - event_start_hour + 1:
        raise ValueError("The check does not have all expected event hours.")

    independent_minimum = min(check_temperatures)
    table_minimum = evening_results[0]["lowest_temperature_c"]

    print()
    print(f"Independent minimum: {independent_minimum:.1f}°C")
    print(f"Results-table minimum: {table_minimum:.1f}°C")
    print(f"Numbers agree: {independent_minimum == table_minimum}")
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
    I clarified the decision rule while working with the agent. The agent asked for precipitation and wind cutoffs, but as an event host, I did not think fixed cutoffs for those variables were necessary for this tool. I wanted to use fixed event hours and a minimum temperature requirement to determine which evenings qualify. I then asked the agent to rank qualifying evenings by lowest maximum hourly precipitation probability, followed by lowest maximum wind speed.

    This rule appears in Section 4, in the cell that builds evening_results and selects best_evening. In my first run, I checked the output in Section 5: October 20 and 21 tied at 0% maximum hourly precipitation probability, and the tool selected October 21 because its maximum wind speed was lower: 5.9 km/h compared with 9.4 km/h.
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
    Function 1: find_location()

    This function takes the city, province, country code, API address, search limit, and timeout. It searches for the location and checks that the result matches Vancouver, British Columbia, Canada. It returns a list containing one matching location, including its coordinates and time zone.

    One line I needed help understanding was data = response.json(). It converts the API’s JSON reply into Python dictionaries and lists so the function can work with the location information.

    Function 2: fetch_hourly_weather()

    This function takes the coordinates, time zone, first date, number of days, API address, and timeout. It requests the forecast and returns a list of hourly records. Each record contains the date and time, temperature, precipitation probability, and wind speed.

    One line I needed help understanding was last_date = first_date + timedelta(days=number_of_days - 1). I asked why this line subtracts one from the number of days. The starting date already counts as the first day, so the function only needs to add six more days to get seven days in total.

    Prediction:

    I predict that lowering the minimum temperature from 17°C to 10°C will make October 21, 2026 the best evening for an event. Its lowest temperature during event hours is 11.8°C (which is the highest minimum evening temperature of the options), so it meets the new limit. It ties October 20 at 0% maximum hourly precipitation probability, but its maximum wind speed is lower: 5.9 km/h compared with 9.4 km/h. This prediction assumes the forecast does not change before I run the tool again.

    Note: These observations describe my first prediction test. In a later run, the forecast values changed, but October 21 remained the best qualifying evening. The main results and the extension showed matching values for the same 6–9 p.m. window.

    What happened:

    My prediction was correct! Five evenings now qualify. October 20 and 21 tie at 0% maximum hourly precipitation probability, and October 21 wins with lower wind: 5.9 versus 9.4 km/h. October 23 also qualifies at exactly 10°C, confirming that a value equal to the temperature limit passes. October 25 also qualifies with a temperature over 10°C.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##9. Going Further
    """)
    return


@app.cell
def _(
    event_time_options,
    first_forecast_date,
    forecast_days,
    local_now,
    minimum_temperature_c,
    timedelta,
    weather_by_time,
):
    for _window in event_time_options:
        _qualifying_dates = 0
        _best_window_evening = None

        for _offset in range(forecast_days):
            _window_date = first_forecast_date + timedelta(days=_offset)

            # Skip today's window if it has already started.
            if (
                _window_date == local_now.date()
                and local_now.hour >= _window["start_hour"]
            ):
                continue

            _window_temperatures = []
            _window_precipitation = []
            _window_wind = []

            for _window_hour in range(
                _window["start_hour"], _window["end_hour"] + 1
            ):
                _window_timestamp = (
                    f"{_window_date}T{_window_hour:02d}:00"
                )

                _window_matches = weather_by_time.get(
                    _window_timestamp, []
                )

                if len(_window_matches) != 1:
                    raise ValueError(
                        f"Expected one record for {_window_timestamp}."
                    )

                _window_record = _window_matches[0]

                if (
                    _window_record["temperature_c"] is None
                    or _window_record["precipitation_probability"] is None
                    or _window_record["wind_kmh"] is None
                ):
                    raise ValueError(
                        f"Missing weather values for {_window_timestamp}."
                    )

                _window_temperatures.append(
                    _window_record["temperature_c"]
                )
                _window_precipitation.append(
                    _window_record["precipitation_probability"]
                )
                _window_wind.append(_window_record["wind_kmh"])

            _window_min_temp = min(_window_temperatures)
            _window_max_precip = max(_window_precipitation)
            _window_max_wind = max(_window_wind)

            if _window_min_temp >= minimum_temperature_c:
                _qualifying_dates = _qualifying_dates + 1

                _candidate = {
                    "date": str(_window_date),
                    "temperature": _window_min_temp,
                    "precipitation": _window_max_precip,
                    "wind": _window_max_wind,
                }

                if _best_window_evening is None:
                    _best_window_evening = _candidate
                elif (
                    _window_max_precip
                    < _best_window_evening["precipitation"]
                ):
                    _best_window_evening = _candidate
                elif (
                    _window_max_precip
                    == _best_window_evening["precipitation"]
                    and _window_max_wind < _best_window_evening["wind"]
                ):
                    _best_window_evening = _candidate

        print(f"Event time: {_window['name']}")
        print(f"Qualifying dates: {_qualifying_dates}")

        if _best_window_evening is None:
            print("No date meets the temperature requirement.")
        else:
            print(f"Best date: {_best_window_evening['date']}")
            print(
                f"Minimum temperature: "
                f"{_best_window_evening['temperature']:.1f}°C"
            )
            print(
                f"Maximum hourly precipitation probability: "
                f"{_best_window_evening['precipitation']:.0f}%"
            )
            print(
                f"Maximum wind speed: "
                f"{_best_window_evening['wind']:.1f} km/h"
            )

        print()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I extended the tool to compare three event times: 5–8 p.m., 6–9 p.m., and 7–10 p.m. I wanted to see whether changing the event time would give me more dates that meet my minimum temperature requirement. For each time window, the tool counts qualifying dates and selects the best date using precipitation probability, then wind speed, with the earliest date breaking any remaining tie.

    Using a minimum temperature of 10°C, I found six qualifying dates for 5–8 p.m., five for 6–9 p.m., and four for 7–10 p.m. October 21 was the best date for all three windows. I found that starting earlier gave me more possible dates which makes sense because as the evening goes on it normally gets cooler.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##10. Time Spent
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I spent 4.5 hours on this tool. Compared to mini project 1, which took me a whole day (maybe 10 hours), this was much faster. I was quicker to decide what kind of tool would be the most compatible for the project as well as useful for my company.
    """)
    return


if __name__ == "__main__":
    app.run()
