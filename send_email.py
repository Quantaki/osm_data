import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

def send_email(subject, body):
    # Email configuration
    sender_email = 'bentorcha.data@gmail.com'
    sender_password = 'pmlcaenhqdnkjvqa'
    receiver_email = 'karimbentorcha@gmail.com'
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    # Create a MIME message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = Header(subject)

    # Attach the body of the email
    message.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()

        print("Email notification sent successfully!")
    except Exception as e:
        print(f"Error sending email notification: {str(e)}")