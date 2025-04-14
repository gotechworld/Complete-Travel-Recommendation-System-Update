from typing import Dict, List, Optional

class TravelRequest:
    def __init__(self, destination: str, dates: str, budget: float,
                 travel_style: str = "Balanced",
                 accommodation_type: str = "Hotel",
                 travelers: int = 2,
                 interests: Optional[List[str]] = None):
        self.destination = destination
        self.dates = dates
        self.budget = budget
        self.travel_style = travel_style
        self.accommodation_type = accommodation_type
        self.travelers = travelers
        self.interests = interests or []

class TravelRecommendation:
    def __init__(self, flights: List[Dict], hotels: List[Dict], activities: List[Dict], travel_plan: str = ""):
        self.flights = flights
        self.hotels = hotels
        self.activities = activities
        self.travel_plan = travel_plan

    def get_total_cost(self) -> float:
        """Calculate the estimated total cost of the trip."""
        flight_cost = sum(flight["price"] for flight in self.flights[:1]) * 2  # Round trip for first option
        hotel_cost = sum(hotel["price"] for hotel in self.hotels[:1]) * 5  # 5 nights at first hotel
        activity_cost = sum(activity["price"] for activity in self.activities[:3])  # Top 3 activities
        return flight_cost + hotel_cost + activity_cost
