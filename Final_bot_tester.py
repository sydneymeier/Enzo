#!/usr/bin/env python
# coding: utf-8
#!/usr/bin/env python


import imaplib
import email
from email.header import decode_header

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import webbrowser
import os
import re


def read_emails(username,password,chosen_emails):
    imap = imaplib.IMAP4_SSL("imap.googlemail.com",993)
    imap.login(username, password)
    imap.select("INBOX")
    _, search_data = imap.search(None,"UNSEEN")
    info = []
    leads = 0
    if search_data == [b'']:
        pass
    else:
        for num in search_data[0].split():
            res, msg = imap.fetch(num, "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):
                    msg = email.message_from_bytes(response[1])
                    subject = decode_header(msg["Subject"])[0][0]
                    from_ = msg.get("From")
                    if any(email in from_ for email in chosen_emails):
                        leads += 1
                        #print("Subject:", subject)
                        #print("From:", from_)
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))
                                try:
                                    body = part.get_payload(decode=True).decode()
                                    info.append(body)
                                except:
                                    pass
                                if content_type == "text/plain" and "attachment" not in content_disposition:
                                    pass
                                    #print(body)
                                elif "attachment" in content_disposition:
                                    filename = part.get_filename()
                                    if filename:
                                        if not os.path.isdir(subject):
                                            os.mkdir(subject)
                                        filepath = os.path.join(subject, filename)
                                        open(filepath, "wb").write(part.get_payload(decode=True))
                        else:
                            content_type = msg.get_content_type()
                            body = msg.get_payload(decode=True).decode()
                            if content_type == "text/plain":
                                pass
                                #print(body)
    if leads == 1:
        response = "You have " + str(leads) + " new lead."
    else:
        response = "You have " + str(leads) + " new leads."
    print(response)
    imap.close()
    imap.logout()
    return(info)


def type1(bod):
    x = bod.split()
    beg = x.index("your") +1
    end = beg + x[beg:].index("You")
    vehicle = " "
    vehicle = vehicle.join(x[beg:end])
    vehicle = vehicle[:-1]
    try:
        g = x.index("Email:") + 1
        second = x[g]
    except ValueError:
        phone = ""
        p = x.index("Phone:")+1
        s = x.index("Stock")
        second = phone.join(x[p:s])
    try:
        comment = ' '
        start = x.index("Comments:")
        comment = comment.join(x[start+1:])
    except ValueError:
        comment = "No comment."
    start = 0
    for i in range(len(x)):
        matchN = re.search("Name:",x[i])
        if matchN:
            start = i + 1
            break
        else:
            pass
    name = x[start] + ' ' + x[start+1]
    return [name, second, vehicle, comment]


def type2(bod):
    x = bod.split()
    beg = x.index("your") +1
    end = beg + x[beg:].index("I'm")
    vehicle = " "
    vehicle = vehicle.join(x[beg:end])
    vehicle = vehicle[:-1]
    try:
        g = x.index("Email:") + 1
        second = x[g]
    except ValueError:
        phone = ""
        p = x.index("Phone:")+1
        s = x.index("Stock")
        second = phone.join(x[p:s])
    try:
        comment = ' '
        start = x.index("Comments:")
        comment = comment.join(x[start+1:])
    except ValueError:
        comment = "No comment."
    start = 0
    for i in range(len(x)):
        matchN = re.search('Name:',x[i])
        if matchN:
            start = i + 1
            break
        else:
            pass
    name = x[start] + ' ' + x[start+1]
    return [name, second, vehicle, comment]


def type3(bod):
    x = bod.split()
    beg = x.index("your") +1
    end = beg + x[beg:].index("You")
    vehicle = " "
    vehicle = vehicle.join(x[beg:end])
    vehicle = vehicle[:-1]
    try:
        g = x.index("*Email:*") + 1
        second = x[g]
    except ValueError:
        phone = ""
        p = x.index("*Telephone:*")+1
        z = x.index("*ZIP")
        second = phone.join(x[p:z])
    try:
        comment = ' '
        start = x.index("Comments")
        end = x.index("(CarGurus")
        comment = comment.join(x[start+1:end])
    except ValueError:
        comment = "No comment."
    first = 0
    last = 0
    for i in range(len(x)):
        matchN = re.search('[*]+First',x[i])
        matchD = re.search('[*]+Last',x[i])
        if matchN:
            first = i + 2
        if matchD:
            last = i + 2
        else:
            pass
    name = x[first] + ' ' + x[last]
    return [name, second, vehicle, comment]


