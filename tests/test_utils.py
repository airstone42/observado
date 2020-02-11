import unittest

from observado.lib.utils import *


class MyTestCase(unittest.TestCase):
    def test_means(self):
        b = np.array([[x for x in range(0, 18)], [x for x in range(-18, 0)]])
        a = np.array([3, 9])
        self.assertTrue(np.array_equal(np.array([[1, 5.5, 12.5], [-17, -12.5, -5.5]]), means(b, a)))
        self.assertTrue(np.array_equal(np.array([8.5, -9.5]), means(b)))


if __name__ == '__main__':
    unittest.main()
