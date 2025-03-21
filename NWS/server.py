from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("NWS")

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""

@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a specific US state.
    
    Args:
        state: str - The two letter abbreviation of the US state to get alerts for.
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)
    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."
    
    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get the forecast for a specific location.
    
    Args:
        latitude: float - The latitude of the location to get the forecast for.
        longitude: float - The longitude of the location to get the forecast for.
    """
    url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    data = await make_nws_request(url)
    if not data or "properties" not in data:
        return "Unable to fetch forecast or no forecast found."

    forecast_url = data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    periods = forecast_data["properties"]["periods"]

    forecasts = []
    for period in periods:
        forecasts.append(f"""
{period["name"]}:
Temperature: {period["temperature"]} {period["temperatureUnit"]}
Wind: {period["windSpeed"]} {period["windDirection"]}
Precipitation: {period["probabilityOfPrecipitation"]["value"]}%
Forecast: {period["detailedForecast"]}
""")
    return "\n---\n".join(forecasts)

if __name__ == "__main__":
    mcp.run(transport='stdio')