from app.services.rag_chain import answer_question

# Paste the doc_id you got earlier from test_ingest.py
doc_id = "06a3fa1c-9a21-48ff-b66a-54e56904e981"
question = "What is this document about?"

answer, sources = answer_question(doc_id, question)
print("ANSWER:", answer)
print(f"\nBased on {len(sources)} source chunks")