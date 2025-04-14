# search_api.py
import requests
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def search_destination_info(destination, query_type="search"):
    """
    Search for destination information using Serper.dev Google Search API

    Args:
        destination (str): The destination to search for
        query_type (str): Type of search - "search", "images", "places", or "news"

    Returns:
        dict: Search results or error message
    """
    try:
        # Check if API key is available
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            logger.warning("SERPER_API_KEY not found in environment variables")
            return {"error": "API key not configured"}

        # API endpoint
        url = "https://google.serper.dev/search"
        if query_type in ["images", "places", "news"]:
            url = f"https://google.serper.dev/{query_type}"

        # Request headers
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }

        # Request payload
        payload = {
            'q': f"{destination} travel guide",
            'gl': 'us',  # Geolocation (US results)
            'hl': 'en'   # Language (English)
        }

        # Make the API request
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for HTTP errors

        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error(f"API request error: {str(e)}")
        return {"error": f"Failed to fetch data: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"error": f"An unexpected error occurred: {str(e)}"}

def get_destination_images(destination, num_images=4, category=None, time_filter=None):
    """
    Get images for a destination with optional filtering

    Args:
        destination (str): The destination to search for
        num_images (int): Number of images to return
        category (str, optional): Category of images to filter by
        time_filter (str, optional): Time period to filter images by

    Returns:
        list: List of image dictionaries
    """
    # Modify the search query based on category and time filter
    search_query = f"{destination}"

    if category and category != "All":
        search_query += f" {category}"

    # Add time period to search query if specified
    if time_filter:
        if "Latest" in time_filter:
            search_query += " 2025 recent"
        elif "Recent" in time_filter:
            search_query += " recent"
        elif "Classic" in time_filter:
            search_query += " iconic historical"

    # Call the API with the enhanced query
    results = search_destination_info(search_query, query_type="images")

    if "error" in results:
        # Provide fallback images for Paris if the API fails
        if destination.lower() == "paris":
            return [
                {"url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34", "title": "Eiffel Tower", "source": "Unsplash", "photographer": "Chris Karidis", "date": "2025"},
                {"url": "https://images.unsplash.com/photo-1499856871958-5b9627545d1a", "title": "Seine River", "source": "Unsplash", "photographer": "Léonard Cotte", "date": "2024"},
                {"url": "https://images.unsplash.com/photo-1520939817895-060bdaf4fe1b", "title": "Arc de Triomphe", "source": "Unsplash", "photographer": "Anthony DELANOIX", "date": "2025"},
                {"url": "https://images.unsplash.com/photo-1550340499-a6c60fc8287c", "title": "Montmartre", "source": "Unsplash", "photographer": "Léonard Cotte", "date": "2024"}
            ]
        return []

    images = []
    try:
        for item in results.get("images", [])[:num_images]:
            # Extract additional metadata if available
            image_data = {
                "url": item.get("imageUrl"),
                "title": item.get("title", f"Beautiful {destination}"),
                "source": item.get("source", "Web"),
                "date": item.get("date", "2025"),  # Default to current year if not available
                "photographer": item.get("source", "Unknown"),
                "description": f"Stunning view of {item.get('title', destination)}",
                "tags": f"{destination} {category if category else ''} travel tourism"
            }

            # Add category-specific facts for Paris
            if destination.lower() == "paris":
                if "eiffel" in image_data["title"].lower():
                    image_data["fact1"] = "The Eiffel Tower was built for the 1889 World's Fair"
                    image_data["fact2"] = "It was initially criticized by many Parisians"
                    image_data["fact3"] = "The tower is repainted every 7 years"
                elif "louvre" in image_data["title"].lower():
                    image_data["fact1"] = "The Louvre was originally built as a fortress in 1190"
                    image_data["fact2"] = "It's the world's largest art museum"
                    image_data["fact3"] = "The Mona Lisa is viewed by 6 million people annually"
                elif "seine" in image_data["title"].lower():
                    image_data["fact1"] = "The Seine River is 777 km long"
                    image_data["fact2"] = "There are 37 bridges over the Seine in Paris"
                    image_data["fact3"] = "The river has been a UNESCO World Heritage Site since 1991"
                else:
                    image_data["fact1"] = "Paris has 20 administrative districts called arrondissements"
                    image_data["fact2"] = "The city is known as the 'City of Light'"
                    image_data["fact3"] = "Paris hosts over 40 million tourists annually"

            images.append(image_data)

        # If we have a category filter, do additional filtering on the results
        if category and category != "All":
            filtered_images = [img for img in images if category.lower() in img["title"].lower() or
                              category.lower() in img["tags"].lower()]
            if filtered_images:
                return filtered_images

        return images
    except Exception as e:
        logger.error(f"Error processing image results: {str(e)}")
        return []

def get_destination_attractions(destination):
    """Get top attractions for a destination"""
    results = search_destination_info(destination, query_type="places")

    if "error" in results:
        return []

    attractions = []
    try:
        for place in results.get("places", [])[:5]:
            attractions.append({
                "name": place.get("title", ""),
                "rating": place.get("rating", "N/A"),
                "reviews": place.get("reviewsCount", "N/A"),
                "address": place.get("address", ""),
                "description": place.get("description", "")
            })
        return attractions
    except Exception as e:
        logger.error(f"Error processing places results: {str(e)}")
        return []

def get_destination_news(destination):
    """Get latest news about a destination"""
    results = search_destination_info(destination, query_type="news")

    if "error" in results:
        return []

    news = []
    try:
        for item in results.get("news", [])[:3]:
            news.append({
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "date": item.get("date", ""),
                "source": item.get("source", "")
            })
        return news
    except Exception as e:
        logger.error(f"Error processing news results: {str(e)}")
        return []