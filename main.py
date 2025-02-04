import streamlit as st
import pandas as pd
from semopy import Model, calc_stats
import numpy as np
import pyreadstat

# Predefined Model Syntax Examples
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
    "Longitudinal Models": {
        "Cross-Lagged Panel Model": """
# Cross-Lagged Panel Model
Y1 ~ X0
X1 ~ Y0
Y2 ~ Y1 + X1
X2 ~ X1 + Y1
""",
        "Latent Growth Curve Model": """
# Latent Growth Curve Model
Intercept =~ 1*Y1 + 1*Y2 + 1*Y3
Slope =~ 0*Y1 + 1*Y2 + 2*Y3
Y1 ~ Intercept + 0*Slope
Y2 ~ Intercept + 1*Slope
Y3 ~ Intercept + 2*Slope
""",
    },
    "Multi-Group Models": {
        "Measurement Invariance": """
# Measurement Invariance
Factor1 =~ Indicator1 + Indicator2 + Indicator3
Factor2 =~ Indicator4 + Indicator5 + Indicator6
# Invariant across groups
Factor1 ~~ Factor2
""",
        "Structural Multi-Group Model": """
# Structural Multi-Group Model
Mediator ~ IndependentVariable
DependentVariable ~ Mediator + IndependentVariable
Mediator ~~ IndependentVariable
# Constraints across groups
Mediator ~~ IndependentVariable @1
DependentVariable ~~ Mediator @1
""",
    },
    "Advanced Models": {
        "Mediation with Moderation": """
# Mediation with Moderation
Mediator ~ IndependentVariable + Moderator
DependentVariable ~ Mediator + IndependentVariable + Moderator + IndependentVariable*Moderator
IndependentVariable ~~ Moderator
""",
        "Higher-Order Factor Model": """
# Higher-Order Factor Model
Factor1 =~ Indicator1 + Indicator2 + Indicator3
Factor2 =~ Indicator4 + Indicator5 + Indicator6
HigherOrderFactor =~ Factor1 + Factor2
HigherOrderFactor ~~ HigherOrderFactor
""",
        "Latent Interaction Model": """
# Latent Interaction Model
FactorA =~ X1 + X2 + X3
FactorB =~ Y1 + Y2 + Y3
Interaction =~ FactorA * FactorB
DependentVariable ~ Interaction + FactorA + FactorB
""",
        "Bifactor Model": """
# Bifactor Model
GeneralFactor =~ X1 + X2 + X3 + X4 + X5
SpecificFactor1 =~ X1 + X2 + X3
SpecificFactor2 =~ X4 + X5
GeneralFactor ~~ SpecificFactor1 + SpecificFactor2
SpecificFactor1 ~~ SpecificFactor2
""",
    }
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
        "Fit indices (e.g., chi2, RMSEA, CFI, TLI, NFI, GFI, AGFI) will be calculated using semopy.calc_stats."
    )

    # Initialize session state for analysis results if not already set
    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = None

    # Sidebar: Data upload
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

    # Sidebar: Model syntax selection
    st.sidebar.header("2. Define your Model Syntax")
    model_category = st.sidebar.selectbox(
        "Select Model Category", list(MODEL_SYNTAX_EXAMPLES.keys()), key="model_category"
    )
    model_example = st.sidebar.selectbox(
        "Select a Model Example", list(MODEL_SYNTAX_EXAMPLES[model_category].keys()), key="model_example"
    )
    default_syntax = MODEL_SYNTAX_EXAMPLES[model_category][model_example]

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
                    # Calculate fit statistics using semopy.calc_stats
                    stats = calc_stats(model)
                    # Process parameter estimates
                    param_df = model.inspect().copy()
                    param_df['Parameter'] = param_df['lval'] + ' ' + param_df['op'] + ' ' + param_df['rval']
                    param_df = param_df[['Parameter', 'Estimate', 'Std. Err', 'z-value', 'p-value']]
                    param_df.columns = ['Parameter', 'Estimate', 'Std. Error', 'z-value', 'p-value']
                    for col in ['Estimate', 'Std. Error', 'z-value', 'p-value']:
                        param_df[col] = param_df[col].apply(lambda x: f"{x:.3f}" if isinstance(x, (int, float)) else x)
                    
                    # Save analysis results in session state so they persist across reruns.
                    st.session_state.analysis_results = {"param_df": param_df, "stats": stats}
            except Exception as e:
                st.error(f"Error: {str(e)}")

    # Display analysis results if available
    if st.session_state.analysis_results:
        st.subheader("### 📈 Model Fit Statistics")
        # Display the fit indices table; transposing so that indices become rows
        st.table(st.session_state.analysis_results["stats"].T)
        st.subheader("### 🧮 Parameter Estimates")
        st.dataframe(st.session_state.analysis_results["param_df"])

if __name__ == "__main__":
    main()
