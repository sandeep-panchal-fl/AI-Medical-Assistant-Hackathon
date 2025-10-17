from langchain_core.messages import HumanMessage, SystemMessage
import yaml

from bedrock_initializer import BedrockModel

class ReportGeneratorAgent(BedrockModel):

    def __init__(self, **kwargs):
        
        # accessing bedrock model from it self.llm_chat
        super().__init__(**kwargs) 

        # Load prompts
        # prompts_path = "prompts.yaml"
        prompts_path = "/app/scripts/prompts.yaml"
        with open(prompts_path, 'r') as f:
            prompts = yaml.safe_load(f)

        self.report_generator_prompt = prompts['medical_assistant']['report_generator_prompt']

    def generate_final_medical_report(self, full_chat, chat_summary, retrieved_knowledge=None):

        print("____________________________________\n")
        print("=== Generating Final Report ===")
        # severity_flag = self.calculate_severity_flag(chat_summary, full_chat)
        severity_flag = None
        
        enhanced_prompt = f"""
        {self.report_generator_prompt}
        
        ADDITIONAL CONTEXT:
        - Calculated Severity Flag: {severity_flag}
        """

        # - Current Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        
        report = self.llm_chat.invoke([
            SystemMessage(content=enhanced_prompt),
            HumanMessage(content=f"""
            CLINICAL SUMMARY: {chat_summary}
            
            RETRIEVED MEDICAL KNOWLEDGE: {retrieved_knowledge}
            
            FULL CONVERSATION: {full_chat}
            """)
        ])
        
        print("=== Final Report Generated ===")

        return report.content
    
if __name__=="__main__":
    pass

    chat_summary = """Patient reports a throbbing headache with sensitivity to light and nausea,
            onset not precisely determined. The headache is characterized as 10/10 in severity and is located
            diffusely throughout the head. Patient reports nausea alongside the headache, with the onset coinciding
            with the headache's initiation. Clinical examination reveals associated symptoms of photophobia and
            significant discomfort. Further evaluation of the patient’s cardiovascular and pulmonary systems is
            warranted given the acute nature of the symptoms.
        """
            
    full_chat = [
        {'HumanMessage': 'hi i am sandeep'},
        {'AIMessage': 'Hello Sandeep! I’m a medical assistant. What brings you in today?'},
        {'HumanMessage': 'i am having headache'},
        {'AIMessage': "I understand you're experiencing a headache, Sandeep. Can you tell me a little more about it – \
         where exactly do you feel the pain?"},
        {'HumanMessage': 'entire head'},
        {'AIMessage': 'I understand, Sandeep. That sounds tough. Can you describe the pain – \
         is it a throbbing, a dull ache, or something else?'},
        {'HumanMessage': 'throbbing'},
        {'AIMessage': 'Okay, a throbbing headache, Sandeep. When did this headache start, \
         and how severe would you rate it on a scale of 1 to 10, with 1 being very mild and 10 being the worst pain imaginable?'},
        {'HumanMessage': '10'},
        {'AIMessage': 'I understand, Sandeep. A 10 – that’s incredibly intense. \
         Are there any other symptoms you’re experiencing with the headache, like nausea, sensitivity to light,\
         or anything like that?'},
        {'HumanMessage': 'sensitivity to light and nausea'},
        {'AIMessage': 'Okay, Sandeep, so you’re experiencing a throbbing headache with sensitivity to \
         light and nausea. When did the nausea start alongside the headache?'},
        {'HumanMessage': 'stop'},
        {'AIMessage': 'STOP'}
        ]
    
    retrieved_knowledge = """Disease: Migraine | 
                Disease Description: A neurological condition characterized by intense, debilitating headaches. | 
                Precautions Recommendation: Avoid triggers like caffeine and stress, stay hydrated, get adequate sleep. | 
                Medicines Recommendation: ['Triptans', 'NSAIDs', 'Beta-blockers', 'Antidepressants'] |
                Diet Recommendation: ['Magnesium-rich foods', 'Avoid processed meats', 'Limit caffeine', 'Hydrating fluids'] |
                Workouts Recommendation: ['Yoga', 'Meditation', 'Stretching', 'Low-impact aerobic exercise']
                """
    
    obj = ReportGeneratorAgent()

    resp = obj.generate_final_medical_report(full_chat, chat_summary, retrieved_knowledge)
    print(resp)