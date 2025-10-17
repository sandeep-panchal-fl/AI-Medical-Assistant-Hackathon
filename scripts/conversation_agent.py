import yaml
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from bedrock_initializer import BedrockModel

class ConversationAgent(BedrockModel):

    def __init__(self, **kwargs):

        # accessing bedrock model from it self.llm_chat
        super().__init__(**kwargs) 

        self.intermediate_summary_threshold = 10
        self.final_summary_threshold = 20

        self.store = {}
        self.full_chat_session = {}

        # Load prompts
        # prompts_path = "prompts.yaml"
        prompts_path = "/app/scripts/prompts.yaml"
        with open(prompts_path, 'r') as f:
            prompts = yaml.safe_load(f)

        # Access prompts
        self.system_chat_prompt = prompts['medical_assistant']['system_chat_prompt']
        self.intermediate_summary_prompt = prompts['medical_assistant']['intermediate_summary_prompt']
        
        self.chat_with_history = RunnableWithMessageHistory(self.llm_chat, self.get_history)

    def get_conversation_text(self, history):
        """Convert conversation to readable text"""
        conversation_lines = []
        
        for message in history.messages:
            if isinstance(message, HumanMessage):
                conversation_lines.append(f"Patient: {message.content}")
            elif isinstance(message, AIMessage):
                conversation_lines.append(f"Assistant: {message.content}")
        
        # remove last ai message for intermediate summary
        conversation_lines = conversation_lines[:-1]

        return "\n".join(conversation_lines)

    def generate_intermediate_summary(self, session_id):
        """Generate summary - backend only, not shown to user"""
        history = self.store[session_id]

        # Intermediate summary (backend only)
        last_ai_msg = history.messages[-1].content
        conversation_lines = self.get_conversation_text(history)
        summary = self.llm_chat.invoke([
            SystemMessage(content=self.intermediate_summary_prompt),
            HumanMessage(content=conversation_lines)
        ])
        
        # Reset history with summary as context
        self.store[session_id] = ChatMessageHistory()
        self.store[session_id].add_message(SystemMessage(content=self.system_chat_prompt))
        self.store[session_id].add_message(HumanMessage(content=f"Previous conversation summary: {summary.content}"))
        self.store[session_id].add_message(AIMessage(content=last_ai_msg))

        print("=== BACKEND: Intermediate summary completed ===")
        print(summary)
        return None  # Don't return summary to frontend

    def get_history(self, session_id):
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
            self.store[session_id].add_message(SystemMessage(content=self.system_chat_prompt))
        return self.store[session_id]
    
    def get_full_chat(self, user_query, ai_resp, session_id, stop_chat):
        
        full_chat = []

        if session_id not in self.full_chat_session:
            self.full_chat_session[session_id] = ChatMessageHistory()

        if not stop_chat:
            self.full_chat_session[session_id].add_message(HumanMessage(content=user_query))
            self.full_chat_session[session_id].add_message(AIMessage(content=ai_resp.content))
    
        if stop_chat:
            full_chat_history = self.full_chat_session[session_id]
            if full_chat_history:
                for message in full_chat_history.messages:
                    if isinstance(message, HumanMessage):
                        full_chat.append({"HumanMessage":message.content})
                    elif isinstance(message, AIMessage):
                        full_chat.append({"AIMessage":message.content})

        return full_chat

    def chat(self, session_id, user_query):

        history = self.get_history(session_id)
        
        # Add human message to history
        history.add_message(HumanMessage(content=user_query))

        if user_query.lower().strip() in ["stop", "end", "finish"]:
            resp = AIMessage(content="STOP")
        else:
            resp = self.chat_with_history.invoke(
                {"messages":[]},
                config={"configurable": {"session_id": session_id}}
            )

        stop_chat = False

        full_chat = self.get_full_chat(user_query, resp, session_id, stop_chat)
        
        # Check if conversation should stop
        if "stop" in resp.content.lower():
            stop_chat = True
            full_chat = self.get_full_chat(user_query, resp, session_id, stop_chat)
            return resp.content, stop_chat, full_chat

        # Generate intermediate summary if threshold reached (backend only)
        if len(history.messages) == self.intermediate_summary_threshold + 1:
            print("=== BACKEND: Generating intermediate summary ===")
            self.generate_intermediate_summary(session_id)
            # Continue with normal conversation
        
        # Return only the AI response for frontend display
        return resp.content, stop_chat, full_chat
    
if __name__=="__main__":

    import uuid
    
    obj = ConversationAgent()

    session = str(uuid.uuid4())
    user_query ="i have severe headache"

    run_loop = True
    while run_loop:

        user_query = input("Enter your query :- ")
        response, stop_chat, full_chat = obj.chat(session, user_query)

        print(f"AI Response: {response}")
        if stop_chat:
            print(f"Final summary:\n {response}")
            run_loop = False
    
    print("==== Full chat ====")
    print(full_chat)



######################################################################################

# import yaml
# from langchain_community.chat_message_histories import ChatMessageHistory
# from langchain_core.runnables.history import RunnableWithMessageHistory
# from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
# # from dotenv import load_dotenv
# # from langchain_aws import ChatBedrock
# # import boto3

# from bedrock_initializer import BedrockModel

# class ConversationAgent(BedrockModel):

#     def __init__(self, **kwargs):

#         super().__init__(**kwargs) 

#         # load_dotenv(dotenv_path="../.env")

