Data handlers
=============
One of the capabilities of Backendpy framework is the input data handlers, which includes default or user-defined
validators and filters.
With this feature, the main handlers of the requests and the handlers of their input data are separated, and in
this case, instead of the raw data, the validated and filtered data are received inside the main handlers.

With the regular and reusable structure of Data Handlers, much of the need for duplicate coding as well as unrelated
to the main logic within the code is eliminated and speeds up project implementation.

Data handlers are defined as classes that inherit from the :class:`~backendpy.data_handler.data.Data` class.

For example:

.. code-block:: python
    :caption: project/apps/hello/controllers/data_handlers.py

    from backendpy.data_handler.data import Data
    from backendpy.data_handler.fields import String
    from backendpy.data_handler import validators as v
    from backendpy.data_handler import filters as f
    ...

    class UserCreationData(Data):
        group = String('group', field_type=TYPE_URL_VAR)
        first_name = String('first_name', processors=[v.Length(max=50)])
        last_name = String('last_name', processors=[v.Length(max=50)])
        email = String('email', processors=[v.EmailAddress()])
        username = String('username', required=True, processors=[v.UserNamePolicy(), v.Unique(model=Users)])
        password = String('password', required=True, processors=[v.PasswordPolicy()])
        password_re = String('password_re', required=True, processors=[v.IsEqualToField('password')])

each of the items in the example is described below.

After defining a data handler, we must assign it to a request. This allocation is done in the routes definition
section with the ``data_handler`` parameter:

.. code-block:: python
    :caption: project/apps/hello/controllers/handlers.py

    from backendpy.router import Routes
    from .data_handlers import UserCreationData

    routes = Routes()

    @routes.post('/users', data_handler=UserCreationData)
    async def user_creation(request):
        data = await request.get_cleaned_data()
        ...

To get the final validated and filtered data inside the request main handler, we use ``request.get_cleaned_data()``,
which return a dictionary of data with defined fields in our data handler class.

Data fields
-----------
As shown in the previous example, data fields are defined inside the data handler class.
Each field can be an instance of :class:`~backendpy.data_handler.fields.Field` class or other data classes inherited
from this base class.

In the example, :class:`~backendpy.data_handler.fields.String` field is used. Developers can also create and use
their own custom data fields as needed.

The parameters of the base field class are as follows:

.. autoclass:: backendpy.data_handler.fields.Field
    :noindex:

Default field classes:

.. autoclass:: backendpy.data_handler.fields.String
    :noindex:

.. autoclass:: backendpy.data_handler.fields.List
    :noindex:

Example:

.. code-block:: python

    emails = List('emails', item_field=String(processors=[v.NotNull(), v.EmailAddress()]))

.. autoclass:: backendpy.data_handler.fields.Dict
    :noindex:

Example:

.. code-block:: python

    class AddressData(Data):
        country = String('country', required=True, field_type=None)
        state = String('state', required=True, field_type=None)
        city = String('city', required=True, field_type=None)
        street = String('street', field_type=None)
        zip_code = String('zip_code', required=True, field_type=None)

    class UserCreationData(Data):
        ...
        address = Dict('address', data_class=AddressData)


Data processors
---------------
Processors are classes for processing data field values that include validators and filters.

A list of processors is assigned to a data field via the ``processors`` parameter and will run in sequence as
specified. Also in this list, validators and filters can be used with any combination.

Validators
..........
Validators are responsible for reviewing and validating data, and a data is either passed over or, if there is a
discrepancy, the defined error is returned.

Developers can create and use the various validators they need by inheriting from the base
:class:`~backendpy.data_handler.validators.Validator` class.

.. autoclass:: backendpy.data_handler.validators.Validator
    :noindex:

Ready-made validators are also provided in the framework that can be used. The following is a list of them:

Default validators
``````````````````
.. autoclass:: backendpy.data_handler.validators.NotNull
    :noindex:

.. autoclass:: backendpy.data_handler.validators.NotBlank
    :noindex:

.. autoclass:: backendpy.data_handler.validators.In
    :noindex:

Example:

.. code-block:: python

    token_type = String('token_type', required=True, processors=[v.NotNull(), v.In(['basic', 'bearer'])])

.. autoclass:: backendpy.data_handler.validators.NotIn
    :noindex:

.. autoclass:: backendpy.data_handler.validators.Length
    :noindex:

.. autoclass:: backendpy.data_handler.validators.Limit
    :noindex:

.. autoclass:: backendpy.data_handler.validators.Numeric
    :noindex:

.. autoclass:: backendpy.data_handler.validators.Integer
    :noindex:

