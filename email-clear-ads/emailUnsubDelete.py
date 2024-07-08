
import imaplib
import email
import re
import requests
from bs4 import BeautifulSoup

# imap server address corresponding to email account
imap_server = 'imap.gmail.com'

# method that performs unsubscribing and deleting function
# requires amount of emails you want to scan through, email, and specific app password
def clearSpam( numScanning , email_address , password ):

    # logging in to imap server with email and app password
    try:
        m = imaplib.IMAP4_SSL(imap_server)
        m.login(email_address, password)
        print("Logged in successfully")
    except imaplib.IMAP4.error as e:
        print(f"Login failed: {e}")
        return

    # specific inbox selected for unsubscribing and deletion
    m.select('inbox')

    # searching through all emails in inbox for inbox status and unique IDs
    status, email_ids = m.search(None, 'ALL')
    if status != 'OK':
        print("Failed to search emails")
        return

    # splitting tuple formatted like ["status" , ['b' 1 2 3 4 5...]] into ["status", ['b' 1, 'b' 2,...]]
    email_ids = email_ids[0].split()
    # reversing ID order so scanning is chronological, then printing how many IDs total were found
    email_ids.reverse()
    print(f"Found {len(email_ids)} emails")

    # looping through every email ID from largest to smallest
    for num in email_ids:
        # end condition, once numScanning reaches zero
        if numScanning < 1:
            break

        # fetches string if fetch was successful and tuple of emails in RFC822 (header+body) formatting
        status, msg_data = m.fetch(num, '(RFC822)')

        # checking fetch status if fails then goes to next email
        if status != 'OK':
            print(f"Failed to fetch email with ID: {num}")
            continue

        # loops through each part of email tuple from header to body
        for response_part in msg_data:

            if isinstance(response_part, tuple):
                # email method that returns an EmailMessage object from the raw email data
                msg = email.message_from_bytes(response_part[1])
                email_body = ""
                # this part of the code decodes each part of the EmailMessage object and concats the readable text to
                # an email_body string, that then will be searched through for the word 'unsubscribe'
                # some emails may have unsubscribe links hidden under other names like "email preferences",
                # so I will work to give the code multiple success pathways, and also exceptions for emails
                # from certain companies that you may want to keep
                if msg.is_multipart():
                    for part in msg.walk():
                        # checks message type then attempts to decode into UTF-8 or LATIN-1 readable text
                        if part.get_content_type() == "text/plain":
                            try:
                                email_body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            except UnicodeDecodeError:
                                email_body += part.get_payload(decode=True).decode('latin-1', errors='ignore')
                        elif part.get_content_type() == 'text/html':
                            try:
                                email_body += part.get_payload(decode=True).decode()
                            except UnicodeDecodeError:
                                print(f"{num} has uncommon characters")
                else:
                    try:
                        email_body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except UnicodeDecodeError:
                        email_body = msg.get_payload(decode=True).decode('latin-1', errors='ignore')
                # finally checks full string of email decoded text for the word unsubscribe and then proceeds
                # with finding the link in html and requesting to click the link
                if 'unsubscribe' in email_body.lower():
                    print(f"Unsubscribe found in email ID: {num}")
                    # parses email body for all html and stores in soup var
                    soup = BeautifulSoup(email_body, 'html.parser')
                    unsubscribe_link = None

                    # Regex to find unsubscribe link
                    link_regex = re.compile(r'unsubscribe', re.IGNORECASE)

                    # for each link in the html of the email, if unsubscribe is in the link, update unsubscribe_link
                    # so that it equals the link with name 'unsubscribe'
                    for link in soup.find_all('a', href=True):
                        if link_regex.search(link['href']):
                            unsubscribe_link = link['href']
                            break

                    # clicks unsubscribe link if found and returns link
                    if unsubscribe_link:
                        response = requests.get(unsubscribe_link)

                        if response.status_code == 200:
                            print(f"Unsubscribed successfully from: {unsubscribe_link}")
                        else:
                            print(f"Failed to unsubscribe from: {unsubscribe_link}")
                    else:
                        print("No unsubscribe link found.")
                    # stores email in deletion queue regardless if a link was found or not
                    m.store(num, '+FLAGS', '\\Deleted')
                    # decrements scanned emails
                    numScanning -= 1
                else:
                    print(f"No unsubscribe in email ID: {num}")
                    # decrements scanned emails
                    numScanning -= 1
    # clears deletion queue and logs out of email
    m.expunge()
    m.logout()
    print(f"Logged out and completed")

''' thinking about clearing decoding segment for unnecessary code and checks, as well as just printing all 
unsubscribe links once found and adding a way for exceptions in emails to be included, as well as a way for
exceptions that don't mention unsubscribe in their links to be caught, perhaps by decoding then just requesting the
final link in the body once the word unsubscribe is found?
'''
clearSpam(1, "email@gmail.com", "password")