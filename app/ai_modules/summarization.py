# app/ai_modules/summarization.py
from llama_index import GPTSimpleVectorIndex, Document

def index_data(structured_data: Dict[str, Any]) -> GPTSimpleVectorIndex:
    documents = []
    for key, content in structured_data.items():
        if isinstance(content, dict):
            for sub_key, sub_content in content.items():
                documents.append(Document(text=str(sub_content)))
        elif isinstance(content, list):
            for item in content:
                documents.append(Document(text=str(item)))
        else:
            documents.append(Document(text=str(content)))
    
    index = GPTSimpleVectorIndex(documents)
    index.save_to_disk("index.json")
    return index


# app/ai_modules/summarization.py
from langchain import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def generate_business_summary(index: GPTSimpleVectorIndex) -> str:
    # Load the index
    index = GPTSimpleVectorIndex.load_from_disk("index.json")
    
    # Query the index
    query = "Generate a comprehensive summary of the business based on the indexed data."
    response = index.query(query)
    
    # Use LangChain to process the response
    llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4")
    prompt = PromptTemplate(
        input_variables=["response"],
        template="Summarize the following business information:\n{response}"
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    summary = chain.run(response=response)
    return summary
