Code Documentation
==================

Main Functions
~~~~~~~~~~~~~~

.. autofunction:: llamator.start_testing
   :noindex:

.. note::

   This function starts the testing process with different configurations.

Abstract Classes
~~~~~~~~~~~~~~~~

.. autoclass:: llamator.ClientBase
   :undoc-members:

.. note::

   ClientBase is an abstract base class for client implementations.

.. autoclass:: llamator.TestBase
   :undoc-members:

.. note::

   TestBase is an abstract base class designed for attack handling in the testing framework.

Available Clients
~~~~~~~~~~~~~~~~~

.. autoclass:: llamator.ClientLangChain
   :undoc-members:
   :show-inheritance:
   :noindex:

.. note::

   ClientLangChain is a client implementation for LangChain-based services.

.. autoclass:: llamator.ClientOpenAI
   :undoc-members:
   :show-inheritance:
   :noindex:

.. note::

   ClientOpenAI is a client implementation for OpenAI-based services.

Additional Utility Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: llamator.utils.test_presets.get_test_preset
   :noindex:

.. note::

   This function generates an example code snippet for configuring basic_tests based on a preset configuration.
   It returns a code snippet as a string.

.. autofunction:: llamator.utils.test_presets.print_test_preset
   :noindex:

.. note::

   This function prints an example configuration for basic_tests based on a preset to the console.

.. autofunction:: llamator.client.langchain_integration.print_chat_models_info
   :noindex:

.. note::

   This function prints information about LangChain chat models in a well-formatted manner.
   It displays details such as the model name, a short description, and its supported parameters.