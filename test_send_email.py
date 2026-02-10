import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Update these with YOUR actual credentials
sender = "hawkeyeinventorysystems@gmail.com"
password = "mhlw dmkq vvvq jjiq"
recipient = "connorwadesmith@gmail.com"

print(f"Testing SMTP connection...")
print(f"Sender: {sender}")
print(f"Recipient: {recipient}")

try:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "TEST Email from HawkEye"
    msg["From"] = sender
    msg["To"] = recipient
    
    text = "This is a test email to verify SMTP connectivity."
    html = "<p>This is a <b>test</b> email to verify SMTP connectivity.</p>"
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))
    
    print("Connecting to Gmail SMTP server...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        print("Connected! Logging in...")
        server.login(sender, password)
        print("Login successful! Sending email...")
        server.sendmail(sender, recipient, msg.as_string())
        print("Email sent successfully!")
        
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
