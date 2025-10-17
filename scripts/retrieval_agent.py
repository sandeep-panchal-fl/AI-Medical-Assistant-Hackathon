import os
import boto3
from dotenv import load_dotenv
from opensearchpy import OpenSearch

from medical_data_store import MedicalDataStore

class MedicalDataRetrieval:
    
    def __init__(self,) -> None:

        self.med_data = MedicalDataStore()
        
        """Initialize embedding + OpenSearch connection."""
        load_dotenv(dotenv_path="/app/.env")

        self.bedrock = boto3.client("bedrock-runtime")  # IAM must allow bedrock:InvokeModel
        self.index_name = "medical-embeddings"

        # AWS setup
        self.region = os.getenv("AWS_REGION")
        self.host = os.getenv("AWS_OPENSEARCH_HOST")
        self.embedding_model = os.getenv("AWS_TITAN_EMBEDDING_MODEL")
        self.username = os.getenv("AWS_OPENSEARCH_USERNAME")
        self.password = os.getenv("AWS_OPENSEARCH_PASSWORD")

        self.opensearch = OpenSearch(
            hosts=[{"host": self.host, "port": 443}],
            http_auth=(self.username, self.password),
            use_ssl=True,
            verify_certs=True
            )

        self.retrieve_threshold = 0.5
    
    def retrieve_data(self, query: str, k: int = 1):

        """
        Retrieve the top-k most relevant chunks for a query.
        """ 
        print("____________________________________\n")
        print("=== Retrieving Medical Data ===")

        query_emb = self.med_data.get_embedding(query)

        query = {
            "size": k,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": query_emb,
                        "k": k
                    }
                }
            }
        }

        response = self.opensearch.search(index=self.index_name, body=query)

        # print(f"🧠 Disease: {results["hits"]["hits"][0]["_score"]}")
        # print(f"🧠 Disease: {results["hits"]["hits"][0]["_source"]["disease"]}")
        # print(f"Description: {results["hits"]["hits"][0]["_source"]["combined_text"]}\n")

        # if response:
        #     score = response["hits"]["hits"][0]["_score"]
        #     if score >= self.retrieve_threshold:

        if response:
            result = response["hits"]["hits"][0]["_source"]["combined_text"]

        return result
    
if __name__ == "__main__":

    # Initialize store
    store = MedicalDataRetrieval()

    # Test query
    query = """Patient reports a throbbing headache with sensitivity to light and nausea,
            onset not precisely determined. The headache is characterized as 10/10 in severity and is located
            diffusely throughout the head. Patient reports nausea alongside the headache, with the onset coinciding
            with the headache's initiation. Clinical examination reveals associated symptoms of photophobia and
            significant discomfort. Further evaluation of the patient’s cardiovascular and pulmonary systems is
            warranted given the acute nature of the symptoms."""
    
    # query = """Disease: common headache | Disease Description: Recurring headache | Symptoms: Throbbing headache | Precautions: Stay hydrated – consume hydrating fluids, Avoid known stressors | Treatment: Relaxation techniques, adequate sleep, gentle yoga, meditation or stretching | Medicine: Triptans, NSAIDs, beta-blockers, or antidepressants"""
    
    results = store.retrieve_data(query)

    print(results)
    
    # print("🔍 Top results:")
    # for r in results:
    #     print(f"🧠 Disease: {r.metadata['disease']}")
    #     print(f"🧠 Disease: {r.metadata['source']}")
    #     print(f"Snippet: {r.page_content}")
