from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool


#basemodel defines what parameters should be passed into the tool:
class numberModel(BaseModel):
     a: int = Field(
          description="first number that you want to perform an operation on"
     )
     b: int = Field(
          description="second number that you want to perform an operation on"
     )

# BASIC TOOL USED AS TOOL PLACEHOLDER AND EXAMPLE
#defines the tool, takes in basemodel as an argsschema and defines a function for the tool
@tool("perform_multiplication", return_direct=False, args_schema=numberModel)
def multiplication_tool(a: float, b: float) -> float:
    "Use this tool to multiply two numbers"
    return a * b