Contract Risk Agent
The Contract Risk Agent is an AI-powered application built to assist users in reviewing legal documents. By combining document processing, advanced OCR capabilities, and large language models (LLMs), the agent automatically scans files to identify potential legal liabilities, provides executive summaries, and allows users to query specific contract clauses using natural language.

Core Features
Automated Risk Analysis: The system evaluates contracts and assigns an overall risk score (0-100), categorizing issues into High, Medium, or Low risk levels.

AI-Powered Summarization: It generates clear, concise executive summaries, saving users time by highlighting the "bottom line" of the contract.

Interactive Contract Q&A: Powered by Retrieval-Augmented Generation (RAG), the agent allows users to ask specific questions about the document, such as termination clauses or payment terms, with direct source attribution.

Downloadable Reporting: Once the analysis is complete, users can export a comprehensive PDF risk report summarizing the findings and top-risk issues.

Wide File Support: The agent handles a variety of formats including PDF, DOCX, images (JPG/PNG), text files, and email (EML) formats.

Technology Stack
User Interface: Built using Streamlit, providing an interactive and responsive web dashboard for uploading documents and viewing results.

Intelligence Layer: Powered by Groq’s Llama-3.1 model, ensuring fast and accurate contract comprehension.

Document Processing: Uses LangChain for text chunking and embedding, combined with OCR tools like Tesseract for parsing non-text documents like images and scans.

Deployment Environment: Hosted on Streamlit Cloud, utilizing Linux-based system dependencies for heavy-duty processing tasks.

Local Installation and Setup
Clone the Repository:
Download the project to your local machine using: git clone https://github.com/yourusername/contract-risk-agent.git.

Environment Setup:
It is recommended to create a virtual environment to manage dependencies. Run python -m venv venv and activate it via venv\Scripts\activate on Windows.

Install Dependencies:
Install all necessary libraries by running pip install -r requirements.txt.

Configure API Keys:
Create a .env file in the root directory and add your Groq API key: GROQ_API_KEY=your_actual_api_key_here.

Launch the Application:
Start the application locally by running streamlit run app.py.

Deployment Guide
To deploy this application to Streamlit Cloud, ensure your GitHub repository contains the following critical configuration files:

requirements.txt: This must contain all your Python dependencies (e.g., streamlit, langchain, etc.).

packages.txt: This is required for Linux-based servers to handle OCR and image processing. It should contain:

tesseract-ocr

libtesseract-dev

poppler-utils

libmagic-dev

Secrets: Do not hardcode your API keys. Instead, use the Streamlit Cloud "Secrets" management tab and add your key in the following TOML format: GROQ_API_KEY = "your_actual_api_key_here".

Disclaimer
This tool is intended for educational and informational purposes only. It is not a substitute for professional legal advice, and its output should not be considered legally binding. Always consult with a qualified legal professional before signing or agreeing to any contract.
