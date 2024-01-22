import random
from django.core.mail import send_mail
from .models import OTP


def generate_and_send_otp(request, user_data):
    # Generate a 6-digit OTP.
    otp = ''.join(random.choice('1234567890') for _ in range(6))
    # Store the OTP and the user data in the session
    request.session['otp'] = otp
    request.session['register_form_data'] = user_data

    # Send the OTP to the user's email.
    subject = 'One-Time Password'
    message = f'Your one-time password for confirming your Email: {otp}'
    from_email = 'your@example.com'
    recipient_list = [user_data['email']]

    send_mail(subject, message, from_email, recipient_list)
