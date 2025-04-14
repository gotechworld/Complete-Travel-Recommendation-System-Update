from typing import List, Dict
from .interface import TravelRequest, TravelRecommendation
import random

def get_flights(request: TravelRequest) -> List[Dict]:
    """Retrieve flight options based on the travel request."""
    # Simulate retrieving flight information from an API
    destination = request.destination.lower()

    # Base flights data
    flights = [
        {"airline": "Air France", "departure": "08:00", "arrival": "10:00", "price": 300.0},
        {"airline": "Lufthansa", "departure": "10:30", "arrival": "12:30", "price": 350.0},
        {"airline": "British Airways", "departure": "14:00", "arrival": "16:00", "price": 380.0},
        {"airline": "KLM", "departure": "16:30", "arrival": "18:30", "price": 320.0},
        {"airline": "Tarom", "departure": "12:00", "arrival": "14:00", "price": 500.0},
    ]

    # Adjust prices based on travel style
    if request.travel_style == "Luxury":
        for flight in flights:
            flight["price"] *= 1.5
            flight["class"] = "Business"
    elif request.travel_style == "Budget":
        for flight in flights:
            flight["price"] *= 0.8
            flight["class"] = "Economy"

    # Filter flights based on budget
    return [flight for flight in flights if flight["price"] <= request.budget]

def get_hotels(request: TravelRequest) -> List[Dict]:
    """Retrieve hotel options based on the travel request."""
    # Simulate retrieving hotel information from an API
    destination = request.destination.lower()

    # Base hotels data
    hotels = [
        {"name": "Zoku Paris", "rating": 8.9, "price": 250.0, "type": "Hotel"},
        {"name": "Villa M", "rating": 8.8, "price": 450.0, "type": "Boutique"},
        {"name": "Citizen M", "rating": 8.7, "price": 200.0, "type": "Hotel"},
        {"name": "Generator Paris", "rating": 8.2, "price": 120.0, "type": "Hostel"},
        {"name": "Le Bristol Paris", "rating": 9.5, "price": 950.0, "type": "Luxury"},
        {"name": "Airbnb in Le Marais", "rating": 8.6, "price": 180.0, "type": "Apartment"},
    ]

    # Adjust based on accommodation preference
    preferred_hotels = [hotel for hotel in hotels if hotel["type"].lower() == request.accommodation_type.lower()]
    if not preferred_hotels:
        preferred_hotels = hotels

    # Adjust prices based on number of travelers
    for hotel in preferred_hotels:
        if request.travelers > 2:
            hotel["price"] *= (1 + (request.travelers - 2) * 0.25)  # 25% increase per additional traveler

    # Filter hotels based on budget (per night)
    return [hotel for hotel in preferred_hotels if hotel["price"] <= request.budget / 5]  # Assuming 5-night stay

def get_activities(request: TravelRequest) -> List[Dict]:
    """Retrieve activity options based on the travel request."""
    # Simulate retrieving activity information from an API
    destination = request.destination.lower()

    # Base activities data for Paris
    activities = [
        {"name": "Louvre Museum", "duration": "3 hours", "price": 17.0, "category": "Art"},
        {"name": "Eiffel Tower", "duration": "2 hours", "price": 26.8, "category": "Sightseeing"},
        {"name": "Seine River Cruise", "duration": "1 hour", "price": 15.0, "category": "Relaxation"},
        {"name": "Montmartre Walking Tour", "duration": "2 hours", "price": 25.0, "category": "History"},
        {"name": "Cooking Class", "duration": "3 hours", "price": 95.0, "category": "Food"},
        {"name": "Wine Tasting", "duration": "2 hours", "price": 65.0, "category": "Food"},
        {"name": "Versailles Palace", "duration": "4 hours", "price": 18.0, "category": "History"},
        {"name": "Moulin Rouge Show", "duration": "2 hours", "price": 115.0, "category": "Nightlife"},
        {"name": "Bike Tour", "duration": "3 hours", "price": 35.0, "category": "Sports"},
        {"name": "Admission to Disneyland Paris", "duration": "Full day", "price": 100.0, "category": "Entertainment"},
        {"name": "Sightseeing Cruise from the Eiffel Tower", "duration": "1 hour", "price": 75.0, "category": "Sightseeing"},
    ]

    # Filter based on interests if provided
    if request.interests:
        interest_categories = {
            "History": ["History"],
            "Food": ["Food"],
            "Nature": ["Relaxation", "Sports"],
            "Shopping": ["Shopping"],
            "Art": ["Art"],
            "Nightlife": ["Nightlife"],
            "Sports": ["Sports"]
        }

        relevant_categories = []
        for interest in request.interests:
            if interest in interest_categories:
                relevant_categories.extend(interest_categories[interest])

        if relevant_categories:
            filtered_activities = [activity for activity in activities
                                  if activity["category"] in relevant_categories]
            if filtered_activities:
                activities = filtered_activities

    # Adjust prices based on travel style
    if request.travel_style == "Luxury":
        for activity in activities:
            activity["price"] *= 1.3
            activity["type"] = "Private"
    elif request.travel_style == "Budget":
        for activity in activities:
            activity["price"] *= 0.9
            activity["type"] = "Group"

    # Filter activities based on budget
    return [activity for activity in activities if activity["price"] <= request.budget / 10]  # Assuming ~10 activities

