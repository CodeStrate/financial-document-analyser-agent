## Importing libraries and files
from crewai import Task
from os import makedirs
from crew.agents import financial_analyst, investment_advisor, risk_assessor, executive_summarizer

# Ensure we create outputs
makedirs("outputs", exist_ok=True)

# This task reads the provided PDF at {file_path} to generate a comprehensive financial report
financial_analysis_task = Task(
    description=
    """
    Use the Read PDF Tool to read the financial document at {file_path} and extract key financial data about the company.
    
    ### INSTRUCTIONS:
    1. First, use the Read PDF Tool with the file_path: {file_path}
    2. Analyze the extracted content for key financial metrics
    3. Focus on metrics such as revenue, profit margins, net income and earnings per share (EPS)
    4. Identify any financial trends or patterns
    5. Conduct a comprehensive SWOT (Strengths, Weaknesses, Opportunities and Threats) Analysis
    6. Only provide objective financial analysis - no investment advice or risk assessment
    """,

    expected_output=
    """
    A well-structured financial analysis report containing the following:
    1. Executive summary of the document, only highlighting key points.
    2. Extracted key financial metrics in clear format (Revenue: $X, Net Income: $Y, etc.).
    3. An analysis of financial trends like growth rates, YOY (year-over-year) changes.
    4. A short SWOT analysis (Strengths, Weaknesses, Opportunities and Threats) with 4-5 bullet points for each category.
    """,

    agent=financial_analyst,
    # Outputting the task result to see how or what the agent did.
    output_file="outputs/financial_analysis.txt",
)

## Creating an investment analysis task, taking context from the previous task
investment_analysis_task = Task(
    description=
    """
    Based on the financial analysis report provided, develop or formulate a strategic investment recommendations.
    ### CONSIDERATIONS:
    - Company growth trajectory, overall sentiment in market.
    - Market positioning and competitive advantages.
    - User's specific query below:
    Query: {query}

    It's important that the recommendation is backed by evidence from the financial report and is clear and easily actionable.
    """,

    expected_output=
    """
    A concise report detailing the investment recommendations/advisory with following:
    1. Summary of key financial health indicators (3-4 key indicators)
    2. Investment potential evaluation (growth prospects, company valuation)
    3. Clear investment recommendation (buy/hold/sell with reasoning)
    4. Specifc action items based on provided user query
    """,

    agent=investment_advisor,
    # We provide this agent the result of the previous agent as context to make a flow
    context=[financial_analysis_task],
    output_file="outputs/investment_advice.txt",
)

## Creating a risk assessment task
risk_assessment_task = Task(
    description=
    """
    Evaluate investment risks based on the financial analysis and investment recommendations provided.
    ### ASSESS THE FOLLOWING:
    - Financial risks like liquidity of assets, debt, and profitability.
    - Market risks like competition and industry trends.
    - Operational risks like management and regulation.

    Use web search tools to find current market conditions of the company or news that may impact it's risk profile.

    Provide balanced and realistic risk assessment that's data driven, objective and avoid sensationalizing the company in any way.
    """,

    expected_output=
    """
    A structured Risk assessment report that includes:
    1. An overall risk level classification (Low/Medium/High).
    2. A comprehensive list of identified risks categorized by type (Market, Financial, etc.).
    3. Analysis of potential portfolio impact and the likelihood of each risk.
    4. A simple summary of company risk profile and any timeline considerations for investment decisions.
    """,

    agent=risk_assessor,
    context=[financial_analysis_task, investment_analysis_task],
    output_file="outputs/risk_assessment.txt"
)

# Executive Summary Task: Consolidates all analysis into final report
executive_summary_task = Task(
    description=
    """
    Create a comprehensive executive summary that consolidates the financial analysis, investment recommendations, 
    and risk assessment into a single, professional report.
    
    ### STRUCTURE THE REPORT AS FOLLOWS:
    1. Executive Summary (2-3 paragraphs highlighting key findings)
    2. Financial Health Overview (key metrics and trends)
    3. Investment Recommendation (clear buy/hold/sell with rationale)
    4. Risk Profile Summary (overall risk level and key concerns)
    5. Action Items and Timeline (specific next steps)
    
    ### REQUIREMENTS:
    - Write in clear, professional language suitable for executives
    - Prioritize actionable insights over technical details
    - Ensure consistency across all recommendations
    - Address the user's specific query: {query}
    """,

    expected_output=
    """
    A polished executive summary report (2-3 pages) containing:
    1. Executive Summary with key findings and overall recommendation
    2. Financial Health Overview with critical metrics
    3. Clear Investment Recommendation with supporting rationale
    4. Consolidated Risk Assessment with overall risk rating
    5. Specific Action Items with recommended timeline
    6. Appendix with key data points for reference
    
    The report should be decision-ready and provide clear guidance for investment actions.
    """,

    agent=executive_summarizer,
    context=[financial_analysis_task, investment_analysis_task, risk_assessment_task],
    output_file="outputs/executive_summary.txt"
)

# Extra Notes: We can simply prompt the first agent for verification, making a task for it is redundant.
# Also output_file just serves a debug purpose to see if the agents' output is desirable to the given task.

# verification = Task(... REMOVED
