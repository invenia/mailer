"""
Creates a runnable suite of all tests in the mailer.test module.
"""
import unittest


def build():
    """
    Build the test suite.
    """
    from mailer.test.test_mailer import TestMailer

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMailer))

    return suite


def run(verbosity=2):
    """
    Build and run the test suite.

    verbosity: how verbose the test runner should be (default 2)
    """
    unittest.TextTestRunner(verbosity=verbosity).run(build())

if __name__ == '__main__':
    # This code pushes mailer onto the path if necessary, so testing
    # can be done without installation. It is duplicated across all
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

    run()
