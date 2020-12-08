import unittest

from plot_station_fullness import split_dates_and_modulo_time


class Tester(unittest.TestCase):

    def test_split_dates_and_modulo_time(self):
        self.assertEqual(split_dates_and_modulo_time([0, 1, 2, 3], [[1, 1, 2, 2], [3, 3, 4, 4]],
                                                     date_lambda=lambda x: x // 2, time_lambda=lambda x: x % 2),
                         [[[0, 1], [1, 1], [3, 3]], [[0, 1], [2, 2], [4, 4]]])


if __name__ == '__main__':
    unittest.main()
