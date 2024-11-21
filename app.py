from flask import Flask, request, jsonify
from flask_cors import CORS
import spacy
import requests

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Load NLP model
nlp = spacy.load("en_core_web_sm")

CALENDLY_API_TOKEN = "eyJraWQiOiIxY2UxZTEzNjE3ZGNmNzY2YjNjZWJjY2Y4ZGM1YmFmYThhNjVlNjg0MDIzZjdjMzJiZTgzNDliMjM4MDEzNWI0IiwidHlwIjoiUEFUIiwiYWxnIjoiRVMyNTYifQ.eyJpc3MiOiJodHRwczovL2F1dGguY2FsZW5kbHkuY29tIiwiaWF0IjoxNzMxNzQ3MTUyLCJqdGkiOiI5OWVlNjA1Yy0wMDJiLTQ2Y2EtOTdjMi1lOTdhMWFkODJkMjUiLCJ1c2VyX3V1aWQiOiJlMDM2MDhlOS1jYmUyLTQ1OTQtYTBmYy01YzVkNDc0MzBlMDcifQ.uzjWHlBGyydpdn41ynOZluX2X2E_KieiDOL3s3Ilwxgim1W6_K1--LVgdD0ZDyq3avo7AUHgZSvItwk8R_Mt3A"

# Mock doctor availability for demo purposes
def get_doctor_availability(doctor_name):
    mock_availability = {
        "Dr. Alice Johnson": ["10:00 AM", "2:00 PM", "4:00 PM"],
        "Dr. John Smith": ["11:00 AM", "1:00 PM", "3:00 PM"]
    }
    return mock_availability.get(doctor_name, [])

# Schedule appointment via Calendly
def book_appointment_with_calendly(doctor_name, patient_name, time_slot):
    url = "https://api.calendly.com/scheduled_events"
    headers = {"Authorization": f"Bearer {CALENDLY_API_TOKEN}"}
    data = {
        "doctor_name": doctor_name,
        "patient_name": patient_name,
        "time_slot": time_slot
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return {"message": "Appointment booked successfully"}
    return {"error": "Failed to book appointment"}

# Reschedule appointment via Calendly
def reschedule_appointment(appointment_id, new_time_slot):
    url = f"https://api.calendly.com/scheduled_events/{appointment_id}/reschedule"
    headers = {"Authorization": f"Bearer {CALENDLY_API_TOKEN}"}
    data = {"new_time_slot": new_time_slot}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return {"message": "Appointment rescheduled successfully"}
    return {"error": "Failed to reschedule"}

# Chatbot API
@app.route('/chat', methods=['POST'])
def chatbot():
    data = request.json  # Receive JSON payload from the frontend
    message = data.get("message", "").lower()  # Extract user's message
    response_text = "Sorry, I didn't understand that."  # Default response

    # Basic intent recognition (example implementation)
    if "availability" in message:
        doctor_name = "Dr. Alice Johnson"  # Default doctor for demo
        availability = get_doctor_availability(doctor_name)
        response_text = f"{doctor_name} is available at: {', '.join(availability)}"
    
    elif "book appointment" in message:
        doctor_name = data.get("doctor_name", "Dr. Alice Johnson")
        patient_name = data.get("patient_name", "John Doe")
        time_slot = data.get("time_slot", "10:00 AM")
        result = book_appointment_with_calendly(doctor_name, patient_name, time_slot)
        response_text = result.get("message", result.get("error"))

    elif "reschedule appointment" in message:
        appointment_id = data.get("appointment_id")
        new_time_slot = data.get("new_time_slot")
        result = reschedule_appointment(appointment_id, new_time_slot)
        response_text = result.get("message", result.get("error"))

    return jsonify({"response": response_text})

# Health check
@app.route("/", methods=["GET"])
def health_check():
    return "Chatbot API is running!"

if __name__ == "__main__":
    app.run(debug=True)
