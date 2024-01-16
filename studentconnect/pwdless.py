import jwt
import email
import smtplib
from jinja2 import Environment, PackageLoader
from datetime import datetime

env = Environment(loader = PackageLoader("studentconnect"))


def generate_token(user):
    payload = {
        "sub": user['id'],
        "exp": datetime.now().timestamp() + 300
    }
    token = jwt.encode(payload, user['secret'], algorithm="HS256")
    return token


def verify_token(token, db):
    payload = jwt.decode(token, algorithms="HS256", options={"verify_signature": False})
    user = db.execute("SELECT * FROM user WHERE id = ?", (payload['sub'],)).fetchone()
    if user is None:
        return None
    secret = user['secret']
    payload_verified = jwt.decode(token, secret, algorithms="HS256")
    return payload_verified["sub"]

def send_token(token, user, base_url):
    token_url = '?token='.join([base_url, token])

    details = {
        'name': user['FirstName'],
        'token_url': token_url
    }

    msg = email.message.EmailMessage()
    msg['Subject'] = "Magic link"
    msg['From'] = email.headerregistry.Address(
        "Student Connect", "studentconnect", "davidohuabunwa.net"
        )
    msg['To'] = email.headerregistry.Address(addr_spec=user['email'])
    msg.set_content(env.get_template("pwdless/email.txt").render(details))
    msg.add_alternative(env.get_template("pwdless/email.html").render(details), subtype='html')

    server = smtplib.SMTP_SSL("smtp.sendgrid.net", 465)
    server.login("apikey", "secret")
    server.send_message(msg)
    server.quit()

    print(token)
