.. currentmodule:: slack

.. _api-models:

Models
======

.. note::

    Nearly all classes here have slots defined which means that it is
    impossible to have dynamic attributes to the data classes.


Messages
--------

Message
~~~~~~~

.. attributetable:: Message

.. autoclass:: Message()
    :members:

DeletedMessage
~~~~~~~~~~~~~~

.. attributetable:: DeletedMessage

.. autoclass:: DeletedMessage()
    :members:
    :inherited-members:


JoinMessage
~~~~~~~~~~~

.. attributetable:: JoinMessage

.. autoclass:: JoinMessage()
    :members:
    :inherited-members:

ScheduledMessage
~~~~~~~~~~~~~~~~

.. attributetable:: ScheduledMessage

.. autoclass:: ScheduledMessage()
    :members:

Blocks
------

Block
~~~~~

.. attributetable:: Block

.. autoclass:: Block()
    :members:

Action
~~~~~~

.. attributetable:: Action

.. autoclass:: Action()
    :members:


Channels
--------

Channel
~~~~~~~

.. attributetable:: Channel

.. autoclass:: Channel()
    :inherited-members:
    :members:

DeletedChannel
~~~~~~~~~~~~~~

.. attributetable:: DeletedChannel

.. autoclass:: DeletedChannel()
    :members:
    :inherited-members:

Teams
-----

.. attributetable:: Team

.. autoclass:: Team()
    :members:

Icon
~~~~

.. attributetable:: Icon

.. autoclass:: Icon()
    :members:



Members
-------

.. attributetable:: Member

.. autoclass:: Member()
    :members:
    :inherited-members:

Reactions
---------

ReactionComponent
~~~~~~~~~~~~~~~~~

.. attributetable:: ReactionComponent

.. autoclass:: ReactionComponent()
    :members:

Reaction-Event
~~~~~~~~~~~~~~

.. attributetable:: ReactionEvent

.. autoclass:: ReactionEvent()
    :members:
