import httpx
import json
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("api-resources")

# API keys (in a real application, use environment variables or secure storage)
WEATHER_API_KEY = "your_weather_api_key"
NEWS_API_KEY = "your_news_api_key"

@mcp.resource(
    uri="api://weather/current/{city}",
    name="Current Weather",
    description="Get current weather for a city"
)
async def current_weather(city):
    """Get current weather for a specified city."""
    try:
        # Connect to OpenWeatherMap API
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": WEATHER_API_KEY,
            "units": "metric"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
        
        # Format the response
        weather = {
            "city": data.get("name", city),
            "country": data.get("sys", {}).get("country", ""),
            "temperature": {
                "current": data.get("main", {}).get("temp", 0),
                "feels_like": data.get("main", {}).get("feels_like", 0),
                "min": data.get("main", {}).get("temp_min", 0),
                "max": data.get("main", {}).get("temp_max", 0),
                "unit": "°C"
            },
            "humidity": data.get("main", {}).get("humidity", 0),
            "wind": {
                "speed": data.get("wind", {}).get("speed", 0),
                "direction": data.get("wind", {}).get("deg", 0)
            },
            "conditions": [condition.get("description", "") for condition in data.get("weather", [])],
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(weather, indent=2)
    
    except Exception as e:
        return f"Error fetching weather data: {str(e)}"

@mcp.resource(
    uri="api://weather/forecast/{city}/{days}",
    name="Weather Forecast",
    description="Get weather forecast for a city"
)
async def weather_forecast(city, days="5"):
    """Get weather forecast for a specified city."""
    try:
        # Convert days to integer
        days_int = int(days)
        if days_int > 7:
            days_int = 7  # Limit to 7 days
        
        # Connect to OpenWeatherMap API
        url = f"https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": city,
            "appid": WEATHER_API_KEY,
            "units": "metric",
            "cnt": days_int * 8  # 8 forecasts per day
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
        
        # Format the response
        forecast = {
            "city": data.get("city", {}).get("name", city),
            "country": data.get("city", {}).get("country", ""),
            "days": []
        }
        
        # Group by day
        forecasts_by_day = {}
        for item in data.get("list", []):
            date = item.get("dt_txt", "").split(" ")[0]
            if date not in forecasts_by_day:
                forecasts_by_day[date] = []
            
            forecasts_by_day[date].append({
                "time": item.get("dt_txt", "").split(" ")[1],
                "temperature": item.get("main", {}).get("temp", 0),
                "conditions": [w.get("description", "") for w in item.get("weather", [])],
                "humidity": item.get("main", {}).get("humidity", 0),
                "wind_speed": item.get("wind", {}).get("speed", 0)
            })
        
        # Add days to forecast
        for date, items in forecasts_by_day.items():
            forecast["days"].append({
                "date": date,
                "forecasts": items
            })
        
        return json.dumps(forecast, indent=2)
    
    except Exception as e:
        return f"Error fetching forecast data: {str(e)}"

@mcp.resource(
    uri="api://news/{topic}/{count}",
    name="News Articles",
    description="Get news articles by topic"
)
async def news_articles(topic, count="5"):
    """Get news articles by topic."""
    try:
        # Convert count to integer
        count_int = int(count)
        if count_int > 10:
            count_int = 10  # Limit to 10 articles
        
        # Connect to News API
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": topic,
            "apiKey": NEWS_API_KEY,
            "pageSize": count_int,
            "language": "en",
            "sortBy": "publishedAt"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
        
        # Format the response
        articles = []
        for article in data.get("articles", []):
            articles.append({
                "title": article.get("title", ""),
                "source": article.get("source", {}).get("name", ""),
                "author": article.get("author", ""),
                "published": article.get("publishedAt", ""),
                "url": article.get("url", ""),
                "description": article.get("description", "")
            })
        
        result = {
            "topic": topic,
            "count": len(articles),
            "articles": articles
        }
        
        return json.dumps(result, indent=2)
    
    except Exception as e:
        return f"Error fetching news data: {str(e)}"

@mcp.resource(
    uri="api://github/repos/{username}",
    name="GitHub Repositories",
    description="Get GitHub repositories for a user"
)
async def github_repos(username):
    """Get GitHub repositories for a specified user."""
    try:
        # Connect to GitHub API
        url = f"https://api.github.com/users/{username}/repos"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "MCP-Server-Example"
#Authentication:You would need to authenticate your request using an  access token if you are interacting with private repositories or exceeding rate limits. 
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()
            data = response.json()
        
        # Format the response
        repos = []
        for repo in data:
            repos.append({
                "name": repo.get("name", ""),
                "description": repo.get("description", ""),
                "url": repo.get("html_url", ""),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "language": repo.get("language", ""),
                "created_at": repo.get("created_at", ""),
                "updated_at": repo.get("updated_at", "")
            })
        
        result = {
            "username": username,
            "repository_count": len(repos),
            "repositories": repos
        }
        
        return json.dumps(result, indent=2)
    
    except Exception as e:
        return f"Error fetching GitHub data: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
