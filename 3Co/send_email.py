from string import Template
from email.mime.text import MIMEText
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
import os,shutil




My_address = 'doit4meproject@outlook.com'
Password = 'BerkaySonerErsin'


### FUNCTION READ
def read_output(filename):
    with open(filename ,'r') as file_read:
        return file_read.read()



### FUNCTION READ - READ CONTACT LIST
def get_contacts(filename):
    names = []
    emails = []
    with open(filename, mode='r', encoding='utf-8') as contacts_file:
        for contact_info in contacts_file:
            names.append(contact_info.split()[0])
            emails.append(contact_info.split()[1])
    return names, emails



### FUNCTION READ - READ TEMPLATE MESSAGE BODY
def read_template(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)


    
####################################################################################################
####################################################################################################
####################                       MAIN FUNCTIONS                       ####################
####################################################################################################
####################################################################################################

def main():
    names, emails = get_contacts('mycontacts.txt') # Read contacts
    output_message = read_output('summary.log') # Read summary.log
    message_template = read_template('message.txt') # Read message body

    # set up the SMTP server
    mail_server = smtplib.SMTP(host='smtp.office365.com', port=587)
    mail_server.starttls()
    mail_server.login(My_address, Password)

    # For each contact, send the email:
    for name, email in zip(names, emails):
        msg = MIMEMultipart()       # create a message
        msg['From']=My_address
        msg['To']=email
        msg['Subject']="3CO Output Reports"
        
        message = message_template.substitute(PERSON_NAME = name, OUTPUT_MESSAGE = output_message)
        

        
    # Check the directory which contains outputs from comparing tool
    files = os.listdir("email_attachments")
    for file in files:
        attachment = open(f"email_attachments\\{file}", "rb")
        attach = MIMEBase('application', 'octet-stream')
        attach.set_payload((attachment).read())
        encoders.encode_base64(attach)
        attach.add_header('Content-Disposition', 'attachment',filename='%s' % file)
        msg.attach(attach)
       
    
    msg.attach(MIMEText(message, "html"))
    mail_server.send_message(msg)
    del msg
        
    mail_server.quit()
    
    
main()
shutil.rmtree("email_attachments")