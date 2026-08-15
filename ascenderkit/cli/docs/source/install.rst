The preferred way to install the Ascender CLI is through pip:

.. code:: bash

    pip install ascender-kit

Some features are kept behind optional extras so the base install stays small:

.. code:: bash

    pip install "ascender-kit[websockets]"   # follow job output over a websocket
    pip install "ascender-kit[formatting]"   # jq-style filtering of JSON output
    pip install "ascender-kit[crypto]"       # encrypted credential support

To install from source instead, clone the repository and install it in editable
mode:

.. code:: bash

    git clone https://github.com/ctrliq/ascender-kit.git
    cd ascender-kit
    pip install -e .

To see a list of all available releases, visit:
https://github.com/ctrliq/ascender-kit/releases
