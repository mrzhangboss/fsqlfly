from collections import namedtuple
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from django.test import TestCase
from api.search_utils import build_function

Sample = namedtuple('Sample', ['a', 'b', 'c', 'd', 'e', 'f', 'g'])


# Create your tests here.
class SearchTestCase(TestCase):
    def generate_test_function(self, code='$a > 0 and $b == 1'):
        return build_function(code)

    def generate_test_data(self):
        data = []
        now = datetime.now()
        for i in range(100):
            dt = now + timedelta(days=1)
            data.append(
                Sample(i, str(i), float(i), Decimal(i), dt, dt.date(), time(i % 24, i % 60, (i ** 2) % 60))
            )
        return data

    def test_build_function(self):
        assert callable(self.generate_test_function())

    def test_function_correct(self):
        for x in self.generate_test_data():
            for real_func, fake in [
                (lambda x: x.a > 50 and x.b == 50, '$a > 50 and $b == 50'),
                (lambda x: 5 < x.a < 100, '5 < $a < 100'),
                (lambda x: (x.a > 50 and x.b == 50) or x.c == 1, '($a > 50 and $b == 50) or $c == 1'),
                (lambda x: x.a > 50 and x.c < 50, '$a > 50 and $c < 50'),
                (lambda x: x.e > datetime(2001, 1, 1) or x.c < 50, '$e > datetime(2001, 1, 1) or $c < 50'),
                (lambda x: x.g > time(20, 1, 1) or x.c < 50, '$g > time(20, 1, 1) or $c < 50'),
            ]:
                generate_func = build_function(fake)
                assert generate_func(x) == real_func(x)
                print(x, real_func(x))
