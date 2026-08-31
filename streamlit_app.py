"""
AI Document Assistant -- redesigned frontend.
Functionality is UNCHANGED from before: upload a PDF/TXT via POST /upload,
ask questions via POST /ask. Only the visual design changed.

Signature element: a rotating 3D stack of pages with a glowing scan-line
sweeping through them (Three.js, loaded via CDN inside a components.html
iframe) -- visualizes "AI reading a document," tied directly to what
this app actually does.
"""
import streamlit as st
import streamlit.components.v1 as components
import requests
import time

API_BASE = "https://ai-document-qa-system-5fd2.onrender.com"

st.set_page_config(page_title="AI Document Assistant", page_icon="◆", layout="centered")

# ============================================================================
# THEME -- ink background, single cyan-glow accent, Space Grotesk + Inter
# ============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

* { font-family: 'Inter', sans-serif; }

.stApp {
    background: #0A0E14;
    color: #EDEFF2;
}
#MainMenu, footer, header { visibility: hidden; }

h1, h2, h3, .hero-title {
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: -0.3px;
}

.hero-title {
    font-size: 30px; font-weight: 700; color: #EDEFF2;
    text-align: center; margin: 4px 0 2px 0;
}
.hero-sub {
    text-align: center; color: #7C8591; font-size: 14.5px;
    margin-bottom: 8px; max-width: 460px; margin-left: auto; margin-right: auto;
}

.panel-label {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 15px; font-weight: 600; color: #EDEFF2;
    margin-bottom: 2px; display: flex; align-items: center; gap: 8px;
}
.panel-label .dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #22D3C9; box-shadow: 0 0 8px #22D3C9;
}

/* Glass-surface panels -- deliberately NOT identical rounded cards with
   the same shadow; differentiated by a hairline border that glows on
   focus/hover within, not decoration on the container itself. */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(20, 25, 32, 0.6) !important;
    border: 1px solid #262C36 !important;
    border-radius: 10px !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] p,
div[data-testid="stVerticalBlockBorderWrapper"] label,
div[data-testid="stVerticalBlockBorderWrapper"] span {
    color: #C7CCD3 !important;
}

div[data-testid="stFileUploaderDropzone"] {
    background: rgba(34, 211, 201, 0.04) !important;
    border: 1px dashed #2E3844 !important;
    border-radius: 8px !important;
}
div[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #22D3C9 !important;
}

div[data-testid="stTextInput"] input {
    background: #10141B !important;
    border: 1px solid #262C36 !important;
    color: #EDEFF2 !important;
    border-radius: 8px !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #22D3C9 !important;
    box-shadow: 0 0 0 3px rgba(34, 211, 201, 0.12) !important;
}

.stButton > button {
    background: #22D3C9 !important;
    color: #0A0E14 !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 8px 18px !important;
    transition: box-shadow 0.15s ease, transform 0.15s ease !important;
}
.stButton > button:hover {
    box-shadow: 0 0 20px rgba(34, 211, 201, 0.4) !important;
    transform: translateY(-1px);
}

div[data-testid="stNotification"] { border-radius: 8px !important; }

.doc-status {
    font-size: 12.5px; color: #22D3C9; margin-top: 6px;
    display: flex; align-items: center; gap: 6px;
}

.answer-box {
    background: rgba(34, 211, 201, 0.05);
    border-left: 2px solid #22D3C9;
    padding: 14px 16px; border-radius: 6px;
    color: #EDEFF2; line-height: 1.6; margin-top: 10px;
}

.app-footer {
    text-align: center; color: #4A5260; font-size: 12px;
    margin-top: 32px; padding-top: 16px; border-top: 1px solid #1B212B;
}

