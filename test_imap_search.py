import imaplib
from imaplib import IMAP4_SSL
import os
from dotenv import load_dotenv

load_dotenv(".env")
imap_host = 'imap.gmail.com'
imap_user = os.environ.get('EMAIL_HOST_USER')
imap_pass = os.environ.get('EMAIL_HOST_PASSWORD')
mail = IMAP4_SSL(imap_host)
mail.login(imap_user, imap_pass)
mail.select("inbox")

try:
    s, m = mail.search(None, 'X-GM-RAW', '"subject:Notificación"'.encode("utf-8"))
    print("Success with X-GM-RAW:", s)
except Exception as e:
    print("Error with X-GM-RAW:", e)

