from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from django.conf import settings

class TwilioNotificationService:
    def __init__(self):
        self.client = Client(
            settings.TWILIO_CONFIG['account_sid'],
            settings.TWILIO_CONFIG['auth_token']
        )
        self.notify_service = settings.TWILIO_CONFIG['notify_service_sid']

    def _create_bindings(self, user):
        bindings = []
        
        if user.notificationpreference.receive_sms and user.notificationpreference.phone:
            bindings.append(f'sms:{user.notificationpreference.phone}')
            
        if user.notificationpreference.receive_email and user.notificationpreference.email:
            bindings.append(f'email:{user.notificationpreference.email}')
            
        if user.notificationpreference.receive_push and user.notificationpreference.fcm_token:
            bindings.append(f'fcm:{user.notificationpreference.fcm_token}')
            
        return bindings

    def send_notification(self, user, message):
        try:
            bindings = self._create_bindings(user)
            if not bindings:
                return False

            notification = self.client.notify.services(self.notify_service) \
                .notifications.create(
                    to_binding=bindings,
                    body=message
                )
            return notification.status == 'sent'
            
        except TwilioRestException as e:
            print(f"Twilio Error: {str(e)}")
            return False