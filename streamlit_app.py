import streamlit as st
import requests

API_BASE = "https://ai-document-qa-system-5fd2.onrender.com"

st.set_page_config(page_title="AI Document Assistant", page_icon="📄", layout="wide")

st.markdown("""
<style>
.stApp{
 background:linear-gradient(135deg,#0b1120,#111827,#1e293b);
 color:#f8fafc;
}
.block-container{padding-top:2rem;max-width:1200px;}
h1{font-size:3rem!important;text-align:center;color:#60a5fa;}
.subtitle{text-align:center;color:#94a3b8;margin-bottom:2rem;}
.card{
 background:rgba(17,24,39,.92);
 border:1px solid rgba(255,255,255,.08);
 border-radius:18px;
 padding:22px;
 box-shadow:0 10px 30px rgba(0,0,0,.35);
 margin-bottom:20px;
}
.stButton>button{
 width:100%;
 border:none;
 border-radius:12px;
 padding:.7rem;
 font-weight:700;
 color:white;
 background:linear-gradient(90deg,#2563eb,#06b6d4);
}
.stButton>button:hover{transform:translateY(-2px);}
.answer{
 background:#0f172a;
 border-left:5px solid #38bdf8;
 padding:18px;
 border-radius:12px;
}
.source{
 background:#1f2937;
 padding:12px;
 border-radius:10px;
 border:1px solid #374151;
 margin-bottom:10px;
}
footer{text-align:center;color:#94a3b8;padding:25px;}
</style>
""", unsafe_allow_html=True)

if "doc_id" not in st.session_state:
    st.session_state.doc_id=None
    st.session_state.filename=None

st.markdown("<h1>📄 AI Document Assistant</h1>",unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Upload a document and chat with it using AI.</div>",unsafe_allow_html=True)

left,right=st.columns([1,1])

with left:
    st.markdown("<div class='card'>",unsafe_allow_html=True)
    st.subheader("📁 Upload")
    uploaded_file=st.file_uploader("Drag & drop a PDF or TXT",type=["pdf","txt"])
    if uploaded_file and st.button("🚀 Upload & Process"):
        with st.spinner("Indexing document..."):
            files={"file":(uploaded_file.name,uploaded_file.getvalue())}
            r=requests.post(f"{API_BASE}/upload",files=files)
        if r.status_code==200:
            d=r.json()
            st.session_state.doc_id=d["doc_id"]
            st.session_state.filename=d["filename"]
            st.success(f"Ready! **{d['filename']}** indexed into **{d['num_chunks']}** chunks.")
        else:
            st.error(r.json().get("detail","Upload failed"))
    st.markdown("</div>",unsafe_allow_html=True)

with right:
    st.markdown("<div class='card'>",unsafe_allow_html=True)
    st.subheader("💬 Ask")
    if st.session_state.filename:
        st.info(f"Current document: **{st.session_state.filename}**")
    q=st.text_input("Ask anything about the uploaded document...")
    if st.button("🤖 Ask AI"):
        if not st.session_state.doc_id:
            st.warning("Upload a document first.")
        elif not q.strip():
            st.warning("Enter a question.")
        else:
            with st.spinner("Thinking..."):
                payload={"doc_id":st.session_state.doc_id,"question":q}
                r=requests.post(f"{API_BASE}/ask",json=payload)
            if r.status_code==200:
                d=r.json()
                st.markdown("<div class='answer'><h4>🤖 AI Answer</h4></div>",unsafe_allow_html=True)
                st.write(d["answer"])
                if d["sources"]:
                    st.markdown("### 📚 Sources")
                    for s in d["sources"]:
                        st.markdown(f"<div class='source'><b>Chunk {s['chunk_index']}</b><br><br>{s['content'][:350]}...</div>",unsafe_allow_html=True)
            else:
                st.error(r.json().get("detail","Unknown error"))
    st.markdown("</div>",unsafe_allow_html=True)

st.markdown("<footer>Built with ❤️ using FastAPI • LangChain • Ollama • ChromaDB • Streamlit</footer>",unsafe_allow_html=True)