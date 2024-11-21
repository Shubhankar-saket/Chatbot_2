from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

CALENDLY_API_TOKEN = "eyJraWQiOiIxY2UxZTEzNjE3ZGNmNzY2YjNjZWJjY2Y4ZGM1YmFmYThhNjVlNjg0MDIzZjdjMzJiZTgzNDliMjM4MDEzNWI0IiwidHlwIjoiUEFUIiwiYWxnIjoiRVMyNTYifQ.eyJpc3MiOiJodHRwczovL2F1dGguY2FsZW5kbHkuY29tIiwiaWF0IjoxNzMyMTgzNTA1LCJqdGkiOiJkMGNkNGYyMi0wOGM0LTRhZmQtODc0Ni04MjY4ZDVhZjVlMzUiLCJ1c2VyX3V1aWQiOiJlMDM2MDhlOS1jYmUyLTQ1OTQtYTBmYy01YzVkNDc0MzBlMDcifQ.xWfMmcGLgXCFz90ibTxy_o2J_ht54eqnFhvyD36FgJaUrOLun6CkbiaVEpydlAN-PiahIOBEt6kSotlicP1q8g"

# Convert time slot to ISO 8601 format
def to_iso_format(time_slot):
    try:
        # Convert "10:00 AM" to ISO 8601 format
        time_obj = datetime.strptime(time_slot, "%I:%M %p")
        iso_format = datetime.combine(datetime.today(), time_obj.time()).isoformat()
        return iso_format + "Z"  # Append 'Z' for UTC
    except ValueError:
        return None  # Return None if format is invalid

# Mock doctor availability for demo purposes
def get_doctor_availability(doctor_name):
    mock_availability = {
        "Dr. Alice Johnson": ["10:00 AM", "2:00 PM", "4:00 PM"],
        "Dr. John Smith": ["11:00 AM", "1:00 PM", "3:00 PM"]
    }
    return mock_availability.get(doctor_name, [])

# Schedule appointment via Calendly
def book_appointment_with_calendly(doctor_name, patient_name, time_slot_iso):
    url = "https://api.calendly.com/scheduled_events"  # Correct Calendly endpoint
    headers = {
        "Authorization": f"Bearer {CALENDLY_API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "event": "https://api.calendly.com/users/e03608e9-cbe2-4594-a0fc-5c5d47430e07",  # Replace with valid event type URI
        "invitee": {
            "name": patient_name,
            "email": "patient@example.com"  # Replace with actual email
        }
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        return {"message": "Appointment booked successfully"}
    else:
        return {
            "error": f"Failed to book appointment. Status: {response.status_code}, Response: {response.text}"
        }

# Cancel appointment via Calendly (if needed)
def cancel_appointment(appointment_id):
    url = f"https://api.calendly.com/scheduled_events/{appointment_id}/cancel"
    headers = {"Authorization": f"Bearer {CALENDLY_API_TOKEN}"}
    response = requests.post(url, headers=headers)

    if response.status_code == 204:
        return {"message": "Appointment canceled successfully"}
    else:
        return {
            "error": f"Failed to cancel appointment. Status: {response.status_code}, Response: {response.text}"
        }

# Reschedule appointment via Calendly
def reschedule_appointment(appointment_id, new_time_slot_iso):
    cancel_result = cancel_appointment(appointment_id)
    if "error" in cancel_result:
        return cancel_result

    # Book new appointment with the updated time slot
    # Replace "Doctor Name" and "Patient Name" with appropriate values
    return book_appointment_with_calendly("Dr. Alice Johnson", "John Doe", new_time_slot_iso)

# Chatbot API
@app.route('/chat', methods=['POST'])
def chatbot():
    data = request.json  # Receive JSON payload from the frontend
    message = data.get("message", "").lower()
    response_text = "Sorry, I didn't understand that."  # Default response

    try:
        # Handle availability request
        if "availability" in message:
            doctor_name = data.get("doctor_name", "Dr. Alice Johnson")
            availability = get_doctor_availability(doctor_name)
            response_text = f"{doctor_name} is available at: {', '.join(availability)}"

        # Handle appointment booking
        elif "book appointment" in message:
            doctor_name = data.get("doctor_name", "Dr. Alice Johnson")
            patient_name = data.get("patient_name", "John Doe")
            time_slot = data.get("time_slot", "10:00 AM")
            time_slot_iso = to_iso_format(time_slot)

            if not time_slot_iso:
                response_text = "Invalid time slot format. Please provide a valid time (e.g., '10:00 AM')."
            else:
                result = book_appointment_with_calendly(doctor_name, patient_name, time_slot_iso)
                response_text = result.get("message", result.get("error"))

        # Handle appointment rescheduling
        elif "reschedule appointment" in message:
            appointment_id = data.get("appointment_id")
            new_time_slot = data.get("new_time_slot")
            new_time_slot_iso = to_iso_format(new_time_slot)

            if not appointment_id or not new_time_slot_iso:
                response_text = "Please provide both appointment_id and a valid new_time_slot."
            else:
                result = reschedule_appointment(appointment_id, new_time_slot_iso)
                response_text = result.get("message", result.get("error"))

    except Exception as e:
        print("Error:", str(e))  # Log the error for debugging
        response_text = "An error occurred while processing your request."

    return jsonify({"response": response_text})

# Health check
@app.route("/", methods=["GET"])
def health_check():
    return "Chatbot API is running!"

if __name__ == "__main__":
    app.run(debug=True)
