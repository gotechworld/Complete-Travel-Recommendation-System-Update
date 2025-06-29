import streamlit as st
import io
import os
import re
import datetime
from agentic.interface import TravelRequest
from agentic.workflow import get_flights, get_hotels, get_activities
from langchain_integration import generate_travel_plan
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from search_api import (
    get_destination_images,
    get_destination_attractions,
    get_destination_news
)

def create_pdf(content, destination, dates, budget, hotels, flights, activities):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)

    # Create styles
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        name='CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=24
    )

    heading1_style = ParagraphStyle(
        name='Heading1',
        parent=styles['Heading1'],
        fontSize=18,
        spaceBefore=16,
        spaceAfter=10,
        textColor=colors.darkblue
    )

    heading2_style = ParagraphStyle(
        name='Heading2',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=12,
        spaceAfter=8,
        textColor=colors.navy
    )

    heading3_style = ParagraphStyle(
        name='Heading3',
        parent=styles['Heading3'],
        fontSize=12,
        spaceBefore=10,
        spaceAfter=6,
        textColor=colors.darkblue
    )

    normal_style = ParagraphStyle(
        name='CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceBefore=4,
        spaceAfter=4,
        alignment=TA_JUSTIFY
    )

    bullet_style = ParagraphStyle(
        name='CustomBullet',
        parent=styles['Normal'],
        fontSize=10,
        spaceBefore=2,
        spaceAfter=2,
        leftIndent=20,
        bulletIndent=10
    )

    italic_style = ParagraphStyle(
        name='CustomItalic',
        parent=styles['Italic'],
        fontSize=10,
        alignment=TA_CENTER
    )

    footer_style = ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.darkblue,
        alignment=TA_CENTER
    )

    # Build document
    elements = []

    # Logo and header
    # Check if logo exists, if not, create a text-based header
    logo_path = 'smart-travel.png'  # Update with the actual path to your logo
    if os.path.exists(logo_path):
        # Add logo with proper sizing
        elements.append(Image(logo_path, width=2*inch, height=0.75*inch))
    else:
        # Text-based logo as fallback
        elements.append(Paragraph("<b>SMART TRAVEL</b>",
                                 ParagraphStyle(name='LogoText',
                                              parent=styles['Title'],
                                              fontSize=20,
                                              alignment=TA_CENTER,
                                              textColor=colors.darkblue)))

    elements.append(Spacer(1, 0.25*inch))

    # Title
    elements.append(Paragraph(f"Travel Itinerary", title_style))
    elements.append(Spacer(1, 0.25*inch))

    # Add current date and time
    current_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    datetime_style = ParagraphStyle(
    name='DateTime',
    parent=styles['Normal'],
    fontSize=9,
    textColor=colors.darkblue,
    alignment=TA_RIGHT
    )
    elements.append(Paragraph(f"Generated on: {current_datetime}", datetime_style))
    elements.append(Spacer(1, 0.1*inch))

    # Trip summary table with better styling
    trip_info = [
        ['Destination:', destination],
        ['Travel Dates:', dates],
        ['Budget:', f"${budget}"]
    ]

    trip_table = Table(trip_info, colWidths=[1.5*inch, 4*inch])
    trip_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightsteelblue),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.darkblue),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]))
    elements.append(trip_table)
    elements.append(Spacer(1, 0.5*inch))

    # Process the travel plan content to properly format sections
    # This is the key improvement - parsing the content to create proper sections

    # First, let's clean up the content by ensuring proper line breaks
    content = content.replace('# ', '\n# ').replace('## ', '\n## ').replace('* ', '\n* ')

    # Split the content by sections
    sections = re.split(r'(# [^\n]+)', content)

    if len(sections) > 1:  # If we have proper sections
        # The first element might be empty or introductory text
        if sections[0].strip():
            elements.append(Paragraph(sections[0].strip(), normal_style))
            elements.append(Spacer(1, 0.2*inch))

        # Process each section
        for i in range(1, len(sections), 2):
            if i < len(sections):
                # Section title
                section_title = sections[i].replace('# ', '').strip()
                elements.append(Paragraph(section_title, heading1_style))

                # Section content
                if i+1 < len(sections):
                    section_content = sections[i+1]

                    # Process subsections
                    subsections = re.split(r'(## [^\n]+)', section_content)

                    if len(subsections) > 1:  # If we have subsections
                        # The first element might be content before any subsection
                        if subsections[0].strip():
                            # Process bullet points
                            bullets = subsections[0].split('\n* ')
                            if len(bullets) > 1:
                                elements.append(Paragraph(bullets[0].strip(), normal_style))
                                for bullet in bullets[1:]:
                                    if bullet.strip():
                                        elements.append(Paragraph(f"• {bullet.strip()}", bullet_style))
                            else:
                                elements.append(Paragraph(subsections[0].strip(), normal_style))

                        # Process each subsection
                        for j in range(1, len(subsections), 2):
                            if j < len(subsections):
                                # Subsection title
                                subsection_title = subsections[j].replace('## ', '').strip()
                                elements.append(Paragraph(subsection_title, heading2_style))

                                # Subsection content
                                if j+1 < len(subsections):
                                    # Process bullet points
                                    bullets = subsections[j+1].split('\n* ')
                                    if len(bullets) > 1:
                                        elements.append(Paragraph(bullets[0].strip(), normal_style))
                                        for bullet in bullets[1:]:
                                            if bullet.strip():
                                                elements.append(Paragraph(f"• {bullet.strip()}", bullet_style))
                                    else:
                                        elements.append(Paragraph(subsections[j+1].strip(), normal_style))
                    else:
                        # No subsections, just process the content
                        # Process bullet points
                        bullets = section_content.split('\n* ')
                        if len(bullets) > 1:
                            elements.append(Paragraph(bullets[0].strip(), normal_style))
                            for bullet in bullets[1:]:
                                if bullet.strip():
                                    elements.append(Paragraph(f"• {bullet.strip()}", bullet_style))
                        else:
                            elements.append(Paragraph(section_content.strip(), normal_style))
    else:
        # No sections found, just add the content as is
        elements.append(Paragraph(content, normal_style))

    # Add a page break before recommendations
    elements.append(PageBreak())

    # Flight information with improved styling
    elements.append(Paragraph("Flight Options", heading1_style))
    elements.append(Spacer(1, 0.1*inch))

    flight_data = [['Airline', 'Price', 'Departure', 'Arrival']]
    for flight in flights[:3]:  # Show top 3 flights
        flight_data.append([
            flight['airline'],
            f"${flight['price']}",
            flight['departure'],
            flight['arrival']
        ])

    flight_table = Table(flight_data, colWidths=[1.25*inch, 1*inch, 1.5*inch, 1.5*inch])
    flight_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    elements.append(flight_table)
    elements.append(Spacer(1, 0.3*inch))

    # Hotel information with improved styling
    elements.append(Paragraph("Accommodation Options", heading1_style))
    elements.append(Spacer(1, 0.1*inch))

    hotel_data = [['Hotel', 'Price per Night', 'Rating']]
    for hotel in hotels[:3]:  # Show top 3 hotels
        hotel_data.append([
            hotel['name'],
            f"${hotel['price']}",
            f"{hotel['rating']}⭐"
        ])

    hotel_table = Table(hotel_data, colWidths=[2.5*inch, 1.5*inch, 1*inch])
    hotel_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    elements.append(hotel_table)
    elements.append(Spacer(1, 0.3*inch))

    # Activities with improved styling
    elements.append(Paragraph("Recommended Activities", heading1_style))
    elements.append(Spacer(1, 0.1*inch))

    activity_data = [['Activity', 'Price', 'Duration']]
    for activity in activities[:5]:  # Show top 5 activities
        activity_data.append([
            activity['name'],
            f"${activity['price']}",
            activity['duration']
        ])

    activity_table = Table(activity_data, colWidths=[3*inch, 1*inch, 1*inch])
    activity_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    elements.append(activity_table)
    elements.append(Spacer(1, 0.5*inch))

    # Enhanced footer with contact information
    elements.append(Paragraph("Thank you for using our Smart Travel Planner!", italic_style))
    elements.append(Spacer(1, 0.1*inch))

    # Contact information in footer
    elements.append(Paragraph(
        f"Contact us: <b>Email:</b> petru.giurca@pm.me | <b>Phone:</b> +40 754215612",
        footer_style
    ))

    # Build PDF with custom page template for header/footer
    class FooterCanvas:
        def __init__(self, canvas, doc):
            self.canvas = canvas
            self.doc = doc
            self.width = letter[0]
            self.height = letter[1]

        def __call__(self, canvas, doc):
            # Save state
            canvas.saveState()

            # Add a horizontal line above footer
            canvas.setStrokeColor(colors.lightgrey)
            canvas.setLineWidth(0.5)
            canvas.line(72, 60, self.width - 72, 60)

            # Add footer text
            canvas.setFont('Helvetica', 8)
            canvas.setFillColor(colors.darkblue)

            # Company name and copyright
            canvas.drawCentredString(self.width/2, 45, "Smart Travel - Your Journey, Our Expertise")
            canvas.drawCentredString(self.width/2, 30, "Email: petru.giurca@pm.me | Phone: +40 754215612")

            # Add page number
            page_num = canvas.getPageNumber()
            canvas.drawRightString(self.width - 72, 30, f"Page {page_num}")

            # Restore state
            canvas.restoreState()

    # Build PDF with custom footer
    doc.build(elements, onFirstPage=FooterCanvas(None, None), onLaterPages=FooterCanvas(None, None))
    buffer.seek(0)
    return buffer

