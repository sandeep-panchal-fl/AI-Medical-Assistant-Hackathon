import os
import re
import boto3
from dotenv import load_dotenv
from opensearchpy import OpenSearch
import json
from s3_bucket import S3DataBucket
from tqdm import tqdm

class MedicalDataStore:

    def __init__(self):

        self.s3_obj = S3DataBucket()

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
        
        self.index_body = {
            "settings": {"index": {"knn": True}},
            "mappings": {
                "properties": {
                    "disease": {"type": "keyword"},
                    "combined_text": {"type": "text"},
                    "embedding": {"type": "knn_vector", "dimension": 1024},
                    "metadata": {
                        "properties": {
                            "source": {"type": "keyword"}
                        }
                    }
                }
            }
        }

        if not self.opensearch.indices.exists(index=self.index_name):
            self.opensearch.indices.create(index=self.index_name, body=self.index_body)

    def get_embedding(self, text: str):

        if not isinstance(text, str) or text.strip() == "":
            raise ValueError("Input text must be a non-empty string")
        
        payload = {"inputText": text}  # MUST be 'input_text'
        
        response = self.bedrock.invoke_model(
            modelId=self.embedding_model,   # embedding model
            body=json.dumps(payload),
            contentType="application/json"
        )
        
        result = json.loads(response["body"].read())
        return result["embedding"]  # list of floats

    # -------------------- DATA STORAGE --------------------
    def store_in_vectordb(self):

        """Load CSV from S3, embed, and store in OpenSearch."""
        df = self.s3_obj.s3_get_data()

        if "disease" not in df.columns or "combined_text" not in df.columns:
            raise ValueError("CSV must have 'disease' and 'combined_text' columns.")
        
        for _, row in tqdm(df.iterrows(), total=len(df)):
            text = row["combined_text"]

            if not isinstance(text, str) or text.strip() == "":
                continue  # skip empty rows
            emb = self.get_embedding(text)

            doc = {
                "disease": row["disease"],
                "combined_text": text,
                "embedding": emb,
                "metadata": {
                    "source": "original_data",
                }
            }

            self.opensearch.index(index=self.index_name, body=doc)

        print(" === Data stored in OpenSearch ===")

    # -------------------- VALIDATED REPORT STORAGE --------------------
    def store_validated_report(self, formatted_output: str):

        """Store doctor-validated text into OpenSearch."""
        match = re.search(r"Disease:\s*(.*?)\s*\|", formatted_output)
        disease_name = match.group(1).strip() if match else "Unknown"

        emb = self.get_embedding(formatted_output)

        doc = {
            "disease": disease_name,
            "combined_text": formatted_output,
            "embedding": emb,
            "metadata": {
                "source": "doctor_validated",
            }
        }


        collection_cnt = {}
        before_adding = self.opensearch.count(index=self.index_name)
        collection_cnt["before_adding"] = before_adding["count"]

        self.opensearch.index(index=self.index_name, body=doc)

        self.opensearch.indices.refresh(index=self.index_name)

        after_adding = self.opensearch.count(index=self.index_name)
        collection_cnt["after_adding"] = after_adding["count"]

        print(f"✅ Added doctor-validated report for {disease_name}")

        print("--- COLLECTION COUNT IN KNOWLEDGEBASE ---")
        print(f"Before adding - {before_adding}")
        print(f"After adding - {after_adding}")

        return collection_cnt

    # -------------------- RETRIEVAL --------------------
    def similarity_search(self, query: str, k: int = 1):

        """Retrieve top-k relevant chunks."""
        query_emb = self.get_embedding(query)

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

        cnt = self.opensearch.count(index=self.index_name)
        print(f"Number of chunks - {cnt['count']}")

        # results = response["hits"]["hits"][0]["_source"]["combined_text"]
        
        # for hit in response["hits"]["hits"]:
        #     print("disease", hit["_source"]["disease"])
        #     print("metadata", hit["_source"]["metadata"])
        #     print("score", hit["_score"])
        #     print("description", hit["_source"]["combined_text"])

        return response


if __name__ == "__main__":

    store = MedicalDataStore()

    # # ---- Step 1: Store CSV data ----
    # store.store_in_vectordb()

    # ---- Step 2: Test retrieval ----
    query = "Patient reports throbbing headache and nausea."
    results = store.similarity_search(query)

    print(f"🧠 Disease: {results["hits"]["hits"][0]["_score"]}")
    print(f"🧠 Disease: {results["hits"]["hits"][0]["_source"]["disease"]}")
    print(f"Description: {results["hits"]["hits"][0]["_source"]["combined_text"]}\n")
