from smolagents import tool

@tool
def search_train_connections(
    origin: str,
    destination: str,
    departure_datetime: str,
    max_results: int = 5,
) -> str:
    """
    Search train schedules and departure times in Europe.

    Args:
        origin: Departure station or city, e.g. "Ljubljana".
        destination: Arrival station or city, e.g. "Milano Centrale".
        departure_datetime: Departure datetime in format YYYY-MM-DD HH:MM.
        max_results: Maximum number of connections to return.
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

    def hafas_post(svc_req):
        body = {
            "lang": "en",
            "svcReqL": [svc_req],
            "client": CLIENT,
            "ver": "1.45",
            "auth": AUTH,
        }
        body_str = json.dumps(body, separators=(",", ":"))
        checksum = hashlib.md5(body_str.encode()).hexdigest()

        r = requests.post(
            f"{OEBB_URL}?checksum={checksum}",
            data=body_str,
            headers=HEADERS,
            timeout=15,
        )
        r.raise_for_status()
        return r.json()

    try:
        dt = datetime.strptime(departure_datetime, "%Y-%m-%d %H:%M")

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

        origin_id, origin_name = resolve_station(origin)
        if not origin_id:
            return f"Origin station not found: {origin}"

        dest_id, dest_name = resolve_station(destination)
        if not dest_id:
            return f"Destination station not found: {destination}"

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

        if not journeys:
            return "No connections found."

        output = [f"Connections from {origin_name} to {dest_name}:"]

        for i, journey in enumerate(journeys[:max_results], 1):
            legs = []

            for leg in journey.get("secL", []):
                if leg.get("type") != "JNY":
                    continue

                dep = leg["dep"]
                arr = leg["arr"]
                jny = leg["jny"]

                dep_name = locs[dep["locX"]]["name"] if "locX" in dep else "Unknown"
                arr_name = locs[arr["locX"]]["name"] if "locX" in arr else "Unknown"

                dep_time = dep.get("dTimeS", "")
                arr_time = arr.get("aTimeS", "")

                dep_time_fmt = f"{dep_time[:2]}:{dep_time[2:4]}" if dep_time else "Unknown"
                arr_time_fmt = f"{arr_time[:2]}:{arr_time[2:4]}" if arr_time else "Unknown"

                product_name = "Train"
                if "prodX" in jny and jny["prodX"] < len(products):
                    product_name = products[jny["prodX"]].get("name", "Train")

                legs.append({
                    "product": product_name,
                    "dep_name": dep_name,
                    "arr_name": arr_name,
                    "dep_time": dep_time_fmt,
                    "arr_time": arr_time_fmt,
                })

            if not legs:
                continue

            first_leg = legs[0]
            last_leg = legs[-1]

            has_bus = any("bus" in leg["product"].lower() for leg in legs)
            mode = "bus + train connection" if has_bus else "train connection"

            output.append(f"\nConnection {i}:")
            output.append(f"Departure from origin: {first_leg['dep_time']} from {first_leg['dep_name']}")
            output.append(f"Arrival at destination: {last_leg['arr_time']} at {last_leg['arr_name']}")
            output.append(f"Mode: {mode}")
            output.append("Route:")

            for leg in legs:
                output.append(
                    f"- {leg['product']}: {leg['dep_name']} → {leg['arr_name']}, "
                    f"{leg['dep_time']} → {leg['arr_time']}"
                )

        return "\n".join(output)

    except Exception as e:
        return f"ÖBB/HAFAS search failed: {e}"