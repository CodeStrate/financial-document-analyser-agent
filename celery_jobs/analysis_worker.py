from job_database.job_db import DocumentAnalysisJobDB, DocumentAnalysisJobs
from crew.crew_utils import run_crew
import os
from celery import Celery
from dotenv import load_dotenv
load_dotenv()

# Fix: Use consistent Redis URL and add proper configuration
celery_app = Celery(
    "crewai_tasks", 
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0")
)

# Add Celery configuration to prevent threading issues
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_always_eager=False,
    task_eager_propagates=False,
    # Worker configuration to prevent threading issues
    worker_prefetch_multiplier=1,  # Process one task at a time
    task_acks_late=True,  # Acknowledge task only after completion
    worker_max_tasks_per_child=1,  # Restart worker after each task to prevent memory leaks
)

@celery_app.task
def analyze_document_task(job_id: str, file_path: str, query: str):
    """
    Celery task to analyze financial documents in the background
    
    Args:
        job_id: Unique job identifier
        file_path: Path to the uploaded PDF file
        query: User's analysis query
    """
    
    # Initialize database connection
    Session = DocumentAnalysisJobDB().get_local_session()
    local_session = Session()
    
    try:
        # Update job status to "Processing"
        job = local_session.query(DocumentAnalysisJobs).filter_by(job_id=job_id).first()
        if not job:
            raise Exception(f"Job {job_id} not found in database")
        
        job.job_status = "Processing"
        local_session.commit()
        print(f"Processing job {job_id} - file {file_path}")
        
        # Run the CrewAI analysis
        crew_result = run_crew(query, file_path)
        
        # Update job with results
        job.job_status = "Completed"
        job.job_result = str(crew_result)
        local_session.commit()
        print(f"Job Done: {job_id}")
        
    except Exception as e:
        # Update job status to failed
        print(f"Encountered Error in processing the job {job_id}: {e}")
        job.job_status = "Failed"
        job.job_result = f"Error: {str(e)}"
        local_session.commit()
        
    finally:
        # cleanup generated output files and file
        if os.path.exists(file_path): os.remove(file_path)

        outputs_dir = "outputs"
        if os.path.exists(outputs_dir):
            for file in os.listdir(outputs_dir):
                if file.endswith(".txt"):
                    try:
                        os.remove(os.path.join(outputs_dir, file))
                    except Exception:
                        pass  # Don't raise exceptions in finally block
                
        # close db session
        local_session.close()
