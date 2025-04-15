from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils import timezone
import json
from .services import PaystackService
from .models import Payment

@csrf_exempt
@require_POST
def paystack_webhook(request):
    try:
        # Get the signature from the request header
        signature = request.headers.get('x-paystack-signature')
        if not signature:
            return HttpResponse('No signature', status=400)

        # Get the payload
        payload = json.loads(request.body)

        # Verify the signature
        paystack_service = PaystackService()
        if not paystack_service.verify_webhook_signature(payload, signature):
            return HttpResponse('Invalid signature', status=400)

        # Handle the event
        event = payload.get('event')
        data = payload.get('data')

        if event == 'charge.success':
            reference = data.get('reference')
            if not reference:
                return HttpResponse('No reference', status=400)

            # Get the payment
            payment = Payment.objects.filter(paystack_reference=reference).first()
            if not payment:
                return HttpResponse('Payment not found', status=404)

            # Update payment status
            payment.status = 'success'
            payment.metadata = data
            payment.save()

            # Update appointment status
            payment.appointment.status = 'confirmed'
            payment.appointment.save()

        return HttpResponse('Webhook processed', status=200)

    except json.JSONDecodeError:
        return HttpResponse('Invalid JSON', status=400)
    except Exception as e:
        return HttpResponse(str(e), status=500) 