.. autoclass:: backendpy.data_handler.validators.Boolean
    :noindex:

.. autoclass:: backendpy.data_handler.validators.Url
    :noindex:

.. autoclass:: backendpy.data_handler.validators.UrlPath
    :noindex:

.. autoclass:: backendpy.data_handler.validators.EmailAddress
    :noindex:

.. autoclass:: backendpy.data_handler.validators.PhoneNumber
    :noindex:

.. autoclass:: backendpy.data_handler.validators.DateTime
    :noindex:

.. autoclass:: backendpy.data_handler.validators.UUID
    :noindex:

.. autoclass:: backendpy.data_handler.validators.MatchRegex
    :noindex:

.. autoclass:: backendpy.data_handler.validators.PasswordPolicy
    :noindex:

.. autoclass:: backendpy.data_handler.validators.UserNamePolicy
    :noindex:

.. autoclass:: backendpy.data_handler.validators.RestrictedFile
    :noindex:

Example:

.. code-block:: python

    image = String('image', processors=[v.NotNull(), v.RestrictedFile(extensions=('jpg', 'jpeg', 'png'), min_size=1, max_size=2048)])

.. autoclass:: backendpy.data_handler.validators.Exists
    :noindex:

.. autoclass:: backendpy.data_handler.validators.Unique
    :noindex:

Example:

.. code-block:: python

    username = String('username', processors=[v.Unique(model=Users)])

In this example, the value sent to the "username" field is queried directly to the "username" column from the "Users"
model and checked for its uniqueness, and returns an error if it is exists.

In the previous example, if the name of the model table field is "user_name" instead of "username", we should change it
as follows:

.. code-block:: python

    username = String('username', processors=[v.Unique(model=Users, model_field_name='user_name')])

The previous example was for adding a new user with a unique username to the database; However, if our request is
to edit a user, the previous example should change as follows to prevent the error from being displayed when the
user's current username is resubmitted:

.. code-block:: python

    id = String('id', processors=[v.Integer(), f.ToIntegerObject()])])
    username = String('username', processors=[v.Unique(model=Users, model_field_name='user_name', exclude_self_by_field=id)])

Note that in this example the "id" column of the model is used to identify each row of data. It is also necessary
to send a field named "id" with the value of the current row id of this user in the database in the submitted data
in order to exclude this row when checking the uniqueness of the username.

.. autoclass:: backendpy.data_handler.validators.IsEqualToField
    :noindex:

.. autoclass:: backendpy.data_handler.validators.DictInnerTypes
    :noindex:

.. autoclass:: backendpy.data_handler.validators.NoDuplicateDictItemValueInList
    :noindex:


Filters
.......
Filters are responsible for modifying data as needed, and changes are made when data passes through it.

Developers can create and use the various filters they need by inheriting from the base
:class:`~backendpy.data_handler.filters.Filter` class.

.. autoclass:: backendpy.data_handler.filters.Filter
    :noindex:

Default filters are also can be used:

Default filters
```````````````
.. autoclass:: backendpy.data_handler.filters.Escape
    :noindex:

.. autoclass:: backendpy.data_handler.filters.Cut
    :noindex:

.. autoclass:: backendpy.data_handler.filters.DecodeBase64
    :noindex:

.. autoclass:: backendpy.data_handler.filters.ParseDateTime
    :noindex:

.. autoclass:: backendpy.data_handler.filters.ToStringObject
    :noindex:

.. autoclass:: backendpy.data_handler.filters.ToIntegerObject
    :noindex:

.. autoclass:: backendpy.data_handler.filters.ToFloatObject
    :noindex:

.. autoclass:: backendpy.data_handler.filters.ToDecimalObject
    :noindex:

.. autoclass:: backendpy.data_handler.filters.ToBooleanObject
    :noindex:

.. autoclass:: backendpy.data_handler.filters.BlankToNull
    :noindex:

.. autoclass:: backendpy.data_handler.filters.ModifyImage
    :noindex:

Example:

.. code-block:: python

    from backendpy.data_handler import validators as v
    from backendpy.data_handler import filters as f
    ...

    image = String('image', processors=(v.NotNull(), f.DecodeBase64(), v.RestrictedFile(extensions=('jpg', 'jpeg', 'png'), min_size=1, max_size=2048), f.ModifyImage(format='JPEG')))

In this example, a combination of validators and filters is used. First it checks that the value is not null, then
it applies a filter to the received data and decodes it from base64 format, then it checks the allowed extensions for
the received file with validator, and if it passes, it converts the file to jpeg format with another filter.