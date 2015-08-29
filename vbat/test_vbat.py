import unittest

from . import Vbat

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

    def test_main_class(self):
        vbati = Vbat("zz")
        self.assertEquals(
            vbati.image_test("test.jpeg"),
            [
                [1, ".", 2, 8, 0, 7, 3, 1],
                [6, ".", 4, 6, 5, 4, 9, 1],
                ["X", 5, 4],
            ])
