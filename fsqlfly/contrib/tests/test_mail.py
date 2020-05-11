import unittest
from fsqlfly.contrib.mail import MailHelper

class MyTestCase(unittest.TestCase):
    def test_send(self):
        MailHelper.send('test', 'hello')


if __name__ == '__main__':
    unittest.main()
