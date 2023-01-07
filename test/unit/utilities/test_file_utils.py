import os
import unittest

from mpa.utilities.file_utils import read_json, write_json


class TestFileUtils(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.test_file_path_json = "test/unit/utilities/test_file.json"

    def setUp(self) -> None:
        check_and_remove_file(self.test_file_path_json)

    def tearDown(self) -> None:
        check_and_remove_file(self.test_file_path_json)

    # writing and reading the same dict
    def test_read_and_write_json(self):

        write_data = {"x": [1, 2, 3], "y": [4, 5, 6]}

        write_json(obj=write_data, path=self.test_file_path_json)

        self.assertEqual(first=True, second=os.path.exists(self.test_file_path_json))

        read_data = read_json(path=self.test_file_path_json)

        self.assertEqual(first=write_data, second=read_data)


def check_and_remove_file(path) -> None:
    if os.path.exists(path=path):
        os.remove(path=path)


if __name__ == "__main__":
    unittest.main()
