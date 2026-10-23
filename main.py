import os
import shutil
import tempfile
import traceback
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import database

from Agents.graph import build_graph

app = FastAPI(title="Data Pipeline Detective")

pipeline_graph = build_graph()

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

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
        
        # Save ONLY the resulting JSON report to SQLite database linked to user
        database.save_investigation(user_id, file.filename, final_state)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Pipeline execution error: {str(e)}")
    finally:
        # Clean up the temporary file after execution
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    return final_state

@app.get("/api/history/{user_id}")
def get_history(user_id: int):
    return database.get_user_investigations(user_id)

@app.get("/", response_class=FileResponse)
async def get_frontend():
    return "frontend/index.html"