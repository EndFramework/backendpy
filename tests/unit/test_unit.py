print(int(float(1)))
print(int(float('1')))
print(int(float(1.0)))
print(int(float(1.5)))
print(int(float('1.0')))
print(int(float('1.5')))


from backendpy.unittest import AsyncTestCase


class MyTestCase(AsyncTestCase):

    def test_something(self):
        self.assertEqual(True, False)
