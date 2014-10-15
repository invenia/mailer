"""
A collection of unittests for the mailer module's Mailer object
"""
import unittest


# unittest.TestCase isn't liked by pylint. Ignore its errors.
# pylint: disable-msg=R0904, R0915, W0212
class TestMailer(unittest.TestCase):
    """
    A collection of unittests for the mailer module's Mailer object
    """
    def test_encoding(self):
        """
        make sure that emails are properly encoded
        """
        from mailer.mailer import _ENCODING

        self.assertEqual(_ENCODING, 'utf-8')

    def test_format_addresses(self):
        """
        test that lists of addresses properly convert into
        comma-separated values
        """
        from mailer.mailer import _format_addresses

        self.assertEqual(_format_addresses([]), '')
        self.assertEqual(_format_addresses(['test@example.com']),
                         'test@example.com')
        self.assertEqual(_format_addresses(['foo@example.com',
                                            'bar@example.com']),
                         'foo@example.com, bar@example.com')

    # test cases can be long, no magic strings
    # pylint: disable-msg=R0912, R0914
    def test_build_message(self):
        """
        test that build_message properly creates mime-typed emails
        """
        from email import message_from_string
        from os.path import abspath, dirname, join

        from mailer.mailer import build_message_string

        to_addr = 'to@example.com'
        from_addr = 'from@example.com'
        subject = 'the subject'
        body = 'the body'
        cc_addr = 'cc@example.com'
        bcc_addr = 'bcc@example.com'

        attachment_a = join(dirname(abspath(__file__)), 'attachmentA.txt')
        attachment_b = join(dirname(abspath(__file__)), 'attachmentB.txt')

        # default settings, by position, single recipient
        message_string = build_message_string([to_addr], subject, body,
                                              from_addr)

        message = message_from_string(message_string)

        self.assertFalse(message.is_multipart())
        self.assertEqual(message.get_content_type(), 'text/plain')
        self.assertEqual(message['To'], to_addr)
        self.assertEqual(message['Subject'], subject)
        self.assertEqual(message['From'], from_addr)
        self.assertEqual(message.get_payload(), body)
        self.assertFalse('Cc' in message)
        self.assertFalse('Bcc' in message)

        # default settings, by name, single recipient
        message_string = build_message_string(recipients=[to_addr],
                                              subject=subject,
                                              body=body,
                                              sender=from_addr)

        message = message_from_string(message_string)

        self.assertFalse(message.is_multipart())
        self.assertEqual(message.get_content_type(), 'text/plain')
        self.assertEqual(message['To'], to_addr)
        self.assertEqual(message['Subject'], subject)
        self.assertEqual(message['From'], from_addr)
        self.assertEqual(message.get_payload(), body)
        self.assertFalse('Cc' in message)
        self.assertFalse('Bcc' in message)

        # default settings, multiple recipients
        message_string = build_message_string(['to1@example.com',
                                               'to2@example.com'],
                                              subject, body, from_addr)

        message = message_from_string(message_string)

        self.assertFalse(message.is_multipart())
        self.assertEqual(message.get_content_type(), 'text/plain')
        self.assertEqual(message['To'], 'to1@example.com, to2@example.com')
        self.assertEqual(message['Subject'], subject)
        self.assertEqual(message['From'], from_addr)
        self.assertEqual(message.get_payload(), body)
        self.assertFalse('Cc' in message)
        self.assertFalse('Bcc' in message)

        # cc and bcc
        message_string = build_message_string([to_addr],
                                              subject, body,
                                              from_addr,
                                              cc_recipients=[cc_addr],
                                              bcc_recipients=[bcc_addr])

        message = message_from_string(message_string)

        self.assertFalse(message.is_multipart())
        self.assertEqual(message.get_content_type(), 'text/plain')
        self.assertEqual(message['To'], to_addr)
        self.assertEqual(message['Subject'], subject)
        self.assertEqual(message['From'], from_addr)
        self.assertEqual(message.get_payload(), body)
        self.assertEqual(message['Cc'], cc_addr)
        self.assertEqual(message['Bcc'], bcc_addr)

        # with single attachment
        message_string = build_message_string([to_addr], subject, body,
                                              from_addr,
                                              attachments=[attachment_a])

        message = message_from_string(message_string)

        self.assertTrue(message.is_multipart())
        self.assertEqual(message.get_content_type(), 'multipart/mixed')
        self.assertEqual(message['To'], to_addr)
        self.assertEqual(message['Subject'], subject)
        self.assertEqual(message['From'], from_addr)
        self.assertFalse('Cc' in message)
        self.assertFalse('Bcc' in message)

        parts = message.get_payload()

        self.assertEqual(len(parts), 2)

        # check the body is there
        for part in parts:
            if part.get_content_type() == 'text/plain':
                self.assertEqual(part.get_payload(), body)
                break
        else:
            raise ValueError('body missing')

        # check the attachment is there
        for part in parts:
            if part.get_content_type() == 'application/octet-stream':
                self.assertEqual(part.get_payload().decode('base_64'),
                                 open(attachment_a, 'r').read())
                break
        else:
            raise ValueError('attachment missing')

        # with two attachments
        message_string = build_message_string([to_addr], subject, body,
                                              from_addr,
                                              attachments=[attachment_a,
                                                           attachment_b])

        message = message_from_string(message_string)

        self.assertTrue(message.is_multipart())
        self.assertEqual(message.get_content_type(), 'multipart/mixed')
        self.assertEqual(message['To'], to_addr)
        self.assertEqual(message['Subject'], subject)
        self.assertEqual(message['From'], from_addr)
        self.assertFalse('Cc' in message)
        self.assertFalse('Bcc' in message)

        parts = message.get_payload()

        self.assertEqual(len(parts), 3)

        # check the body is there
        for part in parts:
            if part.get_content_type() == 'text/plain':
                self.assertEqual(part.get_payload(), body)
                break
        else:
            raise ValueError('body missing')

        # check attachments are there
        for attachment in [attachment_a, attachment_b]:
            for part in parts:
                if (part.get_content_type() == 'application/octet-stream' and
                    part.get_payload().decode('base_64') == open(attachment,
                                                                 'r').read()):
                    break
            else:
                raise ValueError('attachment missing')
    # pylint: enable-msg=R0912, R0914

    def test_smtplib_use(self):
        """
        check that Mailer properly uses smtplib (which means that actual
        email functionality can be skipped)
        """
        # attributes required to check that smtp is used properly
        # pylint: disable-msg=R0902
        class FakeSMTP(object):
            """
            A fake smtp class to assure that the library is being used
            """
            def __init__(self, host):
                self.host = host
                self.tls_counter = 0
                self.close_counter = 0
                self.username = self.password = None
                self.sender = self.recipients = self.message = None

            def starttls(self):
                """
                Make sure tls is started once
                """
                self.tls_counter += 1

            def login(self, username, password):
                """
                Make sure login occurs after tls
                """
                if (self.tls_counter != 1 or self.close_counter != 0 and
                        self.username is None and self.password is None):
                    raise ValueError('not started, or stopped before login')

                self.username = username
                self.password = password

            def close(self):
                """
                make sure close happens after login
                """
                self.close_counter += 1

            def sendmail(self, sender, recipients, message):
                """
                make sure sendmail happens after login
                """
                if (self.tls_counter != 1 or self.close_counter != 0 and
                        self.username is not None and
                        self.password is not None):
                    raise ValueError('not started, or stopped before send')

                self.sender = sender
                self.recipients = recipients
                self.message = message
        # pylint: enable-msg=R0902

        from smtplib import SMTP

        import mailer

        cc_addr = 'cc@example.com'
        bcc_addr = 'bcc@example.com'

        self.assertEqual(SMTP, mailer.mailer.SMTP)

        mailer.mailer.SMTP = FakeSMTP

        mailer_object = mailer.mailer.Mailer('user', 'pass', 'host')
        mailer_object.open()

        server = mailer_object._server

        self.assertTrue(isinstance(server, FakeSMTP))

        self.assertEqual(server.username, 'user')
        self.assertEqual(server.password, 'pass')
        self.assertEqual(server.tls_counter, 1)

        self.assertEqual(server.sender, None)
        self.assertEqual(server.recipients, None)
        self.assertEqual(server.message, None)
        self.assertEqual(server.close_counter, 0)

        mailer_object.send(['r1@example.com', 'r2@example.com'],
                           'subject', 'message',
                           cc_recipients=cc_addr,
                           bcc_recipients=bcc_addr)

        self.assertEqual(server.username, 'user')
        self.assertEqual(server.password, 'pass')
        self.assertEqual(server.tls_counter, 1)

        self.assertEqual(server.sender, 'user')
        self.assertEqual(server.recipients,
                         ['r1@example.com', 'r2@example.com',
                          cc_addr, bcc_addr])

        self.assertTrue(isinstance(server.message, str))
        self.assertEqual(server.close_counter, 0)

        mailer_object.close()

        self.assertEqual(server.username, 'user')
        self.assertEqual(server.password, 'pass')
        self.assertEqual(server.tls_counter, 1)

        self.assertEqual(server.sender, 'user')
        self.assertEqual(server.recipients,
                         ['r1@example.com', 'r2@example.com',
                          cc_addr, bcc_addr])
        self.assertTrue(isinstance(server.message, str))
        self.assertEqual(server.close_counter, 1)

        self.assertEqual(mailer_object._server, None)
# pylint: enable-msg=R0904, R0915, W0212


def run_tests():
    """
    Run all TestMailer tests.
    """
    # This code pushes mailer onto the path if necessary, so testing
    # can be done without installation. It is duplicated accross all
    # mailer.test files so they each can be run independantly.
    # Unfortunately pylint can't locally disble the associated Warning.
    # Leaving the disable in, for when they fix that bug.
    # pylint: disable-msg=R0801
    import imp

    try:
        imp.find_module('mailer')
    except ImportError:
        from os.path import dirname, abspath
        from sys import path

        path.append(dirname(dirname(dirname(abspath(__file__)))))
    # pylint: enable-msg=R0801

    unittest.main()


if __name__ == '__main__':
    run_tests()
