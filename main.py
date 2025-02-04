import streamlit as st
import pandas as pd
from semopy import Model
from semopy.inspector import inspect
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

def format_apa_statistics(stat_dict):
    """
    Formats a dictionary of statistics into APA style strings with corrected keys.
    """
    apa_output = ""
    
    def safe_format(value, fmt=".2f"):
        if isinstance(value, (int, float, np.number)):
            return format(value, fmt) if fmt else str(int(value))
        return str(value)

    chi_sq = safe_format(stat_dict.get('Chi2', 'N/A'), ".2f")
    df = safe_format(stat_dict.get('DoF', 'N/A'), ".0f")  # Ensure integer format
    p_val = safe_format(stat_dict.get('PValue', 'N/A'), ".3f")
    cfi = safe_format(stat_dict.get('CFI', 'N/A'), ".3f")
    tli = safe_format(stat_dict.get('TLI', 'N/A'), ".3f")
    rmsea = safe_format(stat_dict.get('RMSEA', 'N/A'), ".3f")
    rmsea_lower = safe_format(stat_dict.get('RMSEA_CI_lower', 'N/A'), ".3f")
    rmsea_upper = safe_format(stat_dict.get('RMSEA_CI_upper', 'N/A'), ".3f")
    
    apa_output += f"Chi-square: {chi_sq}, df = {df}, p = {p_val}\n"
    apa_output += f"CFI: {cfi}\nTLI: {tli}\n"
    apa_output += f"RMSEA: {rmsea} (90% CI {rmsea_lower} - {rmsea_upper})\n"
    return apa_output

def load_data(uploaded_file):
    """Loads data from various formats with error handling."""
    # (Unchanged, retain original code here)

def main():
    st.set_page_config(page_title="SEM with semopy", layout="wide")
    st.title("📊 Structural Equation Modeling (SEM) with semopy")
    st.write("...")  # Original description

    # Sidebar file upload
    uploaded_file = st.sidebar.file_uploader(...)
    if uploaded_file is not None:
        data = load_data(uploaded_file)
        if data is not None:
            # Handle missing data
            if data.isnull().sum().sum() > 0:
                st.warning("⚠️ Dataset contains missing values. SEM requires complete cases.")
                if st.checkbox("Drop rows with missing values?"):
                    data = data.dropna().reset_index(drop=True)
                    st.write(f"Using {len(data)} complete cases.")

            st.write("### 📂 Dataset Preview")
            st.dataframe(data.head())

            # Model syntax portfolio and input (unchanged)
            model_syntax = st.sidebar.text_area(...)

            if st.sidebar.button("🚀 Run SEM"):
                if not model_syntax.strip():
                    st.error("Please define model syntax.")
                else:
                    try:
                        with st.spinner("Fitting model..."):
                            model = Model(model_syntax)
                            model.fit(data)
                            stats = inspect(model)  # Get fit statistics
                            apa_stats = format_apa_statistics(stats)
                            
                            # Process parameter estimates
                            params = model.inspect().copy()
                            params['Parameter'] = params['lval'] + ' ' + params['op'] + ' ' + params['rval']
                            params = params[['Parameter', 'Estimate', 'Std. Err', 'z-value', 'p-value']]
                            params.columns = ['Parameter', 'Estimate', 'Std. Error', 'z-value', 'p-value']

                            # Formatting parameters
                            for col in ['Estimate', 'Std. Error', 'z-value', 'p-value']:
                                params[col] = params[col].apply(lambda x: f"{x:.3f}" if isinstance(x, (int, float)) else x)

                        st.write("### 📈 Model Fit Statistics")
                        st.code(apa_stats)
                        
                        st.write("### 🧮 Parameter Estimates")
                        st.dataframe(params)
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
