import streamlit as st
import pandas as pd
from semopy import Model
from semopy.inspector import inspect
import numpy as np

# Additional imports for handling different file formats
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

def format_apa_statistics(stat_dict):
    """
    Formats a dictionary of statistics into APA style strings.
    Safely handles non-numeric values by checking their type before formatting.
    """
    apa_output = ""
    
    # Helper function to format values
    def safe_format(value, fmt=".2f"):
        if isinstance(value, (int, float, np.number)):
            return format(value, fmt)
        else:
            return value

    chi_sq = safe_format(stat_dict.get('Chi-square', 'N/A'), ".2f")
    df = safe_format(stat_dict.get('df', 'N/A'), "")
    p_val = safe_format(stat_dict.get('p-value', 'N/A'), ".3f")
    cfi = safe_format(stat_dict.get('CFI', 'N/A'), ".3f")
    tli = safe_format(stat_dict.get('TLI', 'N/A'), ".3f")
    rmsea = safe_format(stat_dict.get('RMSEA', 'N/A'), ".3f")
    rmsea_lower = safe_format(stat_dict.get('RMSEA Lower', 'N/A'), ".3f")
    rmsea_upper = safe_format(stat_dict.get('RMSEA Upper', 'N/A'), ".3f")
    
    # Construct APA-formatted string
    apa_output += f"Chi-square: {chi_sq}, df = {df}, p = {p_val}\n"
    apa_output += f"CFI: {cfi}\n"
    apa_output += f"TLI: {tli}\n"
    apa_output += f"RMSEA: {rmsea} (90% CI {rmsea_lower} - {rmsea_upper})\n"
    
    return apa_output

def load_data(uploaded_file):
    """
    Loads data from various file formats into a pandas DataFrame.
    """
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    try:
        if file_extension == 'csv':
            data = pd.read_csv(uploaded_file)
        elif file_extension in ['xls', 'xlsx']:
            data = pd.read_excel(uploaded_file, engine='openpyxl' if file_extension == 'xlsx' else 'xlrd')
        elif file_extension in ['sav', 'por']:
            df, meta = pyreadstat.read_sav(uploaded_file)
            data = df
        elif file_extension == 'dta':
            data = pd.read_stata(uploaded_file)
        elif file_extension == 'json':
            data = pd.read_json(uploaded_file)
        else:
            st.error(f"Unsupported file format: {file_extension.upper()}")
            return None
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def main():
    st.set_page_config(page_title="SEM with semopy", layout="wide")
    st.title("📊 Structural Equation Modeling (SEM) with semopy")
    st.write("""
    This app allows you to perform Structural Equation Modeling using your own dataset.
    Upload your data in various formats, explore different SEM models, and view the results formatted in APA style.
    This tool is designed to support statistical education by providing clear and comprehensive modeling examples.
    """)

    # Sidebar for file upload
    st.sidebar.header("🔍 Configuration Panel")
    uploaded_file = st.sidebar.file_uploader(
        "Upload your dataset",
        type=["csv", "xlsx", "xls", "sav", "por", "dta", "json"]
    )

    if uploaded_file is not None:
        data = load_data(uploaded_file)
        if data is not None:
            st.sidebar.success("✅ Data successfully uploaded!")
            st.write("### 📂 Dataset Preview")
            st.dataframe(data.head())

            # Display variable names
            st.write("### 🗂️ Available Variables")
            st.markdown(f"**Total Variables:** {len(data.columns)}")
            st.write(data.columns.tolist())

            # Sidebar for model specification
            st.sidebar.header("📝 Define Model Syntax")
            st.sidebar.markdown("""
            Define your SEM model using the **semopy** syntax. 
            Each relationship should be on a new line. 
            Use the **Model Syntax Portfolio** below to explore and select example models.
            """)
            
            # Model Syntax Portfolio
            with st.sidebar.expander("📚 Model Syntax Portfolio"):
                st.markdown("### 🔍 Select a Model Example")
                # Category Selection
                category = st.selectbox("Select Model Category", options=list(MODEL_SYNTAX_EXAMPLES.keys()))
                
                # Example Selection based on Category
                example = st.selectbox("Select Model Example", options=list(MODEL_SYNTAX_EXAMPLES[category].keys()))
                
                # Display Selected Example
                if example:
                    example_syntax = MODEL_SYNTAX_EXAMPLES[category][example]
                    st.markdown(f"**Example: {example}**")
                    st.code(example_syntax, language='python')
                    
                    # Button to Load Example into Text Area
                    if st.button("📝 Load Example into Model Syntax"):
                        st.session_state['model_syntax'] = example_syntax.strip()
            
            # Model Syntax Text Area
            model_syntax = st.sidebar.text_area(
                "✍️ Model Syntax",
                height=400,
                key='model_syntax',
                help="Define your SEM model syntax here. You can write your own model or use the examples from the Model Syntax Portfolio."
            )

            # Button to run SEM
            if st.sidebar.button("🚀 Run SEM"):
                if not model_syntax.strip():
                    st.sidebar.error("Please define the model syntax before running SEM.")
                else:
                    try:
                        with st.spinner("Fitting the SEM model..."):
                            model = Model(model_syntax)
                            model.fit(data)
                            results = model.inspect()

                            # Get model statistics
                            stats = inspect(model)
                            apa_stats = format_apa_statistics(stats)

                        st.write("### 📈 Model Fit Statistics (APA Style)")
                        st.text(apa_stats)

                        # Parameter Estimates
                        st.write("### 🧮 Parameter Estimates")
                        params = model.inspect().reset_index()

                        # Dynamically rename columns based on the number of columns
                        expected_columns = ['Parameter', 'Estimate', 'Std. Error', 'z-value', 'p-value', 'CI Lower', 'CI Upper']
                        if params.shape[1] == len(expected_columns):
                            params.columns = expected_columns
                        elif params.shape[1] > len(expected_columns):
                            # Handle extra columns by keeping only the expected ones
                            params = params.iloc[:, :len(expected_columns)]
                            params.columns = expected_columns
                        else:
                            # If fewer columns, append 'N/A' to match
                            additional_cols = len(expected_columns) - params.shape[1]
                            for _ in range(additional_cols):
                                params[f'Extra_{_+1}'] = 'N/A'
                            params.columns = expected_columns

                        # Function to safely format parameter estimates
                        def safe_param_format(val, fmt="{:.3f}"):
                            try:
                                return fmt.format(val)
                            except:
                                return val

                        # Apply formatting
                        params_formatted = params.copy()
                        for col in ['Estimate', 'Std. Error', 'z-value', 'p-value', 'CI Lower', 'CI Upper']:
                            if col in params_formatted.columns:
                                params_formatted[col] = params_formatted[col].apply(lambda x: safe_param_format(x, "{:.3f}"))

                        st.dataframe(params_formatted)

                    except Exception as e:
                        st.error(f"An error occurred while running SEM: {e}")

    else:
        st.info("🔄 Awaiting data file to be uploaded. Supported formats: CSV, Excel (XLS/XLSX), SPSS (SAV), Stata (DTA), JSON.")

if __name__ == "__main__":
    main()
