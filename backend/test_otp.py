"""
Test script to verify OTP email sending
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, get_smtp_credentials, send_email
import smtplib

print("="*60)
print("OTP EMAIL SENDING TEST")
print("="*60)
print()

# Test email config
with app.app_context():
    sender, password, smtp_server, smtp_port = get_smtp_credentials()
    
    print(f"Sender Email: {sender}")
    print(f"SMTP Server: {smtp_server}")
    print(f"SMTP Port: {smtp_port}")
    print()
    
    # Test SMTP connection
    print("Testing SMTP connection...")
    try:
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=20)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=20)
            server.starttls()
        with server:
            server.login(sender, password)
        print("✓ SMTP Connection successful!")
        print()
        
        # Test sending OTP
        print("Generating test OTP...")
        test_otp = "123456"
        test_email = sender  # Send to self for testing
        
        print(f"Sending test OTP to: {test_email}")
        result = send_email(test_email, test_otp)
        
        if result:
            print("✓ OTP Email sent successfully!")
            print(f"Check your inbox at {test_email}")
        else:
            print("✗ Failed to send OTP email")
            
    except smtplib.SMTPAuthenticationError as e:
        print(f"✗ SMTP Authentication Failed: {e}")
        print("Please check your email and app password are correct")
    except smtplib.SMTPException as e:
        print(f"✗ SMTP Error: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")

print()
print("="*60)
