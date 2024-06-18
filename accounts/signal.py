# signals.py

# from django.dispatch import receiver
# from admin_honeypot.signals import honeypot

# @receiver(honeypot)
# def handle_honeypot(sender, **kwargs):
#     # Your custom logic here to handle honeypot signals
#     print(f"Honeypot triggered: {sender}")
#     # Example: Log the request details
#     request = kwargs.get('request')
#     if request:
#         print(f"Request from: {request.META.get('REMOTE_ADDR')}")
