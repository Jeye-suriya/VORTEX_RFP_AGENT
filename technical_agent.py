import json
from typing import List, Dict
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()


class TechnicalAgent:
    """Maps requirements to services using RAG for contextual evidence and produces compliance scores."""

    def __init__(self, catalog: List[str] = None, chroma_dir: str = "chroma_db", model_name: str = "gpt-4o-mini"):
        self.llm = ChatGroq(temperature=0, model=model_name)
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.persistent_dir = chroma_dir
        self.catalog = catalog or [
            "Cloud Migration",
            "Managed Services",
            "Application Development",
            "Security & Compliance",
            "Data Engineering",
            "DevOps & Automation",
        ]

    def _get_retriever(self):
        if not self.persistent_dir:
            raise ValueError("Chroma directory not configured")
        vectordb = Chroma(persist_directory=self.persistent_dir, embedding_function=self.embeddings)
        return vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 5})

    def map_requirements(self, requirements: List[Dict]) -> List[Dict]:
        retriever = self._get_retriever()
        mappings = []

        for req in requirements:
            req_text = req.get('text', '')
            retrieved = retriever.invoke(req_text)
            evidence = "\n\n".join(d.page_content for d in retrieved)

            prompt = (
                "You are a senior solutions architect. Given the requirement and the retrieved contextual evidence, map the requirement to the best matching services in the catalog. "
                "For each mapping return JSON with keys: requirement_id, services (array), approach (2-3 sentences), compliance_score (0-100), evidence (short excerpt).\n\n"
                f"Catalog: {', '.join(self.catalog)}\nRequirement: '{req_text[:800]}'\nEvidence:\n{evidence}\n\nJSON:\n"
            )

            try:
                resp = self.llm(prompt)
                text_resp = resp.generations[0][0].text if hasattr(resp, 'generations') else str(resp)
                jstart = text_resp.find('{')
                j = json.loads(text_resp[jstart:])
                mappings.append(j)
            except Exception:
                mappings.append({
                    "requirement_id": req.get('id', ''),
                    "services": [self.catalog[0]],
                    "approach": "We propose a standard approach using the selected service.",
                    "compliance_score": 50,
                    "evidence": evidence[:500],
                })
        return mappings
