# app/ai_modules/text_splitter.py

import tiktoken

def split_text(text, max_tokens=2048, overlap=200):
    """
    Splits text into chunks not exceeding max_tokens.
    
    Parameters:
        text (str): The text to split.
        max_tokens (int): Maximum tokens per chunk.
        overlap (int): Number of overlapping tokens between chunks.
    
    Returns:
        List[str]: A list of text chunks.
    """
    encoder = tiktoken.get_encoding("cl100k_base")  # Adjust based on your model
    tokens = encoder.encode(text)
    total_tokens = len(tokens)
    
    chunks = []
    start = 0
    
    while start < total_tokens:
        end = start + max_tokens
        chunk_tokens = tokens[start:end]
        chunk_text = encoder.decode(chunk_tokens)
        chunks.append(chunk_text)
        start += max_tokens - overlap  # Move the window with overlap
    
    return chunks
