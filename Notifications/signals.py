from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone
from .models import UserNotificationPreference, Notification
from Appointments.models import Appointment
from datetime import timedelta, datetime
from .services import EmailService
from Payment.payment_service import PaystackService

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_preference(sender, instance, created, **kwargs):
    if created:
        UserNotificationPreference.objects.get_or_create(
            user=instance,
            defaults={
                'email': instance.email,
                'email_enabled': True
            }
        )

def send_notification(notification):
    """Helper function to send a notification email"""
    try:
        preference = getattr(notification.user, 'usernotificationpreference', None)
        if preference and preference.email_enabled:
            email_service = EmailService()
            success, message = email_service.send_email(
                preference.email,
                notification.subject,
                notification.message,
                notification.html_message
            )
            notification.status = 'sent' if success else 'failed'
        else:
            notification.status = 'failed'
    except Exception as e:
        notification.status = 'failed'
    finally:
        notification.save()

@receiver(post_save, sender=Appointment)
def handle_appointment_notification(sender, instance, created, **kwargs):
    if created:
        # Only send confirmation email for new appointments
        notification_type = 'appointment_created'
        subject = f'New Appointment Confirmation - {instance.service.name}'
        
        # Get payment URL
        try:
            paystack_service = PaystackService()
            payment_url = paystack_service.initialize_payment(
                appointment=instance,
                email=instance.user.email,
                amount=instance.pricing.price
            )
        except Exception as e:
            payment_url = None
        
        # Format price information
        price_info = ""
        if instance.pricing:
            price_info = f"Price: {instance.pricing.currency} {instance.pricing.price}"
        
        # Create and send immediate notification
        notification = Notification.objects.create(
            user=instance.user,
            notification_type=notification_type,
            subject=subject,
            message=f'Your appointment for {instance.service.name} is scheduled for {instance.timeslot.date} at {instance.timeslot.start_time}. {price_info}',
            html_message=f'''
                <h2>{notification_type.replace("_", " ").title()}</h2>
                <p>Service: {instance.service.name}</p>
                <p>Date: {instance.timeslot.date.strftime("%B %d, %Y")}</p>
                <p>Time: {instance.timeslot.start_time.strftime("%I:%M %p")}</p>
                <p>Duration: {instance.timeslot.start_time.strftime("%I:%M %p")} - {instance.timeslot.end_time.strftime("%I:%M %p")}</p>
                {f'<p>Price: {instance.pricing.currency} {instance.pricing.price}</p>' if instance.pricing else ''}
                {f'<p><a href="{payment_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 20px;">Pay Now</a></p>' if payment_url else ''}
                <p>Please be on time for your appointment.</p>
                <h3>Thank you for choosing <strong>Easybook</strong>!</h3>
                ''',
            scheduled_at=timezone.now()
        )
        send_notification(notification)
    else:
        # Handle appointment updates
        notification_type = 'appointment_updated'
        subject = f'Appointment Update - {instance.service.name}'
        
        # Format price information
        price_info = ""
        if instance.pricing:
            price_info = f"Price: {instance.pricing.currency} {instance.pricing.price}"
        
        notification = Notification.objects.create(
            user=instance.user,
            notification_type=notification_type,
            subject=subject,
            message=f'Your appointment for {instance.service.name} has been updated. It is now scheduled for {instance.timeslot.date} at {instance.timeslot.start_time}. {price_info}',
            html_message=f'''
                <h2>{notification_type.replace("_", " ").title()}</h2>
                <p>Service: {instance.service.name}</p>
                <p>Date: {instance.timeslot.date.strftime("%B %d, %Y")}</p>
                <p>Time: {instance.timeslot.start_time.strftime("%I:%M %p")}</p>
                <p>Duration: {instance.timeslot.start_time.strftime("%I:%M %p")} - {instance.timeslot.end_time.strftime("%I:%M %p")}</p>
                {f'<p>Price: {instance.pricing.currency} {instance.pricing.price}</p>' if instance.pricing else ''}
                <p>Please be on time for your appointment.</p>
                <h3>Thank you for choosing <strong>Easybook</strong>!</h3>
            ''',
            scheduled_at=timezone.now()
        )
        send_notification(notification)

@receiver(post_save, sender=Appointment)
def handle_appointment_reminder(sender, instance, **kwargs):
    """Handle appointment reminders 24 hours before the appointment"""
    reminder_time = timezone.make_aware(datetime.combine(instance.timeslot.date, instance.timeslot.start_time)) - timedelta(hours=24)
    
    # Only create and send reminder if we're within 1 minute of the reminder time
    if abs((timezone.now() - reminder_time).total_seconds()) <= 60:
        reminder_notification = Notification.objects.create(
            user=instance.user,
            notification_type='appointment_reminder',
            subject=f'Reminder: Upcoming Appointment - {instance.service.name}',
            message=f'This is a reminder that you have an appointment for {instance.service.name} tomorrow at {instance.timeslot.start_time}.',
            html_message=f'''
                <h2>Appointment Reminder</h2>
                <p>Don't forget about your appointment tomorrow!</p>
                <p>Service: {instance.service.name}</p>
                <p>Time: {instance.timeslot.start_time.strftime("%I:%M %p")}</p>
                <p>Duration: {instance.timeslot.start_time.strftime("%I:%M %p")} - {instance.timeslot.end_time.strftime("%I:%M %p")}</p>
                <p>Please be on time for your appointment.</p>
                <h3>Thank you for choosing <strong>Easybook</strong>!</h3>
            ''',
            scheduled_at=timezone.now()
        )
        send_notification(reminder_notification)

@receiver(post_delete, sender=Appointment)
def handle_appointment_cancellation(sender, instance, **kwargs):
    notification = Notification.objects.create(
        user=instance.user,
        notification_type='appointment_cancelled',
        subject=f'Appointment Cancelled - {instance.service.name}',
        message=f'Your appointment for {instance.service.name} scheduled for {instance.timeslot.date} at {instance.timeslot.start_time} has been cancelled.',
        html_message=f'''
            <h2>Appointment Cancelled</h2>
            <p>Your appointment has been cancelled.</p>
            <p>Service: {instance.service.name}</p>
            <p>Original Date: {instance.timeslot.date.strftime("%B %d, %Y")}</p>
            <p>Original Time: {instance.timeslot.start_time.strftime("%I:%M %p")}</p>
            <h3>Thank you for choosing <strong>Easybook</strong>!</h3>
        ''',
        scheduled_at=timezone.now()
    )
    send_notification(notification)