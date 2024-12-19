import streamlit as st
import pandas as pd
from semopy import Model
from semopy.inspector import inspect
import numpy as np

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

def main():
    st.title("Structural Equation Modeling (SEM) with semopy")
    st.write("""
    This app allows you to perform Structural Equation Modeling using your own dataset.
    Upload your data, select variables, define your model, and view the results formatted in APA style.
    """)

    # Sidebar for file upload
    st.sidebar.header("1. Upload Data")
    uploaded_file = st.sidebar.file_uploader("Upload your dataset (CSV)", type=["csv"])

    if uploaded_file is not None:
        try:
            data = pd.read_csv(uploaded_file)
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
                        st.dataframe(params)

                        # Optionally, you can add more detailed APA formatting here
                        
                    except Exception as e:
                        st.error(f"An error occurred while running SEM: {e}")

        except Exception as e:
            st.error(f"Error loading data: {e}")
    else:
        st.info("Awaiting CSV file to be uploaded.")

if __name__ == "__main__":
    main()
