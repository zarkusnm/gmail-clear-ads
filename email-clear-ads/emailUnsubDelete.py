# required imports, pip install each in command prompt to run program
import imaplib
import email
import re
import requests
from bs4 import BeautifulSoup



# imap server address corresponding to email account
''' gmail: imap.gmail.com , yahoo: imap.mail.yahoo.com , yahoo mail plus: plus.imap.mail.yahoo.com , yahoo mail uk: imap.mail.yahoo.co.uk , yahoo mail deutschland : imap.mail.yahoo.com , 
yahoo mail au/nz : imap.mail.yahoo.au , aol.com : imap.aol.com , at&t : imap.att.yahoo.com , NTL @ntlworld.com : imap.ntlworld.com , btconnect : imap4.btconnect.com , o2 deutschland : imap.o2online.de ,
t-online deutschland : secureimap.t-online.de , 1&1 : imap.1and1.com , 1&1 deutschland : imap.1und1.de , verizon : incoming.verizon.net , zoho mail : imap.zoho.com , mail.com : imap.mail.com , gmx.com : imap.gmx.com ,
net address by usa.net : imap.postoffice.net
'''

imap_server = 'imap.gmail.com'


# method that performs unsubscribing and deleting function
# requires amount of emails you want to scan through, email, specific app password (not general password), keyword set to look for, and exception set also to look for 
def clearSpam( numScanning , email_address , password, keywords, xeptions ):
    # initiate list of links
    unsublinks=[]
    unsubfinds=0
    # logging in to imap server with email and app!!! password
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

        # fetches string if fetch was successful and tuple of email parts in RFC822 (header+body) formatting
        status, msg_data = m.fetch(num, '(RFC822)')

        # checking fetch status, if fails goes to next email
        if status != 'OK':
            print(f"Failed to fetch email with ID: {num}")
            continue

        # loops through each part of email tuple from header to body
        for response_part in msg_data:

            if isinstance(response_part, tuple):
                # email method that returns an EmailMessage object from the raw email data
                msg = email.message_from_bytes(response_part[1])
                email_body = ""
                # this part of the code decodes each part of the raw EmailMessage object and concats the readable text to
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
                                print(f"{num} has a decoding error, check the html")
                else:
                    try:
                        email_body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except UnicodeDecodeError:
                        email_body = msg.get_payload(decode=True).decode('latin-1', errors='ignore')
                # finally checks full string of email decoded text for the keywords and then proceeds
                # with finding the link in html and requesting to click the link
                if any(keyword in email_body.lower() for keyword in keywords):
                    # checks if any of the exception words/phrases are found in the email, then passes through if false
                    if not any(xeption in email_body.lower() for xeption in xeptions):
                        print(f"Unsubscribe found in {num}")
                        unsubfinds += 1
                        # parses email body for all html and stores in soup var
                        soup = BeautifulSoup(email_body, 'html.parser')
                        

                        # creates regex compatible string for all keywords
                        pattern = '|'.join(keywords)
                        link_regex = re.compile(pattern, re.IGNORECASE)
                        

                        # grabs all links in the body of the email
                        links = soup.find_all('a', href=True)

                        # for each link in the html of the email, if a keyword is in the link, append unsublinks to have that link
                        # so that it equals the link with name 'unsubscribe' or keyword 
                        if links:
                            checker1 = len(unsublinks)
                            for link in links:
                                if link_regex.search(link['href']) and checker1 == len(unsublinks):
                                    unsublinks.append(link['href'])
                            if checker1 != len(unsublinks):
                                print("Unsub link found")
                        # stores email in deletion queue regardless if a link was found or not
                        m.store(num, '+FLAGS', '\\Deleted')
                        # decrements scanned emails
                        numScanning -= 1
                    else:
                        print(f"Exception in {num}")
                        # decrements scanned emails
                        numScanning -= 1
                else:
                    print(f"No unsubscribe in {num}")
                    # decrements scanned emails
                    numScanning -= 1
    # prints percent of emails with a keyword in them that returned a link
    try:
        print(f"{(len(unsublinks)/unsubfinds)*100} percent of emails with a keyword in them returned a link!")
    except:
        print("No keywords found")
    # prints all found links after attempting to unsubscribe from each, returning if successful as well, separated by lines of ==
    if unsublinks:
        for value in unsublinks:
            print("===================================================================================================================================================")
            response = requests.get(value)
            if response.status_code == 200:
                print("Unsubscribed successfully! (Check link to verify)")
                print(value)
                print("===================================================================================================================================================")
            else:
                print("Manual Unsubscription Needed, Click Here To Confirm:")
                print(value)
                print("===================================================================================================================================================")
    # clears deletion queue and logs out of email
    m.expunge()
    m.logout()

    print(f"Logged out and completed")

# inputs, placeholder values given below
keywords = { "unsubscribe" , "opt out", "email preferences"}
xeptions = {"amazon", "ebay"}
clearSpam(2000, "email@gmail.com", "app password", keywords, xeptions)
