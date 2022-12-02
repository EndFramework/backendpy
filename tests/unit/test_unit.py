from backendpy.unittest import AsyncTestCase


class MyTestCase(AsyncTestCase):

    def test_something(self):
        self.assertEqual(True, False)
