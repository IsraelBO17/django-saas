from .helpers import USER_FORGOT_PASSWORD, USER_VERIFY_ACCOUNT, hash_text


def send_verification_email(user):
    string_context = user.get_context_string(context=USER_VERIFY_ACCOUNT)
    token = hash_text(string_context)

    user.email_user(
        subject='Verification Email',
        message=f'Verify your account with this token:{token}, and uid:{user.pk}',
        fail_silently=True
    )

def send_successful_verification_email(user):    
    user.email_user(
        subject='Successful Verification',
        message='This is to notify you that you are been verified.',
        fail_silently=True
    )

def send_password_reset_email(user):
    string_context = user.get_context_string(context=USER_FORGOT_PASSWORD)
    token = hash_text(string_context)

    user.email_user(
        subject='Reset Password',
        message=f'Reset your password with this token:{token}, and uid:{user.pk}',
        fail_silently=True
    )

def send_successful_password_reset_email(user):    
    user.email_user(
        subject='Successful Password Reset',
        message='This is to notify you that you have successfully rest your password. Kindly, reach out to HR or Admin if this was done without your knowledge.',
        fail_silently=True
    )

def send_deactivation_email(user):    
    user.email_user(
        subject='Dectivation Email',
        message='This is to notify you that you are been deactivated. Kindly, reach out to HR or Admin.',
        fail_silently=True
    )

