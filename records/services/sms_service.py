"""
SMS Service Module

This module provides functionality for sending SMS notifications.
In a production environment, this would integrate with an actual SMS gateway.
For development, it will log messages to the console.
"""
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def send_sms(phone_number, message):
    """
    Send an SMS message to the specified phone number.
    
    Args:
        phone_number (str): The recipient's phone number
        message (str): The message to send
        
    Returns:
        bool: True if the message was sent successfully, False otherwise
    """
    try:
        if not phone_number or not message:
            logger.warning("SMS not sent: Missing phone number or message")
            return False
            
        # In a real application, this would connect to an SMS gateway like Twilio, Nexmo, etc.
        # For development, we'll just log the message
        logger.info(f"[SMS to {phone_number}]: {message}")
        
        # If you want to implement a real SMS service, you can uncomment and configure this:
        """
        # Example with Twilio (requires twilio package)
        # from twilio.rest import Client
        # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        # message = client.messages.create(
        #     body=message,
        #     from_=settings.TWILIO_PHONE_NUMBER,
        #     to=phone_number
        # )
        # return message.sid is not None
        """
        
        return True
    except Exception as e:
        logger.error(f"Error sending SMS to {phone_number}: {str(e)}", exc_info=True)
        return False

def send_bulk_sms(phone_numbers, message):
    """
    Send the same SMS message to multiple phone numbers.
    
    Args:
        phone_numbers (list): List of recipient phone numbers
        message (str): The message to send
        
    Returns:
        dict: A dictionary with phone numbers as keys and success status as values
    """
    results = {}
    for number in phone_numbers:
        results[number] = send_sms(number, message)
    return results