def retrieve_info(bodies):
    result = []
    counter = 0
    for counter in range(len(bodies)):
        mod = counter % 2
        if (mod > 0):
            continue
        try:
            lead_info = type1(bodies[counter])
            result.append(lead_info)
            pass
        except ValueError:
            try:
                lead_info = type2(bodies[counter])
                result.append(lead_info)
                pass
            except ValueError:
                try:
                    lead_info = type3(bodies[counter])
                    result.append(lead_info)
                    pass
                except ValueError:
                    print('Email format not accepted')
                    print(info[counter])
                    continue
    return result


def send_emails(lead_info):
    successes = 0
    phones = 0
    for i in range(len(lead_info)):
        if '@' in lead_info[i][1]:
            #send email to customer
            FROM = username
            TO = lead_info[i][1]
            CC = 'syd.meier.723@gmail.com' #'ben@gatewayauto.co'
            senders = [TO,CC]
            subject = 'Your inquiry about ' + lead_info[i][2] + ' at Gateway Auto.'
        
            msg = MIMEMultipart()
            msg["From"] = FROM
            msg["To"] = TO
            msg["Subject"] = subject
            msg["cc"] = CC
            message_text =  'Hi ' + lead_info[i][0] + ', \n\nThis is Enzo, Gateway Auto\'s automated service agent. To answer your question, yes, the ' + lead_info[i][2] + ' is still available.             \n\nYou can use this link, https://gatewayauto.co/scheduleappointment/, to set up a test drive or you can call Ben, Owner & Car Sales Lead, at 402-669-9038 any time.             \n\nIf you have any additional questions, you can also send them here and Ben will get them. He\'s cc\'d on this email.             \n\nEnzo \nAutomate Service Agent \n(402)932-0500 \ngatwayauto.co\n' 
            text = MIMEText(message_text, 'plain')
            msg.attach(text)
            body = msg.as_string()
            #print(msg)
            try:
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.ehlo()
                server.login(username, password)
                server.sendmail(FROM, senders, body)
                server.close()
                successes += 1
                #print('Email sent!')
            except:
                print('Something went wrong sending to customer...')

        else:
            #send email to ben
            FROM = username
            TO = 'syd.meier.723@gmail.com' #'ben@gatewayauto.co'
            subject = 'CALL ' + lead_info[i][0].upper() + ' ABOUT ' + lead_info[i][2].upper() + ' AT ' + lead_info[i][1]
            msg = MIMEMultipart()
            msg["From"] = FROM
            msg["To"] = TO
            msg["Subject"] = subject
            message_text = 'Hey Ben, sorry about opening this before you got to it. Here\'s ' + lead_info[i][0] + '\'s initial inquiry for you:             \n\n' + 'Name: ' + lead_info[i][0] + ' \nPhone: ' + lead_info[i][1] + ' \nVehicle: ' + lead_info[i][2] + ' \nComments: ' + lead_info[i][3]
            text = MIMEText(message_text, 'plain')
            msg.attach(text)
            body = msg.as_string()
            #print(msg)
            try:
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.ehlo()
                server.login(username, password)
                server.sendmail(FROM, TO, body)
                server.close()
                phones += 1
                #print('Email sent!')
            except:
                print('Something went wrong sending to Ben...')
        message = str(successes) + " emails sent to customers. " + str(phones) + " emails sent to Ben for followup."
        print(message)

        

def read_and_send_emails(username,password,chosen_emails):
    try:
        total_emails = read_emails(username,password,chosen_emails)
    except ValueError:
        print("There was an error in reading the emails.")
    if total_emails == []:
        print("No new emails sent.")
    else:
        try:
            lead_info = retrieve_info(total_emails)
        except ValueError:
            print("There was an error in gathering data from the leads.")
        try:
            send_emails(lead_info)
            print("All emails sent!")
        except ValueError:
            print("There was an error sending the emails.")

username = "gatoradebottlenextome@gmail.com"
password = "Hard2guess!"
chosen_emails = ["syd.meier.723@gmail.com"]
#username = 'ben@gatewayauto.co'
#password = input("Password: ")
#chosen_emails = ['dealer-leads@messages.cargurus.com','donotreply@dealercarsearch.com']
read_and_send_emails(username,password,chosen_emails)





