### Test Result
### In 4c-2.9g computer get 1000 result
### async  cost  1.8666772842407227  s  0.03111128807067871  min  speed  535.7112385962062  c/s
### sync  cost  1.8722515106201172  s  0.03120419184366862  min  speed  534.1162735495859  c/s
### pool_async  cost  10.745956897735596  s  0.1790992816289266  min  speed  93.05825525977323  c/s
###

import time
import unittest
from unittest import TestCase
import requests
from concurrent.futures import ThreadPoolExecutor


class TestSpeed(TestCase):
    def run_once(self, path):
        res = requests.get(f'http://localhost:8889/{path}')
        # print(res.text)

    def run_path(self, path):
        start = time.time()
        num = 1000
        pool = ThreadPoolExecutor()
        for i in range(num):
            pool.submit(self.run_once, path)
        pool.shutdown()
        cost = time.time() - start

        print(path, ' cost ', cost, ' s ', cost / 60, ' min', ' speed ', num / cost, ' c/s')
        return cost

    def test_main(self):
        # async_cost = self.run_path('async')
        # sync_cost = self.run_path('sync')
        pool_async_cost = self.run_path('pool_async')
        # assert async_cost < pool_async_cost < sync_cost


if __name__ == '__main__':
    unittest.main()
