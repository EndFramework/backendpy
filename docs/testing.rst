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
    from backendpy.unittest import TestCase
    from backendpy.utils import http

    class MyTestCase(TestCase):

        def setUp(self) -> None:
            self.client = http.Client('127.0.0.1', 8000)

        def test_user_creation(self):
            with self.client as session:
                data = {'first_name': 'Jalil',
                        'last_name': 'Hamdollahi Oskouei',
                        'username': 'my_user',
                        'password': 'my_pass'}
                result = session.post('/users', json=data)
                self.assertEqual(result.status, 200)
                self.assertNotEqual(result.data, '')

    if __name__ == '__main__':
        unittest.main()
