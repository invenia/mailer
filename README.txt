= Mailer =
The mailer module provides a convenient way to send emails. It consists of a Mailer object that handles building emails and connecting to a mail server. It can be imported using:
{{{
from mailer import Mailer
}}}

To instantiate a Mailer object, you must give it a username, password and host address. If you are using google's mail service (even with a custom domain), the host address is "smtp.gmail.com:587":
{{{
mailer = Mailer('user@example.com', 'secure_password', 'smtp.gmail.com:587')
}}}

The Mailer object will not connect with the server until you use its open method. Once it's connected, it will not disconnect until you use it's close method:
{{{
mailer = Mailer(user, password, host)

# emails can't be send
...

mailer.open()

# emails can be sent
...

mailer.close()

# email can no longer be sent
}}}

To check whether the Mailer object is currently connected to the server, you can use the is_open method

If you are sending all of your emails at one time without disconnecting, the easiest way to send mail is using the with statement:
{{{
with Mailer(user, password, host) as mailer:
    # send emails here
    ...

# mailer object automatically disconnected
}}}

To send an email, use the send command. The only required paramaters are: recipients (which is either a string address, or a list of string addresses), subject, and body.
{{{
with Mailer(user, password, host) as mailer:
    mailer.send('recipient@example.com', 'Foo meeting at 16:00', 'The Foo meeting will be held at Bar at 16:00')
}}}

By default, the sender address will be the same as the supplied username to create the mailer object. To send an email as a different user, user the mail_as paramater. CCs and BCC can be given in the same format as recipients using the cc_recipients, and bcc_recipients paramaters. The attachments paramater takes either a filename, or a list of filenames, and will automatically encode those files in your email.
