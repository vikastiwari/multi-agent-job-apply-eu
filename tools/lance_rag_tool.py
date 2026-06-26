import os
import time
import requests
import lancedb
import pyarrow as pa
from duckduckgo_search import DDGS
import google.generativeai as genai
from crewai.tools import BaseTool
from pydantic import Field, ConfigDict

class CompanyContextRAGTool(BaseTool):
    name: str = "Company Context RAG Tool"
    description: str = "Searches the web for a company's engineering blog or 'About Us' page, reads the content, and performs a semantic search to retrieve deep context about their tech stack, core values, and recent news. Input should be the company name."

    # Using ConfigDict to allow arbitrary types for internal variables if needed
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run(self, company_name: str) -> str:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return "Error: GEMINI_API_KEY environment variable not set."
            
        genai.configure(api_key=api_key)
        
        # 1. Search DuckDuckGo for the company URL
        query = f"{company_name} engineering blog OR about us OR culture"
        try:
            results = DDGS().text(query, max_results=1)
            if not results:
                return f"No results found for {company_name}."
            url = results[0]['href']
        except Exception as e:
            return f"Error searching DuckDuckGo: {e}"

        # 2. Extract content using Jina Reader
        try:
            jina_url = f"https://r.jina.ai/{url}"
            headers = {"Accept": "application/json"}
            response = requests.get(jina_url, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            content = data.get("data", {}).get("content", "")
            if not content:
                content = data.get("data", {}).get("text", "")
        except Exception as e:
            return f"Error extracting content from {url}: {e}"

        if not content:
            return f"Failed to extract meaningful content from {url}."

        # 3. Chunk the content (simple paragraph splitting)
        chunks = [c.strip() for c in content.split('\n\n') if len(c.strip()) > 100]
        if not chunks:
             # fallback if no double newlines
             chunks = [content[i:i+1000] for i in range(0, len(content), 1000)]
             
        # Limit chunks to avoid API rate limits
        chunks = chunks[:20] 

        # 4. Generate embeddings using Gemini
        try:
            embeddings_result = genai.embed_content(
                model="models/text-embedding-004",
                content=chunks,
                task_type="retrieval_document"
            )
            embeddings = embeddings_result['embedding']
        except Exception as e:
            return f"Error generating embeddings: {e}"

        # 5. Create an ephemeral LanceDB table
        # We use a temporary directory in memory or /tmp
        db_path = "/tmp/lancedb_company_context"
        db = lancedb.connect(db_path)
        
        table_name = f"company_{int(time.time())}"
        data = [{"text": chunk, "vector": emb} for chunk, emb in zip(chunks, embeddings)]
        table = db.create_table(table_name, data=data)

        # 6. Perform semantic search for target queries
        search_query = "core engineering values, tech stack, architecture, culture, recent product launches"
        try:
            query_embedding_result = genai.embed_content(
                model="models/text-embedding-004",
                content=search_query,
                task_type="retrieval_query"
            )
            query_embedding = query_embedding_result['embedding']
            
            # Retrieve top 3 most relevant chunks
            results = table.search(query_embedding).limit(3).to_pandas()
        except Exception as e:
            db.drop_table(table_name)
            return f"Error searching vector database: {e}"

        # Clean up
        db.drop_table(table_name)

        # 7. Synthesize context
        retrieved_texts = results['text'].tolist()
        context = f"Company: {company_name}\nSource URL: {url}\n\nTop Semantic Insights:\n"
        for i, text in enumerate(retrieved_texts, 1):
            context += f"Insight {i}:\n{text}\n\n"
            
        return context
