## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()
from crewai.tools import BaseTool

from crewai_tools import tools

# using the correct Serper import 
from crewai_tools import SerperDevTool

# using PyPDFium2 Loader from Langchain
from langchain_community.document_loaders.pdf import PyPDFium2Loader
## Creating search tool
search_tool = SerperDevTool()

## Creating custom pdf reader tool
class ReadPDFTool(BaseTool):
    name: str = "Read PDF Tool"
    description: str = "This tool reads the entire content of a PDF file given its file_path"
    def _read_pdf(self, file_path='data/sample.pdf'):
        """Tool to read data from a pdf file from a path

        Args:
            path (str, optional): Path of the pdf file. Defaults to 'data/sample.pdf'.

        Returns:
            str: Full Financial Document file
        """

        if not file_path or not os.path.exists(file_path):
            return f"Error: File not found at {file_path}"
        
        if not file_path.lower().endswith(".pdf"):
            return "Error: This tool only works with PDF (.pdf) files"
        
        try:
            # we'll load it page wise asynchronously
            docs = PyPDFium2Loader(file_path=file_path, mode="page").load()
        except Exception as e:
            raise Exception(f"Error loading the PDF: {str(e)}")

        full_report = ""
        for page_num, data in enumerate(docs, 1):
            # Clean and format the financial document data
            content = data.page_content

            # skip pages with no content
            if not content.strip(): continue

            # Remove extra whitespaces and format properly
            while "\n\n\n" in content:
                content = content.replace("\n\n\n", "\n\n")
            while "\n\n" in content:
                content = content.replace("\n\n", "\n")

            # fix any common spacing issues
            content = content.replace("$ ", "$") 
            content = content.replace(" %", "%") 
            content = content.replace(" ,", ",") 
                
            # add page number as a separator
            full_report += f"----------- Page Number {page_num} ---------------\n{content.strip()}\n\n"
            
        return full_report.strip()

## Creating Investment Analysis Tool
# class InvestmentTool:
#     async def analyze_investment_tool(financial_document_data):
#         # Process and analyze the financial document data
#         processed_data = financial_document_data
        
#         # Clean up the data format
#         i = 0
#         while i < len(processed_data):
#             if processed_data[i:i+2] == "  ":  # Remove double spaces
#                 processed_data = processed_data[:i] + processed_data[i+1:]
#             else:
#                 i += 1
                
#         # TODO: Implement investment analysis logic here
#         return "Investment analysis functionality to be implemented"

# ## Creating Risk Assessment Tool
# class RiskTool:
#     async def create_risk_assessment_tool(financial_document_data):        
#         # TODO: Implement risk assessment logic here
#         return "Risk assessment functionality to be implemented"