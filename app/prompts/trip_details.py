def format_trip_details(state: dict) -> str:
    return f"""
Departure city: {state['origin']}
Destination: {state['destination']}
Dates: {state['start_date']} to {state['end_date']}
Trip length: {state['num_days']} days, {state['num_days'] - 1} nights
Travelers: {state['travelers']}
Total budget: {state['budget']} {state['currency']}
Interests: {', '.join(state['interests'])}
Accommodation type: {state['accommodation_type']}
Preferred transport: {', '.join(state['transport_preference'])}
Food preference: {state['food_preference']}
Pace: {state['pace']}
Special requirements: {state['special_requirements'] or 'None'}
"""