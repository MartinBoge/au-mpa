import unittest

from mpa.utilities.support_functions import create_subsets


class TestFileUtils(unittest.TestCase):
    def test_create_subsets(self):

        # Test for n = 3
        subset_n_3 = create_subsets(3)
        self.assertEqual(subset_n_3, [[0, 1], [0, 2], [1, 2]])
        self.assertEqual(len(subset_n_3), 3)

        # Test for n = 4
        subset_n_4 = create_subsets(4)

        self.assertEqual(
            subset_n_4,
            [
                [0, 1],
                [0, 2],
                [1, 2],
                [0, 1, 2],
                [0, 3],
                [1, 3],
                [0, 1, 3],
                [2, 3],
                [0, 2, 3],
                [1, 2, 3],
            ],
        )
        self.assertEqual(len(subset_n_4), 10)

        # Test for n = 0
        self.assertEqual(create_subsets(0), [])


if __name__ == "__main__":
    unittest.main()
