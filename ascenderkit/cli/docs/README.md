Building the Documentation
--------------------------
To build the docs, spin up a real Ascender server, `pip install sphinx sphinxcontrib-autoprogram`, and run:

    ~ CONTROLLER_HOST=https://ascender.example.org CONTROLLER_USERNAME=example CONTROLLER_PASSWORD=secret make clean html
    ~ cd build/html/ && python -m http.server
    Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ..

Why this is not built in CI
--------------------------
`ascenderkit/cli/sphinx.py` ends with `parser = render()`, so importing the
extension performs an HTTP OPTIONS request against every resource of a running
Ascender. Sphinx cannot start without one, which is why no workflow builds these
pages. Moving `render()` out of import time is the prerequisite for a CI job,
not the job itself.
