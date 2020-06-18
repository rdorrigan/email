import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
from email.utils import make_msgid

class EmailServer():

    def __init__(self):
        self.my_email = os.environ['emailWork']
        self.my_pass = os.environ['smtpPW']
        self.server = self.set_up_server()
        self.signature = os.environ['emailSignature']
        self.signature_image = os.path.join(os.getenv('userprofile'),'Pictures/gearcoop.png')

    def set_up_server(self):
        # Set up server
        server = smtplib.SMTP(host = 'smtp.gmail.com', port =587,timeout = 600 )
        server.ehlo_or_helo_if_needed()
        server.starttls()
        server.ehlo_or_helo_if_needed()
        #Log in to server
        server.login(self.my_email, self.my_pass)

        return server

    def send_email(self, to, subject, body, body_type = "plain", cc = [], attachment = ""):
        '''
        if attachement is a dict the key should be the file path and the value is a specific encoding
        this should only be used for non UTF-8 encodings
        '''
        # body_type must be one of ('plain','html')
        body_types = ('plain','html')
        #Set up email
        msg = MIMEMultipart()
        msg['From'] = self.my_email
        if isinstance(to,(tuple,list)):
            if len(to) == 1:
                msg['To'] = to[0]
            else:
                msg['To'] = ",".join(to)
        else:
            msg['To'] = to
        msg['Subject'] = subject
        if cc:
            if isinstance(cc,(tuple,list)):
                if len(cc) == 1:
                    msg['Cc'] = cc[0]
                else:
                    msg['Cc'] = ','.join(cc)
            else:
                msg['Cc'] = cc
        if body_type == 'plain':
            body += self.signature
        if not body_type in body_types:
            msg.attach(MIMEText(body, body_types[0]))
        # if body_type == body_types[1]:
        #     # msg.attach(MIMEText('<b>{}</b><br><img src="cid:{}"><br>'.format(body,os.path.basename(self.signature_image)), body_type))
        #     image_cid = make_msgid(domain=self.signature_image)
        #     msg.attach(MIMEText("""\
        #         <html>
        #             <body>
        #                 <p>{}<br>
        #                 </p>
        #                 <img src="cid:{image_cid}">
        #             </body>
        #         </html>
        #         """.format(body,os.path.basename(self.signature_image)), body_type))
        else:
            msg.attach(MIMEText(body, body_type))
        # Need to add image as a part of the signature, the below attaches as a file
        # img = open(self.signature_image,'rb')
        # mime_img = MIMEImage(img.read())
        # mime_img.add_header('Content-ID',os.path.basename(self.signature_image))
        # msg.attach(mime_img)
        # img.close()

        if attachment:
            if isinstance(attachment,str):
                filename = os.path.basename(attachment)
                with open(attachment, "rb") as file:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload((file).read())
                    encoders.encode_base64(part)
                    part.add_header('content-Disposition', 'attachment; filename= %s' % filename)
                
                msg.attach(part)
            elif isinstance(attachment,(tuple,list,set)):
                for a in attachment:
                    filename = os.path.basename(a)
                    with open(a, "rb") as file:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload((file).read())
                        encoders.encode_base64(part)
                        part.add_header('content-Disposition', 'attachment; filename= %s' % filename)
                    msg.attach(part)
                    del part
            elif isinstance(attachment,(dict)):
                for k,v in attachment.items():
                    filename = os.path.basename(a)
                    with open(a, "rb",encoding=v) as file:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload((file).read())
                        encoders.encode_base64(part)
                        part.add_header('content-Disposition', 'attachment; filename= %s' % filename)
                    msg.attach(part)
                    del part

        #Send Email
        print('Sending email to: {}{}'.format(to,cc))
        self.server.send_message(msg)
        print('Email Sent')

