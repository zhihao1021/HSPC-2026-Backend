from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from os import getenv
from smtplib import SMTP
import ssl
from dotenv import load_dotenv
load_dotenv(".env.development")

SMTP_USERNAME = getenv("SMTP_USERNAME")
SMTP_PASSWORD = getenv("SMTP_PASSWORD")
SMTP_HOST = getenv("SMTP_HOST")
SMTP_PORT = int(getenv("SMTP_PORT", "587"))
SENDER_EMAIL = getenv("SMTP_SENDER")

if SMTP_USERNAME is None or SMTP_PASSWORD is None or SMTP_HOST is None or SENDER_EMAIL is None:
    raise RuntimeError(
        "SMTP configuration is incomplete. Please set SMTP_USERNAME, SMTP_PASSWORD, SMTP_HOST, and SMTP_SENDER in the environment variables.")

BODY_TEXT = "This Body text"
BODY_HTML = """<html>
<body>
  <h1>Amazon SES SMTP Email Test</h1>
  <p>This email was sent with Amazon SES using the
    <a href='https://www.python.org/'>Python</a>
    <a href='https://docs.python.org/3/library/smtplib.html'>smtplib</a> library.</p>
</body>
</html>
"""

# Create the root message and set the headers
msg = MIMEMultipart("alternative")
msg["Subject"] = "Test"
msg["From"] = SENDER_EMAIL
msg["To"] = "contact@chih-hao.xyz"

part1 = MIMEText(BODY_TEXT, "plain")
part2 = MIMEText(BODY_HTML, "html")
msg.attach(part1)
msg.attach(part2)

context = ssl.create_default_context()
try:
    with SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(
            SENDER_EMAIL,
            to_addrs=["contactl@chih-hao.xyz"],
            msg=msg.as_string()
        )
        server.close()
        print("Email sent successfully!")
    # server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    # server.ehlo()
    # server.starttls(context=context)
    # server.ehlo()
    # server.login(SMTP_USERNAME, SMTP_PASSWORD)
    # server.sendmail(SENDER_EMAIL, "noreply@dev.chih-hao.xyz", msg.as_string())
    # print("Email sent successfully!")
    # server.quit()
except Exception as e:
    print(f"Error: {e}")
