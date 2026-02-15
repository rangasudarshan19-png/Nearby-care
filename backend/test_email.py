import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_email():
    sender = "nnearbycare@gmail.com"
    password = "afstbmbkaizifiry"
    recipient = "nnearbycare@gmail.com"  # Send to self for testing
    
    print(f"Testing email with:")
    print(f"  Sender: {sender}")
    print(f"  Password length: {len(password)}")
    print(f"  Password: {password}")
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Test Email"
        msg["From"] = sender
        msg["To"] = recipient
        
        html = "<html><body><h1>Test Email</h1><p>If you receive this, email is working!</p></body></html>"
        msg.attach(MIMEText(html, "html"))
        
        print("\nConnecting to Gmail SMTP server...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            print("Logging in...")
            server.login(sender, password)
            print("Sending email...")
            server.sendmail(sender, recipient, msg.as_string())
            print("✓ Email sent successfully!")
            return True
            
    except Exception as e:
        print(f"\n✗ Email error: {e}")
        print("\nPossible solutions:")
        print("1. Verify the app password is correct (no spaces)")
        print("2. Check if 2-Step Verification is enabled on the Gmail account")
        print("3. Regenerate the app password from Google Account settings")
        print("4. Make sure 'Less secure app access' is not blocking it")
        return False

if __name__ == "__main__":
    test_email()
