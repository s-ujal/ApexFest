# from participantINFO.models import Student
import time
from django.core.mail import send_mail
from django.conf import settings

def run_this_funtion():
    print("function started")
    print("function started...")

    time.sleep(2)
    print("fucntion executed")

def send_email_to_client(email):
    subject = "Apex Fest"
    message = "HII you successfully login the Apexfest!"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [str(email)]
    send_mail(subject,message,from_email,recipient_list)
