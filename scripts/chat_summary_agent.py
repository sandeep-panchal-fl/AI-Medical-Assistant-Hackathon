import yaml
from langchain_core.messages import HumanMessage, SystemMessage

from bedrock_initializer import BedrockModel

class ChatSummaryAgent(BedrockModel):

    def __init__(self, **kwargs):

        # accessing bedrock model from it self.llm_chat
        super().__init__(**kwargs) 

        # Load prompts
        # prompts_path = "prompts.yaml"
        prompts_path = "/app/scripts/prompts.yaml"
        with open(prompts_path, 'r') as f:
            prompts = yaml.safe_load(f)

        # # Access prompts
        self.rag_summary_prompt = prompts['medical_assistant']['rag_summary_prompt']
        
    def generate_chat_summary(self, full_chat):

        print("____________________________________\n")
        print("=== GENERATING FINAL CHAT SUMMARY ===")

        conversation_lines = []
        
        for messages_dict in full_chat:
            if "HumanMessage" in messages_dict:
                conversation_lines.append(f"Patient: {messages_dict['HumanMessage']}")
            elif "AIMessage" in messages_dict:
                conversation_lines.append(f"Assistant: {messages_dict['AIMessage']}")

        conversation_lines = "\n".join(conversation_lines)

        # Final summary (can be shown to user)
        summary = self.llm_chat.invoke([
            SystemMessage(content=self.rag_summary_prompt),
            HumanMessage(content=conversation_lines)
        ])

        print("=== FINAL CHAT SUMMARY GENERATED ===")
        
        return summary.content
    
if __name__=="__main__":

    
    obj = ChatSummaryAgent()

    full_chat = [{'HumanMessage': 'hi i am sandeep'}, {'AIMessage': 'Hello! I’m a medical assistant. What brings you in today, संदीप?'}, {'HumanMessage': 'i am having headache'}, {'AIMessage': "I understand you're experiencing a headache, संदीप. Can you tell me a little more about it – where exactly do you feel the pain?"}, {'HumanMessage': 'entire head'}, {'AIMessage': 'I understand you’re experiencing a headache all over your head, संदीप. That sounds tough. On a scale of 1 to 10, with 1 being very mild and 10 being the worst pain imaginable, how severe is the headache right now?'}, {'HumanMessage': '10'}, {'AIMessage': 'Okay, संदीप. A 10 – that’s very intense. Can you describe what the pain feels like? Is it a throbbing, a pressure, or something else?'}, {'HumanMessage': 'throbbing'}, {'AIMessage': 'I understand you’re experiencing a throbbing headache, संदीप. How long have you been having this headache?'}, {'HumanMessage': 'stop'}, {'AIMessage': 'STOP'}]

    response = obj.generate_chat_summary(full_chat)
    
    print("==== Final summary ====")
    print(response)
