Testing
=======
Because of the use of the async architecture in the Backendpy framework, we will need to run the tests as async for
most sections in our applications. Hence, the Backendpy framework provides the :class:`~backendpy.unittest.AsyncTestCase`
class, which is the subclass of :class:`unittest.TestCase`, to which async execution has been added.

Example of testing a database query:

.. code-block:: python
    :caption: project/apps/hello/tests/test_db.py

    import unittest
    from asyncio import current_task
    from backendpy.unittest import AsyncTestCase
    from backendpy.db import get_db_engine, get_db_session
    from ..db import queries


    DATABASE = {'host': 'localhost', 'port': '5432', 'name': 'your_db_name',
                'username': 'your_db_user', 'password': 'your_db_password'}

    class QueriesTestCase(AsyncTestCase):

        def setUp(self) -> None:
            self.db_engine = get_db_engine(DATABASE, echo=True)
            self.db_session = get_db_session(self.db_engine, scope_func=current_task)

        async def tearDown(self) -> None:
            await self.db_session.remove()
            await self.db_engine.dispose()

        async def test_get_users(self):
            result = await queries.get_users(self.db_session())
            self.assertNotEqual(result, False)

    if __name__ == '__main__':
        unittest.main()


API test example:

.. code-block:: python
    :caption: project/apps/hello/tests/test_api.py

    import unittest
    from backendpy.unittest import AsyncTestCase
    from backendpy.utils import http

    class MyTestCase(AsyncTestCase):
        async def setUp(self) -> None:
            self.client = http.AsyncHttpClient()

        async def test_user_creation(self):
            async with self.client as http_session:
                data = {'first_name': 'Jalil',
                       'last_name': 'Hamdollahi Oskouei',
                       'username': 'my_user',
                       'password': 'my_pass'}
                result = await http_session.post('http://127.0.0.1:5000/users', json=data)
                self.assertEqual(result.get('status'), 'success')

    if __name__ == '__main__':
        unittest.main()
