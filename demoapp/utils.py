# demoapp/utils.py
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def generate_verification_link(user, request):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return f"http://{request.get_host()}/verify/{uid}/{token}/"

def send_verification_email(user, request):
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email
    subject = "Verify your Email - Django App"

    link = generate_verification_link(user, request)

    context = {
        'user': user,
        'link': link
    }

    html_message = render_to_string("verify_email.html", context)

    email = EmailMultiAlternatives(subject, '', from_email, [to_email])
    email.attach_alternative(html_message, "text/html")
    email.send()



