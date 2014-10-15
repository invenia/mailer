"""
The Mailer class provides a simple way to send emails.
"""
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from smtplib import SMTP

_ENCODING = 'utf-8'


class Mailer(object):
    """
    The Mailer class provides a simple way to send emails.
    """
    def __init__(self, username, password, host='smtp.gmail.com:587'):
        self._username = username
        self._password = password
        self._host = host

        self._server = None

    def open(self):
        """
        Open the mail server for sending messages
        """
        self._server = SMTP(self._host)
        self._server.starttls()
        self._server.login(self._username, self._password)

    def close(self):
        """
        Close the mail server
        """
        self._server.close()
        self._server = None

    def is_open(self):
        """
        Checks whether the connection to the mail server is open
        """
        return self._server is not None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.is_open():
            self.close()

    # I'm fine with the number of arguments
    # pylint: disable-msg=R0913
    def send(self, recipients, subject, body, mail_as=None, cc_recipients=None,
             bcc_recipients=None, attachments=None):
        """
        Send an email message.

        recipients: either an email address, or a list of email
                    addresses of the direct recipients of the message.
        subject: the header of the message
        body: the message body
        mail_as: an alias to use for sending the message. If None,
                 the username for logging into the server is used.
                 Default: None
        cc_recipients: either an email address, or a list of email
                       addresses of all recipients who are to be receive
                       Carbon Copies of the message. Default: None
        bcc_recipients: either an email address, or a list of email
                       addresses of all recipients who are to be receive
                       Blind Carbon Copies of the message. Default: None
        attachments: either a filepath, or list of filepaths of all
                     files that should be added to the message as
                     attachments. Default: None
        """
        if isinstance(recipients, basestring):
            recipients = [recipients]

        if mail_as is None:
            mail_as = self._username

        if cc_recipients is None:
            cc_recipients = []
        elif isinstance(cc_recipients, basestring):
            cc_recipients = [cc_recipients]

        if bcc_recipients is None:
            bcc_recipients = []
        elif isinstance(bcc_recipients, basestring):
            bcc_recipients = [bcc_recipients]

        if attachments is None:
            attachments = []
        elif isinstance(attachments, basestring):
            attachments = [attachments]

        message = build_message_string(recipients, subject, body, mail_as,
                                       cc_recipients, bcc_recipients,
                                       attachments)

        all_recipients = recipients + cc_recipients + bcc_recipients

        self._server.sendmail(mail_as, all_recipients, message)
    # pylint: enable-msg=R0913


# pylint: disable-msg=R0913
def build_message_string(recipients, subject, body, sender, cc_recipients=None,
                         bcc_recipients=None, attachments=None):
    """
    Build an email message.

    NOTE: It's recommended that you use the Mailer object to accomplish
    this. besides handling (interfacing) smtp, it also alllows fuller
    defaults.

    recipients: a list of email addresses of the direct recipients.
    subject: the header of the message
    body: the message body
    mail_as: an alias to use for sending the message. If None,
             the username for logging into the server is used.
             Default: None
    cc_recipients: a list of email addresses of all recipients who are
                   to be receive Carbon Copies of the message.
                   Default: None
    bcc_recipients: a list of email addresses of all recipients who are
                    to be receive Blind Carbon Copies of the message.
                    Default: None
    attachments: a list of filepaths of all files that should be added
                 to the message as attachments. Default: None
    """
    subject = subject.encode(_ENCODING)

    message = MIMEText(body.encode(_ENCODING), _charset=_ENCODING)

    if attachments:
        full_message = MIMEMultipart()
        full_message.attach(message)
        message = full_message

        for attachment in attachments:
            application = MIMEApplication(open(attachment, 'rb').read())
            application.add_header('Content-Disposition', 'attachment',
                                   filename=os.path.basename(attachment))
            message.attach(application)

    message['Subject'] = subject
    message['From'] = sender
    message['To'] = _format_addresses(recipients)

    if cc_recipients:
        message['Cc'] = _format_addresses(cc_recipients)

    if bcc_recipients:
        message['Bcc'] = _format_addresses(bcc_recipients)

    return message.as_string()
# pylint: enable-msg=R0913


def _format_addresses(addresses):
    """
    build an address string from a list of addresses
    """
    return ', '.join(addresses).encode(_ENCODING)
