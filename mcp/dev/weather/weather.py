from typing import Any
import httpx
# Update the import path below if FastMCP is located elsewhere, or install the mcp package if missing.
# Example alternative import if FastMCP is in the same directory or a parent directory:
# from fastmcp import FastMCP
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

@mcp.tool()
async def get_alerts(state: str) -> str:
    """
    获取美国某个州当前生效的天气预警信息
    :param state: 州的缩写（例如：CA, NY）
    :return: 当前生效的天气预警信息
    """
    url = f"{NWS_API_BASE}/alerts/active?area={state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "没有找到相关的天气预警信息"
    
    if not data["features"]:
        return "当前没有生效的天气预警"
    
    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)
    
@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """
    获取指定经纬度的天气预报
    :param latitude: 纬度
    :param longitude: 经度
    :return: 天气预报信息
    """
    url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    data = await make_nws_request(url)

    if not data or "properties" not in data:
        return "没有找到相关的天气预报信息"
    
    forecast_url = data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "没有找到相关的天气预报数据"
    
    periods = forecast_data.get("properties", {}).get("periods", [])
    forecasts = []
    for period in periods[:5]:
        forecast = f"""
{period['name']}:
温度：{period['temperature']}°{period['temperatureUnit']}
风力：{period['windSpeed'] }{period['windDirection']}
预报：{period['detailedForecast']}
"""
    forecasts.append(forecast.strip())
        
    return "\n---\n".join(forecasts)

async def make_nws_request(url: str) -> dict[str,Any] | None:
    """
    发起对NWS API的请求
    :param url: 请求的URL
    :return: 返回的JSON数据或None
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP错误: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"请求错误: {e}")
        return None
    
def format_alert(feature: dict[str, Any]) -> str:
    """
    格式化天气预警信息
    :param feature: NWS API返回的预警信息
    :return: 格式化后的预警信息字符串
    """
    properties = feature.get("properties", {})
    return f"""
预警类型: {properties.get('event', '未知')}
预警类型: {properties.get('areaDesc', '未知')}
预警类型: {properties.get('severity', '未知')}
预警描述: {properties.get('description', '无描述信息')}
生效时间: {properties.get('instruction', '无具体指令')}
"""

if __name__ == "__main__":
    mcp.run(transport='stdio')