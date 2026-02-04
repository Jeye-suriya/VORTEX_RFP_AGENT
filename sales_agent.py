import json
import os
from typing import Dict, List
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

load_dotenv()


class SalesAgent:
    """SalesAgent performs document ingestion, builds a vector store (Chroma),
    and uses an LLM to extract structured RFP information from the RFP text using RAG."""

    def __init__(self, persist_directory: str = "chroma_db", model_name: str = "gpt-4o-mini"):
        self.llm = ChatGroq(temperature=0, model=model_name)
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.persistent_dir = persist_directory

    def _build_vector_store(self, text: str) -> Chroma:
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = splitter.split_text(text)
        if not os.path.exists(self.persistent_dir):
            os.makedirs(self.persistent_dir, exist_ok=True)
        vectordb = Chroma.from_texts(docs, embedding=self.embeddings, persist_directory=self.persistent_dir)
        # vectordb.persist()  # No longer needed as of Chroma 0.4.x
        return vectordb

    def analyze(self, text: str) -> Dict:
        """Returns a structured summary dict and builds a local Chroma vectorstore for RAG retrieval."""
        vectordb = self._build_vector_store(text)
        retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 4})

        # Use LLM with retrieved context to extract structured JSON
        system = (
            "You are a helpful assistant that reads RFP content and extracts structured fields. "
            "Use any provided context to answer accurately."
        )
        user_prompt = (
            "Extract the following from the context: client, submission_deadline (ISO or blank), "
            "a 1-2 sentence summary, and a list of requirements. "
            "Each requirement should be an object with 'id' and 'text' fields. "
            "Return ONLY valid JSON. If any field is missing, use empty string or empty list.\n\n"
            "Context:\n{context}\n\nJSON:\n"
        )

        # aggregate retrieved docs
        retrieved = retriever.invoke("Extract RFP structure")
        context_str = "\n\n".join(d.page_content for d in retrieved)
        prompt = system + "\n\n" + user_prompt.format(context=context_str)

        try:
            resp = self.llm(prompt)
            # LLM returns ChatGeneration; get text
            text_response = resp.generations[0][0].text if hasattr(resp, 'generations') else str(resp)
            json_start = text_response.find('{')
            json_text = text_response[json_start:]
            data = json.loads(json_text)
            # Ensure requirements have ids
            if 'requirements' in data and isinstance(data['requirements'], list):
                for i, req in enumerate(data['requirements']):
                    if 'id' not in req:
                        req['id'] = f"REQ-{i+1}"
            # attach vectorstore info
            data['_vectordb_dir'] = self.persistent_dir
            return data
        except Exception as e:
            # fallback
            return {
                "client": "",
                "submission_deadline": "",
                "summary": text[:400].replace('\n', ' '),
                "requirements": [{"id": "REQ-1", "text": text[:300]}],
                "_error": str(e),
            }
