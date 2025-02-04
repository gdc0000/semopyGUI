import streamlit as st
import pandas as pd
from semopy import Model
import numpy as np
import pyreadstat

# Predefined Model Syntax Examples (unchanged)
MODEL_SYNTAX_EXAMPLES = {
    "Cross-Sectional Models": {
        "Simple Mediation Model": """
# Simple Mediation Model
Mediator ~ IndependentVariable
DependentVariable ~ Mediator + IndependentVariable
""",
        "Full Mediation Model": """
# Full Mediation Model
Mediator ~ IndependentVariable
DependentVariable ~ Mediator
IndependentVariable ~~ Mediator
""",
        "Confirmatory Factor Analysis": """
# Confirmatory Factor Analysis
Factor1 =~ Indicator1 + Indicator2 + Indicator3
Factor2 =~ Indicator4 + Indicator5 + Indicator6
Factor1 ~~ Factor2
""",
    },
    # Other examples truncated for brevity...
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
    st.write("Upload your dataset, choose or enter your model syntax, and run the model. Note: Fit statistics are not available with your current semopy version.")

    # Initialize session state for analysis results if not already set
    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = None

    # Sidebar: Data upload
    st.sidebar.header("1. Upload your Dataset")
    uploaded_file = st.sidebar.file_uploader("Choose a CSV, Excel, or SAS file", type=["csv", "txt", "xlsx", "xls", "sas7bdat"])

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

    # Sidebar: Model syntax selection
    st.sidebar.header("2. Define your Model Syntax")
    model_category = st.sidebar.selectbox("Select Model Category", list(MODEL_SYNTAX_EXAMPLES.keys()), key="model_category")
    model_example = st.sidebar.selectbox("Select a Model Example", list(MODEL_SYNTAX_EXAMPLES[model_category].keys()), key="model_example")
    default_syntax = MODEL_SYNTAX_EXAMPLES[model_category][model_example]

    # Store model syntax in session state to preserve user modifications
    if "model_syntax" not in st.session_state:
        st.session_state.model_syntax = default_syntax
    model_syntax = st.sidebar.text_area("Edit Model Syntax", value=st.session_state.model_syntax, height=200, key="model_syntax")

    # Run Analysis
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
                    
                    # Process parameter estimates
                    param_df = model.inspect().copy()
                    param_df['Parameter'] = param_df['lval'] + ' ' + param_df['op'] + ' ' + param_df['rval']
                    param_df = param_df[['Parameter', 'Estimate', 'Std. Err', 'z-value', 'p-value']]
                    param_df.columns = ['Parameter', 'Estimate', 'Std. Error', 'z-value', 'p-value']
                    
                    for col in ['Estimate', 'Std. Error', 'z-value', 'p-value']:
                        param_df[col] = param_df[col].apply(lambda x: f"{x:.3f}" if isinstance(x, (int, float)) else x)
                    
                    # Save analysis results in session state so they persist across reruns.
                    st.session_state.analysis_results = {"param_df": param_df, "stats": {}}
            except Exception as e:
                st.error(f"Error: {str(e)}")

    # Display analysis results if available
    if st.session_state.analysis_results:
        st.subheader("### 🧮 Parameter Estimates")
        st.dataframe(st.session_state.analysis_results["param_df"])
        
        # Optional: Toggle full statistics view
        show_full = st.checkbox("Show full fit statistics dictionary", key="show_full")
        if show_full:
            st.json(st.session_state.analysis_results["stats"])

if __name__ == "__main__":
    main()
