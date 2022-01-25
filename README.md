![alt text](https://github.com/savangco/backend.py/blob/master/assets/backendpy_logo_small.png?raw=true)

# Backendpy
Async (ASGI) Python web framework for building the backend of your project!

Some features:
* Application-based architecture and the ability to install third-party applications in a project
* Support of middlewares for different layers such as Application, Handler, Request or Response
* Supports events by hook feature
* Data handler classes, including validators and filters to automatically apply to request input data
* Supports a variety of responses including JSON, HTML, file and… with various settings such as stream, gzip and…
* Router with the ability to define urls as Python decorator or as separate files
* Application-specific error codes
* Optional default database layer by the Sqlalchemy async ORM with management of sessions for the scope of each request
* Optional default templates layer by the Jinja template engine
* …

### Requirements
Python 3.8+

### Installation
```shell
$ pip3 install backendpy
```
Or use the following command to install optional additional libraries:
```shell
$ pip3 install backendpy[full]
```
You also need to install an ASGI server such as Uvicorn, Hypercorn or Daphne:
```shell
$ pip3 install uvicorn
```
### Examples
#### Basic usage

*asgi.py*
```python
from backendpy.app import Backendpy
from backendpy.response import response

backendpy = Backendpy()

@backendpy.uri(r'^/hello-world$', ['GET'])
async def hello(request):
    return response.Text('Hello, World!')
```
Run:
```shell
$ uvicorn asgi:backendpy
```

#### Application based usage

Example app:

*python_path/hello_app/main.py*
```python
from backendpy.app import App
from .handlers import routes

app = App(
    routes=[routes])
```
*python_path/hello_app/handlers.py*
```python
from backendpy.router import Routes
from backendpy.response import response

routes = Routes()

@routes.uri(r'^/hello-world$', ['GET'])
async def hello(request):
    return response.Text('Hello World!')
```
Example project:

*project/asgi.py*
```python
from backendpy.app import Backendpy

backendpy = Backendpy()
```
*project/config.ini*
```ini
[apps]
active =
    python_path.hello_app
```
Run project with `uvicorn asgi:backendpy`
