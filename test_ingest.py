from app.services.ingestion import ingest_document

# Change this to match your actual PDF filename
file_path = "2300080373_Abhi.pdf"

doc_id, num_chunks = ingest_document(file_path)
print(f"Document ID: {doc_id}")
print(f"Number of chunks created: {num_chunks}")