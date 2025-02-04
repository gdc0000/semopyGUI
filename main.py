import streamlit as st
import pandas as pd
from semopy import Model, calc_stats
import numpy as np
import pyreadstat

def add_footer():
    """Adds a footer with professional information and links."""
    st.markdown("---")
    st.markdown("### **Gabriele Di Cicco, PhD in Social Psychology**")
    st.markdown("""
    [GitHub](https://github.com/gdc0000) | 
    [ORCID](https://orcid.org/0000-0002-1439-5790) | 
    [LinkedIn](https://www.linkedin.com/in/gabriele-di-cicco-124067b0/)
    """)

# Predefined Model Syntax Examples (unchanged from original)
MODEL_SYNTAX_EXAMPLES = {
    # ... (keep the original MODEL_SYNTAX_EXAMPLES dictionary exactly as provided)
}

@st.cache_data(show_spinner=False)
def load_data(uploaded_file):
    """Loads data from various formats with error handling."""
    try:
        file_extension = uploaded_file.name.split(".")[-1].lower()
        if file_extension in ["csv", "txt"]:
            data = pd.read_csv(uploaded_file)
        elif file_extension in ["xlsx", "xls"]:
            data = pd.read_excel(uploaded_file)
        elif file_extension == "sas7bdat":
            data, _ = pyreadstat.read_sas7bdat(uploaded_file)
        else:
            st.error("Unsupported file type.")
            return None
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def main():
    st.set_page_config(page_title="SEM with semopy", layout="wide")
    st.title("📊 Structural Equation Modeling (SEM) with semopy")
    st.write(
        "Upload your dataset, choose or edit your model syntax, and run the model. "
        "Fit indices (χ2, RMSEA, CFI, TLI, NFI, GFI, AGFI) will be calculated using semopy.calc_stats."
    )

    # Initialize session state variables
    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = None
    if "last_selection" not in st.session_state:
        st.session_state.last_selection = None

    # Sidebar: Data upload section
    st.sidebar.header("1. Upload your Dataset")
    uploaded_file = st.sidebar.file_uploader(
        "Choose a CSV, Excel, or SAS file",
        type=["csv", "txt", "xlsx", "xls", "sas7bdat"]
    )

    data = None
    if uploaded_file is not None:
        data = load_data(uploaded_file)
        if data is not None:
            if data.isnull().sum().sum() > 0:
                st.sidebar.warning("⚠️ Dataset contains missing values. SEM requires complete cases.")
                if st.sidebar.checkbox("Drop rows with missing values?"):
                    data = data.dropna().reset_index(drop=True)
                    st.sidebar.info(f"Using {len(data)} complete cases.")
            st.subheader("📂 Dataset Preview")
            st.dataframe(data.head())
        else:
            st.stop()

    # Sidebar: Model syntax selection with fixed template loading
    st.sidebar.header("2. Define your Model Syntax")
    
    # Get current category and example selection
    model_category = st.sidebar.selectbox(
        "Select Model Category", 
        list(MODEL_SYNTAX_EXAMPLES.keys()), 
        key="model_category"
    )
    model_example = st.sidebar.selectbox(
        "Select a Model Example", 
        list(MODEL_SYNTAX_EXAMPLES[model_category].keys()), 
        key="model_example"
    )
    
    # Get current template selection
    current_selection = MODEL_SYNTAX_EXAMPLES[model_category][model_example]
    
    # Update session state only when selection changes
    if st.session_state.last_selection != current_selection:
        st.session_state.model_syntax = current_selection
        st.session_state.last_selection = current_selection
    
    # Model syntax editor with refresh button
    model_syntax = st.sidebar.text_area(
        "Edit Model Syntax",
        value=st.session_state.get("model_syntax", current_selection),
        height=200,
        key="model_syntax_editor"  # Unique key to prevent conflicts
    )
    
    # Add template refresh button
    if st.sidebar.button("🔄 Load Selected Template"):
        st.session_state.model_syntax = current_selection
        st.experimental_rerun()

    # Run analysis section
    st.sidebar.header("3. Run Analysis")
    if st.sidebar.button("🚀 Run SEM"):
        if data is None:
            st.error("Please upload a dataset first.")
            return
        if not model_syntax.strip():
            st.error("Please define model syntax.")
        else:
            try:
                with st.spinner("Fitting model..."):
                    model = Model(model_syntax)
                    model.fit(data)
                    stats = calc_stats(model)
                    param_df = model.inspect().copy()
                    param_df['Parameter'] = param_df['lval'] + ' ' + param_df['op'] + ' ' + param_df['rval']
                    param_df = param_df[['Parameter', 'Estimate', 'Std. Err', 'z-value', 'p-value']]
                    param_df.columns = ['Parameter', 'Estimate', 'Std. Error', 'z-value', 'p-value']
                    for col in ['Estimate', 'Std. Error', 'z-value', 'p-value']:
                        param_df[col] = param_df[col].apply(lambda x: f"{x:.3f}" if isinstance(x, (int, float)) else x)
                    
                    st.session_state.analysis_results = {
                        "param_df": param_df, 
                        "stats": stats
                    }
            except Exception as e:
                st.error(f"Error: {str(e)}")

    # Display results section
    if st.session_state.analysis_results:
        st.subheader("### 📈 Model Fit Statistics")
        try:
            stats = st.session_state.analysis_results["stats"]
            if not isinstance(stats, pd.DataFrame):
                stats = pd.DataFrame(stats)
            st.table(stats.T)
        except Exception as e:
            st.error(f"Error displaying fit statistics: {e}")
        
        st.subheader("### 🧮 Parameter Estimates")
        st.dataframe(st.session_state.analysis_results["param_df"])

    add_footer()

if __name__ == "__main__":
    main()