::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #262C36; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# HERO: 3D animated document scanner (Three.js) -- the signature element
# ============================================================================
def render_3d_hero():
    components.html("""
    <div id="scanner-canvas" style="width:100%; height:220px;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
    const container = document.getElementById('scanner-canvas');
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / 220, 0.1, 100);
    camera.position.set(0, 1.4, 5.5);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, 220);
    renderer.setClearColor(0x000000, 0);
    container.appendChild(renderer.domElement);

    const pageGroup = new THREE.Group();
    const pageCount = 7;
    const pageGeo = new THREE.PlaneGeometry(2.4, 3.1);

    for (let i = 0; i < pageCount; i++) {
        const edgeMat = new THREE.MeshBasicMaterial({
            color: 0x22D3C9, wireframe: true, transparent: true, opacity: 0.35
        });
        const fillMat = new THREE.MeshBasicMaterial({
            color: 0x141920, transparent: true, opacity: 0.85, side: THREE.DoubleSide
        });
        const fill = new THREE.Mesh(pageGeo, fillMat);
        const edge = new THREE.Mesh(pageGeo, edgeMat);
        const offset = (i - pageCount / 2) * 0.09;
        fill.position.set(offset * 0.4, offset, -i * 0.02);
        edge.position.copy(fill.position);
        pageGroup.add(fill);
        pageGroup.add(edge);
    }
    pageGroup.rotation.x = 0.15;
    scene.add(pageGroup);

    // Glowing scan-line that sweeps through the page stack
    const lineGeo = new THREE.PlaneGeometry(2.6, 0.035);
    const lineMat = new THREE.MeshBasicMaterial({
        color: 0x22D3C9, transparent: true, opacity: 0.9
    });
    const scanLine = new THREE.Mesh(lineGeo, lineMat);
    scanLine.position.z = 0.3;
    scene.add(scanLine);

    let t = 0;
    function animate() {
        requestAnimationFrame(animate);
        t += 0.012;
        pageGroup.rotation.y = Math.sin(t * 0.4) * 0.35;
        scanLine.position.y = Math.sin(t * 1.3) * 1.6;
        scanLine.position.x = Math.sin(t * 0.4) * 0.35 * 0.4;
        renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', () => {
        const w = container.clientWidth;
        camera.aspect = w / 220;
        camera.updateProjectionMatrix();
        renderer.setSize(w, 220);
    });
    </script>
    """, height=225)


render_3d_hero()

st.markdown('<div class="hero-title">AI Document Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Upload a document. Ask it anything. Answers are grounded strictly in what you gave it.</div>', unsafe_allow_html=True)
st.write("")

# ============================================================================
# SESSION STATE (unchanged logic)
# ============================================================================
if "doc_id" not in st.session_state:
    st.session_state.doc_id = None
    st.session_state.filename = None

# ============================================================================
# UPLOAD PANEL
# ============================================================================
upload_panel = st.container(border=True)
with upload_panel:
    st.markdown('<div class="panel-label"><span class="dot"></span>Upload</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Drag & drop a PDF or TXT", type=["pdf", "txt"], label_visibility="collapsed")

    if uploaded_file is not None:
        if st.button("Upload & Process", key="upload_btn"):
            with st.spinner("Reading and indexing your document..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                    r = requests.post(f"{API_BASE}/upload", files=files)
                    r.raise_for_status()
                    data = r.json()
                    st.session_state.doc_id = data["doc_id"]
                    st.session_state.filename = data["filename"]
                    st.success(f"Indexed '{data['filename']}' — {data['num_chunks']} chunks ready.")
                except requests.exceptions.RequestException as e:
                    try:
                        detail = r.json().get("detail", "Upload failed")
                    except Exception:
                        detail = f"Upload failed ({e}). If the server was asleep, try again in a moment."
                    st.error(detail)

    if st.session_state.doc_id:
        st.markdown(f'<div class="doc-status">● Active document: {st.session_state.filename}</div>', unsafe_allow_html=True)

st.write("")

# ============================================================================
# ASK PANEL
# ============================================================================
ask_panel = st.container(border=True)
with ask_panel:
    st.markdown('<div class="panel-label"><span class="dot"></span>Ask</div>', unsafe_allow_html=True)
    question = st.text_input("Ask anything about the uploaded document...", label_visibility="collapsed", placeholder="Ask anything about the uploaded document...")

    if st.button("Ask AI", key="ask_btn"):
        if not st.session_state.doc_id:
            st.warning("Upload a document first.")
        elif not question.strip():
            st.warning("Type a question first.")
        else:
            with st.spinner("Thinking..."):
                try:
                    start = time.time()
                    r = requests.post(f"{API_BASE}/ask", json={"doc_id": st.session_state.doc_id, "question": question})
                    r.raise_for_status()
                    elapsed = time.time() - start
                    data = r.json()
                    st.markdown(f'<div class="answer-box">{data["answer"]}</div>', unsafe_allow_html=True)
                    st.caption(f"{elapsed:.1f}s")
                except requests.exceptions.RequestException as e:
                    try:
                        detail = r.json().get("detail", "Failed to get answer")
                    except Exception:
                        detail = f"Failed to get answer ({e})."
                    st.error(detail)

st.markdown('<div class="app-footer">FastAPI · LangChain · Qdrant · Groq · Streamlit</div>', unsafe_allow_html=True)