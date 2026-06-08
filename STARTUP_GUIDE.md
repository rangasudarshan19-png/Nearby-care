# Nearby Care Startup Guide

Use the single launcher in the project root:

```bat
RUN.bat
```

`RUN.bat` does the full startup flow:

- checks Python and npm are available
- creates the backend logs folder
- creates the SQLite database if it is missing
- installs frontend packages if `node_modules` is missing
- starts the Flask backend on http://localhost:5000
- starts the React frontend on http://localhost:3000
- opens http://localhost:3000 in your browser

Keep the two server command windows open while using the app. Close those windows to stop the backend and frontend.

If startup fails, read the error shown in the `RUN.bat` window first. Most failures are missing Python, missing Node.js/npm, or a port already being used.
