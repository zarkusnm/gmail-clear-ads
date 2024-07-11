This program uses IMAPlib to unsubscribe and delete all emails with a set of keywords in the email body, excluding emails with a set of exception words in the email body.
The continuous problem I am trying to solve with this program is the purposeful tedious nature of unsubscribing from auto-subscription email lists that market constantly and clutter your email box.
The issue and reason there are not a lot of good tools out there to do this (without stealing your data and subscribing you to MORE of these marketing lists like unroll.me) is because there is not a
universal email formatting for unsubscriptions, specifically because companies want to continue marketing as much as possible and get around tools like this.

Under the 2003 CAN-SPAM Act, quote:
"This Act establishes requirements for those who send unsolicited commercial email. The Act bans false or misleading header information and prohibits deceptive subject lines. It also requires that unsolicited commercial email be identified as advertising and provide recipients with a method for opting out of receiving any such email in the future."

Which guarantees there is some way for people to unsubscribe from pesky emails, although companies get around this by forcing you to go through multiple pages, check boxes, and changing the names of the link to things like
"email preferences", "opting out", etc. to prevent bots from scraping through and mass unsubscribing (like I attempt to do). Most companies assume correctly that the average person will not go through every email manually to unsubscribe, but hopefully this program makes that easier to do, with my deleting of emails, grabbing and listing of links, and using exceptions and keywords to snatch all possible instances you want to delete.

Can't use http requests for a 200 status code check because:
The initial request (which gets a 200 status code) only indicates that this page was successfully reached, not that the subsequent actions were completed.
If your code checks for a 200 status code and assumes unsubscription, it can lead to false positives. This is because the successful loading of the page does not necessarily mean that the unsubscription was performed. The page might require additional user actions to complete the process.


Requires import of IMAPlib, email, regex, requests, and beautifulsoup
