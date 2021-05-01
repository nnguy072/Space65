How to Run
===

Windows
---

Install
```
1. install python
2. In root directory run: python3 -m venv venv
    1. or just: python -m venv venv
3. In the root directory run: `venv\Scripts\activate`
4. Within the activated env run: `pip install -r requirements.txt`
5. Run: `$env:FLASK_APP=app.py`
6. To quit the activated env run: `deactivate`
```

Run
```
1. In the root directory run: `venv\Scripts\activate`
2. You should see something like (venv)
3. If this is your first time setting up the project do: 
    1. `$env:FLASK_APP=app.py`
    2. `$env:FLASK_RUN_PORT=3030`
4. To run do: `flask run`
```