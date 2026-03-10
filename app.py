import streamlit as st
import pandas as pd
import google.generativeai as genai

from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# -----------------------------
# Load Excel
# -----------------------------
file_path = "ManpowerPython_BI.xlsx"
df = pd.read_excel(file_path)

# -----------------------------
# Convert rows → Documents
# -----------------------------
docs = []

for _, row in df.iterrows():
    docs.append(Document(page_content=str(row.to_dict())))

# -----------------------------
# Gemini API Setup
# -----------------------------
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# -----------------------------
# Create Embeddings
# -----------------------------
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=st.secrets["GOOGLE_API_KEY"]
)

# -----------------------------
# Create Vector Database
# -----------------------------
vectorstore = FAISS.from_documents(docs, embeddings)

# -----------------------------
# Retriever
# -----------------------------
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# -----------------------------
# Gemini Model
# -----------------------------
model = genai.GenerativeModel("gemini-1.5-flash")

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("AI Assistant")

query = st.text_input("Ask AI")

if query:

    # Retrieve relevant rows
    retrieved_docs = retriever.get_relevant_documents(query)

    context = "\n".join([doc.page_content for doc in retrieved_docs])

    prompt = f"""
You are an AI assistant.
Answer ONLY from the provided Excel data.

DATA:
{context}

QUESTION:
{query}
"""

    response = model.generate_content(prompt)

    st.write("Answer")
    st.write(response.text)

