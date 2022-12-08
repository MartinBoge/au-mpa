import unittest

from project_name.foo import to_upper


class TestFoo(unittest.TestCase):
    def test_upper(self):

        foo = to_upper("foo")
        self.assertEqual(foo, "FOO")


if __name__ == "__main__":
    unittest.main()
