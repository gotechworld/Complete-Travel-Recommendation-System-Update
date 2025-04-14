# langchain_integration.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_llm():
    """Initialize and return the LLM with proper error handling."""
    try:
        # Check if API key is available
        if not os.getenv("GOOGLE_API_KEY"):
            logger.warning("GOOGLE_API_KEY not found in environment variables")
            # Fallback message if API key is missing
            return None

        # Initialize the LLM
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.7,
            max_output_tokens=2048,
            top_p=0.95,
            top_k=40
        )
    except Exception as e:
        logger.error(f"Error initializing LLM: {str(e)}")
        return None

# Define a more detailed LangChain template for generating travel recommendations
template = """
You are an expert travel consultant with extensive knowledge of global destinations.
Create a personalized travel plan for a trip to {destination} during {dates} with a budget of ${budget}.

Please provide a comprehensive and well-structured itinerary including:

# DESTINATION OVERVIEW
- Brief introduction to {destination}
- Current weather and seasonal considerations for {dates}
- Local customs, etiquette, and language tips
- Currency and payment information

# DAILY ITINERARY
Create a day-by-day plan covering the entire duration of the trip ({dates}), including:
- Morning activities
- Afternoon explorations
- Evening entertainment
- Recommended dining options for each day

# PRACTICAL INFORMATION
## Transportation
- Best ways to get around {destination}
- Public transit options and approximate costs
- Recommended transportation apps

## Accommodation
- Neighborhoods that best match the traveler's budget
- Estimated nightly rates
- Special amenities to look for

## Budget Breakdown
- Approximate daily costs for food, activities, and transportation
- Suggested allocation of the ${budget} budget
- Money-saving tips specific to {destination}

## Must-See Attractions
- Top 5 attractions with estimated visit duration and costs
- Lesser-known local gems
- Recommended booking methods to avoid lines

## Culinary Experiences
- Local specialties and where to find them
- Price ranges for different dining options
- Food markets and culinary tours worth exploring

Format the itinerary in a clear, organized manner with appropriate headings and bullet points.
Make specific recommendations rather than generic advice.
"""

prompt = PromptTemplate(
    input_variables=["destination", "dates", "budget"],
    template=template,
)

def generate_travel_plan(destination, dates, budget):
    """Generate a travel plan using LangChain with error handling."""
    try:
        # Get LLM instance
        llm = get_llm()

        # If LLM initialization failed, return a fallback message
        if llm is None:
            return "Unable to generate travel plan at this time. Please try again later."

        # Create the chain
        travel_chain = LLMChain(
            llm=llm,
            prompt=prompt,
            verbose=False,  # Set to True for debugging
        )

        # Run the chain
        result = travel_chain.run(
            destination=destination,
            dates=dates,
            budget=budget
        )

        return result

    except Exception as e:
        logger.error(f"Error generating travel plan: {str(e)}")
        return f"Sorry, we encountered an issue while creating your travel plan. Please try again with different parameters or contact support if the problem persists."
