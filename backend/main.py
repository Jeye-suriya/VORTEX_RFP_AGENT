import os
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from orchestrator_agent import OrchestratorAgent

app = FastAPI()

# Allow CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/upload")
async def upload_rfp(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return {"filename": file.filename}

@app.post("/generate")
async def generate_proposal(filename: str, background_tasks: BackgroundTasks):
    pdf_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="File not found.")
    output_file = os.path.join(OUTPUT_DIR, f"proposal_{filename}")
    def run_orchestrator():
        orch = OrchestratorAgent()
        orch.run_and_export(pdf_path, output_file)
    background_tasks.add_task(run_orchestrator)
    return {"message": "Proposal generation started.", "output_file": f"proposal_{filename}"}

@app.get("/download/{output_file}")
async def download_proposal(output_file: str):
    file_path = os.path.join(OUTPUT_DIR, output_file)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Proposal not ready yet.")
    return FileResponse(file_path, media_type="application/pdf", filename=output_file)

@app.get("/health")
def health():
    return {"status": "ok"}
