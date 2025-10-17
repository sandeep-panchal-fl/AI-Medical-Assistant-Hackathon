import boto3
from dotenv import load_dotenv
from langchain_aws import ChatBedrock
import os

class BedrockModel:
    """
    A class to initialize and hold a ChatBedrock language model instance.
    """
    def __init__(self,
        custom_model_kwargs: dict = None, # Default kwargs allow the user to easily override temperature, etc.
        ):

        # loading the environmental variables
        load_dotenv(dotenv_path= "/app/.env")

        # define standard Bedrock configuration
        region_name = os.getenv("AWS_REGION")
        model_arn = "arn:aws:bedrock:us-east-1:463554030939:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0"
        model_provider = "anthropic"
        
        # base model arguments, which can be overwritten by the user's input
        base_model_kwargs = {"temperature": 0}
        if custom_model_kwargs:
            base_model_kwargs.update(custom_model_kwargs)

        # initialize a Bedrock client
        self.bedrock_client = boto3.client(
            service_name="bedrock-runtime",
            region_name=region_name
        )
        
        # initialize the ChatBedrock instance
        self.llm_chat = ChatBedrock(
            client=self.bedrock_client,
            model_id=model_arn,
            provider=model_provider,
            model_kwargs=base_model_kwargs
        )

if __name__=="__main__":
    pass