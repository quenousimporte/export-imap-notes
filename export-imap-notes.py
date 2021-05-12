from markdownify import markdownify
import imaplib
import email
from email.header import decode_header
import os

username = ""
password = ""

if not os.path.isdir('notes'):
    os.mkdir('notes')

def clean(text):
    return "".join(c if c.isalnum() else "_" for c in text)

# number of top emails to fetch
N = 200

imap = imaplib.IMAP4_SSL("imap.fastmail.com")
imap.login(username, password)

status, messages = imap.select("Notes")

messages = int(messages[0])

for i in range(messages, messages-N, -1):
    res, msg = imap.fetch(str(i), "(RFC822)")
    for response in msg:
        if isinstance(response, tuple):
            msg = email.message_from_bytes(response[1])
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding)

            From, encoding = decode_header(msg.get("From"))[0]
            if isinstance(From, bytes):
                From = From.decode(encoding)

            print(subject)
            filepath = clean(subject) + '.md'
            filepath = os.path.join('notes', filepath)

            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    try:
                        body = part.get_payload(decode=True).decode()
                    except:
                        pass

                    if content_type == "text/plain" and "attachment" not in content_disposition:
                         open(filepath, "w").write(body)
                    elif "attachment" in content_disposition:
                        print('/!\\ attachment')
            else:
                content_type = msg.get_content_type()
                body = msg.get_payload(decode=True).decode()
                if content_type == "text/plain":
                    open(filepath, "w").write(body)

            if content_type == "text/html":
                md = markdownify(body)
                if md[:4] == 'html':
                    md = md[4:]

                open(filepath, "wb").write(md.encode('utf8'))

imap.close()
imap.logout()