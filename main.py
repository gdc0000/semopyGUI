import streamlit as st
import pandas as pd
from semopy import Model
from semopy.inspector import inspect
import numpy as np
import pyreadstat

# Predefined Model Syntax Examples (unchanged)
MODEL_SYNTAX_EXAMPLES = { ... }  # (Retain the original structure here)

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
