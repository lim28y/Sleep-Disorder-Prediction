# 🌙 Sleep Disorder Prediction & Recommendation System

## 📖 Overview
This project is a web application designed to predict potential sleep disorders (such as Insomnia and Sleep Apnea) based on user's lifestyle and health data. Beyond prediction, the system acts as a personalized health assistant, generating evidence-based, actionable sleep  recommendations. 

The application integrates traditional Machine Learning with a local Large Language Model (LLM) powered by a Retrieval-Augmented Generation (RAG) framework to eliminate AI hallucinations and ensure medical accuracy.

## ✨ Key Features
* **Machine Learning Classification:** Utilizes a highly optimized Random Forest model (balanced via SMOTE) to predict sleep disorders with high accuracy from tabular health metrics.
* **Evidence-Based AI Recommendations:** Integrates a local **Llama 3.2** model via Ollama with a **RAG pipeline**. The system retrieves context from verified medical journals stored in a **ChromaDB** vector database to generate personalized, medically sound advice.
* **RESTful API Architecture:** A robust backend built with **Flask** that handles data flow between the machine learning inference engine, the vector database, and the frontend UI.
* **Interactive Health Dashboard:** Visualizes the user's historical sleep patterns, stress levels, and sleep quality over time using interactive **Chart.js** graphs.

## 🛠️ Tech Stack
**Frontend:**
* HTML / CSS / JavaScript

**Backend & API:**
* Python
* Flask (RESTful API)

**Machine Learning & Data Processing:**
* Scikit-Learn
* Pandas / NumPy

**Generative AI & LLM:**
* Llama 3.2 (Hosted locally via Ollama)
* ChromaDB (Vector Database for RAG)
* LangChain / Custom Text Splitters (PDF processing)

## ⚙️ How It Works (Architecture)
1. **Daily Data Logging:** The user logs their daily lifestyle metrics (e.g., sleep duration, stress level, physical activity, heart rate) via the web interface over the course of a week.
2. **Weekly Prediction (ML):** Once the user submits their **7th daily log**, the Flask backend aggregates the data and sends it to the pre-trained Random Forest model. The model evaluates the 7-day trend to classify the user's weekly sleep status.
3. **Context Retrieval (RAG):** Based on the weekly prediction result, the system queries the ChromaDB vector database to retrieve the most relevant medical context from embedded medical journals.
4. **Weekly Recommendation Generation (LLM):**  Llama 3.2 model processes the user's 7-day metrics alongside the retrieved RAG context. It then generates a personalized, bulleted weekly sleep hygiene report to help the user maintain or improve their habits.
5. **Visualization & Alerts:** The weekly prediction results, AI-generated advice, and historical health metrics are displayed on the interactive web dashboard. If a high-risk disorder is consistently predicted across multiple weeks, the system triggers a critical health alert.

## 🚀 Installation & Setup
To run this project locally, follow these steps:

### Prerequisites
* Python 3.9+
* [Ollama](https://ollama.ai/) installed on your machine for running local LLMs.

