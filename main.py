import streamlit as st
import pandas as pd
from semopy import Model
from semopy.inspector import inspect
import numpy as np
import json

# Additional imports for handling different file formats
import pyreadstat

def format_apa_statistics(stat_dict):
    """
    Formats a dictionary of statistics into APA style strings.
    """
    apa_output = ""
    apa_output += f"Chi-square: {stat_dict.get('Chi-square', 'N/A'):.2f}, df = {stat_dict.get('df', 'N/A')}, p = {stat_dict.get('p-value', 'N/A')}\n"
    apa_output += f"CFI: {stat_dict.get('CFI', 'N/A'):.3f}\n"
    apa_output += f"TLI: {stat_dict.get('TLI', 'N/A'):.3f}\n"
    apa_output += f"RMSEA: {stat_dict.get('RMSEA', 'N/A'):.3f} (90% CI {stat_dict.get('RMSEA Lower', 'N/A')} - {stat_dict.get('RMSEA Upper', 'N/A')})\n"
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
    st.title("Structural Equation Modeling (SEM) with semopy")
    st.write("""
    This app allows you to perform Structural Equation Modeling using your own dataset.
    Upload your data in various formats, select variables, define your model, and view the results formatted in APA style.
    """)

    # Sidebar for file upload
    st.sidebar.header("1. Upload Data")
    uploaded_file = st.sidebar.file_uploader(
        "Upload your dataset",
        type=["csv", "xlsx", "xls", "sav", "por", "dta", "json"]
    )

    if uploaded_file is not None:
        data = load_data(uploaded_file)
        if data is not None:
            st.success("Data successfully uploaded!")
            st.write("### Dataset Preview")
            st.dataframe(data.head())

            # Sidebar for variable selection
            st.sidebar.header("2. Select Variables")
            all_columns = data.columns.tolist()
            with st.sidebar.expander("Select Variables for SEM"):
                endogenous = st.multiselect("Endogenous Variables", options=all_columns)
                exogenous = st.multiselect("Exogenous Variables", options=all_columns)

            # Display selected variables
            if endogenous or exogenous:
                st.write("### Selected Variables")
                if endogenous:
                    st.write("**Endogenous Variables:**", ", ".join(endogenous))
                if exogenous:
                    st.write("**Exogenous Variables:**", ", ".join(exogenous))

            # Sidebar for model specification
            st.sidebar.header("3. Define Model Syntax")
            st.sidebar.markdown("""
            Define your SEM model using the **semopy** syntax. 
            Each relationship should be on a new line. 
            For example:
            
            ```
            y1 ~ x1 + x2
            y2 ~ y1 + x3
            x1 ~~ x2
            ```
            """)
            model_syntax = st.sidebar.text_area("Model Syntax", height=200)

            # Button to run SEM
            if st.sidebar.button("Run SEM"):
                if not model_syntax.strip():
                    st.error("Please define the model syntax before running SEM.")
                else:
                    try:
                        model = Model(model_syntax)
                        model.fit(data)
                        results = model.inspect()

                        # Get model statistics
                        stats = inspect(model)
                        apa_stats = format_apa_statistics(stats)

                        st.write("### Model Fit Statistics (APA Style)")
                        st.text(apa_stats)

                        # Parameter Estimates
                        st.write("### Parameter Estimates")
                        params = model.inspect().reset_index()
                        params.columns = ['Parameter', 'Estimate', 'Std. Error', 'z-value', 'p-value', 'CI Lower', 'CI Upper']
                        st.dataframe(params.style.format({
                            'Estimate': '{:.3f}',
                            'Std. Error': '{:.3f}',
                            'z-value': '{:.3f}',
                            'p-value': '{:.3f}',
                            'CI Lower': '{:.3f}',
                            'CI Upper': '{:.3f}'
                        }))

                        # Optionally, you can add more detailed APA formatting here
                        
                    except Exception as e:
                        st.error(f"An error occurred while running SEM: {e}")

    else:
        st.info("Awaiting data file to be uploaded. Supported formats: CSV, Excel (XLS/XLSX), SPSS (SAV), Stata (DTA), JSON.")

if __name__ == "__main__":
    main()
