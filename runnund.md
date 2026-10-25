# Running the AI Medical Report Explainer

Run these commands in **two separate PowerShell terminals** from the repository
root (`D:\College - Projects\AI Medical Report Explainer`).

## Start the backend

Make sure local MySQL Community Server is running and `backend\.env` contains
valid database credentials. To start the backend:

```powershell
Set-Location "D:\College - Projects\AI Medical Report Explainer\backend"
.\venv\Scripts\Activate.ps1
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend API: <http://127.0.0.1:8000>  
API documentation: <http://127.0.0.1:8000/docs>  
Health check: <http://127.0.0.1:8000/health>

If Uvicorn reports `[WinError 10013]` while binding to port `8000`, a backend
is already listening on that port. Check it at the health-check URL above and
do not start a second Uvicorn process. To stop the existing server, press
`Ctrl+C` in the terminal where it is running, then start it again.

The backend uses Gemini when `LLM_PROVIDER=gemini` is set in `backend\.env`.
Set a valid `GEMINI_API_KEY` there; do not place the key in frontend files or
commit it to Git. A missing or invalid key causes Gemini requests to fail with
an error.

## Start the frontend

In a second PowerShell terminal:

```powershell
Set-Location "D:\College - Projects\AI Medical Report Explainer\frontend"
npm install
npm run dev -- --host 127.0.0.1
```

Frontend: <http://127.0.0.1:5173>

## Stop the application

Press `Ctrl+C` in each terminal running the backend and frontend.
