import unittest

class VbatTest(unittest.TestCase):
    def test_true(self):
        # Test that true is true!
        self.assertTrue(True)
        self.assertFalse(not True)
        self.assertEquals(1 + 1, 2, '1 + 1 = 2')

    def test_raises(self):
        def do_something_wrong(x, y, z):
            raise ValueError('Something went wrong!')
        with self.assertRaises(ValueError):
            do_something_wrong(1, 2, 3)
