import requests
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import json


SENDER_EMAIL = "<YOUR_EMAIL>"
SENDER_PASSWORD = "<YOUR PASSWORD>"
SUBJECT = "The ISS Is Overhead!"
MESSAGE = "Take a look outside, the ISS is passing over your area!"
MY_LAT = 51.507351  # Your latitude
MY_LONG = -0.127758  # Your longitude


def send_email(email):
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = email
    msg["Subject"] = SUBJECT
    msg.attach(MIMEText(MESSAGE, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as connection:
        connection.starttls()
        connection.login(SENDER_EMAIL, SENDER_PASSWORD)
        connection.sendmail(from_addr=SENDER_EMAIL, to_addrs=email, msg=msg.as_string())


def is_iss_overhead():

    with open("locations.JSON") as file:
        locations = json.load(file)

    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data = response.json()
    iss_latitude = float(data["iss_position"]["latitude"])
    iss_longitude = float(data["iss_position"]["longitude"])

    for location, info in locations.items():
        lat_distance = abs(info["lat"] - iss_latitude)
        lng_distance = abs(info["long"] - iss_longitude)

        parameters = {
            "lat": info["lat"],
            "lng": info["long"],
            "formatted": 0,
    }

        response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
        response.raise_for_status()
        data = response.json()

        sunrise = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
        sunset = int(data["results"]["sunset"].split("T")[1].split(":")[0])

        time_now = datetime.now().hour

        if -6 < lng_distance < 6 and -6 < lat_distance < 6 and not sunrise < time_now < sunset:
            send_email(info["email"])


while True:
    is_iss_overhead()
    time.sleep(60)
