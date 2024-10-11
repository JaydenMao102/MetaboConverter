import unittest
from program import add_me
from program import divide

class TestAdd(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add_me(1,2), 3)
    
    def test_add_Two(self):
        self.assertNotEqual(add_me(1,2), 2)

    def test_divide(self):
        self.assertEqual(divide(4,0),2)

    def test_bad_divide(self):
        with self.assertRaises(ZeroDivisionError):
            divide(4,0)

if __name__ == '__main__':
    unittest.main()