#         # # Initialize a Bedrock client
#         # bedrock_client = boto3.client(
#         #     service_name="bedrock-runtime",
#         #     region_name="us-east-1" # Replace with your desired region
#         # )
        
#         # # Define the model ARN and provider
#         # model_arn = "arn:aws:bedrock:us-east-1:463554030939:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0" # Replace with your actual ARN
#         # model_provider = "anthropic"

#         # # Initialize ChatBedrock with both model_id (ARN) and provider
#         # self.llm_chat = ChatBedrock(
#         #     client=bedrock_client,
#         #     model_id=model_arn,
#         #     provider=model_provider,
#         #     model_kwargs={"temperature": 0}
#         # )

#         self.intermediate_summary_threshold = 10
#         self.final_summary_threshold = 20

#         self.store = {}
#         self.full_chat_session = {}

#         # Load prompts
#         with open('prompts.yaml', 'r') as f:
#             prompts = yaml.safe_load(f)

#         # Access prompts
#         self.system_chat_prompt = prompts['medical_assistant']['system_chat_prompt']
#         self.intermediate_summary_prompt = prompts['medical_assistant']['intermediate_summary_prompt']
        
#         self.chat_with_history = RunnableWithMessageHistory(self.llm_chat, self.get_history)

#     def get_conversation_text(self, history):
#         """Convert conversation to readable text"""
#         conversation_lines = []
        
#         for message in history.messages:
#             if isinstance(message, HumanMessage):
#                 conversation_lines.append(f"Patient: {message.content}")
#             elif isinstance(message, AIMessage):
#                 conversation_lines.append(f"Assistant: {message.content}")
        
#         # remove last ai message for intermediate summary
#         conversation_lines = conversation_lines[:-1]

#         return "\n".join(conversation_lines)

#     def generate_intermediate_summary(self, session_id):
#         """Generate summary - backend only, not shown to user"""
#         history = self.store[session_id]

#         # Intermediate summary (backend only)
#         last_ai_msg = history.messages[-1].content
#         conversation_lines = self.get_conversation_text(history)
#         summary = self.llm_chat.invoke([
#             SystemMessage(content=self.intermediate_summary_prompt),
#             HumanMessage(content=conversation_lines)
#         ])
        
#         # Reset history with summary as context
#         self.store[session_id] = ChatMessageHistory()
#         self.store[session_id].add_message(SystemMessage(content=self.system_chat_prompt))
#         self.store[session_id].add_message(HumanMessage(content=f"Previous conversation summary: {summary.content}"))
#         self.store[session_id].add_message(AIMessage(content=last_ai_msg))

#         print("=== BACKEND: Intermediate summary completed ===")
#         print(summary)
#         return None  # Don't return summary to frontend

#     def get_history(self, session_id):
#         if session_id not in self.store:
#             self.store[session_id] = ChatMessageHistory()
#             self.store[session_id].add_message(SystemMessage(content=self.system_chat_prompt))
#         return self.store[session_id]
    
#     def get_full_chat(self, user_query, ai_resp, session_id, stop_chat):
        
#         full_chat = []

#         if session_id not in self.full_chat_session:
#             self.full_chat_session[session_id] = ChatMessageHistory()

#         if not stop_chat:
#             self.full_chat_session[session_id].add_message(HumanMessage(content=user_query))
#             self.full_chat_session[session_id].add_message(AIMessage(content=ai_resp.content))
    
#         if stop_chat:
#             full_chat_history = self.full_chat_session[session_id]
#             if full_chat_history:
#                 for message in full_chat_history.messages:
#                     if isinstance(message, HumanMessage):
#                         full_chat.append({"HumanMessage":message.content})
#                     elif isinstance(message, AIMessage):
#                         full_chat.append({"AIMessage":message.content})

#         return full_chat

#     def chat(self, session_id, user_query):

#         history = self.get_history(session_id)
        
#         # Add human message to history
#         history.add_message(HumanMessage(content=user_query))

#         if user_query.lower().strip() in ["stop", "end", "finish"]:
#             resp = AIMessage(content="STOP")
#         else:
#             resp = self.chat_with_history.invoke(
#                 {"messages":[]},
#                 config={"configurable": {"session_id": session_id}}
#             )

#         stop_chat = False

#         full_chat = self.get_full_chat(user_query, resp, session_id, stop_chat)
        
#         # Check if conversation should stop
#         if "stop" in resp.content.lower():
#             stop_chat = True
#             full_chat = self.get_full_chat(user_query, resp, session_id, stop_chat)
#             return resp.content, stop_chat, full_chat

#         # Generate intermediate summary if threshold reached (backend only)
#         if len(history.messages) == self.intermediate_summary_threshold + 1:
#             print("=== BACKEND: Generating intermediate summary ===")
#             self.generate_intermediate_summary(session_id)
#             # Continue with normal conversation
        
#         # Return only the AI response for frontend display
#         return resp.content, stop_chat, full_chat
    
# if __name__=="__main__":

#     import uuid
    
#     obj = ConversationAgent()

#     session = str(uuid.uuid4())
#     user_query ="i have severe headache"

#     run_loop = True
#     while run_loop:

#         user_query = input("Enter your query :- ")
#         response, stop_chat, full_chat = obj.chat(session, user_query)

#         print(f"AI Response: {response}")
#         if stop_chat:
#             print(f"Final summary:\n {response}")
#             run_loop = False
    
#     print("==== Full chat ====")
#     print(full_chat)
