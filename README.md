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

## 💻 User Interface
**DAILY LOG INTERFACE:**

<img width="1919" height="934" alt="Daily Log Interface" src="https://github.com/user-attachments/assets/fcca688e-69af-4a7b-9b8b-0c27df48f6dd" />



**AFTER LOG IS SUCCESSFULLY SUBMITTED:**

<img width="1722" height="943" alt="Not 7th Log" src="https://github.com/user-attachments/assets/040c6fe1-d371-4bea-8073-702fde369b6f" />



**WEEKLY PREDICTION & RECOMMENDATION:**

<img width="1636" height="898" alt="Result and Recommendations" src="https://github.com/user-attachments/assets/088624a8-29af-4d5f-aae3-2172e9588933" />



**DAILY LOG HISTORY (LIST):**

<img width="1697" height="931" alt="History List" src="https://github.com/user-attachments/assets/ae99be5d-46f9-445e-80f1-d2d8750acada" />



**DAILY LOG HISTORY (CHART):**

<img width="1679" height="642" alt="History Chart" src="https://github.com/user-attachments/assets/1dd461cb-ce41-44ce-b954-4e80eea9b315" />



**WEEKLY PROGRESS INTERFACE:**

<img width="1678" height="293" alt="Weeekly Progress" src="https://github.com/user-attachments/assets/5a847828-1952-4065-a8d8-5473da1e28f1" />



**VIEW ADVICE BUTTON IS CLICKED:**

<img width="478" height="696" alt="image" src="https://github.com/user-attachments/assets/1c029a7f-607a-46f1-a7a4-13b6ce88ad5c" />


## 🚀 Installation & Setup
To run this project locally, follow these steps:

### Prerequisites
* Python 3.9+
* [Ollama](https://ollama.ai/) installed on your machine for running local LLMs.

