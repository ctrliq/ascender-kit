Usage Examples
==============

Verifying CLI Configuration
---------------------------

To confirm that you've properly configured ``ascender`` to point at the correct
Ascender host, and that your authentication credentials are correct, run:

.. code:: bash

    ascender config

.. note:: For help configuring authentication settings with the ascender CLI, see :ref:`authentication`.

Printing the History of a Particular Job
----------------------------------------

To print a table containing the recent history of any jobs named ``Example Job Template``:

.. code:: bash

    ascender jobs list --all --name 'Example Job Template' \
        -f human --filter 'name,created,status'

Creating and Launching a Job Template
-------------------------------------

Assuming you have an existing Inventory named ``Demo Inventory``, here's how
you might set up a new project from a GitHub repository, and run (and monitor
the output of) a playbook from that repository:

.. code:: bash

    ascender projects create --wait \
        --organization 1 --name='Example Project' \
        --scm_type git --scm_url 'https://github.com/ansible/ansible-tower-samples' \
        -f human
    ascender job_templates create \
        --name='Example Job Template' --project 'Example Project' \
        --playbook hello_world.yml --inventory 'Demo Inventory' \
        -f human
    ascender job_templates launch 'Example Job Template' --monitor -f human

Updating a Job Template with Extra Vars
---------------------------------------

.. code:: bash

    ascender job_templates modify 1 --extra_vars "@vars.yml"
    ascender job_templates modify 1 --extra_vars "@vars.json"

Importing an SSH Key
--------------------

.. code:: bash

    ascender credentials create --credential_type 'Machine' \
        --name 'My SSH Key' --user 'alice' \
        --inputs '{"username": "server-login", "ssh_key_data": "@~/.ssh/id_rsa"}'

Import/Export
-------------

Intended to be similar to `tower-cli send` and `tower-cli receive`.

Exporting everything:

.. code:: bash

    ascender export

Exporting everything of some particular type or types:

.. code:: bash

    ascender export --users

Exporting a particular named resource:

.. code:: bash

    ascender export --users admin

Exporting a resource by id:

.. code:: bash

    ascender export --users 42

Importing a set of resources stored as a file:

.. code:: bash

    ascender import < resources.json
