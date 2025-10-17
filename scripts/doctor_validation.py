from langchain.schema import SystemMessage, HumanMessage
import yaml

from medical_data_store import MedicalDataStore
from bedrock_initializer import BedrockModel

class SummarizeValidatedReport(BedrockModel):

    def __init__(self, **kwargs):

        self.med_data_store = MedicalDataStore()
        
        # accessing bedrock model from it self.llm_chat
        super().__init__(**kwargs) 

        # Load prompts
        # prompts_path = "prompts.yaml"
        prompts_path = "/app/scripts/prompts.yaml"
        with open(prompts_path, 'r') as f:
            prompts = yaml.safe_load(f)

        # # Access prompts
        self.doc_validation_prompt = prompts['medical_assistant']['summarizing_doctor_validated_report']
        
    def summarize_doctor_validated_report(self, report):

        print("____________________________________\n")
        print("=== FORMATTING OUTPUT OF DOCTOR VALIDATION ===")

        # 1️⃣ Run LLM to extract structured summary

        if report and isinstance(report, str):
            input_llm = self.doc_validation_prompt + "\n" + report
            llm_response = self.llm_chat.invoke([
                SystemMessage(content="You are a helpful medical assistant."),
                HumanMessage(content=input_llm)
            ])

        formatted_output = llm_response.content.strip()
        print("\n=== FORMATTED OUTPUT ===")
        print("____________________________________\n")

        collection_cnt = self.med_data_store.store_validated_report(formatted_output)

        print("--- COLLECTION COUNT IN KNOWLEDGEBASE ---")
        print(f"Before adding {collection_cnt['before_adding']}")
        print(f"After adding {collection_cnt['after_adding']}")

        return None
    
if __name__=="__main__":


    report = """## Medical Assessment Report – Sandeep

**Date:** October 26, 2023 (Assumed – based on provided context)
**Patient Name:** Sandeep

**1. PATIENT INFORMATION SECTION**

*   **Patient Name:** Sandeep
*   **Age:** Not specified
*   **Gender:** Not specified

**2. CLINICAL ASSESSMENT SECTION**

*   **PRESENTING COMPLAINT:**
    *   Primary symptom: Throbbing headache
    *   Duration: 2 days
    *   Onset Context: Started 2 days prior to presentation
    *   Pain Location: Throughout entire head
*   **SYMPTOM ANALYSIS:**
    *   Location: Entire head
    *   Character: Throbbing
    *   Severity: Not specified (Calculated Severity Flag: None)
    *   Aggravating/Relieving Factors: Not specified
    *   Associated Symptoms: None reported
*   **SEVERITY FLAGGING LOGIC:**
    *   HIGH: Severity â‰¥8, chest pain, breathing difficulty, neurological symptoms
    *   MEDIUM: Severity 5-7, multiple symptoms, functional impact
    *   LOW: Severity â‰¤4, single mild symptom

**3. MEDICAL RECOMMENDATIONS SECTION**

*   **POTENTIAL CONSIDERATIONS:**
    *   common headache
*   **PRECAUTIONS & SELF-CARE:**
    *   Immediate Do’s:
        *   Stay hydrated – consume hydrating fluids.
        *   Avoid known triggers – particularly caffeine.
    *   Don’ts:
        *   Avoid known stressors.
    *   Activity Modifications: Gentle yoga, meditation, or stretching may be beneficial.
    *   Monitoring Advice: Monitor headache frequency and severity.  Note any associated symptoms.
*   **TREATMENT SUGGESTIONS:**
    *   Medications:  Consideration of triptans, NSAIDs, beta-blockers, or antidepressants (as indicated by a physician).
    *   Non-pharmacological approaches:  Relaxation techniques, adequate sleep.
    *   Home remedies: Magnesium-rich foods may be beneficial.
*   **MEDICAL FOLLOW-UP:**
    *   When to seek urgent care:  If headache severity increases significantly, is accompanied by neurological symptoms (e.g., vision changes, weakness), or if you experience a sudden, severe headache.
    *   Recommended specialist if needed:  Neurologist for further evaluation and management.
    *   Timeline for re-evaluation:  Follow-up appointment within 7-14 days to assess response to initial recommendations and adjust treatment plan.

**4. KNOWLEDGE & DISCLAIMER SECTION**

These recommendations are based on evidence-based medical knowledge regarding migraine management.  This report is for informational purposes only and does not constitute a diagnosis.  It is crucial to consult with a qualified healthcare professional for an accurate diagnosis and personalized treatment plan.

**Disclaimer:** The information provided here is not a substitute for professional medical advice.  Self-treating can be dangerous.  Always seek the advice of a qualified healthcare provider for any health concerns or before making any decisions related to your health or treatment.  The accuracy of this information is based on the knowledge base provided at the time of generation.
"""
    obj = SummarizeValidatedReport()
    response = obj.summarize_doctor_validated_report(report)
