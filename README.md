# 🩺 AI Medical Assistant
An AI-powered medical assistant that leverages AWS Bedrock and OpenSearch to provide symptom-based insights and auto-generated clinical summaries.


## 🚀 Inspiration
Healthcare professionals spend a significant portion of their time collecting patient details, summarizing symptoms, and preparing medical reports. This repetitive process delays diagnosis and reduces face-to-face time with patients.  
We were inspired to create an **AI Medical Assistant** that automates early-stage symptom analysis, retrieves relevant medical knowledge, and generates structured reports — helping doctors focus on clinical decisions rather than documentation.

## 🏗️ Architecture Overview
Our architecture includes multiple specialized agents:
- **Conversation Agent** – Handles patient dialogue via natural language.  
- **Chat Summary Agent** – Extracts and summarizes user responses for clarity.  
- **Retrieval Agent** – Connects to an **OpenSearch Knowledge Base** for context-aware retrieval.  
- **Report Generator Agent** – Produces a structured clinical summary and recommendation draft.  
- **Feedback Loop** – Updates knowledgebase based on doctor edits.  

All these components are orchestrated through **Streamlit UI**, backed by **AWS Bedrock models** for LLM and embeddings, and **OpenSearch** for knowledgebase

## ⚙️ How We Built It
- **Frontend:** Streamlit for an intuitive conversational interface.  
- **LLM Backbone:** AWS Bedrock (Claude by Anthrophc) for reasoning, summarization and clinical report generation.  
- **Retrieval:** OpenSearch used directly  for efficient semantic search.    
- **Deployment:** Dockerized application pushed to **Amazon ECR**, deployed on **ECS (Fargate)** for scalability.  


---

## 🧩 Tech Stack Used

| Layer | Technology | Purpose |
|-------|-------------|----------|
| **Frontend (UI)** | 🖥️ [Streamlit](https://streamlit.io/) | Interactive web interface for users to chat with the assistant |
| **LLM (Language Model)** | 🧠 [AWS Bedrock - Claude - Sonnet](https://aws.amazon.com/bedrock/) | Handles conversational reasoning, summarization, and report generation |
| **Embeddings** | 🧩 [Bedrock Titan Embeddings Model](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html) | Vector representation of medical text for retrieval |
| **Retrieval Layer** | 🔍 [OpenSearch](https://opensearch.org/) | Stores and retrieves relevant medical knowledge |
| **Backend Logic** | 🐍 Python 3.12 | Core application logic for conversation flow and data retrieval |
| **Containerization** | 🐳 Docker | Builds portable images for deployment |
| **Deployment** | ☁️ AWS ECS + ECR | Runs containerized app and stores image versions |
---

# ⚙️ How to Run the AI Medical Assistant

This section explains how to build, configure, and run the AI Medical Assistant either locally or on AWS ECS using Docker and ECR.

---

## 🧩 Prerequisites

Before running the project, make sure you have:

- Python 3.12+
- Docker installed and running
- AWS CLI configured with access to ECR and ECS
- OpenSearch domain available and credentials ready
- AWS Bedrock access (for LLM + embeddings)
- Streamlit installed (for local testing)

---

## 🔐 Environment Setup

The project uses a `.env` file for configuration.  
**For security reasons**, the actual `.env` file is not shared. I have masked the keys for security reasons.

You can create your own `.env` file inside the project root:

```bash
touch .env
```
Then add your own credentials and configuration values:


```
AWS_REGION="us-east-1"
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_TITAN_EMBEDDING_MODEL="amazon.titan-embed-text-v2:0"
AWS_S3_BUCKET_NAME=your_created_bucket
AWS_OPENSEARCH_HOST=https://your-opensearch-domain.us-east-1.es.amazonaws.com
AWS_OPENSEARCH_USERNAME=username
AWS_OPENSEARCH_PASSWORD=password
```
**Note:** Bedrock claude sonnet variant model is mentioned in bedrock_initializer.py


## 🐳 Running with Docker (Local)

You can build and run the project locally using Docker:
```
# Step 1: Build Docker image
docker build -t docker_name:tag .

# Step 2: Run the container
docker run -it -p 8501:8501 docker_name:tag
```

Now open your browser and navigate to:
👉 http://localhost:8501

You should see the Streamlit UI for the Medical Assistant.

## 🧠 Testing the Pipeline

1) Once deployed (locally or via ECS):
2) Open the Streamlit app in your browser.
3) Enter your symptoms or medical queries.
4) The Conversation Agent will start a guided chat.
5) The Retrieval Agent fetches relevant knowledge from OpenSearch.
6) The Report Generator Agent creates a medical report draft.
7) A doctor can review and validate before sending back to the user.

---


## 🧭 Future Improvements

- ✅ Integrate **voice input** and **speech summarization** (using AWS Transcribe)  
- ✅ Add **medical ontology-based retrieval** for higher accuracy  
- ✅ Store anonymized chat summaries in **DynamoDB** for analytics  
- ✅ Extend report export formats (PDF, FHIR-compliant JSON)  
- ✅ Integrate fine-tuned Bedrock model for clinical response alignment  

---

> 🚀 **Final Note:**  
> This project showcases how LLMs, retrieval systems, and AWS cloud infrastructure can combine to build a safe, explainable, and context-aware **AI Medical Assistant** that supports both patients and clinicians.

---
