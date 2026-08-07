from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed

# SEND EMAIL FUNCTION FOR ALL TYPES OF EMAILS LIKE VERIFICATION, PASSWORD RESET, ORDER CONFIRMATION, ETC.
def send_email(subject,message,recipient_list):
    try:
        from_email = getattr(settings, 'EMAIL_HOST_USER', None) or 'noreply@ecommerce.com'
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=True,
        )
        return True
    except Exception:
        return False

# Utility function to generate JWT tokens for a user
def get_tokens_for_user(user):
    if not user.is_active:
        raise AuthenticationFailed('User is not active.')

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }