from backendpy.unittest import AsyncTestCase


class MyTestCase(AsyncTestCase):

    def setUp(self):
        pass

    def test_something(self):
        self.assertEqual(True, False)
