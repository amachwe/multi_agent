from google.adk.agents import LlmAgent
from google.adk.models import  LlmRequest
from google.adk.agents.callback_context import CallbackContext
import logging
import yfinance
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Ensure log directory exists
os.makedirs('log', exist_ok=True)

AGENT_NAME = "greeter_agent"

# Configure file logging for main_agent
file_handler = logging.FileHandler('log/main_agent.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

MODEL="gemini-2.5-flash"

instructions="""
You have memory provided in memory section.
You can answer questions based your knowledge and the memory.
You are a friendly assistant.


"""
def before_model(callback_context: CallbackContext, llm_request: LlmRequest):
    logger.debug("Before model callback")
    logger.debug(f"Current session state: {callback_context}")
    logger.debug("----LlmRequest Details----")
    logger.debug(f"LlmRequest: {llm_request}")
    logger.debug("--------")
    text = llm_request.contents[0].parts[0].text
    llm_request.contents[0].parts[0].text = f"User's input: {text}\n\n## Use the following memory context:\n{callback_context.state.get('memory_snapshot','')}"
    logger.debug(f"LlmRequest: {llm_request}")
    logger.debug("----End of before model callback----")
    
def extract_stock_info(ticker: str) -> dict:
    """
    Extract stock information for a given ticker symbol.
    ticker - string ticker symbol for the stock
    """
    print("--- Extracting stock info ---")
    stock = yfinance.Ticker(ticker)
    return stock.info

agent = LlmAgent(
    name="Lead_Agent",
    model=MODEL,
    description="An agent that leads the task resoluton by using tools.",
    instruction=instructions,
    before_model_callback=before_model,
    tools=[extract_stock_info]
)



root_agent = agent