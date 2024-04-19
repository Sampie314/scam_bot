from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
import checkscam
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)

#basemodel defines what parameters should be passed into the tool:
class numberModel(BaseModel):
     a: int = Field(
          description="first number that you want to perform an operation on"
     )
     b: int = Field(
          description="second number that you want to perform an operation on"
     )
class scamMessageModel(BaseModel):
    message: str = Field(
        description="message that you want to check if it is a scam"
    )

# BASIC TOOL USED AS TOOL PLACEHOLDER AND EXAMPLE
#defines the tool, takes in basemodel as an argsschema and defnes a function for the tooli
@tool("perform_multiplication", return_direct=False, args_schema=numberModel)
def multiplication_tool(a: float, b: float) -> float:
    "DONT USE THIS TOOL AT ALL IT IS JUST A PLACEHOLDER"
    return a * b


@tool("check_if_message_is_scam", return_direct=False, args_schema=scamMessageModel)
def check_scam_message_tool(message: str) -> int:
     "Use this tool to check how many times users have submitted this message to check if it is a scam"
     logging.debug('check_scam_message_tool called')
     seen_times = checkscam.retrieve_message_seen_count(message)

     # prompt = checkscam.generate_check_scam_prompt(message, seen_times)
     return seen_times