Building the Documentation
--------------------------
To build the docs, spin up a real Ascender server, install the `docs` extra with `pip install -e ".[docs]"`, and run:

    ~ CONTROLLER_HOST=https://ascender.example.org CONTROLLER_USERNAME=example CONTROLLER_PASSWORD=secret make clean html
    ~ cd build/html/ && python -m http.server
    Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ..
