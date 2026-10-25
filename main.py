import math
import os
import numpy as np
import shutil
import tempfile
import traceback
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import sqlite3
from dotenv import load_dotenv

load_dotenv()

from Agents.graph import build_graph
import database

app = FastAPI(title="Data Pipeline Detective")

pipeline_graph = build_graph()

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

def clean_nans(obj):
    """Recursively convert float NaN, Infinity, and numpy scalar types to None for valid JSON serialization."""
    if isinstance(obj, (float, np.floating)):
        if math.isnan(obj) or math.isinf(obj) or np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)
    elif isinstance(obj, (int, np.integer)):
        return int(obj)
    elif isinstance(obj, dict):
        return {str(k): clean_nans(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [clean_nans(v) for v in obj]
    return obj

@app.post("/api/signup")
def signup(username: str = Form(...), password: str = Form(...)):
    res = database.create_user(username, password)
    if not res["success"]:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

@app.post("/api/login")
def login(username: str = Form(...), password: str = Form(...)):
    res = database.authenticate_user(username, password)
    if not res["success"]:
        raise HTTPException(status_code=401, detail=res["error"])
    return res

@app.post("/api/investigate")
async def investigate_pipeline(
    file: UploadFile = File(...),
    user_id: int = Form(...)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
    
    # Save uploaded file to a temporary location
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_file_path = tmp.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save temporary file: {str(e)}")

    # Initialize the LangGraph state
    initial_state = {
        "file_path": temp_file_path,
        "profile": {},
        "anomaly": {},
        "root_cause": "",
        "database_fix": "",
        "validation": {}
    }

    try:
        # Run the agent team workflow
        final_state = pipeline_graph.invoke(initial_state)
        
        # Clean NaNs and Infs FIRST so json.dumps inside database storage won't crash
        cleaned_state = clean_nans(final_state)
        
        # Save the sanitized JSON report to SQLite database linked to user
        database.save_investigation(user_id, file.filename, cleaned_state)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Pipeline execution error: {str(e)}")
    finally:
        # Clean up the temporary file after execution
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    return cleaned_state

@app.get("/api/history/{user_id}")
def get_history(user_id: int):
    history= database.get_user_investigations(user_id)
    return clean_nans(history)

@app.get("/", response_class=FileResponse)
async def get_frontend():
    return "frontend/index.html"

secret_key = os.getenv("SECRET_KEY")

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(key: str = Query(...)):
    if key != secret_key:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    conn = sqlite3.connect("detective.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()
    
    cursor.execute("SELECT id, user_id, filename, timestamp FROM investigations ORDER BY id DESC")
    investigations = cursor.fetchall()
    
    conn.close()
    
    # Generate clean HTML view of the live container database
    users_rows = "".join([f"<tr><td class='p-2 border border-slate-800'>{u[0]}</td><td class='p-2 border border-slate-800'>{u[1]}</td></tr>" for u in users])
    inv_rows = "".join([f"<tr><td class='p-2 border border-slate-800'>{i[0]}</td><td class='p-2 border border-slate-800'>{i[1]}</td><td class='p-2 border border-slate-800'>{i[2]}</td><td class='p-2 border border-slate-800'>{i[3]}</td></tr>" for i in investigations])
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Detective Admin Panel</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-slate-100 p-8 font-sans">
        <div class="max-w-4xl mx-auto space-y-6">
            <h1 class="text-3xl font-extrabold text-blue-400">Live Render Container Database</h1>
            
            <div>
                <h2 class="text-lg font-semibold text-amber-400 mb-2">Registered Users ({len(users)})</h2>
                <table class="w-full border border-slate-800 bg-slate-900 text-left text-sm rounded-xl overflow-hidden">
                    <tr class="bg-slate-800"><th class="p-2 border border-slate-700">ID</th><th class="p-2 border border-slate-700">Username</th></tr>
                    {users_rows if users_rows else "<tr><td colspan='2' class='p-4 text-slate-500 text-center'>No users found.</td></tr>"}
                </table>
            </div>

            <div>
                <h2 class="text-lg font-semibold text-emerald-400 mb-2">Past Investigations ({len(investigations)})</h2>
                <table class="w-full border border-slate-800 bg-slate-900 text-left text-sm rounded-xl overflow-hidden">
                    <tr class="bg-slate-800"><th class="p-2 border border-slate-700">ID</th><th class="p-2 border border-slate-700">User ID</th><th class="p-2 border border-slate-700">Filename</th><th class="p-2 border border-slate-700">Timestamp</th></tr>
                    {inv_rows if inv_rows else "<tr><td colspan='4' class='p-4 text-slate-500 text-center'>No investigations found.</td></tr>"}
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)