def main():
    st.set_page_config(page_title="Travel Recommendation System", layout="wide")

    st.title("✈️ 🌍 🧳 Smart Travel Planner")
    st.write("Let our AI-powered system create your perfect vacation itinerary!")

    st.markdown("---")
    st.subheader("📝 Tell us about your dream trip")

    # User input with more context
    col1, col2, col3 = st.columns(3)
    with col1:
        destination = st.text_input("🏙️ Destination", "Paris")
        st.caption("Enter city, country, or region")
    with col2:
        dates = st.text_input("📅 Travel Dates", "August 5-9, 2025")
        st.caption("Format: Month Day-Day, Year")
    with col3:
        budget = st.number_input("💰 Budget ($)", min_value=100, value=5000, step=100)
        st.caption("Total budget for your trip")

    # Additional preferences
    st.subheader("🔍 Refine your preferences (optional)")
    col1, col2 = st.columns(2)
    with col1:
        travel_style = st.selectbox("🧭 Travel Style",
                                   ["Balanced", "Luxury", "Budget", "Adventure", "Cultural", "Relaxation"])
        accommodation_type = st.selectbox("🏠 Accommodation Preference",
                                        ["Hotel", "Resort", "Apartment", "Hostel", "Boutique"])
    with col2:
        travelers = st.number_input("👨‍👩‍👧‍👦 Number of Travelers", min_value=1, value=10)
        interests = st.multiselect("🎯 Interests",
                                  ["History", "Food", "Nature", "Shopping", "Art", "Nightlife", "Sports"])

    if st.button("🚀 Generate My Travel Plan"):
        with st.spinner("✨ Creating your personalized travel experience..."):
            # Create a travel request
            request = TravelRequest(destination, dates, budget)

            # Get recommendations using the agentic workflow
            flights = get_flights(request)
            hotels = get_hotels(request)
            activities = get_activities(request)

            # Generate a travel plan using LangChain
            travel_plan = generate_travel_plan(destination, dates, budget)

            st.success("🎉 Your travel plan is ready!")
            st.markdown("---")

            # Display recommendations with enhanced visuals
            st.subheader("✈️ Flight Options")
            st.caption("Best flight options based on price and convenience")
            for flight in flights:
                st.write(f"**{flight['airline']}**: ${flight['price']} "
                         f"(🛫 Departure: {flight['departure']}, 🛬 Arrival: {flight['arrival']})")

            st.markdown("---")
            st.subheader("🏨 Accommodation Options")
            st.caption("Places to stay that match your preferences")
            for hotel in hotels:
                st.write(f"**{hotel['name']}**: 💵 ${hotel['price']} per night (⭐ Rating: {hotel['rating']}/5)")

            st.markdown("---")
            st.subheader("🎭 Recommended Activities")
            st.caption("Exciting things to do at your destination")
            for activity in activities:
                st.write(f"**{activity['name']}**: 💵 ${activity['price']} (⏱️ {activity['duration']})")

            st.markdown("---")
            st.subheader("📋 Your Personalized Itinerary")
            st.info("🤖 AI-Generated Travel Plan")
            st.write(travel_plan)

            # Weather forecast
            st.markdown("---")
            st.subheader("☀️ Weather Forecast")
            st.caption(f"Expected weather in {destination} during your stay ({dates})")

            # Import required libraries for weather API
            import requests
            from datetime import datetime, timedelta
            import time
            import pandas as pd
            import re
            import os
            from dotenv import load_dotenv

            # Load environment variables
            load_dotenv()

            def get_weather_forecast_openweathermap(city, start_date, end_date):
                """
                Get weather forecast for a city between two dates using OpenWeatherMap API

                Args:
                    city (str): City name
                    start_date (datetime): Start date
                    end_date (datetime): End date

                Returns:
                    list: Weather forecast data for each day
                """
                try:
                    # Get API key from environment variables or use a default one
                    api_key = os.getenv("OPENWEATHER_API_KEY")

                    if not api_key:
                        st.warning("OpenWeatherMap API key not found. Using historical averages instead.")
                        return None

                    # Get coordinates for the city using OpenWeatherMap Geocoding API
                    geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
                    geo_response = requests.get(geocoding_url)
                    geo_data = geo_response.json()

                    if not geo_data:
                        st.warning(f"Could not find coordinates for {city}. Using historical averages instead.")
                        return None

                    lat = geo_data[0]['lat']
                    lon = geo_data[0]['lon']

                    # Get 5-day forecast using OpenWeatherMap 5 day / 3 hour forecast API
                    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={api_key}"
                    forecast_response = requests.get(forecast_url)
                    forecast_data = forecast_response.json()

                    if forecast_data.get('cod') != '200':
                        st.warning(f"Error fetching weather data: {forecast_data.get('message')}. Using historical averages instead.")
                        return None

                    # Process forecast data
                    weather_data = []
                    forecast_list = forecast_data['list']

                    # Group forecasts by day
                    daily_forecasts = {}

                    for forecast in forecast_list:
                        timestamp = forecast['dt']
                        date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

                        if date not in daily_forecasts:
                            daily_forecasts[date] = []

                        daily_forecasts[date].append(forecast)

                    # Calculate daily averages and get conditions
                    for date, forecasts in daily_forecasts.items():
                        date_obj = datetime.strptime(date, '%Y-%m-%d')

                        # Skip if outside our date range
                        if date_obj < start_date or date_obj > end_date:
                            continue

                        # Calculate average temperatures
                        temps = [f['main']['temp'] for f in forecasts]
                        max_temp = max([f['main']['temp_max'] for f in forecasts])
                        min_temp = min([f['main']['temp_min'] for f in forecasts])

                        # Get most common weather condition
                        conditions = [f['weather'][0]['main'] for f in forecasts]
                        condition = max(set(conditions), key=conditions.count)

                        # Get description and icon for the most common condition
                        descriptions = [f['weather'][0]['description'] for f in forecasts if f['weather'][0]['main'] == condition]
                        description = max(set(descriptions), key=descriptions.count)

                        icons = [f['weather'][0]['icon'] for f in forecasts if f['weather'][0]['description'] == description]
                        icon_code = icons[0] if icons else "01d"

                        # Map OpenWeatherMap icon codes to emoji
                        icon_map = {
                            "01d": "☀️", "01n": "🌙",  # clear sky
                            "02d": "⛅", "02n": "⛅",  # few clouds
                            "03d": "☁️", "03n": "☁️",  # scattered clouds
                            "04d": "☁️", "04n": "☁️",  # broken clouds
                            "09d": "🌧️", "09n": "🌧️",  # shower rain
                            "10d": "🌦️", "10n": "🌦️",  # rain
                            "11d": "⛈️", "11n": "⛈️",  # thunderstorm
                            "13d": "❄️", "13n": "❄️",  # snow
                            "50d": "🌫️", "50n": "🌫️"   # mist
                        }

                        emoji = icon_map.get(icon_code, "🌤️")

                        # Calculate precipitation probability and amount
                        precipitation_prob = max([f.get('pop', 0) for f in forecasts]) * 100

                        # Calculate precipitation amount (rain or snow)
                        precipitation_amount = 0
                        for f in forecasts:
                            if 'rain' in f and '3h' in f['rain']:
                                precipitation_amount += f['rain']['3h']
                            elif 'snow' in f and '3h' in f['snow']:
                                precipitation_amount += f['snow']['3h']

                        # Calculate average humidity and wind speed
                        avg_humidity = sum([f['main']['humidity'] for f in forecasts]) / len(forecasts)
                        avg_wind = sum([f['wind']['speed'] for f in forecasts]) / len(forecasts)

                        # Calculate feels like temperature
                        avg_feels_like = sum([f['main']['feels_like'] for f in forecasts]) / len(forecasts)

                        # Calculate sunrise and sunset (use city data)
                        if 'city' in forecast_data and 'sunrise' in forecast_data['city'] and 'sunset' in forecast_data['city']:
                            sunrise = datetime.fromtimestamp(forecast_data['city']['sunrise'])
                            sunset = datetime.fromtimestamp(forecast_data['city']['sunset'])
                            day_length = (sunset - sunrise).total_seconds() / 3600
                        else:
                            day_length = 12  # Default day length

                        weather_data.append({
                            "date": date_obj.strftime("%b %d, %Y"),
                            "icon": emoji,
                            "temp": f"{max_temp:.1f}°C/{min_temp:.1f}°C",
                            "condition": description.title(),
                            "precipitation": f"{precipitation_prob:.0f}%",
                            "precipitation_mm": f"{precipitation_amount:.1f} mm",
                            "humidity": f"{avg_humidity:.0f}%",
                            "wind": f"{avg_wind:.1f} m/s",
                            "feels_like": f"{avg_feels_like:.1f}°C",
                            "day_length": f"{day_length:.1f} hours",
                            "api_source": "OpenWeatherMap"
                        })

                    return weather_data

                except Exception as e:
                    st.warning(f"Error fetching weather data: {str(e)}. Using historical averages instead.")
                    return None

            # Function to parse travel dates with better error handling
            def parse_travel_dates(date_string):
                """
                Parse travel dates from various formats with robust error handling

                Args:
                    date_string (str): Date string in format like "August 5-9, 2025"

                Returns:
                    tuple: (start_date, end_date, month_num) or None if parsing fails
                """
                try:
                    # Define month mappings
                    months = {
                        "january": 1, "february": 2, "march": 3, "april": 4, "August": 5, "june": 6,
                        "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
                        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "August": 5, "jun": 6,
                        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
                    }

                    # Try to extract month, day range, and year using regex
                    pattern = r"([a-zA-Z]+)\s+(\d+)[-–—](\d+),?\s+(\d{4})"
                    match = re.search(pattern, date_string)

                    if match:
                        month_name, start_day, end_day, year = match.groups()
                        month_num = months.get(month_name.lower(), 5)  # Default to August if not found

                        start_date = datetime(int(year), month_num, int(start_day))
                        end_date = datetime(int(year), month_num, int(end_day))

                        return start_date, end_date, month_num

                    # Try alternative format: "Month Year" (e.g., "August 2025")
                    alt_pattern = r"([a-zA-Z]+)\s+(\d{4})"
                    alt_match = re.search(alt_pattern, date_string)

                    if alt_match:
                        month_name, year = alt_match.groups()
                        month_num = months.get(month_name.lower(), 5)

                        # Use current day as start, and 5 days later as end
                        today = datetime.now().day
                        start_date = datetime(int(year), month_num, min(today, 28))
                        end_date = datetime(int(year), month_num, min(today + 4, 28))

                        return start_date, end_date, month_num

                    # If all parsing fails, use current month and year with generic days
                    current_date = datetime.now()
                    start_date = datetime(current_date.year, current_date.month, 1)
                    end_date = datetime(current_date.year, current_date.month, 5)
                    month_num = current_date.month

                    return start_date, end_date, month_num

                except Exception as e:
                    st.warning(f"Date parsing error: {str(e)}. Using current date range.")
                    # Fallback to current date
                    current_date = datetime.now()
                    return (
                        current_date,
                        current_date + timedelta(days=4),
                        current_date.month
                    )

            # Get historical weather data for a destination and month
            def get_historical_weather(destination, month_num):
                """
                Get historical weather data for a destination and month

                Args:
                    destination (str): Destination name
                    month_num (int): Month number (1-12)

                Returns:
                    dict: Weather data for the destination and month
                """
                # Default weather data
                default_data = {
                    "icons": ["🌤️", "🌦️", "☀️", "🌤️", "☀️"],
                    "temperatures": ["22°C/15°C", "21°C/14°C", "24°C/16°C", "23°C/15°C", "25°C/17°C"],
                    "conditions": ["Partly Cloudy", "Light Showers", "Sunny", "Partly Cloudy", "Sunny"],
                    "precipitation": ["15%", "35%", "5%", "20%", "5%"]
                }

                # Paris weather data by season
                if destination.lower() == "paris":
                    if month_num == 5:  # August
                        return {
                            "icons": ["🌤️", "🌦️", "☀️", "🌤️", "☀️"],
                            "temperatures": ["19°C/10°C", "18°C/11°C", "21°C/12°C", "20°C/11°C", "22°C/13°C"],
                            "conditions": ["Partly Cloudy", "Light Showers", "Sunny", "Partly Cloudy", "Sunny"],
                            "precipitation": ["10%", "30%", "5%", "15%", "5%"]
                        }
                    elif month_num in [6, 7, 8]:  # Summer
                        return {
                            "icons": ["☀️", "☀️", "⛅", "☀️", "🌦️"],
                            "temperatures": ["24°C/15°C", "25°C/16°C", "23°C/15°C", "26°C/17°C", "24°C/16°C"],
                            "conditions": ["Sunny", "Sunny", "Partly Cloudy", "Sunny", "Light Showers"],
                            "precipitation": ["5%", "5%", "10%", "5%", "25%"]
                        }
                    elif month_num in [9, 10, 11]:  # Fall
                        return {
                            "icons": ["🌤️", "🌧️", "🌤️", "🌦️", "🌤️"],
                            "temperatures": ["18°C/10°C", "16°C/9°C", "17°C/8°C", "15°C/7°C", "14°C/6°C"],
                            "conditions": ["Partly Cloudy", "Rainy", "Partly Cloudy", "Light Showers", "Partly Cloudy"],
                            "precipitation": ["15%", "60%", "20%", "40%", "25%"]
                        }
                    else:  # Winter
                        return {
                            "icons": ["🌧️", "🌫️", "🌧️", "⛅", "🌧️"],
                            "temperatures": ["8°C/3°C", "7°C/2°C", "6°C/1°C", "8°C/2°C", "7°C/1°C"],
                            "conditions": ["Rainy", "Foggy", "Rainy", "Partly Cloudy", "Rainy"],
                            "precipitation": ["65%", "40%", "70%", "30%", "60%"]
                        }
                # New York weather data by season
                elif destination.lower() == "new york":
                    if month_num in [3, 4, 5]:  # Spring
                        return {
                            "icons": ["🌤️", "🌦️", "🌧️", "🌤️", "☀️"],
                            "temperatures": ["15°C/5°C", "17°C/7°C", "18°C/8°C", "16°C/6°C", "19°C/9°C"],
                            "conditions": ["Partly Cloudy", "Light Showers", "Rainy", "Partly Cloudy", "Sunny"],
                            "precipitation": ["20%", "35%", "60%", "25%", "10%"]
                        }
                    elif month_num in [6, 7, 8]:  # Summer
                        return {
                            "icons": ["☀️", "⛅", "🌦️", "☀️", "⛈️"],
                            "temperatures": ["28°C/18°C", "29°C/19°C", "27°C/18°C", "30°C/20°C", "26°C/17°C"],
                            "conditions": ["Sunny", "Partly Cloudy", "Light Showers", "Sunny", "Thunderstorm"],
                            "precipitation": ["5%", "15%", "30%", "5%", "70%"]
                        }
                    elif month_num in [9, 10, 11]:  # Fall
                        return {
                            "icons": ["🌤️", "☀️", "🌧️", "🌤️", "🌦️"],
                            "temperatures": ["22°C/12°C", "18°C/8°C", "16°C/6°C", "14°C/4°C", "12°C/2°C"],
                            "conditions": ["Partly Cloudy", "Sunny", "Rainy", "Partly Cloudy", "Light Showers"],
                            "precipitation": ["20%", "5%", "65%", "25%", "40%"]
                        }
                    else:  # Winter
                        return {
                            "icons": ["❄️", "🌨️", "❄️", "☁️", "🌨️"],
                            "temperatures": ["4°C/-4°C", "2°C/-6°C", "0°C/-8°C", "3°C/-5°C", "1°C/-7°C"],
                            "conditions": ["Snow", "Light Snow", "Snow", "Cloudy", "Light Snow"],
                            "precipitation": ["60%", "40%", "70%", "30%", "50%"]
                        }

                # Return default data for other destinations
                return default_data

            # Try to parse the travel dates
            try:
                # Use the improved date parsing function
                start_date, end_date, month_num = parse_travel_dates(dates)

                # Get weather forecast from OpenWeatherMap API
                weather_data = get_weather_forecast_openweathermap(destination, start_date, end_date)

                # If API call failed or returned no data, use historical averages
                if not weather_data:
                    st.info("Using historical weather averages for your trip dates.")

                    # Get historical weather data for this destination and month
                    historical_data = get_historical_weather(destination, month_num)

                    # Create a row for each day in the range
                    weather_data = []
                    days_in_range = (end_date - start_date).days + 1

                    for i in range(days_in_range):
                        current_date = start_date + timedelta(days=i)
                        idx = i % len(historical_data["icons"])  # Use modulo to handle longer stays

                        weather_data.append({
                            "date": current_date.strftime("%b %d, %Y"),
                            "icon": historical_data["icons"][idx],
                            "temp": historical_data["temperatures"][idx],
                            "condition": historical_data["conditions"][idx],
                            "precipitation": historical_data["precipitation"][idx],
                            "precipitation_mm": f"{float(historical_data['precipitation'][idx].replace('%', '')) / 10:.1f} mm",
                            "humidity": f"{60 + (idx * 5)}%",  # Simulated humidity
                            "wind": f"{5 + (idx * 0.5):.1f} m/s",  # Simulated wind speed
                            "feels_like": f"{int(historical_data['temperatures'][idx].split('/')[0].replace('°C', '')) - 2}°C",  # Simulated feels like
                            "day_length": f"{12 + (idx % 3 - 1):.1f} hours"  # Simulated day length
                        })

            except Exception as e:
                # Fallback if date parsing fails
                st.warning(f"Could not parse travel dates: {str(e)}. Using generic forecast.")

                # Generate generic weather data for 5 days
                weather_data = [
                    {"date": "Day 1", "icon": "🌤️", "temp": "22°C/15°C", "condition": "Partly Cloudy", "precipitation": "15%", "precipitation_mm": "0.5 mm", "humidity": "65%", "wind": "5.0 m/s", "feels_like": "20°C", "day_length": "12.5 hours"},
                    {"date": "Day 2", "icon": "🌦️", "temp": "21°C/14°C", "condition": "Light Showers", "precipitation": "35%", "precipitation_mm": "2.1 mm", "humidity": "70%", "wind": "5.5 m/s", "feels_like": "19°C", "day_length": "12.4 hours"},
                    {"date": "Day 3", "icon": "☀️", "temp": "24°C/16°C", "condition": "Sunny", "precipitation": "5%", "precipitation_mm": "0.0 mm", "humidity": "60%", "wind": "4.5 m/s", "feels_like": "23°C", "day_length": "12.6 hours"},
                    {"date": "Day 4", "icon": "🌤️", "temp": "23°C/15°C", "condition": "Partly Cloudy", "precipitation": "20%", "precipitation_mm": "0.8 mm", "humidity": "65%", "wind": "5.2 m/s", "feels_like": "21°C", "day_length": "12.5 hours"},
                    {"date": "Day 5", "icon": "☀️", "temp": "25°C/17°C", "condition": "Sunny", "precipitation": "5%", "precipitation_mm": "0.0 mm", "humidity": "55%", "wind": "4.8 m/s", "feels_like": "24°C", "day_length": "12.7 hours"}
                ]

            # Create a more visually appealing weather display
            st.markdown("""
            <style>
            .weather-card {
                background: linear-gradient(135deg, #6dd5ed, #2193b0);
                border-radius: 15px;
                padding: 15px;
                color: white;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                height: 100%;
                transition: transform 0.3s ease;
            }
            .weather-card:hover {
                transform: translateY(-5px);
            }
            .weather-card.rainy {
                background: linear-gradient(135deg, #616161, #9bc5c3);
            }
            .weather-card.sunny {
                background: linear-gradient(135deg, #ff9966, #ff5e62);
            }
            .weather-card.cloudy {
                background: linear-gradient(135deg, #8e9eab, #eef2f3);
                color: #333;
            }
            .weather-card.snow {
                background: linear-gradient(135deg, #e6dada, #274046);
            }
            .weather-card.fog {
                background: linear-gradient(135deg, #bdc3c7, #2c3e50);
            }
            .weather-card.storm {
                background: linear-gradient(135deg, #373B44, #4286f4);
            }
            .weather-date {
                font-size: 14px;
                margin-bottom: 5px;
                font-weight: bold;
            }
            .weather-icon {
                font-size: 40px;
                margin: 10px 0;
            }
            .weather-temp {
                font-size: 18px;
                font-weight: bold;
                margin: 5px 0;
            }
            .weather-condition {
                margin: 5px 0;
                font-size: 14px;
            }
            .weather-details {
                font-size: 12px;
                margin-top: 10px;
                text-align: left;
                color: rgba(255, 255, 255, 0.9);
            }
            .weather-card.cloudy .weather-details {
                color: rgba(0, 0, 0, 0.7);
            }
            .weather-detail-item {
                display: flex;
                justify-content: space-between;
                margin-bottom: 3px;
            }
            .weather-summary {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 15px;
                margin-top: 20px;
            }
            .weather-bar {
                height: 10px;
                border-radius: 5px;
                margin: 5px 0;
                background: #f0f0f0;
                overflow: hidden;
            }
            .weather-bar-fill {
                height: 100%;
                border-radius: 5px;
            }
            </style>
            """, unsafe_allow_html=True)

            # Add weather view options
            view_options = ["Cards", "Detailed", "Compact"]
            selected_view = st.radio("Display Style", view_options, horizontal=True, index=0)

            # Display weather data based on selected view
            if selected_view == "Cards":
                # Display weather data in a nice format with enhanced cards
                cols = st.columns(min(len(weather_data), 5))  # Limit to 5 columns max
                for i, day in enumerate(weather_data[:5]):  # Show max 5 days
                    # Determine card style based on weather condition
                    card_class = "weather-card"
                    condition_lower = day['condition'].lower()
                    if "rain" in condition_lower or "shower" in condition_lower or "drizzle" in condition_lower:
                        card_class += " rainy"
                    elif "sun" in condition_lower or "clear" in condition_lower:
                        card_class += " sunny"
                    elif "cloud" in condition_lower or "overcast" in condition_lower:
                        card_class += " cloudy"
                    elif "snow" in condition_lower or "ice" in condition_lower:
                        card_class += " snow"
                    elif "fog" in condition_lower or "mist" in condition_lower:
                        card_class += " fog"
                    elif "thunder" in condition_lower or "storm" in condition_lower:
                        card_class += " storm"

                    with cols[i]:
                        st.markdown(f"""
                        <div class="{card_class}">
                            <div class="weather-date">{day['date']}</div>
                            <div class="weather-icon">{day['icon']}</div>
                            <div class="weather-temp">{day['temp']}</div>
                            <div class="weather-condition">{day['condition']}</div>
                            <div class="weather-details">
                                <div class="weather-detail-item">
                                    <span>Rain:</span><span>{day['precipitation']}</span>
                                </div>
                                <div class="weather-detail-item">
                                    <span>Humidity:</span><span>{day['humidity']}</span>
                                </div>
                                <div class="weather-detail-item">
                                    <span>Wind:</span><span>{day['wind']}</span>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

            elif selected_view == "Detailed":
                # Display detailed weather information in a table format
                st.markdown("### Detailed Weather Forecast")

                # Create a DataFrame for better display
                weather_df = pd.DataFrame([
                    {
                        "Date": day['date'],
                        "Condition": f"{day['icon']} {day['condition']}",
                        "High/Low": day['temp'],
                        "Feels Like": day['feels_like'],
                        "Rain Chance": day['precipitation'],
                        "Rainfall": day.get('precipitation_mm', 'N/A'),
                        "Humidity": day['humidity'],
                        "Wind": day['wind'],
                        "Day Length": day.get('day_length', 'N/A')
                    } for day in weather_data
                ])

                st.dataframe(weather_df, use_container_width=True)

                # Add a detailed chart for temperature trends
                st.markdown("#### Temperature Trend")

                # Extract temperature data
                dates = [day['date'] for day in weather_data]
                max_temps = [float(day['temp'].split('/')[0].replace('°C', '')) for day in weather_data]
                min_temps = [float(day['temp'].split('/')[1].replace('°C', '')) for day in weather_data]
                feels_like = [float(day['feels_like'].replace('°C', '')) for day in weather_data]

                # Create a DataFrame for the chart
                temp_df = pd.DataFrame({
                    'Date': dates,
                    'Max Temperature (°C)': max_temps,
                    'Min Temperature (°C)': min_temps,
                    'Feels Like (°C)': feels_like
                })

                # Plot the chart
                st.line_chart(temp_df.set_index('Date'))

                # Add precipitation chart
                st.markdown("#### Precipitation Forecast")

                # Extract precipitation data
                precip_chance = [float(day['precipitation'].replace('%', '')) for day in weather_data]

                # Create a DataFrame for the chart
                precip_df = pd.DataFrame({
                    'Date': dates,
                    'Precipitation Chance (%)': precip_chance
                })

                # Plot the chart
                st.bar_chart(precip_df.set_index('Date'))

            else:  # Compact view
                # Display compact weather information
                st.markdown("### 5-Day Forecast")

                # Create a compact horizontal display
                for day in weather_data[:5]:
                    col1, col2, col3, col4 = st.columns([1, 1, 2, 1])

                    with col1:
                        st.markdown(f"**{day['date']}**")

                    with col2:
                        st.markdown(f"<span style='font-size: 24px;'>{day['icon']}</span> {day['temp']}", unsafe_allow_html=True)

                    with col3:
                        st.markdown(f"{day['condition']} | Rain: {day['precipitation']} | Wind: {day['wind']}")

                    with col4:
                        # Add a small visual indicator for precipitation
                        precip_pct = float(day['precipitation'].replace('%', ''))
                        precip_color = "#2193b0" if precip_pct > 50 else "#6dd5ed" if precip_pct > 20 else "#e0f7fa"

                        st.markdown(f"""
                        <div class="weather-bar">
                            <div class="weather-bar-fill" style="width: {precip_pct}%; background-color: {precip_color};"></div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("---")

            # Add a "See More Days" button if there are more than 5 days and in Cards view
            if len(weather_data) > 5 and selected_view == "Cards":
                if st.button("See More Days"):
                    # Display additional days
                    st.markdown("### Additional Forecast Days")
                    extra_cols = st.columns(min(len(weather_data) - 5, 5))
                    for i, day in enumerate(weather_data[5:10]):  # Show next 5 days max
                        # Determine card style based on weather condition
                        card_class = "weather-card"
                        condition_lower = day['condition'].lower()
                        if "rain" in condition_lower or "shower" in condition_lower:
                            card_class += " rainy"
                        elif "sun" in condition_lower or "clear" in condition_lower:
                            card_class += " sunny"
                        elif "cloud" in condition_lower or "overcast" in condition_lower:
                            card_class += " cloudy"
                        elif "snow" in condition_lower:
                            card_class += " snow"
                        elif "fog" in condition_lower or "mist" in condition_lower:
                            card_class += " fog"
                        elif "thunder" in condition_lower or "storm" in condition_lower:
                            card_class += " storm"

                        with extra_cols[i]:
                            st.markdown(f"""
                            <div class="{card_class}">
                                <div class="weather-date">{day['date']}</div>
                                <div class="weather-icon">{day['icon']}</div>
                                <div class="weather-temp">{day['temp']}</div>
                                <div class="weather-condition">{day['condition']}</div>
                                <div class="weather-details">
                                    <div class="weather-detail-item">
                                        <span>Rain:</span><span>{day['precipitation']}</span>
                                    </div>
                                    <div class="weather-detail-item">
                                        <span>Humidity:</span><span>{day['humidity']}</span>
                                    </div>
                                    <div class="weather-detail-item">
                                        <span>Wind:</span><span>{day['wind']}</span>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

            # Weather summary with enhanced calculations and visualization
            try:
                # Calculate averages and statistics
                avg_high = sum([float(day['temp'].split('/')[0].replace('°C', '')) for day in weather_data]) / len(weather_data)
                avg_low = sum([float(day['temp'].split('/')[1].replace('°C', '')) for day in weather_data]) / len(weather_data)
                rainy_days = sum(1 for day in weather_data if float(day['precipitation'].replace('%', '')) > 30)
                sunny_days = sum(1 for day in weather_data if "sun" in day['condition'].lower() or "clear" in day['condition'].lower())

                # Calculate total precipitation
                total_precip = 0
                if 'precipitation_mm' in weather_data[0]:
                    total_precip = sum([float(day['precipitation_mm'].split(' ')[0]) for day in weather_data])

                # Determine overall weather description
                if sunny_days > len(weather_data) * 0.6:
                    overall = "Mostly sunny and pleasant"
                elif rainy_days > len(weather_data) * 0.6:
                    overall = "Predominantly rainy, pack an umbrella!"
                elif rainy_days > len(weather_data) * 0.3:
                    overall = "Mixed conditions with several rainy periods"
                else:
                    overall = "Mostly pleasant with occasional showers"

                # Create a more visual summary
                st.markdown("### Weather Summary")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"""
                    #### Temperature
                    - 🌡️ Average High: **{avg_high:.1f}°C**
                    - 🌡️ Average Low: **{avg_low:.1f}°C**
                    - 🌞 Sunny Days: **{sunny_days}/{len(weather_data)}**
                    - 🌧️ Rainy Days: **{rainy_days}/{len(weather_data)}**
                    - 💧 Total Precipitation: **{total_precip:.1f} mm**
                    """)

                with col2:
                    # Create a simple chart showing weather distribution
                    st.markdown("#### Weather Distribution")

                    # Calculate percentages
                    sunny_percent = sunny_days / len(weather_data) * 100
                    rainy_percent = rainy_days / len(weather_data) * 100
                    mixed_percent = 100 - sunny_percent - rainy_percent

                    # Create a visual bar
                    st.markdown(f"""
                    <div style="background-color: #f0f0f0; border-radius: 5px; height: 30px; width: 100%; margin-bottom: 10px;">
                        <div style="display: flex; height: 100%; width: 100%;">
                            <div style="background-color: #FFD700; width: {sunny_percent}%; height: 100%; border-radius: 5px 0 0 5px;"></div>
                            <div style="background-color: #87CEEB; width: {mixed_percent}%; height: 100%;"></div>
                            <div style="background-color: #4682B4; width: {rainy_percent}%; height: 100%; border-radius: 0 5px 5px 0;"></div>
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 12px;">
                        <div>☀️ Sunny ({sunny_percent:.0f}%)</div>
                        <div>⛅ Mixed ({mixed_percent:.0f}%)</div>
                        <div>🌧️ Rainy ({rainy_percent:.0f}%)</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Overall assessment and packing tips
                st.markdown(f"""
                #### Overall Forecast: {overall}

                **Packing Tips:**
                """)

                # Generate packing tips based on weather
                tips = []
                if avg_high > 25:
                    tips.append("👕 Light, breathable clothing")
                elif avg_high < 10:
                    tips.append("🧥 Warm jacket and layers")
                else:
                    tips.append("👚 Light layers for variable temperatures")

                if rainy_days > 0:
                    tips.append("☂️ Compact umbrella or raincoat")

                if destination.lower() == "paris":
                    tips.append("🧣 Light scarf (a Parisian essential!)")

                if avg_high > 22:
                    tips.append("🧴 Sunscreen and sunglasses")

                if avg_low < 5:
                    tips.append("🧤 Gloves and warm accessories")

                if total_precip > 10:
                    tips.append("👢 Waterproof footwear")

                # Display tips
                for tip in tips:
                    st.markdown(f"- {tip}")

                # Add data source information
                if any('api_source' in day for day in weather_data):
                    api_source = next((day['api_source'] for day in weather_data if 'api_source' in day), "Weather API")
                    st.caption(f"Weather data provided by {api_source}. Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}.")
                else:
                    st.caption("Note: Weather forecast is based on historical averages and August vary. Check closer to your travel date for more accurate predictions.")

            except Exception as e:
                st.warning(f"Could not generate weather summary: {str(e)}")
                st.caption("Note: Weather forecast is based on historical averages and August vary. Check closer to your travel date for more accurate predictions.")
            # Local tips
            st.markdown("---")
            st.subheader("💡 Local Tips")
            st.caption("Insider advice to enhance your trip")
            
            # Create local tips based on destination
            if destination.lower() == "paris":
                # Create tabs for different categories of tips
                tip_tabs = st.tabs(["🍽️ Dining", "💰 Money-Saving", "🚇 Transportation", "🗣️ Language", "⚠️ Safety"])
            
                with tip_tabs[0]:  # Dining tips
                    st.markdown("### Dining Like a Local")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("""
                        **Best Times to Eat:**
                        - Cafés open early (7-8am)
                        - Lunch: 12-2pm
                        - Dinner: 7:30-10pm (restaurants August not open before 7pm)
            
                        **Ordering Water:**
                        - Ask for "une carafe d'eau" for free tap water
                        - Bottled water is charged extra
            
                        **Service & Tipping:**
                        - "Service compris" means tip is included
                        - Round up or leave €1-2 for good service
                        """)
                    with col2:
                        st.markdown("""
                        **Local Specialties to Try:**
                        - Croissants from award-winning bakeries like Du Pain et des Idées
                        - Steak frites at Le Relais de l'Entrecôte
                        - Falafel in Le Marais at L'As du Fallafel
                        - Macarons from Pierre Hermé or Ladurée
                        - Wine and cheese plate at any local wine bar
            
                        **Etiquette:**
                        - Always greet with "Bonjour" when entering shops
                        - Keep bread on the table, not on your plate
                        """)
            
                with tip_tabs[1]:  # Money-saving tips
                    st.markdown("### Budget-Friendly Paris")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("""
                        **Free Attractions:**
                        - Museums on first Sunday of each month
                        - Père Lachaise Cemetery
                        - Sacré-Cœur Basilica
                        - Notre-Dame Cathedral (exterior)
                        - Jardin du Luxembourg
            
                        **Affordable Dining:**
                        - Eat main meal at lunch with "formule" menu
                        - Shop at markets like Marché d'Aligre
                        - Picnic in parks with baguettes, cheese, and wine
                        """)
                    with col2:
                        st.markdown("""
                        **Transportation Savings:**
                        - Buy a carnet of 10 metro tickets (cheaper than singles)
                        - Consider Paris Museum Pass for multiple attractions
                        - Use Vélib' bike sharing for short trips
                        - Walk between nearby attractions
            
                        **Shopping Tips:**
                        - Tax refund available for purchases over €100
                        - Best sales (soldes) in January and July
                        """)
            
                with tip_tabs[2]:  # Transportation tips
                    st.markdown("### Getting Around Paris")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("""
                        **Metro Tips:**
                        - Download RATP app for navigation
                        - Metro runs 5:30am-1:15am (2:15am weekends)
                        - Keep ticket until you exit (inspections occur)
                        - Line 1 connects many major attractions
            
                        **Airport Transfers:**
                        - RER B train: CDG to central Paris (€11.40)
                        - Orlybus: Orly to Denfert-Rochereau (€9.50)
                        - Allow 60-90 minutes for airport transfers
                        """)
                    with col2:
                        st.markdown("""
                        **Walking Routes:**
                        - Seine riverside paths connect many attractions
                        - Covered passages (Passage des Panoramas, etc.)
                        - Canal Saint-Martin for trendy neighborhoods
            
                        **Avoiding Crowds:**
                        - Major attractions open early (8-9am)
                        - Visit Louvre on Wednesday/Friday evenings
                        - Eiffel Tower least crowded during dinner hours
                        - Book tickets online to skip lines
                        """)
            
                with tip_tabs[3]:  # Language tips
                    st.markdown("### Essential French Phrases")
                    phrases = {
                        "Hello": "Bonjour (bon-zhoor)",
                        "Good evening": "Bonsoir (bon-swahr)",
                        "Please": "S'il vous plaît (seel voo pleh)",
                        "Thank you": "Merci (mehr-see)",
                        "You're welcome": "De rien (duh ree-en)",
                        "Excuse me": "Excusez-moi (ex-koo-zay mwah)",
                        "Do you speak English?": "Parlez-vous anglais? (par-lay voo on-glay)",
                        "I don't understand": "Je ne comprends pas (zhuh nuh kom-pron pah)",
                        "Where is...?": "Où est...? (oo eh)",
                        "How much is it?": "C'est combien? (say kom-bee-en)",
                        "The bill, please": "L'addition, s'il vous plaît (lah-dee-see-ohn seel voo pleh)"
                    }
            
                    # Display phrases in a nice format
                    for phrase, translation in phrases.items():
                        st.markdown(f"**{phrase}:** {translation}")
            
                    st.info("💡 Tip: Even a simple 'Bonjour' before speaking English is greatly appreciated by locals!")
            
                with tip_tabs[4]:  # Safety tips
                    st.markdown("### Safety & Etiquette")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("""
                        **Common Scams to Avoid:**
                        - Petition signers (distraction technique)
                        - Friendship bracelet offers (especially near Sacré-Cœur)
                        - "Gold ring" found on the ground
                        - Forced help with ticket machines
            
                        **Pickpocket Awareness:**
                        - Be vigilant on metro line 1 and at tourist spots
                        - Front pockets or money belts recommended
                        - Keep bags zipped and in front of you
                        """)
                    with col2:
                        st.markdown("""
                        **Emergency Numbers:**
                        - General Emergency: 112
                        - Police: 17
                        - Ambulance: 15
                        - Fire: 18
            
                        **Health & Comfort:**
                        - Pharmacies marked with green cross signs
                        - Public toilets (sanisettes) are free
                        - Drinking water from Wallace fountains is safe
                        - Dress in layers for changing weather
                        """)
            
                    st.warning("⚠️ Be especially vigilant around the Eiffel Tower, Louvre, and Montmartre areas where pickpockets target tourists.")
            
            else:
                # Generic tips for other destinations
                st.info(f"Local tips for {destination} would appear here. Our travel experts are constantly updating our database with insider knowledge for destinations worldwide.")
            
                # Placeholder for generic tips
                st.markdown("""
                ### General Travel Tips:
            
                - Research local customs and etiquette before your trip
                - Learn a few basic phrases in the local language
                - Keep digital and physical copies of important documents
                - Notify your bank of travel plans to avoid card blocks
                - Consider purchasing travel insurance
                - Stay hydrated and be mindful of jet lag
                - Use apps like Google Maps to download offline maps
                """)
            
            # Download option
            pdf_buffer = create_pdf(
                travel_plan,
                destination,
                dates,
                budget,
                hotels,
                flights,
                activities
            )
            st.download_button(
                label="📥 Download Travel Plan as PDF",
                data=pdf_buffer,
                file_name=f"{destination}_travel_plan.pdf",
                mime="application/pdf"
    
            )

    # Add destination information from Google Search API
    st.markdown("---")
    st.subheader("🔍 Destination Information")
    st.caption(f"Discover the beauty and charm of {destination}")

    # Create tabs for different types of information
    search_tabs = st.tabs(["📸 Gallery", "🏛️ Attractions", "📰 News"])

    with search_tabs[0]:  # Images tab
        st.subheader(f"✨ Stunning Views of {destination} ✨")

        # Add image category filter
        image_categories = ["All", "Landmarks", "Nightlife", "Food & Cuisine", "Street Scenes", "Hidden Gems"]
        selected_category = st.select_slider("Explore by Category", options=image_categories)

        # Add time filter for latest images
        time_filter = st.radio("Show images from:", ["Latest (This Month)", "This Season", "All Time"], horizontal=True)

        # Add view style selector
        view_style = st.radio("Gallery Style:", ["Grid View", "Carousel", "Fullscreen"], horizontal=True)

        images = get_destination_images(destination, category=selected_category, time_filter=time_filter)

        if not images:
            st.info("No images available. Please check your API key configuration.")

            # Add fallback images for Paris
            if destination.lower() == "paris":
                st.markdown("### Enjoy these curated images of Paris instead:")
                fallback_images = [
                    {"url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34", "title": "Eiffel Tower", "source": "Unsplash", "photographer": "Chris Karidis"},
                    {"url": "https://images.unsplash.com/photo-1499856871958-5b9627545d1a", "title": "Seine River", "source": "Unsplash", "photographer": "Léonard Cotte"},
                    {"url": "https://images.unsplash.com/photo-1520939817895-060bdaf4fe1b", "title": "Arc de Triomphe", "source": "Unsplash", "photographer": "Anthony DELANOIX"},
                    {"url": "https://images.unsplash.com/photo-1550340499-a6c60fc8287c", "title": "Montmartre", "source": "Unsplash", "photographer": "Léonard Cotte"}
                ]
                images = fallback_images

        if view_style == "Grid View":
            # Enhanced grid view with hover effects
            st.markdown("""
            <style>
            .image-container {
                position: relative;
                overflow: hidden;
                border-radius: 10px;
                transition: transform 0.3s;
            }
            .image-container:hover {
                transform: scale(1.02);
                box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            }
            .image-caption {
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                background: linear-gradient(0deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0) 100%);
                color: white;
                padding: 10px;
                opacity: 0;
                transition: opacity 0.3s;
            }
            .image-container:hover .image-caption {
                opacity: 1;
            }
            </style>
            """, unsafe_allow_html=True)

            # Create a more dynamic grid with 3 columns
            cols = st.columns(3)
            for i, image in enumerate(images):
                with cols[i % 3]:
                    # Create container with hover effect
                    st.markdown(f"""
                    <div class="image-container">
                        <img src="{image['url']}" style="width:100%; border-radius:10px;" alt="{image.get('title', 'Paris')}">
                        <div class="image-caption">
                            <h4>{image.get('title', 'Beautiful Paris')}</h4>
                            <p>📸: {image.get('photographer', image.get('source', 'Unknown'))}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Add like button and share options
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.button(f"❤️ Like", key=f"like_{i}")
                    with col2:
                        st.button(f"🔗 Share", key=f"share_{i}")

        elif view_style == "Carousel":
            # Create a carousel effect
            st.markdown("""
            <style>
            .carousel {
                width: 100%;
                overflow: hidden;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            </style>
            """, unsafe_allow_html=True)

            # Select image to display
            selected_img_index = st.slider("Browse Gallery", 0, len(images)-1, 0)
            selected_img = images[selected_img_index]

            # Display the selected image in a large format
            st.markdown(f"""
            <div class="carousel">
                <img src="{selected_img['url']}" style="width:100%;" alt="{selected_img.get('title', 'Paris')}">
            </div>
            """, unsafe_allow_html=True)

            # Image details
            st.markdown(f"""
            ### {selected_img.get('title', 'Beautiful Paris')}
            📸 Photographer: {selected_img.get('photographer', 'Unknown')}
            🔍 Source: {selected_img.get('source', 'Web')}
            📅 Captured: {selected_img.get('date', 'Recently')}
            """)

            # Add download and share buttons
            col1, col2 = st.columns(2)
            with col1:
                st.button("⬇️ Download Image", key=f"download_{selected_img_index}")
            with col2:
                st.button("🔗 Share Image", key=f"share_carousel_{selected_img_index}")

        else:  # Fullscreen view
            # Create an immersive fullscreen gallery
            st.markdown("""
            <style>
            .fullscreen-gallery {
                position: relative;
                height: 80vh;
                overflow: hidden;
                border-radius: 15px;
                box-shadow: 0 15px 40px rgba(0,0,0,0.3);
            }
            .fullscreen-image {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }
            .image-overlay {
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                background: linear-gradient(0deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0) 100%);
                color: white;
                padding: 20px;
            }
            </style>
            """, unsafe_allow_html=True)

            # Select image to display
            selected_img_index = st.select_slider("Experience Paris",
                                                 options=range(len(images)),
                                                 format_func=lambda i: images[i].get('title', f'Image {i+1}'))
            selected_img = images[selected_img_index]

            # Display the selected image in fullscreen
            st.markdown(f"""
            <div class="fullscreen-gallery">
                <img src="{selected_img['url']}" class="fullscreen-image" alt="{selected_img.get('title', 'Paris')}">
                <div class="image-overlay">
                    <h2>{selected_img.get('title', 'Beautiful Paris')}</h2>
                    <p>Experience the magic of Paris through this stunning view.</p>
                    <p>📸: {selected_img.get('photographer', selected_img.get('source', 'Unknown'))}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Add image description and facts
            st.markdown(f"""
            ### About this Location
            {selected_img.get('description', 'This breathtaking view showcases the beauty of Paris, one of the world\'s most romantic and culturally rich cities.')}

            #### 🌟 Fun Facts
            - {selected_img.get('fact1', 'Paris has 37 bridges crossing the Seine River.')}
            - {selected_img.get('fact2', 'The Eiffel Tower was originally intended as a temporary structure.')}
            - {selected_img.get('fact3', 'Paris has more than 400 parks and gardens throughout the city.')}
            """)

        # Add image collection feature
        st.markdown("---")
        st.markdown("### 💾 Save Your Favorite Views")

        # Import required modules
        import re
        from datetime import datetime

        # Initialize session state variables if they don't exist
        if 'collections' not in st.session_state:
            st.session_state.collections = {}
        if 'current_collection' not in st.session_state:
            st.session_state.current_collection = None
        if 'favorites' not in st.session_state:
            st.session_state.favorites = []
        if 'show_collection_form' not in st.session_state:
            st.session_state.show_collection_form = False
        if 'show_phone_form' not in st.session_state:
            st.session_state.show_phone_form = False
        if 'collection_created' not in st.session_state:
            st.session_state.collection_created = False
        if 'favorites_saved' not in st.session_state:
            st.session_state.favorites_saved = False
        if 'sent_to_phone' not in st.session_state:
            st.session_state.sent_to_phone = False

        # Function to toggle collection form
        def toggle_collection_form():
            st.session_state.show_collection_form = not st.session_state.show_collection_form
            st.session_state.collection_created = False

        # Function to toggle phone form
        def toggle_phone_form():
            st.session_state.show_phone_form = not st.session_state.show_phone_form
            st.session_state.sent_to_phone = False

        # Function to create a new collection
        def create_collection(name, description):
            if name:
                st.session_state.collections[name] = {
                    'description': description,
                    'items': [],
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'destination': destination
                }
                st.session_state.current_collection = name
                st.session_state.collection_created = True
                st.session_state.show_collection_form = False
                return True
            return False

        # Function to save favorites to current collection
        def save_favorites():
            if not st.session_state.current_collection:
                st.warning("Please create a collection first.")
                st.session_state.show_collection_form = True
                return False

            # In a real app, you would get the actual selected items
            # For this example, we'll simulate adding some items
            if 'items' not in st.session_state.collections[st.session_state.current_collection]:
                st.session_state.collections[st.session_state.current_collection]['items'] = []

            # Add favorites to the collection
            for item in st.session_state.favorites:
                if item not in st.session_state.collections[st.session_state.current_collection]['items']:
                    st.session_state.collections[st.session_state.current_collection]['items'].append(item)

            st.session_state.favorites_saved = True
            return True

        # Function to send collection to phone
        def send_to_phone(phone_number, method):
            if not phone_number:
                return False

            # Validate phone number (basic validation)
            if not re.match(r'^\+?[0-9]{10,15}$', phone_number):
                return False

            # In a real app, you would implement actual sending logic
            # For this example, we'll just simulate success
            st.session_state.sent_to_phone = True
            st.session_state.show_phone_form = False
            return True

        # Create columns for collection options
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("📁 Create Collection", on_click=toggle_collection_form):
                pass

        with col2:
            if st.button("⭐ Save Favorites"):
                save_favorites()

        with col3:
            if st.button("📱 Send to Phone", on_click=toggle_phone_form):
                pass

        # Display collection form if button was clicked
        if st.session_state.show_collection_form:
            st.markdown("#### Create New Collection")
            with st.form("collection_form"):
                collection_name = st.text_input("Collection Name", placeholder="My Paris Trip")
                collection_desc = st.text_area("Description", placeholder="My favorite views of Paris")
                submit_button = st.form_submit_button("Create")

                if submit_button:
                    if create_collection(collection_name, collection_desc):
                        st.success(f"Collection '{collection_name}' created successfully!")
                    else:
                        st.error("Please provide a collection name.")

        # Display success message if collection was created
        if st.session_state.collection_created:
            st.success(f"Collection '{st.session_state.current_collection}' created successfully!")
            st.session_state.collection_created = False

        # Display success message if favorites were saved
        if st.session_state.favorites_saved:
            st.success(f"Favorites saved to '{st.session_state.current_collection}'!")
            st.session_state.favorites_saved = False

        # Display phone form if button was clicked
        if st.session_state.show_phone_form:
            st.markdown("#### Send to Phone")
            with st.form("phone_form"):
                phone_number = st.text_input("Phone Number", placeholder="+1234567890")
                send_method = st.radio("Send via", ["SMS"], horizontal=True)
                submit_button = st.form_submit_button("Send")

                if submit_button:
                    if send_to_phone(phone_number, send_method):
                        st.success(f"Collection sent to {phone_number} via {send_method}!")
                    else:
                        st.error("Please provide a valid phone number.")

        # Display success message if sent to phone
        if st.session_state.sent_to_phone:
            st.success("Collection sent to your phone!")
            st.session_state.sent_to_phone = False

        # Display current collections if any exist
        if st.session_state.collections:
            st.markdown("#### Your Collections")

            # Create tabs for each collection
            collection_names = list(st.session_state.collections.keys())
            if collection_names:
                tabs = st.tabs(collection_names)

                for i, name in enumerate(collection_names):
                    with tabs[i]:
                        collection = st.session_state.collections[name]
                        st.markdown(f"**Description**: {collection['description']}")
                        st.markdown(f"**Created**: {collection['created_at']}")
                        st.markdown(f"**Destination**: {collection['destination']}")

                        if collection['items']:
                            st.markdown(f"**Items**: {len(collection['items'])}")

                            # Display items in a grid (simulated)
                            cols = st.columns(3)
                            for j, item in enumerate(collection['items']):
                                with cols[j % 3]:
                                    st.markdown(f"Item {j+1}")
                                    # In a real app, you would display the actual image
                                    st.image("https://placehold.co/200x150", caption=f"View {j+1}")
                        else:
                            st.info("No items in this collection yet.")

                        # Add export options
                        export_col1, export_col2 = st.columns(2)
                        with export_col1:
                            if st.button("📤 Export as PDF", key=f"pdf_{name}"):
                                try:
                                    # Import required libraries for PDF generation
                                    import io
                                    from reportlab.lib.pagesizes import letter
                                    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ReportLabImage, Table, TableStyle
                                    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                                    from reportlab.lib import colors
                                    from reportlab.lib.units import inch
                                    import base64
                                    from PIL import Image as PILImage
                                    import requests
                                    from io import BytesIO

                                    # Create a BytesIO buffer to receive PDF data
                                    buffer = io.BytesIO()

                                    # Create the PDF object using ReportLab
                                    doc = SimpleDocTemplate(buffer, pagesize=letter)
                                    styles = getSampleStyleSheet()

                                    # Create custom styles
                                    title_style = ParagraphStyle(
                                        'Title',
                                        parent=styles['Heading1'],
                                        fontSize=18,
                                        textColor=colors.darkblue,
                                        spaceAfter=12
                                    )

                                    subtitle_style = ParagraphStyle(
                                        'Subtitle',
                                        parent=styles['Heading2'],
                                        fontSize=14,
                                        textColor=colors.darkblue,
                                        spaceAfter=10
                                    )

                                    normal_style = ParagraphStyle(
                                        'Normal',
                                        parent=styles['Normal'],
                                        fontSize=10,
                                        spaceAfter=6
                                    )

                                    # Create the content for the PDF
                                    content = []

                                    # Add title
                                    content.append(Paragraph(f"Travel Collection: {name}", title_style))
                                    content.append(Spacer(1, 0.25*inch))

                                    # Add collection details
                                    content.append(Paragraph("Collection Details", subtitle_style))
                                    content.append(Paragraph(f"<b>Description:</b> {collection['description']}", normal_style))
                                    content.append(Paragraph(f"<b>Destination:</b> {collection['destination']}", normal_style))
                                    content.append(Paragraph(f"<b>Created:</b> {collection['created_at']}", normal_style))
                                    content.append(Paragraph(f"<b>Items:</b> {len(collection['items'])}", normal_style))
                                    content.append(Spacer(1, 0.25*inch))

                                    # Add items section
                                    if collection['items']:
                                        content.append(Paragraph("Collection Items", subtitle_style))

                                        # Function to get placeholder image
                                        def get_placeholder_image(size=(200, 150)):
                                            try:
                                                response = requests.get(f"https://placehold.co/{size[0]}x{size[1]}")
                                                img = PILImage.open(BytesIO(response.content))
                                                img_byte_arr = BytesIO()
                                                img.save(img_byte_arr, format='PNG')
                                                return img_byte_arr.getvalue()
                                            except:
                                                # Fallback to a very simple colored rectangle if network fails
                                                img = PILImage.new('RGB', size, color=(200, 200, 200))
                                                img_byte_arr = BytesIO()
                                                img.save(img_byte_arr, format='PNG')
                                                return img_byte_arr.getvalue()

                                        # Create a table for items (2 columns)
                                        table_data = []
                                        row = []

                                        for i, item in enumerate(collection['items']):
                                            # Get placeholder image
                                            img_data = get_placeholder_image()
                                            img = ReportLabImage(BytesIO(img_data), width=2*inch, height=1.5*inch)

                                            # Create a cell with image and caption
                                            cell_content = [
                                                img,
                                                Paragraph(f"<b>{item}</b>", normal_style)
                                            ]

                                            row.append(cell_content)

                                            # Create a new row after every 2 items
                                            if len(row) == 2 or i == len(collection['items']) - 1:
                                                # If we have an odd number of items, add an empty cell
                                                while len(row) < 2:
                                                    row.append("")

                                                table_data.append(row)
                                                row = []

                                        # Create the table
                                        if table_data:
                                            table = Table(table_data, colWidths=[2.75*inch, 2.75*inch])
                                            table.setStyle(TableStyle([
                                                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                                                ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                                                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                                                ('TOPPADDING', (0, 0), (-1, -1), 10),
                                            ]))
                                            content.append(table)
                                    else:
                                        content.append(Paragraph("No items in this collection yet.", normal_style))

                                    # Add travel tips section
                                    content.append(Spacer(1, 0.5*inch))
                                    content.append(Paragraph("Travel Tips", subtitle_style))

                                    tips_data = [
                                        f"Best time to visit {collection['destination']}: Check local weather and events",
                                        "Remember to pack essential travel documents",
                                        "Consider purchasing travel insurance",
                                        "Research local customs and etiquette",
                                        "Download offline maps for your destination"
                                    ]

                                    for tip in tips_data:
                                        content.append(Paragraph(f"• {tip}", normal_style))

                                    # Build the PDF
                                    doc.build(content)

                                    # Get the PDF value from the BytesIO buffer
                                    pdf_data = buffer.getvalue()

                                    # Create a download link for the PDF
                                    b64_pdf = base64.b64encode(pdf_data).decode()
                                    pdf_filename = f"{name.lower().replace(' ', '_')}_collection.pdf"
                                    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_filename}">Click here to download your PDF</a>'

                                    st.markdown(href, unsafe_allow_html=True)
                                    st.success("PDF generated successfully! Click the link above to download.")

                                except Exception as e:
                                    st.error(f"Error generating PDF: {str(e)}")
                                    st.info("Try again or check if all required libraries are installed.")
                        with export_col2:
                            if st.button("🔗 Share Link", key=f"share_{name}"):
                                st.code(f"https://travel-recommendation-system.fra1.cdn.digitaloceanspaces.com/collection/{name.lower().replace(' ', '-')}")
                                st.success("Link copied to clipboard!")

        # Add a demo section with real destination images
        st.markdown("---")
        st.markdown("### 🖼️ Destination Gallery: Add to Favorites")

        # Define real destination images based on the current destination
        def get_gallery_images(destination):
            # Dictionary of real destination images
            destination_images = {
                "paris": [
                    {"url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTF8fEVpZmZlbCUyMFRvd2VyfGVufDB8fDB8fHww", "caption": "Eiffel Tower"},
                    {"url": "https://images.unsplash.com/photo-1567942585146-33d62b775db0?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8TG91dnJlJTIwTXVzZXVtfGVufDB8fDB8fHww", "caption": "Louvre Museum"},
                    {"url": "https://images.unsplash.com/photo-1700427941735-79402616d706?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NDJ8fFNhY3JlJTIwQ291ZXIlMjBCYXNpbGljYXxlbnwwfHwwfHx8MA%3D%3D", "caption": "Sacré-Cœur Basilica"},
                    {"url": "https://images.unsplash.com/photo-1504896287989-ff1fbde00199?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8U2VpbmUlMjBSaXZlcnxlbnwwfHwwfHx8MA%3D%3D", "caption": "Seine River"},
                    {"url": "https://images.unsplash.com/photo-1623009070764-45002990256e?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8TW9udG1hcnRyZXxlbnwwfHwwfHx8MA%3D%3D", "caption": "Montmartre"},
                    {"url": "https://images.unsplash.com/photo-1664008546045-a85ca0b2e869?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8THV4ZW1ib3VyZyUyMEdhcmRlbnN8ZW58MHx8MHx8fDA%3D", "caption": "Luxembourg Gardens"},
                    {"url": "https://images.unsplash.com/photo-1678737615122-29cf527318f0?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MzB8fFJlc3RhdXJhbnRzJTIwUGFyaXN8ZW58MHx8MHx8fDA%3D", "caption": "Les Deux Musees Restaurant"},
                    {"url": "https://images.unsplash.com/photo-1649695121665-fb2f81f41cf8?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTJ8fENpbmVtYSUyMFBhcmlzfGVufDB8fDB8fHww", "caption": "Le Champo Cinema"}
                ],
            }

            # Default to Paris if destination not found
            dest_lower = destination.lower()
            if dest_lower in destination_images:
                return destination_images[dest_lower]
            else:
                # For any other destination, return a mix of global landmarks
                return [
                    {"url": "https://images.unsplash.com/photo-1648167805828-9f6832996954?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8VGFqJTIwTWFoYWwlMkMlMjBJbmRpYXxlbnwwfHwwfHx8MA%3D%3D", "caption": "Taj Mahal, India"},
                    {"url": "https://images.unsplash.com/photo-1707985664379-c0d3fe6c7608?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Q29sb3NzZXVtJTJDJTIwUm9tZXxlbnwwfHwwfHx8Mg%3D%3D", "caption": "Colosseum, Rome"},
                    {"url": "https://images.unsplash.com/photo-1608037521277-154cd1b89191?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8R3JlYXQlMjBXYWxsJTIwb2YlMjBDaGluYXxlbnwwfHwwfHx8Mg%3D%3D", "caption": "Great Wall of China"},
                    {"url": "https://images.unsplash.com/photo-1580619305218-8423a7ef79b4?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8TWFjaHUlMjBQaWNjaHUlMkMlMjBQZXJ1fGVufDB8fDB8fHwy", "caption": "Machu Picchu, Peru"},
                    {"url": "https://images.unsplash.com/photo-1688664562000-4c1f7cdb48f8?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8U2FudG9yaW5pJTJDJTIwR3JlZWNlfGVufDB8fDB8fHwy", "caption": "Santorini, Greece"},
                    {"url": "https://images.unsplash.com/photo-1615811648503-479d06197ff3?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8UGV0cmElMkMlMjBKb3JkYW58ZW58MHx8MHx8fDI%3D", "caption": "Petra, Jordan"},
                    {"url": "https://images.unsplash.com/photo-1685887892075-d97b977c2d62?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTF8fFB5cmFtaWRzJTJDJTIwRWd5cHR8ZW58MHx8MHx8fDI%3D", "caption": "Pyramids, Egypt"},
                    {"url": "https://images.unsplash.com/photo-1624138784614-87fd1b6528f8?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8U3lkbmV5JTIwT3BlcmElMjBIb3VzZXxlbnwwfHwwfHx8Mg%3D%3D", "caption": "Sydney Opera House"}
                ]

        # Initialize image metadata in session state if not exists
        if 'image_metadata' not in st.session_state:
            st.session_state.image_metadata = {}

        # Get images for the current destination
        destination_images = get_gallery_images(destination)

        # Add filter options
        st.markdown("#### Filter Gallery")
        filter_cols = st.columns([2, 2, 1])
        with filter_cols[0]:
            view_mode = st.radio("View Mode", ["Grid", "Carousel"], horizontal=True)
        with filter_cols[1]:
            sort_by = st.radio("Sort By", ["Popular", "Alphabetical"], horizontal=True)
        with filter_cols[2]:
            show_selected = st.checkbox("Show Selected Only")

        # Sort images based on selection
        if sort_by == "Alphabetical":
            destination_images = sorted(destination_images, key=lambda x: x["caption"])

        # Allow user to upload their own images
        st.markdown("#### 📤 Upload Your Own Images")
        uploaded_files = st.file_uploader("Upload images of your favorite places",
                                         type=["jpg", "jpeg", "png"],
                                         accept_multiple_files=True)

        # Process uploaded files
        if uploaded_files:
            for uploaded_file in uploaded_files:
                # Generate a unique ID for the uploaded file
                file_id = f"uploaded_{uploaded_file.name}"

                # Store the file in session state if not already there
                if file_id not in st.session_state.image_metadata:
                    st.session_state.image_metadata[file_id] = {
                        "caption": uploaded_file.name,
                        "source": "user_upload",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }

        # Combine destination images with uploaded images
        all_images = destination_images.copy()
        for file_id, metadata in st.session_state.image_metadata.items():
            if metadata["source"] == "user_upload":
                all_images.append({"url": file_id, "caption": metadata["caption"], "is_upload": True})

        # Display images based on view mode
        if view_mode == "Grid":
            # Create a grid of images
            st.markdown("#### 🖼️ Image Gallery")

            # Filter images if show_selected is checked
            display_images = [img for img in all_images if not show_selected or
                             img["caption"] in st.session_state.favorites]

            # Create rows with 4 images each
            for i in range(0, len(display_images), 4):
                row_images = display_images[i:i+4]
                cols = st.columns(4)

                for j, img in enumerate(row_images):
                    with cols[j]:
                        # Display the image
                        if img.get("is_upload", False):
                            # For uploaded files, get from session state
                            file_id = img["url"]
                            for uploaded_file in uploaded_files:
                                if uploaded_file.name == st.session_state.image_metadata[file_id]["caption"]:
                                    st.image(uploaded_file, caption=img["caption"], use_container_width=True)
                                    break
                        else:
                            # For destination images, use the URL
                            # Add size parameters to Unsplash URL for better loading
                            img_url = f"{img['url']}?auto=format&fit=crop&w=300&h=200&q=80"
                            st.image(img_url, caption=img["caption"], use_container_width=True)

                        # Add a checkbox to select as favorite
                        checkbox_key = f"favorite_{img['caption']}"
                        if st.checkbox("Add to favorites", key=checkbox_key,
                                      value=img["caption"] in st.session_state.favorites):
                            if img["caption"] not in st.session_state.favorites:
                                st.session_state.favorites.append(img["caption"])
                        elif img["caption"] in st.session_state.favorites:
                            st.session_state.favorites.remove(img["caption"])

        else:  # Carousel view
            st.markdown("#### 🎠 Image Carousel")

            # Filter images if show_selected is checked
            display_images = [img for img in all_images if not show_selected or
                             img["caption"] in st.session_state.favorites]

            if not display_images:
                st.info("No images to display. Try changing your filter or adding favorites.")
            else:
                # Initialize carousel index in session state if not exists
                if 'carousel_index' not in st.session_state:
                    st.session_state.carousel_index = 0

                # Navigation buttons
                col1, col2, col3 = st.columns([1, 3, 1])
                with col1:
                    if st.button("⬅️ Previous"):
                        st.session_state.carousel_index = (st.session_state.carousel_index - 1) % len(display_images)
                with col3:
                    if st.button("Next ➡️"):
                        st.session_state.carousel_index = (st.session_state.carousel_index + 1) % len(display_images)

                # Display current image
                current_img = display_images[st.session_state.carousel_index]

                # Display the image
                if current_img.get("is_upload", False):
                    # For uploaded files, get from session state
                    file_id = current_img["url"]
                    for uploaded_file in uploaded_files:
                        if uploaded_file.name == st.session_state.image_metadata[file_id]["caption"]:
                            st.image(uploaded_file, caption=current_img["caption"], use_container_width=True)
                            break
                else:
                    # For destination images, use the URL with higher quality for carousel
                    img_url = f"{current_img['url']}?auto=format&fit=crop&w=800&h=500&q=90"
                    st.image(img_url, caption=current_img["caption"], use_container_width=True)

                # Add a checkbox to select as favorite
                checkbox_key = f"carousel_favorite_{current_img['caption']}"
                if st.checkbox("Add to favorites", key=checkbox_key,
                              value=current_img["caption"] in st.session_state.favorites):
                    if current_img["caption"] not in st.session_state.favorites:
                        st.session_state.favorites.append(current_img["caption"])
                elif current_img["caption"] in st.session_state.favorites:
                    st.session_state.favorites.remove(current_img["caption"])

                # Display carousel position
                st.caption(f"Image {st.session_state.carousel_index + 1} of {len(display_images)}")

        # Display current favorites
        if st.session_state.favorites:
            st.markdown("### ⭐ Your Favorites")

            # Create a visual display of favorites
            fav_cols = st.columns(4)
            for i, fav in enumerate(st.session_state.favorites):
                with fav_cols[i % 4]:
                    # Find the image data
                    img_data = next((img for img in all_images if img["caption"] == fav), None)

                    if img_data:
                        # Display a thumbnail
                        if img_data.get("is_upload", False):
                            # For uploaded files
                            file_id = img_data["url"]
                            for uploaded_file in uploaded_files:
                                if uploaded_file.name == st.session_state.image_metadata[file_id]["caption"]:
                                    st.image(uploaded_file, width=100)
                                    break
                        else:
                            # For destination images
                            img_url = f"{img_data['url']}?auto=format&fit=crop&w=150&h=100&q=70"
                            st.image(img_url, width=100)

                        st.markdown(f"**{fav}**")

                        # Add remove button
                        if st.button("❌ Remove", key=f"remove_{fav}"):
                            st.session_state.favorites.remove(fav)
                            st.experimental_rerun()

            # Add a button to save all favorites to collection
            if st.button("💾 Save All Favorites to Collection"):
                if not st.session_state.current_collection:
                    st.warning("Please create a collection first.")
                    st.session_state.show_collection_form = True
                else:
                    save_favorites()
                    st.success(f"All favorites saved to '{st.session_state.current_collection}'!")
        else:
            st.info("Select your favorite images by checking the boxes below each image.")

        # Add image metadata to session state for PDF generation
        for img in destination_images:
            if img["caption"] not in st.session_state.image_metadata:
                st.session_state.image_metadata[img["caption"]] = {
                    "url": img["url"],
                    "source": "destination_gallery",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

        # Add photographer credits and image usage information
        st.markdown("---")
        st.caption("Images are sourced from various photographers and platforms. All rights belong to their respective owners.")

        # Add image search feature
        st.markdown("### 🔍 Looking for something specific?")

        # Create a more dynamic search interface
        search_col1, search_col2 = st.columns([3, 1])

        with search_col1:
            # Make the placeholder dynamic based on destination
            placeholder_text = f"Search {destination} images (e.g., '{destination} landmarks', 'restaurants', 'streets')"
            image_search = st.text_input(placeholder_text, key="image_search_input")

        with search_col2:
            # Add search filters dropdown
            search_filter = st.selectbox(
                "Filter by",
                ["All", "Landmarks", "Food", "Culture", "Nature", "Architecture", "Nightlife", "Streets"],
                key="search_filter"
            )

        # Add quick access buttons for popular categories
        st.markdown("#### Quick Access Categories")
        quick_access_cols = st.columns(3)

        # Define URLs for Paris landmarks
        paris_landmark_urls = {
            "Eiffel Tower": "https://ticket.toureiffel.paris/en",
            "Louvre Museum": "https://www.louvre.fr/en/",
            "Notre Dame": "https://www.notredamedeparis.fr/en/",
            "Arc de Triomphe": "https://www.paris-arc-de-triomphe.fr/en/",
            "Sacré-Cœur": "https://www.sacre-coeur-montmartre.com/english/",
            "Champs-Élysées": "https://www.champselysees-paris.com/"
        }
        # Define URLs for Paris food & restaurants
        paris_food_urls = {
            "Cafés": "https://www.timeout.com/paris/en/restaurants/best-cafes-in-paris",
            "Patisseries": "https://www.eater.com/maps/best-pastries-paris-france-patisseries",
            "Fine Dining": "https://elitetraveler.com/finest-dining/best-restaurants-in-paris",
            "Bistros": "https://www.pariseater.com/restaurants/best-bistros-in-paris-read-before-you-travel/",
            "Boulangeries": "https://www.sortiraparis.com/en/news/in-paris/articles/310033-la-meilleure-boulangerie-de-france-2025-the-list-of-the-10-candidates-in-paris-and-its-inner-suburbs",
            "Street Food": "https://www.worldofmouth.app/articles/best-street-food-restaurants-in-paris"
        }
        # Define URLs for Paris neighborhoods
        paris_neighborhood_urls = {
            "Montmartre": "https://www.sortiraparis.com/en/news/in-paris/articles/326711-the-tour-de-france-2025-will-pass-through-montmartre-with-an-exceptional-climb-up-rue-lepic",
            "Le Marais": "https://thetourguy.com/travel-blog/france/paris/where-to-stay-in-le-marais/",
            "Latin Quarter": "https://thetourguy.com/travel-blog/france/paris/the-latin-quarter-paris/",
            "Saint-Germain": "https://en.psg.fr/teams/first-team/content/lfp-unveils-key-dates-for-2025-2026-psg-news",
            "Champs-Élysées": "https://www.lemarianne.com/news/articles/new-year-2025-a-look-back-at-the-celebrations-on-the-champs-elysees-in-paris-61871",
            "Rue Cler": "https://www.tripadvisor.com/Attraction_Review-g187147-d190512-Reviews-Rue_Cler-Paris_Ile_de_France.html"
        }
        # Define URLs for New York landmarks (for completeness)
        ny_landmark_urls = {
            "Statue of Liberty": "https://worldguidestotravel.com/best-statue-of-liberty-tours/",
            "Empire State Building": "https://www.cbsnews.com/newyork/news/empire-state-building-dark-lights-off-today-march-22-2025/",
            "Times Square": "https://www.timessquarenyc.org/news-and-press-releases/nye-2025-official-lineup",
            "Central Park": "https://www.centralpark.com/search/event/upcoming-events/#page=1",
            "Brooklyn Bridge": "https://brooklyneagle.com/articles/2025/03/18/brooklyn-bridge-grand-army-plaza-arch-restoration-projects-receive-landmarks-conservancys-awards/",
            "One World Trade Center": "https://www.archdaily.com/795277/one-world-trade-center-som"
        }

        # Initialize session state variables for search
        if 'temp_search_query' not in st.session_state:
            st.session_state.temp_search_query = ""
        if 'should_update_search' not in st.session_state:
            st.session_state.should_update_search = False

        # Function to update search query without directly modifying widget state
        def update_search_query(query):
            st.session_state.temp_search_query = query
            st.session_state.should_update_search = True
            st.rerun()

        with quick_access_cols[0]:
            landmarks_tab = st.expander("🏛️ Landmarks", expanded=False)
            with landmarks_tab:
                st.markdown("**Popular Landmarks**")
                if destination.lower() == "paris":
                    landmark_buttons = ["Eiffel Tower", "Louvre Museum", "Notre Dame",
                                        "Arc de Triomphe", "Sacré-Cœur", "Champs-Élysées"]
                    landmark_urls = paris_landmark_urls
                elif destination.lower() == "new york":
                    landmark_buttons = ["Statue of Liberty", "Empire State Building", "Times Square",
                                        "Central Park", "Brooklyn Bridge", "One World Trade Center"]
                    landmark_urls = ny_landmark_urls
                else:
                    landmark_buttons = ["Famous Landmarks", "Historic Sites", "Monuments",
                                        "Tourist Attractions", "Must-See Places", "City Views"]

                    landmark_urls = {button: "#" for button in landmark_buttons} # Placeholder URLs

                # Create 2x3 grid for landmark buttons
                for i in range(0, len(landmark_buttons), 2):
                    cols = st.columns(2)
                    for j in range(2):
                        if i+j < len(landmark_buttons):
                            with cols[j]:
                                landmark = landmark_buttons[i+j]
                                url = landmark_urls.get(landmark, "#")
                                st.markdown(f"<a href='{url}' target='_blank' style='text-decoration:none;'><div style='background-color:#1E1E1E;color:white;padding:10px;border-radius:5px;text-align:center;'>{landmark}</div></a>", unsafe_allow_html=True)
                                # Create a search button that also opens the URL in a new tab
                                search_button_html = f"""
                                <a href='{url}' target='_blank' style='text-decoration:none;'>
                                    <button style='background-color:#2c3e50;color:white;border:none;padding:8px 12px;border-radius:5px;width:100%;cursor:pointer;'>
                                        Search {landmark}
                                    </button>
                                </a>
                                """
                                st.markdown(search_button_html, unsafe_allow_html=True)

                                # Hidden button to handle the search functionality
                                if st.button(f"Search {landmark}", key=f"hidden_search_landmark_{i+j}", help="Click to search for this landmark"):
                                    update_search_query(f"{destination} {landmark}")

        with quick_access_cols[1]:
            restaurants_tab = st.expander("🍽️ Restaurants & Food", expanded=False)
            with restaurants_tab:
                st.markdown("**Culinary Experiences**")
                if destination.lower() == "paris":
                    food_buttons = ["Cafés", "Patisseries", "Fine Dining",
                                    "Bistros", "Boulangeries", "Street Food"]
                    food_urls = paris_food_urls
                elif destination.lower() == "new york":
                    food_buttons = [
                        "Pizza Places", "Delis", "Food Trucks",
                        "Rooftop Restaurants", "Bagel Shops", "Steakhouses"]
                else:
                    food_buttons = ["Local Cuisine", "Popular Restaurants", "Street Food",
                                    "Cafés", "Dining Experiences", "Food Markets"]

                    food_urls = {button: "#" for button in food_buttons} # Placeholder URLs

                # Create 2x3 grid for food buttons
                for i in range(0, len(food_buttons), 2):
                    cols = st.columns(2)
                    for j in range(2):
                        if i+j < len(food_buttons):
                            with cols[j]:
                                food = food_buttons[i+j]
                                url = food_urls.get(food, "#")
                                # Display the food category as a clickable link
                                st.markdown(f"<a href='{url}' target='_blank' style='text-decoration:none;'><div style='background-color:#1E1E1E;color:#3498db;padding:10px;border-radius:5px;text-align:center;'>{food}</div></a>", unsafe_allow_html=True)
                                # Create a search button that also opens the URL in a new tab
                                search_button_html = f"""
                                <a href='{url}' target='_blank' style='text-decoration:none;'>
                                    <button style='background-color:#2c3e50;color:white;border:none;padding:8px 12px;border-radius:5px;width:100%;cursor:pointer;'>
                                        Search {food}
                                    </button>
                                </a>
                                """
                                st.markdown(search_button_html, unsafe_allow_html=True)

                                # Hidden button to handle the search functionality
                                if st.button(f"Search {food}", key=f"hidden_search_food_{i+j}", help="Click to search for this food category"):
                                    update_search_query(f"{destination} {food}")

        with quick_access_cols[2]:
            streets_tab = st.expander("🛣️ Streets & Neighborhoods", expanded=False)
            with streets_tab:
                st.markdown("**Explore the City**")
                if destination.lower() == "paris":
                    street_buttons = ["Montmartre", "Le Marais", "Latin Quarter",
                             "Saint-Germain", "Champs-Élysées", "Rue Cler"]
                    street_urls = paris_neighborhood_urls
                elif destination.lower() == "new york":
                    street_buttons = ["5th Avenue", "SoHo", "Greenwich Village",
                                        "Wall Street", "Broadway", "Little Italy"]
                else:
                    street_buttons = ["Main Streets", "Historic Districts", "Shopping Areas",
                        "Pedestrian Zones", "Famous Avenues", "Hidden Alleys"]
                    street_urls = {button: "#" for button in street_buttons} # Placeholder URLs

                # Create 2x3 grid for street buttons
                for i in range(0, len(street_buttons), 2):
                    cols = st.columns(2)
                    for j in range(2):
                        if i+j < len(street_buttons):
                            with cols[j]:
                                street = street_buttons[i+j]
                                url = street_urls.get(street, "#")
                                # Display the neighborhood as a clickable link
                                st.markdown(f"<a href='{url}' target='_blank' style='text-decoration:none;'><div style='background-color:#1E1E1E;color:white;padding:10px;border-radius:5px;text-align:center;'>{street}</div></a>", unsafe_allow_html=True)        
                                # Create a search button that also opens the URL in a new tab
                                search_button_html = f"""
                                <a href='{url}' target='_blank' style='text-decoration:none;'>
                                    <button style='background-color:#2c3e50;color:white;border:none;padding:8px 12px;border-radius:5px;width:100%;cursor:pointer;'>
                                        Search {street}
                                    </button>
                                </a>
                                """
                                st.markdown(search_button_html, unsafe_allow_html=True)
                                # Hidden button to handle the search functionality
                                if st.button(f"Search {street}", key=f"hidden_search_street_{i+j}", help="Click to search for this neighborhood"):
                                    update_search_query(f"{destination} {street}")
                                    

        # Initialize search results in session state if not exists
        if 'search_results' not in st.session_state:
            st.session_state.search_results = []
        if 'search_history' not in st.session_state:
            st.session_state.search_history = []
        if 'is_searching' not in st.session_state:
            st.session_state.is_searching = False
        if 'web_image_mode' not in st.session_state:
            st.session_state.web_image_mode = False

        # Function to perform image search
        def search_images(query, filter_type="All", destination=None):
            """
            Search for images based on query, filter, and destination
            Returns a list of image dictionaries
            """
            # In a real app, this would connect to an image search API
            # For this demo, we'll simulate search results using predefined images

            # Normalize inputs
            query = query.lower()
            destination_lower = destination.lower() if destination else ""

            # Create a dictionary of search terms and corresponding images
            search_terms = {
                # Paris landmarks
                "paris eiffel tower": [
                    {"url": "https://images.unsplash.com/photo-1563216225-425be0cbd18d?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8RWlmZmVsJTIwVG93ZXIlMjBhdCUyMFN1bnNldHxlbnwwfHwwfHx8Mg%3D%3D", "caption": "Eiffel Tower at Sunset", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1711238440837-a1d14ceb2736?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MjF8fEVpZmZlbCUyMFRvd2VyJTIwd2l0aCUyMEJsdWUlMjBTa3l8ZW58MHx8MHx8fDI%3D", "caption": "Eiffel Tower with Blue Sky", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1491902289130-d9862e8c7982?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTF8fEVpZmZlbCUyMFRvd2VyJTIwYXQlMjBOaWdodHxlbnwwfHwwfHx8Mg%3D%3D", "caption": "Eiffel Tower at Night", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1606271342846-34de5c58a135?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8RWlmZmVsJTIwVG93ZXIlMjBmcm9tJTIwQ2hhbXAlMjBkZSUyME1hcnN8ZW58MHx8MHx8fDI%3D", "caption": "Eiffel Tower from Champ de Mars", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1699727813770-2435c9c7c4f5?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Nnx8RWlmZmVsJTIwVG93ZXIlMjB3aXRoJTIwU3ByaW5nJTIwQmxvc3NvbXN8ZW58MHx8MHx8fDI%3D", "caption": "Eiffel Tower with Spring Blossoms", "source": "Unsplash"}
                ],
                "paris louvre museum": [
                    {"url": "https://images.unsplash.com/photo-1459455356093-6495cff2a2c4?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8TG91dnJlJTIwUHlyYW1pZHxlbnwwfHwwfHx8Mg%3D%3D", "caption": "Louvre Pyramid", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1561036114-8473db81fc37?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8SW5zaWRlJTIwdGhlJTIwTG91dnJlfGVufDB8fDB8fHwy", "caption": "Inside the Louvre", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1720774401213-08da3073d9e2?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8TW9uYSUyMExpc2ElMjBhdCUyMHRoZSUyMExvdXZyZXxlbnwwfHwwfHx8Mg%3D%3D", "caption": "Mona Lisa at the Louvre", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1656807721526-875863ed63cf?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8N3x8TG91dnJlJTIwQ291cnR5YXJkfGVufDB8fDB8fHwy", "caption": "Louvre Courtyard", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1557458249-1be70955065c?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8TG91dnJlJTIwTXVzZXVtJTIwYXQlMjBOaWdodHxlbnwwfHwwfHx8Mg%3D%3D", "caption": "Louvre Museum at Night", "source": "Unsplash"}
                ],
                "paris notre dame": [
                    {"url": "https://images.unsplash.com/photo-1581211653431-310ba15ff9bf?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8Tm90cmUlMjBEYW1lJTIwQ2F0aGVkcmFsfGVufDB8fDB8fHwy", "caption": "Notre Dame Cathedral", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1513542328669-daa7f8962b01?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Tm90cmUlMjBEYW1lJTIwR2FyZ295bGVzfGVufDB8fDB8fHwy", "caption": "Notre Dame Gargoyles", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1705057491926-cbca8f0220eb?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8OHx8Tm90cmUlMjBEYW1lJTIwZnJvbSUyMFNlaW5lJTIwUml2ZXJ8ZW58MHx8MHx8fDI%3D", "caption": "Notre Dame from Seine River", "source": "Unsplash"}
                ],
                "paris arc de triomphe": [
                    {"url": "https://images.unsplash.com/photo-1694286433612-cdc3d0c58608?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8QXJjJTIwZGUlMjBUcmlvbXBoZXxlbnwwfHwwfHx8Mg%3D%3D", "caption": "Arc de Triomphe", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1641503855609-5e28a1ed35a9?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Nnx8QXJjJTIwZGUlMjBUcmlvbXBoZSUyMGF0JTIwTmlnaHR8ZW58MHx8MHx8fDI%3D", "caption": "Arc de Triomphe at Night", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1567187156116-8a7d411df217?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8N3x8QXJjJTIwZGUlMjBUcmlvbXBoZSUyMGZyb20lMjBDaGFtcHMlMjAlQzMlODlseXMlQzMlQTllc3xlbnwwfHwwfHx8Mg%3D%3D", "caption": "Arc de Triomphe from Champs-Élysées", "source": "Unsplash"}
                ],
                "paris sacré-cœur": [
                    {"url": "https://images.unsplash.com/photo-1637467727750-f7196c8e2fc8?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8U2FjciVDMyVBOSUyMEMlQzUlOTN1ciUyMEJhc2lsaWNhfGVufDB8fDB8fHwy", "caption": "Sacré-Cœur Basilica", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1636142303230-fbe952bdc4ae?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Nnx8U2FjciVDMyVBOSUyMEMlQzUlOTN1ciUyMGZyb20lMjBNb250bWFydHJlfGVufDB8fDB8fHwy", "caption": "Sacré-Cœur from Montmartre", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1637467727750-f7196c8e2fc8?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8U2FjciVDMyVBOSUyMEMlQzUlOTN1ciUyMEludGVyaW9yfGVufDB8fDB8fHwy", "caption": "Sacré-Cœur Interior", "source": "Unsplash"}
                ],

                # Paris restaurants and food
                "paris cafés": [
                    {"url": "https://images.unsplash.com/photo-1678815122490-d566bfdf9c3c?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8N3x8UGFyaXNpYW4lMjBTaWRld2FsayUyMENhZiVDMyVBOXxlbnwwfHwwfHx8Mg%3D%3D", "caption": "Parisian Sidewalk Café", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1544609499-d9b16fe50243?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8Q2FmJUMzJUE5JTIwZGUlMjBGbG9yZXxlbnwwfHwwfHx8Mg%3D%3D", "caption": "Café de Flore", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1691070468247-5ae03873c09f?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8TGVzJTIwRGV1eCUyME1hZ290cyUyMFBhcmlzfGVufDB8fDB8fHwy", "caption": "Les Deux Magots", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1728058961992-a4f111af7bb7?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MjR8fENhZiVDMyVBOSUyMFRlcnJhY2UlMjBpbiUyMFBhcmlzfGVufDB8fDB8fHwy", "caption": "Café Terrace in Paris", "source": "Unsplash"}
                ],
                "paris patisseries": [
                    {"url": "https://images.unsplash.com/photo-1710077717714-976db5604dd7?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8RnJlbmNoJTIwUGFzdHJpZXN8ZW58MHx8MHx8fDI%3D", "caption": "French Pastries", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1725545904327-4644b45f1a5f?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Nnx8Q3JvaXNzYW50cyUyMGFuZCUyMENvZmZlZXxlbnwwfHwwfHx8Mg%3D%3D", "caption": "Croissants and Coffee", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1718412963214-43a148cb1e39?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8TWFjYXJvbnMlMjBEaXNwbGF5fGVufDB8fDB8fHwy", "caption": "Macarons Display", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1647445848468-0e00067a29f7?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8TGFkdXIlQzMlQTllJTIwUGF0aXNzZXJpZSUyMFBhcmlzfGVufDB8fDB8fHwy", "caption": "Ladurée Patisserie", "source": "Unsplash"}
                ],
                "paris bistros": [
                    {"url": "https://images.unsplash.com/flagged/photo-1590341292401-2f764e4fd118?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8VHJhZGl0aW9uYWwlMjBQYXJpc2lhbiUyMEJpc3Ryb3xlbnwwfHwwfHx8Mg%3D%3D", "caption": "Traditional Parisian Bistro", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1709548145082-04d0cde481d4?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8QmlzdHJvJTIwSW50ZXJpb3J8ZW58MHx8MHx8fDI%3D", "caption": "Bistro Interior", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1716215558018-9f57124218de?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8QmlzdHJvJTIwRGluaW5nfGVufDB8fDB8fHwy", "caption": "Bistro Dining", "source": "Unsplash"}
                ],
                "paris fine dining": [
                    {"url": "https://images.unsplash.com/photo-1722718461737-8b739ef577ab?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8OHx8R291cm1ldCUyMEZyZW5jaCUyMEN1aXNpbmV8ZW58MHx8MHx8fDI%3D", "caption": "Gourmet French Cuisine", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1712488070063-696f22cce02c?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MjJ8fEVsZWdhbnQlMjBSZXN0YXVyYW50JTIwSW50ZXJpb3J8ZW58MHx8MHx8fDI%3D", "caption": "Elegant Restaurant Interior", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1672833634993-a7ce02f7adbc?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MzR8fEZpbmUlMjBEaW5pbmclMjBFeHBlcmllbmNlfGVufDB8fDB8fHwy", "caption": "Fine Dining Experience", "source": "Unsplash"}
                ],

                # Paris streets and neighborhoods
                "paris montmartre": [
                    {"url": "https://images.unsplash.com/photo-1716131369717-0dfad8959410?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8TW9udG1hcnRyZSUyMFN0cmVldHN8ZW58MHx8MHx8fDI%3D", "caption": "Montmartre Streets", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1700625385838-3fc0d6e065a6?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8TW9udG1hcnRyZSUyMFN0ZXBzfGVufDB8fDB8fHwy", "caption": "Montmartre Steps", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1598195947320-2a61a5b94e56?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8QXJ0aXN0cyUyMFNxdWFyZSUyMGluJTIwTW9udG1hcnRyZXxlbnwwfHwwfHx8Mg%3D%3D", "caption": "Artists Square in Montmartre", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1699564625082-3ae9eca15bea?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8TW9udG1hcnRyZSUyMENhZiVDMyVBOXN8ZW58MHx8MHx8fDI%3D", "caption": "Montmartre Cafés", "source": "Unsplash"}
                ],
                "paris le marais": [
                    {"url": "https://images.unsplash.com/photo-1673458908554-fcd918b0ee01?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8TGUlMjBNYXJhaXMlMjBEaXN0cmljdHxlbnwwfHwwfHx8Mg%3D%3D", "caption": "Le Marais District", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1634316164986-3d65b05f123f?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8TGUlMjBNYXJhaXMlMjBTaG9wc3xlbnwwfHwwfHx8Mg%3D%3D", "caption": "Le Marais Shops", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1644316999990-04c86026accb?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8UGxhY2UlMjBkZXMlMjBWb3NnZXN8ZW58MHx8MHx8fDI%3D", "caption": "Place des Vosges", "source": "Unsplash"}
                ],
                "paris latin quarter": [
                    {"url": "https://images.unsplash.com/photo-1722612262679-e7ad8d32aeeb?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTF8fExhdGluJTIwUXVhcnRlciUyMFN0cmVldHN8ZW58MHx8MHx8fDI%3D", "caption": "Latin Quarter Streets", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1678644886790-13e1dcf8f3ff?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8U29yYm9ubmUlMjBVbml2ZXJzaXR5fGVufDB8fDB8fHwy", "caption": "Sorbonne University", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1624549927542-ee9e74d6b624?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTJ8fExhdGluJTIwUXVhcnRlciUyMEJvb2tzaG9wcyUyMFBhcmlzfGVufDB8fDB8fHwy", "caption": "Latin Quarter Bookshops", "source": "Unsplash"}
                ],
                "paris champs-élysées": [
                    {"url": "https://images.unsplash.com/photo-1714052264322-f558833e7842?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8Q2hhbXBzJTIwJUMzJTg5bHlzJUMzJUE5ZXMlMjBBdmVudWV8ZW58MHx8MHx8fDI%3D", "caption": "Champs-Élysées Avenue", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1714891962350-489fde9f2af4?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTR8fENoYW1wcyUyMCVDMyU4OWx5cyVDMyVBOWVzJTIwYXQlMjBOaWdodHxlbnwwfHwwfHx8Mg%3D%3D", "caption": "Champs-Élysées at Night", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1588060016539-9ca9491296d6?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Q2hhbXBzJTIwJUMzJTg5bHlzJUMzJUE5ZXMlMjBWaWV3fGVufDB8fDB8fHwy", "caption": "Champs-Élysées View", "source": "Unsplash"}
                ],
                "paris seine river": [
                    {"url": "https://images.unsplash.com/photo-1689859937146-2d7ed8e8978e?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8U2VpbmUlMjBSaXZlciUyMFZpZXd8ZW58MHx8MHx8fDI%3D", "caption": "Seine River View", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1743450589308-30508cc51304?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8U2VpbmUlMjBSaXZlciUyMENydWlzZXxlbnwwfHwwfHx8Mg%3D%3D", "caption": "Seine River Cruise", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1600656779586-a047188fc1d6?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8U2VpbmUlMjBSaXZlciUyMGF0JTIwTmlnaHR8ZW58MHx8MHx8fDI%3D", "caption": "Seine River at Night", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1652254694635-7a4a775d3dc8?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8U2VpbmUlMjBSaXZlciUyMEJyaWRnZXN8ZW58MHx8MHx8fDI%3D", "caption": "Seine River Bridges", "source": "Unsplash"}
                ],

                # New York search terms
                "new york times square": [
                    {"url": "https://images.unsplash.com/photo-1623007732499-69fec5244a96?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8VGltZXMlMjBTcXVhcmUlMjBhdCUyME5pZ2h0fGVufDB8fDB8fHwy", "caption": "Times Square at Night", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1640356447555-87ef24a8ab9e?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8VGltZXMlMjBTcXVhcmUlMjBCaWxsYm9hcmRzfGVufDB8fDB8fHwy", "caption": "Times Square Billboards", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1668568293039-44e658aa2985?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8VGltZXMlMjBTcXVhcmUlMjBDcm93ZHN8ZW58MHx8MHx8fDI%3D", "caption": "Times Square Crowds", "source": "Unsplash"}
                ],
                "new york central park": [
                    {"url": "https://images.unsplash.com/photo-1575372587186-5012f8886b4e?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8Q2VudHJhbCUyMFBhcmslMjBpbiUyMEZhbGx8ZW58MHx8MHx8fDI%3D", "caption": "Central Park in Fall", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1600932758292-fad945929189?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8Q2VudHJhbCUyMFBhcmslMjBMYWtlfGVufDB8fDB8fHwy", "caption": "Central Park Lake", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1671702274704-c69df4081c79?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8OXx8Q2VudHJhbCUyMFBhcmslMjBpbiUyMFNwcmluZ3xlbnwwfHwwfHx8Mg%3D%3D", "caption": "Central Park in Spring", "source": "Unsplash"}
                ],
                "new york food": [
                    {"url": "https://images.unsplash.com/photo-1712337462866-b4f30571cc15?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTN8fE5ldyUyMFlvcmslMjBQaXp6YXxlbnwwfHwwfHx8Mg%3D%3D", "caption": "New York Pizza", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1717434742464-b1c330a981a2?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Nnx8TmV3JTIwWW9yayUyMEJhZ2Vsc3xlbnwwfHwwfHx8Mg%3D%3D", "caption": "New York Bagels", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1659730251664-6a2815ab562a?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8TmV3JTIwWW9yayUyMEhvdCUyMERvZ3N8ZW58MHx8MHx8fDI%3D", "caption": "New York Hot Dogs", "source": "Unsplash"}
                ],

                # Generic search terms
                "landmarks": [
                    {"url": "https://images.unsplash.com/photo-1627654138934-348ac62d178a?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTd8fEZhbW91cyUyMExhbmRtYXJrfGVufDB8fDB8fHwy", "caption": "Famous Landmark", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1698123080168-4bfcd3ef971a?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8OHx8SGlzdG9yaWMlMjBCdWlsZGluZ3xlbnwwfHwwfHx8Mg%3D%3D", "caption": "Historic Building", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1636493553214-732fccf321bc?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8Q2l0eSUyME1vbnVtZW50JTIwUGFyaXN8ZW58MHx8MHx8fDI%3D", "caption": "City Monument", "source": "Unsplash"}
                ],
                "food": [
                    {"url": "https://images.unsplash.com/photo-1587292106513-770ccd153e67?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTJ8fExvY2FsJTIwQ3Vpc2luZSUyMFBhcmlzfGVufDB8fDB8fHwy", "caption": "Local Cuisine", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1667118399331-c6d546acee11?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MjV8fFJlc3RhdXJhbnQlMjBGb29kJTIwUGFyaXN8ZW58MHx8MHx8fDI%3D", "caption": "Restaurant Food", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1504280221321-f8999ab71415?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8OXx8U3RyZWV0JTIwRm9vZCUyMFBhcmlzfGVufDB8fDB8fHwy", "caption": "Street Food", "source": "Unsplash"}
                ],
                "nature": [
                    {"url": "https://images.unsplash.com/photo-1665422275608-210d15fbd88c?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTd8fFBhcmslMjBWaWV3JTIwUGFyaXN8ZW58MHx8MHx8fDI%3D", "caption": "Park View", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1635473172403-03151dbdfbbb?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8R2FyZGVucyUyMFBhcmlzfGVufDB8fDB8fHwy", "caption": "Gardens", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1725138172406-8786b4a8e094?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTl8fE5hdHVyYWwlMjBTY2VuZXJ5JTIwUGFyaXN8ZW58MHx8MHx8fDI%3D", "caption": "Natural Scenery", "source": "Unsplash"}
                ],
                "nightlife": [
                    {"url": "https://images.unsplash.com/photo-1641228961562-195810a836c5?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8TmlnaHQlMjBDbHViJTIwUGFyaXN8ZW58MHx8MHx8fDI%3D", "caption": "Night Club", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1629624123501-7595e0193fe0?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8RXZlbmluZyUyMEVudGVydGFpbm1lbnQlMjBQYXJpc3xlbnwwfHwwfHx8Mg%3D%3D", "caption": "Evening Entertainment", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1698296886757-2b6941000b3b?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8Q2l0eSUyMGF0JTIwTmlnaHQlMjBQYXJpc3xlbnwwfHwwfHx8Mg%3D%3D", "caption": "City at Night", "source": "Unsplash"}
                ],
                "streets": [
                    {"url": "https://images.unsplash.com/photo-1736117705005-84a38031251e?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NDl8fEhpc3RvcmljJTIwU3RyZWV0JTIwUGFyaXN8ZW58MHx8MHx8fDI%3D", "caption": "Historic Street", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1548266566-fa6249d3491c?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8OXx8U2hvcHBpbmclMjBEaXN0cmljdCUyMFBhcmlzfGVufDB8fDB8fHwy", "caption": "Shopping District", "source": "Unsplash"},
                    {"url": "https://images.unsplash.com/photo-1545253591-7fdd8cf938b0?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MjN8fENoYXJtaW5nJTIwQWxsZXklMjBQYXJpc3xlbnwwfHwwfHx8Mg%3D%3D", "caption": "Charming Alley", "source": "Unsplash"}
                ]
            }

            # Combine destination with search terms
            if destination_lower:
                query = f"{destination_lower} {query}"

            # Apply filter if not "All"
            if filter_type != "All":
                query = f"{query} {filter_type.lower()}"

            # Find matching search terms
            results = []
            for term, images in search_terms.items():
                if term in query or any(word in term for word in query.split()):
                    results.extend(images)

            # If no specific matches, try to match by filter type
            if not results and filter_type != "All":
                filter_lower = filter_type.lower()
                if filter_lower in search_terms:
                    results.extend(search_terms[filter_lower])

            # If still no results, return some generic images based on destination
            if not results and destination_lower:
                for term, images in search_terms.items():
                    if destination_lower in term:
                        results.extend(images)
                        if len(results) >= 6:  # Limit to 6 results
                            break

            # If still no results, return some random images
            if not results:
                import random
                all_images = [img for images in search_terms.values() for img in images]
                results = random.sample(all_images, min(6, len(all_images)))

            # Remove duplicates while preserving order
            seen = set()
            unique_results = []
            for img in results:
                if img['url'] not in seen:
                    seen.add(img['url'])
                    unique_results.append(img)

            return unique_results[:9]  # Return up to 9 results

        # Function to handle search button click
        def handle_search():
            if image_search:
                st.session_state.is_searching = True
                # Add to search history if not already there
                if image_search not in st.session_state.search_history:
                    st.session_state.search_history.insert(0, image_search)
                    # Keep only the last 5 searches
                    st.session_state.search_history = st.session_state.search_history[:5]

                # Perform the search
                st.session_state.search_results = search_images(
                    image_search,
                    filter_type=search_filter,
                    destination=destination
                )
            else:
                st.warning("Please enter a search term")

        # Add web image browsing toggle
        web_browse_col1, web_browse_col2 = st.columns([3, 1])
        with web_browse_col1:
            st.markdown("#### 🌐 Browse Web Images")
            st.caption("Access curated collections of high-quality images from the web")
        with web_browse_col2:
            web_image_toggle = st.toggle("Enable Web Images", value=st.session_state.web_image_mode)
            if web_image_toggle != st.session_state.web_image_mode:
                st.session_state.web_image_mode = web_image_toggle
                st.rerun()

        # Search button
        if st.button("🔎 Search Images", on_click=handle_search):
            pass

        # Display search history
        if st.session_state.search_history:
            st.caption("Recent searches:")
            history_cols = st.columns(len(st.session_state.search_history))
            for i, term in enumerate(st.session_state.search_history):
                with history_cols[i]:
                    if st.button(term, key=f"history_{i}"):
                        # Set the search input to this term and perform search
                        st.session_state.image_search_input = term
                        st.session_state.is_searching = True
                        st.session_state.search_results = search_images(
                            term,
                            filter_type=search_filter,
                            destination=destination
                        )
                        st.rerun()

        # Display web image collections if enabled
        if st.session_state.web_image_mode:
            st.markdown("### 🌐 Web Image Collections")

            # Define web image collections
            web_collections = {
                "paris": {
                    "Official Paris Tourism": "https://en.parisinfo.com/",
                    "Paris Photo Gallery": "https://www.parisphoto.com/en-gb.html",
                    "Paris Museums": "https://www.parisinsidersguide.com/paris-museum-exhibitions.html",
                    "Paris Architecture": "https://www.archdaily.com/tag/paris",
                    "Paris Street Photography": "https://www.vogue.com/slideshow/the-best-street-style-photos-from-the-couture-2025-shows-in-paris"
                },
                "new york": {
                    "NYC Tourism": "https://www.nyctourism.com/",
                    "New York Times Travel": "https://www.nytimes.com/section/travel/destinations/north-america/united-states/new-york",
                    "NYC Parks": "https://www.nycgovparks.org/photo-gallery",
                    "NYC Architecture": "https://www.archdaily.com/tag/new-york",
                    "NYC Street Photography": "https://www.nyc-spc.com/"
                },
                "london": {
                    "Visit London": "https://www.visitlondon.com/",
                    "London Photo Gallery": "https://www.timeout.com/london/attractions/beautiful-london-photos",
                    "London Museums": "https://www.visitlondon.com/things-to-do/sightseeing/london-attraction/museum/free-museums-in-london",
                    "London Architecture": "https://www.archdaily.com/tag/london",
                    "London Street Photography": "https://www.londonstreetphotography.com/"
                }
            }

            # Get collections for current destination or use default
            dest_lower = destination.lower()
            current_collections = web_collections.get(dest_lower, {
                "Official Tourism": f"https://www.google.com/search?q={destination}+tourism&tbm=isch",
                "Travel Photos": f"https://www.google.com/search?q={destination}+travel+photos&tbm=isch",
                "Landmarks": f"https://www.google.com/search?q={destination}+landmarks&tbm=isch",
                "Food & Restaurants": f"https://www.google.com/search?q={destination}+food+restaurants&tbm=isch",
                "Streets & Neighborhoods": f"https://www.google.com/search?q={destination}+streets+neighborhoods&tbm=isch"
            })

            # Display collections as clickable cards
            web_cols = st.columns(3)
            for i, (name, url) in enumerate(current_collections.items()):
                with web_cols[i % 3]:
                    st.markdown(f"""
                    <div style="border:1px solid #ddd; border-radius:5px; padding:10px; margin-bottom:10px;">
                        <h4>{name}</h4>
                        <p>Browse high-quality images from this source</p>
                        <a href="{url}" target="_blank">
                            <button style="background-color:#4CAF50; color:white; border:none; padding:8px 15px;
                            border-radius:4px; cursor:pointer;">Visit Website</button>
                        </a>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")

        # Display search results
        if st.session_state.is_searching:
            if st.session_state.search_results:
                st.markdown(f"### Search Results for '{image_search}'")

                # Add view options
                view_options = st.radio("View as:", ["Grid", "Large Images", "Slideshow"], horizontal=True)

                if view_options == "Grid":
                    # Create a grid of search results
                    for i in range(0, len(st.session_state.search_results), 3):
                        cols = st.columns(3)
                        for j in range(3):
                            if i + j < len(st.session_state.search_results):
                                img = st.session_state.search_results[i + j]
                                with cols[j]:
                                    # Display the image
                                    img_url = f"{img['url']}?auto=format&fit=crop&w=300&h=200&q=80"
                                    st.image(img_url, caption=img['caption'], use_container_width=True)

                                    # Show source
                                    st.caption(f"Source: {img.get('source', 'Web')}")

                                    # Add to favorites button
                                    if st.button("⭐ Add to Favorites", key=f"add_fav_{img['caption']}"):
                                        if img['caption'] not in st.session_state.favorites:
                                            st.session_state.favorites.append(img['caption'])
                                            # Also add to image metadata for PDF generation
                                            if img['caption'] not in st.session_state.image_metadata:
                                                st.session_state.image_metadata[img['caption']] = {
                                                    "url": img['url'],
                                                    "source": "search_results",
                                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                                }
                                            st.success(f"Added '{img['caption']}' to favorites!")
                                        else:
                                            st.info(f"'{img['caption']}' is already in your favorites.")

                elif view_options == "Large Images":
                    # Display images in a single column but larger
                    for i, img in enumerate(st.session_state.search_results):
                        # Display the image
                        img_url = f"{img['url']}?auto=format&fit=crop&w=800&h=500&q=90"
                        st.image(img_url, caption=img['caption'], use_container_width=True)

                        # Show source
                        st.caption(f"Source: {img.get('source', 'Web')}")

                        # Add to favorites button in a smaller column
                        col1, col2 = st.columns([1, 4])
                        with col1:
                            if st.button("⭐ Add to Favorites", key=f"add_fav_large_{img['caption']}"):
                                if img['caption'] not in st.session_state.favorites:
                                    st.session_state.favorites.append(img['caption'])
                                    # Also add to image metadata for PDF generation
                                    if img['caption'] not in st.session_state.image_metadata:
                                        st.session_state.image_metadata[img['caption']] = {
                                            "url": img['url'],
                                            "source": "search_results",
                                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        }
                                    st.success(f"Added '{img['caption']}' to favorites!")
                                else:
                                    st.info(f"'{img['caption']}' is already in your favorites.")

                        st.markdown("---")

                else:  # Slideshow
                    # Initialize slideshow index if not exists
                    if 'slideshow_index' not in st.session_state:
                        st.session_state.slideshow_index = 0

                    # Navigation
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col1:
                        if st.button("⬅️ Previous"):
                            st.session_state.slideshow_index = (st.session_state.slideshow_index - 1) % len(st.session_state.search_results)
                            st.rerun()

                    with col3:
                        if st.button("Next ➡️"):
                            st.session_state.slideshow_index = (st.session_state.slideshow_index + 1) % len(st.session_state.search_results)
                            st.rerun()

                    # Display current image
                    current_img = st.session_state.search_results[st.session_state.slideshow_index]
                    img_url = f"{current_img['url']}?auto=format&fit=crop&w=1000&h=600&q=100"
                    st.image(img_url, caption=current_img['caption'], use_container_width=True)

                    # Show source and position
                    st.caption(f"Source: {current_img.get('source', 'Web')} | Image {st.session_state.slideshow_index + 1} of {len(st.session_state.search_results)}")

                    # Add to favorites button
                    if st.button("⭐ Add to Favorites", key=f"add_fav_slide_{current_img['caption']}"):
                        if current_img['caption'] not in st.session_state.favorites:
                            st.session_state.favorites.append(current_img['caption'])
                            # Also add to image metadata for PDF generation
                            if current_img['caption'] not in st.session_state.image_metadata:
                                st.session_state.image_metadata[current_img['caption']] = {
                                    "url": current_img['url'],
                                    "source": "search_results",
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                            st.success(f"Added '{current_img['caption']}' to favorites!")
                        else:
                            st.info(f"'{current_img['caption']}' is already in your favorites.")

                # Add a "Clear Results" button
                if st.button("Clear Results"):
                    st.session_state.is_searching = False
                    st.rerun()
            else:
                st.info(f"No results found for '{image_search}'. Try a different search term.")

                # Suggest some search terms
                st.markdown("#### Try searching for:")
                suggestion_cols = st.columns(3)
                suggestions = [
                    f"{destination} landmarks",
                    f"{destination} food",
                    f"{destination} streets",
                    f"{destination} parks",
                    f"{destination} nightlife",
                    f"{destination} architecture"
                ]

                for i, suggestion in enumerate(suggestions):
                    with suggestion_cols[i % 3]:
                        if st.button(suggestion, key=f"suggest_{i}"):
                            st.session_state.image_search_input = suggestion
                            st.session_state.is_searching = True
                            st.session_state.search_results = search_images(
                                suggestion,
                                filter_type=search_filter,
                                destination=destination
                            )
                            st.rerun()

    with search_tabs[1]:  # Attractions tab
        st.subheader(f"Top Attractions in {destination}")
        attractions = get_destination_attractions(destination)

        if not attractions:
            st.info("No attraction information available. Please check your API key configuration.")
        else:
            # Add attraction categories with official websites
            categories = ["Historical Sites", "Museums", "Parks & Gardens", "Entertainment", "Architecture"]
            selected_category = st.selectbox("Filter by Category", ["All"] + categories)

            # Add category-specific resource websites
            category_resources = {
                "Historical Sites": {
                    "name": "Historical Sites Resources",
                    "websites": [
                        {"name": "UNESCO World Heritage", "url": "https://whc.unesco.org/en/list/"},
                        {"name": "Atlas Obscura", "url": "https://www.atlasobscura.com/"},
                        {"name": "Historic England", "url": "https://historicengland.org.uk/"},
                        {"name": "National Trust", "url": "https://www.nationaltrust.org.uk/"}
                    ]
                },
                "Museums": {
                    "name": "Museum Resources",
                    "websites": [
                        {"name": "Google Arts & Culture", "url": "https://artsandculture.google.com/"},
                        {"name": "International Council of Museums", "url": "https://icom.museum/en/"},
                        {"name": "Museum Finder", "url": "https://www.findmuseums.org/"},
                        {"name": "TimeOut Museums", "url": "https://www.timeout.com/museums"}
                    ]
                },
                "Parks & Gardens": {
                    "name": "Parks & Gardens Resources",
                    "websites": [
                        {"name": "World of Parks", "url": "https://www.worldofparks.com/"},
                        {"name": "National Parks", "url": "https://www.nationalparks.org/"},
                        {"name": "Botanical Gardens Conservation", "url": "https://www.bgci.org/"},
                        {"name": "Great Gardens", "url": "https://greatbritishgardens.co.uk/"}
                    ]
                },
                "Entertainment": {
                    "name": "Entertainment Resources",
                    "websites": [
                        {"name": "TripAdvisor Events", "url": "https://www.tripadvisor.com/Attractions"},
                        {"name": "Ticketmaster", "url": "https://www.ticketmaster.com/"},
                        {"name": "Eventbrite", "url": "https://www.eventbrite.com/"},
                        {"name": "TimeOut", "url": "https://www.timeout.com/"}
                    ]
                },
                "Architecture": {
                    "name": "Architecture Resources",
                    "websites": [
                        {"name": "ArchDaily", "url": "https://www.archdaily.com/"},
                        {"name": "Architectural Digest", "url": "https://www.architecturaldigest.com/"},
                        {"name": "Open House Worldwide", "url": "https://www.openhouseworldwide.org/"},
                        {"name": "Dezeen", "url": "https://www.dezeen.com/"}
                    ]
                }
            }

            # Display category-specific resource websites if a category is selected
            if selected_category != "All" and selected_category in category_resources:
                with st.expander(f"📚 {category_resources[selected_category]['name']} - Find More Places to Visit"):
                    cols = st.columns(2)
                    for i, website in enumerate(category_resources[selected_category]['websites']):
                        with cols[i % 2]:
                            st.markdown(f"[🔗 {website['name']}]({website['url']})")

            # Add destination-specific websites based on the destination
            if destination.lower() == "paris":
                with st.expander("🗼 Official Paris Tourism Resources"):
                    cols = st.columns(2)
                    paris_resources = [
                        {"name": "Paris Convention and Visitors Bureau", "url": "https://en.parisinfo.com/"},
                        {"name": "Paris Museum Pass", "url": "https://www.parismuseumpass.fr/"},
                        {"name": "RATP (Paris Transport)", "url": "https://www.ratp.fr/en"},
                        {"name": "Louvre Museum", "url": "https://www.louvre.fr/en"},
                        {"name": "Eiffel Tower", "url": "https://www.toureiffel.paris/en"},
                        {"name": "Paris Catacombs", "url": "https://www.catacombes.paris.fr/en"}
                    ]
                    for i, resource in enumerate(paris_resources):
                        with cols[i % 2]:
                            st.markdown(f"[🔗 {resource['name']}]({resource['url']})")

            elif destination.lower() == "new york":
                with st.expander("🗽 Official New York Tourism Resources"):
                    cols = st.columns(2)
                    ny_resources = [
                        {"name": "NYC Official Guide", "url": "https://www.nyctourism.com/spring-2025-arts-guide/"},
                        {"name": "MTA (NY Transit)", "url": "https://rpa.org/work/reports/how-mtas-2025-2029-capital-plan-will-benefit-all-new-yorkers"},
                        {"name": "NYC Parks", "url": "https://www.nycgovparks.org/"},
                        {"name": "Metropolitan Museum", "url": "https://www.metmuseum.org/"},
                        {"name": "Empire State Building", "url": "https://www.esbnyc.com/"},
                        {"name": "Central Park", "url": "https://www.centralparknyc.org/"}
                    ]
                    for i, resource in enumerate(ny_resources):
                        with cols[i % 2]:
                            st.markdown(f"[🔗 {resource['name']}]({resource['url']})")

            # Add sorting options
            sort_by = st.radio("Sort by", ["Rating", "Popularity", "Price"], horizontal=True)

            for attraction in attractions:
                # Only show attractions matching the selected category
                if selected_category == "All" or attraction.get('category', '') == selected_category:
                    with st.expander(f"🎯 {attraction['name']} - ⭐ {attraction['rating']} ({attraction['reviews']} reviews)"):
                        col1, col2 = st.columns([2, 1])

                        with col1:
                            st.write(attraction["description"])
                            st.caption(f"📍 {attraction['address']}")

                            # Add practical information
                            st.markdown("#### ℹ️ Visitor Information")
                            st.markdown(f"""
                            - 🕒 **Opening Hours**: {attraction.get('opening_hours', 'Contact venue')}
                            - 💰 **Entrance Fee**: {attraction.get('price', 'Contact venue')}
                            - ⏱️ **Suggested Duration**: {attraction.get('duration', '1-2 hours')}
                            - 🎫 **Booking Required**: {attraction.get('booking_required', 'Recommended')}
                            """)

                            # Add best times to visit
                            st.markdown("#### ⏰ Best Times to Visit")
                            st.markdown(f"""
                            - 📅 **Peak Season**: {attraction.get('peak_season', 'Summer months')}
                            - 🗓️ **Best Day**: {attraction.get('best_day', 'Weekday mornings')}
                            - ⚡ **Quick Tip**: {attraction.get('visit_tip', 'Book tickets online to avoid queues')}
                            """)

                        with col2:
                            # Add quick action buttons with enhanced website links
                            st.markdown("#### 🎟️ Quick Actions")

                            # Create a container with dark background for the quick actions
                            with st.container():
                                st.markdown("""
                                <div style='background-color:#111; padding:15px; border-radius:5px; margin-bottom:15px;'>
                                <h4 style='color:#FF5252; margin-top:0;'>🔴 Quick Actions</h4>
                                """, unsafe_allow_html=True)

                                # Set default website based on category if not provided
                                default_websites = {
                                    "Historical Sites": "https://whc.unesco.org/en/list/",
                                    "Museums": "https://artsandculture.google.com/",
                                    "Parks & Gardens": "https://www.worldofparks.com/",
                                    "Entertainment": "https://www.tripadvisor.com/Attractions",
                                    "Architecture": "https://www.archdaily.com/"
                                }

                                category = attraction.get('category', '')
                                default_website = default_websites.get(category, '#')

                                # Use attraction's website if available, otherwise use category default
                                website_url = attraction.get('website', default_website)

                                # Add ticket booking with enhanced options
                                booking_options = {
                                    "Paris": {
                                        "Historical Sites": "https://www.parismuseumpass.fr/",
                                        "Museums": "https://www.parismuseumpass.fr/",
                                        "Entertainment": "https://www.fnactickets.com/",
                                        "default": "https://www.tiqets.com/en/paris-attractions-c66746/"
                                    },
                                    "New York": {
                                        "Museums": "https://www.citypass.com/new-york",
                                        "Entertainment": "https://www.broadway.com/",
                                        "default": "https://www.getyourguide.com/new-york-l59/"
                                    },
                                    "default": "https://www.getyourguide.com/"
                                }

                                # Determine booking URL based on destination and category
                                dest_key = destination.lower().capitalize()
                                if dest_key in booking_options:
                                    if category in booking_options[dest_key]:
                                        default_booking = booking_options[dest_key][category]
                                    else:
                                        default_booking = booking_options[dest_key]["default"]
                                else:
                                    default_booking = booking_options["default"]

                                booking_url = attraction.get('booking_url', default_booking)

                                # Create two columns for the buttons
                                button_cols = st.columns(2)

                                with button_cols[0]:
                                    # Visit Website button that opens in a new tab
                                    website_button_html = f"""
                                    <a href='{website_url}' target='_blank' style='text-decoration:none;'>
                                        <div style='background-color:#1E3A8A; color:white; padding:8px 12px; border-radius:5px;
                                             text-align:center; margin:5px 0; display:flex; align-items:center; justify-content:center;'>
                                            <span style='margin-right:5px;'>🌐</span> Visit Website
                                        </div>
                                    </a>
                                    <div style='text-align:center; font-size:0.8em; margin-top:3px;'>
                                        <a href='{website_url}' target='_blank' style='color:#3B82F6; text-decoration:none;'>
                                            Visit Official Website
                                        </a>
                                    </div>
                                    """
                                    st.markdown(website_button_html, unsafe_allow_html=True)

                                with button_cols[1]:
                                    # Book Tickets button that opens in a new tab
                                    booking_button_html = f"""
                                    <a href='{booking_url}' target='_blank' style='text-decoration:none;'>
                                        <div style='background-color:#1E3A8A; color:white; padding:8px 12px; border-radius:5px;
                                             text-align:center; margin:5px 0; display:flex; align-items:center; justify-content:center;'>
                                            <span style='margin-right:5px;'>🎟️</span> Book Tickets
                                        </div>
                                    </a>
                                    <div style='text-align:center; font-size:0.8em; margin-top:3px;'>
                                        <a href='{booking_url}' target='_blank' style='color:#3B82F6; text-decoration:none;'>
                                            Book Tickets Online
                                        </a>
                                    </div>
                                    """
                                    st.markdown(booking_button_html, unsafe_allow_html=True)

                                # Add Nearby Attractions section
                                st.markdown("""
                                <div style='margin-top:15px;'>
                                    <h5 style='margin-bottom:5px;'>📍 Nearby Attractions</h5>
                                    <p style='color:#999; font-size:0.9em; margin-top:0;'>- No data available</p>
                                </div>
                                """, unsafe_allow_html=True)

                                # Add Accessibility section
                                st.markdown("""
                                <div style='margin-top:15px;'>
                                    <h5 style='margin-bottom:5px;'>♿ Accessibility</h5>
                                    <p style='color:#999; font-size:0.9em; margin-top:0;'>Contact venue for accessibility information</p>
                                </div>
                                </div>
                                """, unsafe_allow_html=True)

                                # Hidden buttons to maintain Streamlit state management if needed
                                # These are invisible but keep the original functionality
                                if "website_button_placeholder" not in st.session_state:
                                    st.session_state.website_button_placeholder = False
                                if "booking_button_placeholder" not in st.session_state:
                                    st.session_state.booking_button_placeholder = False

                                # Use empty containers to hide the buttons but keep their functionality
                                with st.container():
                                    st.markdown('<div style="display: none;">', unsafe_allow_html=True)
                                    if st.button(f"🌐 Visit Website", key=f"website_{attraction['name']}"):
                                        st.session_state.website_button_placeholder = True
                                    if st.button(f"🎫 Book Tickets", key=f"tickets_{attraction['name']}"):
                                        st.session_state.booking_button_placeholder = True
                                    st.markdown('</div>', unsafe_allow_html=True)
                            # Add nearby attractions
                            st.markdown("#### 📍 Nearby Attractions")
                            for nearby in attraction.get('nearby_attractions', ['No data available']):
                                st.markdown(f"- {nearby}")

                            # Add accessibility information
                            st.markdown("#### ♿ Accessibility")
                            st.markdown(attraction.get('accessibility', 'Contact venue for accessibility information'))

                    # Add visitor tips
                    with st.expander("💡 Visitor Tips"):
                        st.markdown(f"""
                        #### Pro Tips for {attraction['name']}:
                        - 🎯 **Best Photo Spot**: {attraction.get('photo_spot', 'Various locations available')}
                        - 🚶‍♂️ **Getting There**: {attraction.get('directions', 'Check local transport options')}
                        - 💡 **Insider Tip**: {attraction.get('insider_tip', 'Visit during off-peak hours for better experience')}
                        - 👶 **Family-Friendly**: {attraction.get('family_friendly', 'Suitable for all ages')}
                        """)

                    # Add reviews section
                    with st.expander("📝 Recent Reviews"):
                        for review in attraction.get('recent_reviews', [{'rating': '5⭐', 'comment': 'No reviews available', 'date': 'N/A'}]):
                            st.markdown(f"""
                            **{review['rating']}** - _{review['date']}_
                            > {review['comment']}
                            ---
                            """)

    with search_tabs[2]:  # News tab
        st.subheader(f"Latest News about {destination}")
        news_items = get_destination_news(destination)

        if not news_items:
            st.info("No news available. Please check your API key configuration.")
        else:
            for item in news_items:
                st.markdown(f"### [{item['title']}]({item['link']})")
                st.caption(f"{item['date']} | Source: {item['source']}")


if __name__ == "__main__":
    main()
