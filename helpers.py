from confidential import password
import smtplib, ssl
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def read_template(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
        t_file_content = template_file.read()
    return Template(t_file_content)

def send_reminder(recipient):
    """Sends reminder email to recipient using SMTP_SSL()"""

    sender_email = "team.optimal.app@gmail.com"
    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.starttls()

    message_template = read_template('message.txt')
    msg = MIMEMultipart()
    message = message_template.substitute(USERNAME=recipient.username)

    msg['FROM'] = sender_email
    msg['TO'] = recipient.email
    msg['Subject'] = "A Friendly Reminder to Complete Your Optimal Survey"

    msg.attach(MIMEText(message, 'plain'))

    try:
        s.login(sender_email, password)
        s.send_message(msg)
        del msg
    except Exception as e:
        print(e)
    finally:
        s.quit()

