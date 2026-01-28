import streamlit as st
import trimesh
import numpy as np
import os
import tempfile
import rhino3dm  # Added for 3DM export logic
from PIL import Image

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="JewelBench Premium | AI 3D Engine",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CAD EXPORT ENGINE ---
def export_to_3dm(mesh_data, output_path, metal_type):
    """Converts Mesh data to a Layered 3DM file for MatrixGold/CAD"""
    model = rhino3dm.File3dm()
    
    # Standard Jewelry Layers
    layers = [
        {"name": "JB_Metal", "color": (212, 175, 55, 255)}, # Gold color
        {"name": "JB_Stones", "color": (0, 255, 255, 255)}, # Cyan
        {"name": "JB_Prongs", "color": (0, 255, 0, 255)}    # Green
    ]
    
    for l in layers:
        layer = rhino3dm.Layer()
        layer.Name = l["name"]
        layer.Color = l["color"]
        model.Layers.Add(layer)
        
    # Process Mesh for Rhino
    # Note: In production, this would trigger QuadRemesh on Rhino Compute
    r_mesh = rhino3dm.Mesh()
    for v in mesh_data.vertices:
        r_mesh.Vertices.Add(v[0], v[1], v[2])
    for f in mesh_data.faces:
        r_mesh.Faces.AddFace(f[0], f[1], f[2])
    
    attr = rhino3dm.ObjectAttributes()
    attr.LayerIndex = 0 # Metal Layer
    attr.UserStringList.Set("Material", metal_type)
    attr.UserStringList.Set("Engine", "JewelBench_Elite_v1")
    
    model.Objects.AddMesh(r_mesh, attr)
    model.Write(output_path, 7) # Rhino 7 for Matrix compatibility
    return output_path

# --- CUSTOM CSS FOR PREMIUM FEEL ---
st.markdown("""
    <style>
    /* Main background and font */
    .main {
        background-color: #0e1117;
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-image: linear-gradient(#1e1e2f, #0e1117);
        border-right: 1px solid #30363d;
    }
    
    /* Premium Gold Buttons */
    div.stButton > button:first-child {
        background: linear-gradient(45deg, #d4af37, #f9d976);
        color: #000;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
        padding: 0.6rem 2rem;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.4);
    }
    
    /* Metrics / Cards */
    [data-testid="stMetricValue"] {
        color: #d4af37;
    }
    .stMetric {
        background: #1c2128;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #30363d;
    }
    
    /* Headings */
    h1, h2, h3 {
        color: #ffffff;
        letter-spacing: -0.5px;
    }
    
    /* Success/Info styling */
    .stAlert {
        border-radius: 10px;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR & SETTINGS ---
with st.sidebar:
    st.image("https://jewelbench.ai/wp-content/uploads/2025/05/jewelbench_logo.svg", width=200)
    st.markdown("---")
    st.title("⚙️ Engine Settings")
    
    metal_type = st.selectbox(
        "Material Select",
        ["Gold 18K", "Gold 22K", "Gold 24K", "Platinum", "Silver 925"]
    )
    
    densities = {
        "Gold 18K": 15.58,
        "Gold 22K": 17.50,
        "Gold 24K": 19.32,
        "Platinum": 21.45,
        "Silver 925": 10.36
    }
    
    # Live Price Mock (could be API driven)
    st.markdown("### 💰 Live Spot Price")
    spot_prices = {
        "Gold 18K": 5680,
        "Gold 22K": 6920,
        "Gold 24K": 7550,
        "Platinum": 2850,
        "Silver 925": 92
    }
    current_spot = spot_prices[metal_type]
    st.metric(label="Current Spot (g)", value=f"₹{current_spot}")

# --- MAIN INTERFACE ---
st.title("💎 JewelBench Elite")
st.markdown("#### High-Precision Jewelry STL Analysis & Valuation")
st.markdown("---")

col1, col2 = st.columns([2, 1], gap="large")

with col1:
    st.subheader("📤 3D Asset Upload")
    uploaded_file = st.file_uploader("Drop your STL design here...", type=["stl"])
    
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        
        try:
            with st.spinner("Analyzing geometry..."):
                mesh = trimesh.load(tmp_path)
                volume_mm3 = mesh.volume
                surface_area = mesh.area
                is_watertight = mesh.is_watertight
                
                # Calculations
                weight_g = (volume_mm3 / 1000) * densities[metal_type]
                total_valuation = weight_g * spot_prices[metal_type]
            
            st.success("✅ Mesh Analysis Complete")
            
            # Interactive Visualizer Placeholder (could use streamlit-pyvista-ui or pythreejs)
            st.info("💡 Pro Tip: Ensure your mesh is manifold (watertight) for production accuracy.")
            
            st.subheader("📊 Engineering Metrics")
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("Volume", f"{volume_mm3:.2f} mm³")
            m_col2.metric("Surface Area", f"{surface_area:.1f} mm²")
            m_col3.metric("Manifold Status", "Valid" if is_watertight else "Repair Needed")

        except Exception as e:
            st.error(f"Engine Error: {e}")
        finally:
            os.remove(tmp_path)
    else:
        # Beautiful empty state
        st.markdown("""
        <div style="background: #1c2128; padding: 100px; border-radius: 20px; border: 2px dashed #30363d; text-align: center; color: #7f8c8d;">
            <h3>Waiting for STL input...</h3>
            <p>Upload a high-fidelity mesh to begin synthesis.</p>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.subheader("🏷️ Valuation")
    if uploaded_file and 'weight_g' in locals():
        st.markdown('<div class="stMetric">', unsafe_allow_html=True)
        st.write(f"**Selected Material:** {metal_type}")
        st.metric("Estimated Weight", f"{weight_g:.3f} g")
        st.metric("Total Metal Value", f"₹{total_valuation:,.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("🚀 Production")
        if st.button("📦 Export MatrixGold (.3dm)"):
            with st.spinner("Synthesizing CAD Layers..."):
                cad_path = tempfile.mktemp(suffix=".3dm")
                export_to_3dm(mesh, cad_path, metal_type)
                with open(cad_path, "rb") as f:
                    st.download_button(
                        label="Download 3DM File",
                        data=f,
                        file_name=f"JewelBench_{metal_type.replace(' ', '_')}.3dm",
                        mime="application/octet-stream"
                    )
        st.button("📜 Generate Tech Sheet")
        st.button("🛡️ Validate for Casting")
    else:
        st.write("Results will appear here after upload.")

st.markdown("---")
st.caption("JewelBench Elite | Powered by O.R.I.O.N. 🌌 | Built for high-precision manufacturing.")
