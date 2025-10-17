import uuid
import json
from conversation_agent import ConversationAgent
from chat_summary_agent import ChatSummaryAgent
from report_generator_agent import ReportGeneratorAgent
from retrieval_agent import MedicalDataRetrieval
from doctor_validation import SummarizeValidatedReport

class MedicalPipeline:

    def __init__(self):
        
        self.conversation_agent = ConversationAgent()
        self.chat_summary = ChatSummaryAgent()
        self.retrieval_data = MedicalDataRetrieval()
        self.report_generator = ReportGeneratorAgent()
        self.doc_validated_report = SummarizeValidatedReport()

        self.session_results = {}  # Store results by session_id
    
    def run_pipeline(self, user_symptoms=None, session_id=None):

        """Run complete pipeline from conversation to report generation"""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        final_summary = None
        full_chat = None
        
        print("=" * 60)
        print("MEDICAL SYMPTOM ASSESSMENT PIPELINE")
        print("=" * 60)
        print(f"Session ID: {session_id}")
        
        # Interactive conversation loop
        run_loop = True
        while run_loop:
            user_input = input(f"\nYou: ").strip()

            # Get AI response
            response, stop_chat, full_chat = self.conversation_agent.chat(session_id, user_input)

            print(f"AI Response: {response}")
            if stop_chat:
                run_loop = False
        
        print("==== Full chat ====")
        print(full_chat)
        
        # Generate final report
        if full_chat:

            print("\nGenerating final chat summary...")
            final_summary = self.chat_summary.generate_chat_summary(full_chat)

            print("\nRetrieving medical data...")
            retrieved_data = self.retrieval_data.retrieve_data(final_summary)

            print("\nGenerating medical report...")
            medical_report = self.report_generator.generate_final_medical_report(
                full_chat=full_chat,
                chat_summary=final_summary,
                retrieved_knowledge=retrieved_data  # Skip for now
            )
            
            # Store results
            result = {
                "session_id": session_id,
                "full_chat": full_chat,
                "clinical_summary": final_summary,
                "medical_report": medical_report
            }
            
            print("\n" + "=" * 60)
            print("MEDICAL ASSESSMENT REPORT")
            print("=" * 60)
            print(medical_report)

            print("\n" + "=" * 60)
            print("STORING DOCTOR VALIDATED MEDICAL REPORT DATA")
            print("=" * 60)

            self.doc_validated_report.summarize_doctor_validated_report(medical_report)

            # Save report to file
            self.save_report_to_file(result)
            
            return medical_report, result
        else:
            print("No final summary generated.")
            return None, None
    
    def save_report_to_file(self, result, filename=None):
        """Save report to JSON file"""
        if not filename:
            filename = f"medical_report_{result['session_id']}.json"
        
        # Convert to serializable format
        report_data = {
            "session_id": result["session_id"],
            "conversation_history": result["full_chat"],
            "clinical_summary": result["clinical_summary"],
            "medical_report": result["medical_report"],
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"Report saved to: {filename}")

# Standalone testing
if __name__ == "__main__":
    pipeline = MedicalPipeline()
    
    med_report, resp = pipeline.run_pipeline()