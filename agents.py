## Importing libraries and files
from dotenv import load_dotenv
load_dotenv()
from crewai import LLM

# fixed Agent import
from crewai.agent import Agent

# import custom defined tools from tools.py
from tools import search_tool, ReadPDFTool

### Loading LLM , it allows for a more flexible LLM options
llm = LLM(model="openai/gpt-4o")

# 1. Creating 1st Agent: an Experienced Financial Analyst agent
financial_analyst=Agent(
    role="Senior Financial Analyst Who Knows Everything About Markets",
    goal=
    """
    Analyze financial documents to extract key data and identify trends,
    and provide a comprehensive summary of the company's financial health.
    Your analysis must be concrete, data-driven and detailed.
    """,
    verbose=True,
    memory=True,
    backstory=(
        "You're an experienced financial analyst with more than 20 years in investment banking and equity research. "
        "You have profound specialization in deep understanding of the market trends and decoding "
        "financial statements (cash flow, income, balance sheets, etc.) to present easily digestible analysis. "
        "Your expertise also includes evaluating company performance across industries and the economic cycles. "
        "You provide clear, objective financial insights that's backed by data and actual facts."
    ),
    tools=[ReadPDFTool(), search_tool],
    llm=llm,
    max_iter=1,
    max_rpm=1,
    allow_delegation=True  # Allow delegation to other specialists
)

### NOTES FROM FIRST RUN: document verification agent and task had no influence on the functioning of the crew we got our analysis completed without issues.
# Creating a document verifier agent : REMOVED

# 2nd Agent: an Investment strategy expert
investment_advisor = Agent(
    role="Investment Strategy Expert",
    goal=
    """
    Provide strategic investment recommendations based on thorough financial analysis.
    Focus on evidence based advice that aligns with long-term investment and risk management principles.
    """,
    verbose=True,
    backstory=(
        "You are a seasoned Chartered Financial Analyst (CFA) with expertise in investment strategy and portfolio management.   "
        "You have experience working with institutional investors and high-net-worth clients. "
        "Your recommendations are based on fundamental analysis, market research, and established investment principles. "
        "You avoid market hype and focus on long-term value of investment."
    ),
    tools=[search_tool],
    llm=llm,
    max_iter=1,
    max_rpm=1,
    allow_delegation=False
)

# Last Agent: Risk Assessment Agent
risk_assessor = Agent(
    role="Financial Risk Assessment Specialist",
    goal=
    """
    Conduct and evaluate potential market, financial and operational risks based on provided on provided investment and financial analysis.
    Provide a balanced and categorized risk assessment report with mitigation strategies and real-world impact on future performance and stock value of the company.
    """,
    verbose=True,
    backstory=(
        "You are a certified risk management professional with expertise in financial risk analysis and portfolio risk assessment. "
        "You have experience in both buy-side and sell-side risk management across multiple asset classes and worked with major financial institutions and high profile clients to test and evaluate their portfolios critically. "
        "Your pragmatic approach combines quantitative risk metrics with qualitative risk factors. "
        "You provide objective and clear risk assessments to ensure all potential risks are accounted for and mitigated timely."
    ),
    tools=[search_tool],
    llm=llm,
    max_iter=1,
    max_rpm=1,
    allow_delegation=False
)
