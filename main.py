from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
import os
import uuid
from sqlalchemy.orm import Session
import uvicorn
from job_database.job_db import DocumentAnalysisJobDB, DocumentAnalysisJobs
from celery_jobs.analysis_worker import analyze_document_task



app = FastAPI(title="Financial Document Analyzer (With Job Worker Queues)")

# create a dependency for sqlite db

def get_db():
    local_session = DocumentAnalysisJobDB().get_local_session()
    db = local_session()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Financial Document Analyzer API is running"}

@app.post("/analyze/")
async def analyze_financial_document(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights"),
    db: Session = Depends(get_db)
):
    """Analyze financial document and provide comprehensive investment recommendations"""
    
    file_id = str(uuid.uuid4())
    file_path = f"data/doc_{file.filename}_{file_id}.pdf"
    
    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Save uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Validate query
        if query=="" or query is None:
            query = "Analyze this financial document for investment insights"
            
        # Create a new job entry in DB
        new_analysis_job = DocumentAnalysisJobs(file_path=file_path, analysis_query=query)
        db.add(new_analysis_job)
        db.commit()
        
        analyze_document_task.delay(job_id=new_analysis_job.job_id, file_path=file_path, query=query)
        
        return {
            "status": "success",
            "message": "Analysis Job created and submitted.",
            "job_id": new_analysis_job.job_id,
            "file_processed": file.filename
        }
        
    except Exception as e:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass  # Ignore cleanup errors
        raise HTTPException(status_code=500, detail=f"Error processing financial document: {str(e)}")

@app.get("/status/{job_id}")
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """A GET Endpoint to check the status or progress of our submitted job."""
    job = db.query(DocumentAnalysisJobs).filter(DocumentAnalysisJobs.job_id == job_id).first()
    if not job: raise HTTPException(status_code=404, detail=f"Job with {job_id} doesn't exist.")

    return {
        "job_id" : job.job_id,
        "job_status" : job.job_status,
        "job_created_at" : job.created_at,
        "job_updated_at" : job.updated_at,
        "job_result" : job.job_result,
    }

# Run the app with Uvicorn
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost", 
        port=8000,
        reload=True,
        ws="none"  # Disabled websockets to avoid deprecation warning
    )