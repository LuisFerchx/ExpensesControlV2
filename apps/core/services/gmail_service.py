import os
import email
import imaplib
from email.header import decode_header
from django.conf import settings

def fetch_bank_emails(mail_address, subject, start_date, end_date):
    """
    Fetches emails matching the given criteria using IMAP.
    Requires EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in settings via .env.
    """
    # IMAP settings for Gmail
    imap_host = 'imap.gmail.com'
    imap_user = os.environ.get('EMAIL_HOST_USER')
    imap_pass = os.environ.get('EMAIL_HOST_PASSWORD')
    
    if not imap_user or not imap_pass:
        print("Missing EMAIL_HOST_USER or EMAIL_HOST_PASSWORD in .env")
        return []

    try:
        # Connect to the server
        mail = imaplib.IMAP4_SSL(imap_host)
        # Login
        mail.login(imap_user, imap_pass)
        # Select mailbox
        mail.select("inbox")

        # Format dates for IMAP search: DD-Mon-YYYY
        # Example: 01-Jan-2023
        start_str = start_date.strftime("%d-%b-%Y")
        end_str = end_date.strftime("%d-%b-%Y")

        # Construct IMAP search query
        # We search SINCE start_date and BEFORE end_date
        # Using specific sender and subject
        search_criteria = []
        if mail_address:
            if mail_address.isascii():
                search_criteria.append(f'FROM "{mail_address}"')
        
        # Add subject to IMAP search only if it is ASCII to avoid IMAP encoding errors.
        # Otherwise, we will filter it in Python below.
        if subject and subject.isascii():
            search_criteria.append(f'SUBJECT "{subject}"')
        
        search_criteria.append(f'SINCE "{start_str}"')
        search_criteria.append(f'BEFORE "{end_str}"')
        
        query = f'({ " ".join(search_criteria) })'
        
        status, messages = mail.search(None, query)
        
        if status != "OK":
            print(f"IMAP search failed: {status}")
            return []
            
        email_ids = messages[0].split()
        email_data = []

        for email_id in email_ids:
            # Fetch the email
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            if status != "OK":
                continue
                
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    # Parse the raw email bytes
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Extract subject
                    header_subject = msg.get('Subject', '')
                    msg_subject = ""
                    if header_subject:
                        decoded_list = decode_header(header_subject)
                        for text, encoding in decoded_list:
                            if isinstance(text, bytes):
                                enc = encoding if encoding else 'utf-8'
                                try:
                                    msg_subject += text.decode(enc)
                                except (LookupError, UnicodeDecodeError):
                                    msg_subject += text.decode('utf-8', errors='ignore')
                            else:
                                msg_subject += str(text)
                    
                    # Extract sender
                    msg_from = msg.get('From', '')
                    
                    # Apply Python filters for anything skipped in IMAP query
                    if mail_address and not mail_address.isascii():
                        if mail_address.lower() not in msg_from.lower():
                            continue
                    
                    if subject and not subject.isascii():
                        if subject.lower() not in msg_subject.lower():
                            continue
                            
                    # Extract date
                    msg_date = msg.get('Date', 'No Date')
                    
                    # Extract body
                    body = get_email_body(msg)
                    
                    email_data.append({
                        'id': email_id.decode('utf-8'),
                        'subject': msg_subject,
                        'date': msg_date,
                        'body': body
                    })
                    
        # Logout
        mail.close()
        mail.logout()
        return email_data
        
    except Exception as e:
        print(f"An error occurred fetching emails via IMAP: {e}")
        return []

def get_email_body(msg):
    """
    Recursively extracts the email body from the message object.
    Tries to prefer plain text, but will fallback to HTML.
    """
    body = ""
    if msg.is_multipart():
        # Iterate over parts
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if "attachment" not in content_disposition:
                try:
                    part_body = part.get_payload(decode=True)
                    if part_body:
                        decoded_body = part_body.decode(part.get_content_charset() or 'utf-8', errors='ignore')
                        if content_type == "text/plain":
                            return decoded_body  # Prefer plain text, return immediately
                        elif content_type == "text/html":
                            body = decoded_body  # Save html body as fallback
                except Exception:
                    pass
    else:
        try:
            part_body = msg.get_payload(decode=True)
            if part_body:
                 body = part_body.decode(msg.get_content_charset() or 'utf-8', errors='ignore')
        except Exception:
            pass
            
    return body
