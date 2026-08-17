Building the Documentation
--------------------------
To build the docs, spin up a real Ascender server, `pip install sphinx sphinxcontrib-autoprogram`, and run:

    ~ CONTROLLER_HOST=https://ascender.example.org CONTROLLER_USERNAME=example CONTROLLER_PASSWORD=secret make clean html
    ~ cd build/html/ && python -m http.server
    Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ..
