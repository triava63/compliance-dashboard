import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO

st.set_page_config(page_title="Tracking ID Compliance Checker", layout="centered")

st.title("📦 Tracking ID Compliance Checker")

# Step 1: File uploader
uploaded_file = st.file_uploader("Upload your container CSV file", type=["csv"])

# Step 2: User inputs tracking IDs
tracking_input = st.text_area(
    "Paste your Tracking IDs (comma-separated or line-separated):",
    placeholder="Example:\n628448306791\n360687768083\n628447767975"
)

# Process inputs
if tracking_input:
    # Support both comma-separated and newline-separated inputs
    tracking_ids = [x.strip() for x in tracking_input.replace(',', '\n').split('\n') if x.strip()]
else:
    tracking_ids = []

# Step 3: Once both inputs are provided, process the file
if uploaded_file and tracking_ids:
    df = pd.read_csv(uploaded_file)
    df['container_label'] = df['container_label'].astype(str)

    tracking_ids_set = set(tracking_ids)
    matched_df = df[df['container_label'].isin(tracking_ids)][['container_label', 'dest1']]
    matched_ids = set(matched_df['container_label'].tolist())

    num_matched = len(matched_ids)
    num_unmatched = len(tracking_ids_set - matched_ids)
    total_ids = len(tracking_ids_set)
    compliance_percentage = 100 - (num_unmatched / total_ids) * 100 if total_ids > 0 else 0

    st.subheader("📊 Results Summary")
    st.metric("Matched Tracking IDs", num_matched)
    st.metric("Unmatched Tracking IDs", num_unmatched)
    st.metric("Compliance %", f"{compliance_percentage:.2f}%")

    st.subheader("✅ Matched Tracking IDs with Destinations")
    st.dataframe(matched_df)

    # Gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=compliance_percentage,
        delta={'reference': 100, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
        title={'text': "Compliance Percentage", 'font': {'size': 24}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 70], 'color': 'red'},
                {'range': [70, 90], 'color': 'yellow'},
                {'range': [90, 100], 'color': 'green'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': compliance_percentage
            }
        }
    ))
    fig.update_layout(paper_bgcolor="lavender", font={'color': "black", 'family': "Calibri"})
    st.plotly_chart(fig)

    # Excel download
    output = BytesIO()
    matched_df.to_excel(output, index=False)
    st.download_button(
        label="📥 Download Matched IDs as Excel",
        data=output.getvalue(),
        file_name="matched_tracking_ids.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
elif uploaded_file and not tracking_ids:
    st.warning("Please enter tracking IDs above to continue.")
elif tracking_ids and not uploaded_file:
    st.warning("Please upload a CSV file to continue.")
