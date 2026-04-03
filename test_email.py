import smtplib, os, socket, datetime
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

sender   = "shivprajapati2060@gmail.com"
password = os.getenv("GMAIL_APP_PASSWORD", "")

print("Password loaded :", repr(password))
print("Password length :", len(password))

desktop = socket.gethostname()
ip      = socket.gethostbyname(desktop)
now     = datetime.datetime.now().strftime("%A, %d %B %Y at %I:%M:%S %p")

body = f"Desktop: {desktop}\nIP: {ip}\nTime: {now}"
msg  = MIMEText(body, "plain", "utf-8")
msg["Subject"] = "OMNI Login Alert Test"
msg["From"]    = sender
msg["To"]      = sender

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as s:
        print("Connected to Gmail SMTP")
        s.login(sender, password)
        print("Login OK")
        s.sendmail(sender, sender, msg.as_string())
        print("Email sent successfully!")
except smtplib.SMTPAuthenticationError as e:
    print("AUTH ERROR:", e)
except smtplib.SMTPException as e:
    print("SMTP ERROR:", e)
except Exception as e:
    print("OTHER ERROR:", type(e).__name__, e)
