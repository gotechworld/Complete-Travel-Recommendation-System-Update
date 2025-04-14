# Complete-Travel-Recommendation-System

This application uses Google AI Agentic framework, LangChain, and Streamlit to create personalized travel recommendations based on user preferences.

## Features

- Personalized flight recommendations
- Hotel suggestions based on budget and preferences
- Activity recommendations for your destination
- AI-generated travel itineraries
- Budget optimization

</br>

### Installation
`pip install --no-cache-dir -r requirements.txt`

`streamlit run app.py`

Access the application at http://localhost:8501

</br>

### Containerize Streamlit app

+ Build the image:
`docker image build --no-cache -t travel-planner .`

+ Run the container:
`docker container run -d -p 8501:8501 -e GOOGLE_API_KEY="" -e SERPER_API_KEY="" -e  OPENWEATHER_API_KEY="" travel-planner`

</br>

__Note__: When running the container, you'll need to provide your Google Gemini API key, Serper API key, and OPENWEATHER API key as an environment variable.

### Agentic Workflow

The system implements an agentic workflow that processes user requests through multiple specialized components:

__Workflow steps__:

	"1. User submits travel preferences through the Streamlit interface",
    "2. TravelRequest object is created with destination, dates, budget, and preferences",
    "3. Flight recommendation agent queries for available flights matching criteria",
    "4. Hotel recommendation agent finds accommodations based on preferences",
    "5. Activity recommendation agent suggests things to do filtered by interests",
    "6. Weather forecast agent provides expected conditions during the trip",
    "7. Local tips agent offers cultural and practical advice for the destination",
    "8. LangChain integration generates a natural language travel plan",
    "9. All recommendations are presented to the user with interactive elements",
    "10. User can download a comprehensive PDF travel plan"

### LLM Integration

The system leverages Large Language Models through LangChain to generate natural language travel plans and recommendations:

	"1. Natural language processing of user preferences",
    "2. Generation of coherent travel narratives and itineraries",
    "3. Personalization of recommendations based on travel style",
    "4. Creation of day-by-day itineraries with logical flow",
    "5. Adaptation of suggestions based on weather conditions"


</br>

![image](https://github.com/gotechworld/Complete-Travel-Recommendation-System/blob/main/images/output.png)

</br>

![image](https://github.com/gotechworld/Complete-Travel-Recommendation-System/blob/main/images/output-final.png)

