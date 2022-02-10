![alt text](https://github.com/savangco/backendpy/blob/master/assets/backendpy_logo_small.png?raw=true)

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

*project/main.py*
```python
from backendpy import Backendpy
from backendpy.response import Text

application = Backendpy()

@application.uri(r'^/hello-world$', ['GET'])
async def hello(request):
    return Text('Hello, World!')
```
Run inside the project path:
```shell
$ uvicorn main:application
```

#### Backendpy app based usage

Example app:

*hello_app/main.py*
```python
from backendpy.app import App
from .handlers import routes

app = App(
    routes=[routes])
```
*hello_app/handlers.py*
```python
from backendpy.router import Routes
from backendpy.response import Text

routes = Routes()

@routes.uri(r'^/hello-world$', ['GET'])
async def hello(request):
    return Text('Hello World!')
```
Example project:

*project/main.py*
```python
from backendpy import Backendpy

application = Backendpy()
```
*project/config.ini*
```ini
[apps]
active =
    app_path.hello_app
```
Run project with `uvicorn main:application`

### Command line
#### Project creation
```shell
$ backendpy create_project --name myproject
```
To create a project with more complete sample components:
```shell
$ backendpy create_project --name myproject --full
```
#### App creation
```shell
$ backendpy create_app --name myapp
```
```shell
$ backendpy create_app --name myapp --full
```