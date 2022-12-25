![alt text](https://github.com/savangco/backendpy/blob/master/assets/backendpy_logo_small.png?raw=true)

# Backendpy
Python web framework for building the backend of your project!

Some features:
* Asynchronous programming (ASGI-based projects)
* Application-based architecture and the ability to install third-party applications in a project
* Support of middlewares for different layers such as Application, Handler, Request or Response
* Supports events and hooks
* Data handler classes, including validators and filters to automatically apply to request input data
* Supports a variety of responses including JSON, HTML, file and… with various settings such as stream, gzip and…
* Router with the ability to define urls as Python decorator or as separate files
* Application-specific error codes
* Optional default database layer by the Sqlalchemy async ORM with management of sessions for the scope of each request
* Optional default templating layer by the Jinja template engine
* …

### Requirements
Python 3.8+

### Documentation
Documentation is available at https://backendpy.readthedocs.io.


### Quick Start

#### Installation
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

#### Create Project

*project/main.py*
```python
from backendpy import Backendpy

bp = Backendpy()
```

#### Create Application

*project/apps/hello/main.py*
```python
from backendpy.app import App
from .handlers import routes

app = App(
    routes=[routes])
```
*project/apps/hello/handlers.py*
```python
from backendpy.router import Routes
from backendpy.response import Text

routes = Routes()

@routes.get('/hello-world')
async def hello(request):
    return Text('Hello World!')
```

#### Activate Application

*project/config.ini*
```ini
[networking]
allowed_hosts =
    127.0.0.1:8000

[apps]
active =
    project.apps.hello
```

#### Run Project

Inside the project root path:
```shell
$ uvicorn main:bp
```

#### Command line
The basic structure of a project mentioned above can also be created by commands:
```shell
$ backendpy create_project --name myproject
```
To create a project with more complete sample components:
```shell
$ backendpy create_project --name myproject --full
```
Or to create an application:
```shell
$ backendpy create_app --name myapp
```
```shell
$ backendpy create_app --name myapp --full
```