def generate_weather_forecast(dates: str) -> List[Dict]:
    """Generate a weather forecast for the given dates."""
    if "may" in dates.lower():
        # Paris in May weather data (historical averages)
        weather_icons = ["🌤️", "🌦️", "☀️", "🌤️", "☀️"]
        temperatures = ["19°C/10°C", "18°C/11°C", "21°C/12°C", "20°C/11°C", "22°C/13°C"]
        conditions = ["Partly Cloudy", "Light Showers", "Sunny", "Partly Cloudy", "Sunny"]
        precipitation = ["10%", "30%", "5%", "15%", "5%"]

        # Extract the date range
        date_parts = dates.split("-")
        if len(date_parts) >= 2:
            try:
                start_day = int(date_parts[0].split(" ")[-1])
                end_day = int(date_parts[1].split(" ")[0])
                month = date_parts[0].split(" ")[0]
                year = date_parts[1].split(" ")[-1]

                # Create a row for each day in the range
                weather_data = []
                for i, day in enumerate(range(start_day, end_day + 1)):
                    if i < len(weather_icons):
                        weather_data.append({
                            "date": f"{month} {day}, {year}",
                            "icon": weather_icons[i],
                            "temp": temperatures[i],
                            "condition": conditions[i],
                            "precipitation": precipitation[i]
                        })
                return weather_data
            except (ValueError, IndexError):
                pass

    # Fallback weather data
    return [
        {"date": "Day 1", "icon": "🌤️", "temp": "19°C/10°C", "condition": "Partly Cloudy", "precipitation": "10%"},
        {"date": "Day 2", "icon": "🌦️", "temp": "18°C/11°C", "condition": "Light Showers", "precipitation": "30%"},
        {"date": "Day 3", "icon": "☀️", "temp": "21°C/12°C", "condition": "Sunny", "precipitation": "5%"},
        {"date": "Day 4", "icon": "🌤️", "temp": "20°C/11°C", "condition": "Partly Cloudy", "precipitation": "15%"},
        {"date": "Day 5", "icon": "☀️", "temp": "22°C/13°C", "condition": "Sunny", "precipitation": "5%"}
    ]

def get_local_tips(destination: str) -> Dict[str, List[str]]:
    """Get local tips for the specified destination."""
    tips = {
        "dining": [],
        "money_saving": [],
        "transportation": [],
        "language": [],
        "safety": []
    }

    if destination.lower() == "paris":
        tips["dining"] = [
            "Ask for 'une carafe d'eau' for free tap water",
            "Cafés open early (7-8am), lunch is 12-2pm, dinner starts at 7:30pm",
            "Always greet with 'Bonjour' when entering shops",
            "Try croissants from award-winning bakeries like Du Pain et des Idées",
            "Service is included in the bill ('service compris')"
        ]

        tips["money_saving"] = [
            "Museums are free on first Sunday of each month",
            "Buy a carnet of 10 metro tickets (cheaper than singles)",
            "Eat main meal at lunch with 'formule' menu",
            "Picnic in parks with baguettes, cheese, and wine",
            "Use Vélib' bike sharing for short trips"
        ]

        tips["transportation"] = [
            "Metro runs 5:30am-1:15am (2:15am weekends)",
            "RER B train connects CDG airport to central Paris (€11.40)",
            "Keep ticket until you exit (inspections occur)",
            "Visit Louvre on Wednesday/Friday evenings to avoid crowds",
            "Book tickets online to skip lines at major attractions"
        ]

        tips["language"] = [
            "Bonjour (bon-zhoor) - Hello",
            "Merci (mehr-see) - Thank you",
            "S'il vous plaît (seel voo pleh) - Please",
            "Excusez-moi (ex-koo-zay mwah) - Excuse me",
            "L'addition, s'il vous plaît (lah-dee-see-ohn seel voo pleh) - The bill, please"
        ]

        tips["safety"] = [
            "Be vigilant on metro line 1 and at tourist spots",
            "Avoid petition signers (common scam)",
            "Keep bags zipped and in front of you",
            "Emergency number: 112",
            "Drinking water from Wallace fountains is safe"
        ]

    return tips

def travel_recommendation(request: TravelRequest) -> TravelRecommendation:
    """Generate a complete travel recommendation based on the request."""
    flights = get_flights(request)
    hotels = get_hotels(request)
    activities = get_activities(request)

    # In a real implementation, this would call an LLM to generate the travel plan
    travel_plan = f"Your personalized travel plan for {request.destination} would be generated here."

    return TravelRecommendation(flights, hotels, activities, travel_plan)

def enrich_travel_recommendation(recommendation: TravelRecommendation, destination: str) -> TravelRecommendation:
    """Enrich travel recommendation with data from search API."""
    from search_api import get_destination_attractions

    # Get attractions from search API
    api_attractions = get_destination_attractions(destination)

    # Convert to the format used in the app
    for api_attraction in api_attractions:
        # Create a new activity from the API data
        new_activity = {
            "name": api_attraction["name"],
            "duration": "2 hours",  # Default duration
            "price": 0.0,  # Price unknown from API
            "category": "Sightseeing",
            "rating": api_attraction["rating"],
            "description": api_attraction["description"]
        }

        # Add to activities if not already present
        if not any(activity["name"] == new_activity["name"] for activity in recommendation.activities):
            recommendation.activities.append(new_activity)

    return recommendation