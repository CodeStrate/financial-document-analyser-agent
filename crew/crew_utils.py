from crewai import Crew, Process
from crew.agents import financial_analyst, investment_advisor, risk_assessor, executive_summarizer
from crew.tasks import financial_analysis_task, investment_analysis_task, risk_assessment_task, executive_summary_task

def run_crew(query: str, file_path: str="data/sample.pdf"):
    """To run the whole crew"""
    try:
        financial_crew = Crew(
            agents=[financial_analyst, investment_advisor, risk_assessor, executive_summarizer],
            tasks=[financial_analysis_task, investment_analysis_task, risk_assessment_task, executive_summary_task],
            process=Process.sequential,
        )
        
        result = financial_crew.kickoff(inputs={'query': query, 'file_path' : file_path})
        return result
    
    except AttributeError as ae:
        raise AttributeError(f"Attribute Error in run_crew: {ae}")
    except Exception as e:
        raise Exception(f"Error in run_crew: {e}")