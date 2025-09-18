## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()
from crewai.tools import BaseTool

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
    def _run(self, file_path='data/sample.pdf'):
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

# Creating Investment Analysis Tool: REMOVED

# Creating Risk Assessment Tool: REMOVED

### NOTES WRT FIRST RUN OF CREW
# We see that despite not having tools for investment and risk analysis, the crew had no issues conducting the full analysis of the document.
# Empty tools would just have created problems for the LLM leading to a lot of confusion unnecessarily
# and they served no real purpose hence removed.

