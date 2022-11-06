.. currentmodule:: slack

API Reference
===============

The following section outlines the API of Pycord.

.. note::

    This module uses the Python logging module to log diagnostic and errors
    in an output independent way.  If the logging module is not configured,
    these logs will not be output anywhere.  See for
    more information on how to set up and use the logging module with
    Pycord.

Client
------

.. attributetable:: slack.Client

.. autoclass:: Client
    :members:
    :exclude-members: event

    .. automethod:: Client.event()
        :decorator:

ConnectionState
---------------

.. attributetable:: slack.Message

.. autoclass:: slack.ConnectionState
    :members:


Message
-------

.. attributetable:: slack.Message

.. autoclass:: slack.Message
    :members:

Channel
-------

.. attributetable:: slack.Channel

.. autoclass:: slack.Channel
    :members:

Member
------

.. attributetable:: slack.Member

.. autoclass:: slack.Member
    :members:

Team
----

.. attributetable:: slack.Team

.. autoclass:: slack.Team
    :members:
