from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid
import asyncio
import uvicorn
from crewai import Crew, Process
from agents import financial_analyst, investment_advisor, risk_assessor
from task import financial_analysis_task, investment_analysis_task, risk_assessment_task

app = FastAPI(title="Financial Document Analyzer")

def run_crew(query: str, file_path: str="data/sample.pdf"):
    """To run the whole crew"""
    try:
        financial_crew = Crew(
            agents=[financial_analyst, investment_advisor, risk_assessor],
            tasks=[financial_analysis_task, investment_analysis_task, risk_assessment_task],
            process=Process.sequential,
        )
        
        result = financial_crew.kickoff(inputs={'query': query, 'file_path' : file_path})
        return result
    
    except AttributeError as ae:
        raise AttributeError(f"Attribute Error in run_crew: {ae}")
    except Exception as e:
        raise Exception(f"Error in run_crew: {e}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Financial Document Analyzer API is running"}

@app.post("/analyze")
async def analyze_financial_document(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights")
):
    """Analyze financial document and provide comprehensive investment recommendations"""
    
    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"
    
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
            
        # Process the financial document with all analysts
        response = run_crew(query=query.strip(), file_path=file_path)
        
        return {
            "status": "success",
            "query": query,
            "analysis": str(response),
            "file_processed": file.filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing financial document: {str(e)}")
    
    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass  # Ignore cleanup errors

# Run the app with Uvicorn
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost", 
        port=8000,
        reload=True,
        ws="none"  # Disabled websockets to avoid deprecation warning
    )