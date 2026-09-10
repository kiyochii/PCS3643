import unittest

class TestModelo(unittest.TestCase):

#    def setUp(self):

    def test_hello(self):
        self.assertEqual('hello','hello')

    def test_goodbye(self):
        self.assertTrue('goodbye'=='hello')

#    def tearDown(self):


if __name__ == '__main__':
    unittest.main()