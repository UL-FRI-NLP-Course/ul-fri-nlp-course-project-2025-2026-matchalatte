from smolagents import tool

@tool
def search_train_connections(
    origin: str,
    destination: str,
    departure_datetime: str,
    max_results: int,
) -> list[dict]:
    """
    Search train, bus, or mixed public transport connections in Europe.

    Args:
        origin: Departure city or station name, for example "Ljubljana".
        destination: Arrival city or station name, for example "Vienna".
        departure_datetime: Desired departure date and time in format "YYYY-MM-DD HH:MM".
        max_results: Maximum number of connections to return.

    Returns:
        A list of connection dictionaries. The first item is the earliest returned connection.
        If no connections are found, returns an empty list.
        If an error occurs, returns a list with one dictionary containing the key "error".
    """

    import json
    import hashlib
    import requests
    from datetime import datetime

    OEBB_URL = "https://fahrplan.oebb.at/bin/mgate.exe"
    AUTH = {"type": "AID", "aid": "OWDL4fE4ixNiPBBm"}
    CLIENT = {"type": "IPH", "id": "OEBB", "v": "6030600", "name": "oebbPROD-ADHOC"}

    HEADERS = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    }

    def hafas_post(svc_req: dict) -> dict:
        body = {
            "lang": "en",
            "svcReqL": [svc_req],
            "client": CLIENT,
            "ver": "1.45",
            "auth": AUTH,
        }

        body_str = json.dumps(body, separators=(",", ":"))
        checksum = hashlib.md5(body_str.encode()).hexdigest()

        response = requests.post(
            f"{OEBB_URL}?checksum={checksum}",
            data=body_str,
            headers=HEADERS,
            timeout=15,
        )

        response.raise_for_status()
        return response.json()

    def format_time(time_string: str) -> str:
        if not time_string:
            return "Unknown"
        return f"{time_string[:2]}:{time_string[2:4]}"

    def format_date(date_string: str, fallback_date: str) -> str:
        if not date_string:
            return fallback_date

        try:
            return datetime.strptime(date_string, "%Y%m%d").strftime("%Y-%m-%d")
        except ValueError:
            return fallback_date

    def make_datetime(date_string: str, time_string: str) -> str:
        if date_string == "Unknown" or time_string == "Unknown":
            return "Unknown"

        return f"{date_string} {time_string}"

    def resolve_station(name: str):
        data = hafas_post({
            "meth": "LocMatch",
            "req": {
                "input": {
                    "loc": {"type": "S", "name": name},
                    "maxLoc": 3,
                    "field": "S",
                }
            },
        })

        locs = data["svcResL"][0]["res"]["match"].get("locL", [])

        if not locs:
            return None, None

        return locs[0]["extId"], locs[0]["name"]

    try:
        dt = datetime.strptime(departure_datetime, "%Y-%m-%d %H:%M")
        fallback_date = dt.strftime("%Y-%m-%d")

        origin_id, _ = resolve_station(origin)
        if not origin_id:
            return [{"error": f"Origin station not found: {origin}"}]

        dest_id, _ = resolve_station(destination)
        if not dest_id:
            return [{"error": f"Destination station not found: {destination}"}]

        data = hafas_post({
            "meth": "TripSearch",
            "req": {
                "depLocL": [{"type": "S", "extId": origin_id}],
                "arrLocL": [{"type": "S", "extId": dest_id}],
                "outDate": dt.strftime("%Y%m%d"),
                "outTime": dt.strftime("%H%M%S"),
                "outFrwd": True,
                "numF": max_results,
                "getPolyline": False,
            },
        })

        res = data["svcResL"][0]["res"]
        journeys = res.get("outConL", [])
        common = res.get("common", {})
        locs = common.get("locL", [])
        products = common.get("prodL", [])

        connections = []

        for journey in journeys[:max_results]:
            legs = []

            journey_date = format_date(
                journey.get("date", ""),
                fallback_date,
            )

            for section in journey.get("secL", []):
                if section.get("type") != "JNY":
                    continue

                dep = section["dep"]
                arr = section["arr"]
                jny = section["jny"]

                dep_name = (
                    locs[dep["locX"]]["name"]
                    if "locX" in dep and dep["locX"] < len(locs)
                    else "Unknown"
                )

                arr_name = (
                    locs[arr["locX"]]["name"]
                    if "locX" in arr and arr["locX"] < len(locs)
                    else "Unknown"
                )

                dep_time = format_time(dep.get("dTimeS", ""))
                arr_time = format_time(arr.get("aTimeS", ""))

                dep_date = format_date(
                    dep.get("dDateS", journey.get("date", "")),
                    journey_date,
                )

                arr_date = format_date(
                    arr.get("aDateS", journey.get("date", "")),
                    journey_date,
                )

                product = "Train"

                if "prodX" in jny and jny["prodX"] < len(products):
                    product = products[jny["prodX"]].get("name", "Train")

                leg = {
                    "product": product,
                    "departure": dep_name,
                    "arrival": arr_name,
                    "departure_time": dep_time,
                    "arrival_time": arr_time,
                    "departure_datetime": make_datetime(dep_date, dep_time),
                    "arrival_datetime": make_datetime(arr_date, arr_time),
                }

                legs.append(leg)

            if not legs:
                continue

            first_leg = legs[0]
            last_leg = legs[-1]

            has_bus = any(
                "bus" in leg["product"].lower()
                or "avtobus" in leg["product"].lower()
                for leg in legs
            )

            connection_type = (
                "bus + train connection"
                if has_bus
                else "train connection"
            )

            route = [
                (
                    f"{leg['product']}: {leg['departure']} → {leg['arrival']}, "
                    f"{leg['departure_time']} → {leg['arrival_time']}"
                )
                for leg in legs
            ]

            connections.append({
                "departure": first_leg["departure"],
                "arrival": last_leg["arrival"],
                "departure_time": first_leg["departure_time"],
                "arrival_time": last_leg["arrival_time"],
                "departure_datetime": first_leg["departure_datetime"],
                "arrival_datetime": last_leg["arrival_datetime"],
                "type": connection_type,
                "route": route,
            })

        return connections

    except Exception as e:
        return [{"error": f"ÖBB/HAFAS search failed: {str(e)}"}]
    

OPENWEATHER_KEY = "9442177234af4594189a800863a98fd3"

@tool
def weather_forecast(city: str) -> dict:
    """
    Get current weather for a city
    
    Args:
        city: Name of the city to fetch the weather for

    Returns a dictionary with:
        - city (str): Name of the city
        - forecasts (list[dict]): A list of 5 objects, each containing:
            - date (str): The date of the forecast (YYYY-MM-DD)
            - temperature (float): Predicted midday temperature in Celsius
            - description (str): Weather condition description
    """
    import requests

    #url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_KEY}&units=metric"
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHER_KEY}&units=metric"
    res = requests.get(url).json()

    daily_snapshots = res["list"][:40:8] 
    #print(daily_snapshots)

    forecast_data = []
    for item in daily_snapshots:
        forecast_data.append({
            "date": item["dt_txt"],
            "temperature": item["main"]["temp"],
            "description": item["weather"][0]["description"]
        })

    return {
        "city": city,
        "forecasts": forecast_data
    }