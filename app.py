import streamlit as st
import pandas as pd

# PAGE CONFIGURATION
st.set_page_config(
    page_title="IROS — Workload & Production Dashboard",
    page_icon="⚡",
    layout="wide"
)

# MASTER DATA LOADERS
@st.cache_data
def load_staff_roster():
    return pd.DataFrame([
        {"Name": "Rebecca Neill", "Role": "Executive Director / Owner", "Office": "Chesapeake", "Target_WU": 0},
        {"Name": "Cara Neill", "Role": "Administrative Director / Owner", "Office": "Newport News", "Target_WU": 0},
        {"Name": "Latoya Smith", "Role": "Clinical Director / QDDP Lead", "Office": "Chesapeake", "Target_WU": 20},
        {"Name": "Stephanie Eatton-Johnson", "Role": "Clinical Director / QDDP Lead", "Office": "Newport News", "Target_WU": 20},
        {"Name": "Ayaat Albayati", "Role": "Clinical Operations Director", "Office": "Chesapeake", "Target_WU": 30},
        {"Name": "Ashley Shilo", "Role": "Developmental Disability Associate (DDA)", "Office": "Chesapeake", "Target_WU": 30},
        {"Name": "Ondrea Wilson", "Role": "Developmental Disability Associate (DDA)", "Office": "Newport News", "Target_WU": 30},
        {"Name": "Shalette Shaw", "Role": "Developmental Disability Support 2 (DDS2)", "Office": "Chesapeake", "Target_WU": 30},
        {"Name": "Kristin Williams", "Role": "Developmental Disability Support 2 (DDS2)", "Office": "Chesapeake", "Target_WU": 40},
        {"Name": "Mohammad Qasim", "Role": "Developmental Disability Support 1 (DDS1)", "Office": "Newport News", "Target_WU": 40},
        {"Name": "Denna Smith", "Role": "Business Support Specialist", "Office": "Newport News", "Target_WU": 40},
        {"Name": "Jerry Burton", "Role": "Audit Support Specialist", "Office": "Chesapeake", "Target_WU": 10},
        {"Name": "Terri Thomasson", "Role": "Audit Support Specialist", "Office": "Newport News", "Target_WU": 10}
    ])

st.sidebar.title("⚡ IROS Operating System")
staff_df = load_staff_roster()
selected_staff_name = st.sidebar.selectbox("Select Active Staff Account:", staff_df['Name'].tolist(), index=5)
current_user = staff_df[staff_df['Name'] == selected_staff_name].iloc[0]

st.sidebar.success(f"Logged in as: **{current_user['Name']}**")

st.title("Inspired Resolutions Operating System (IROS)")
st.subheader(f"Welcome back, {current_user['Name']}!")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Weekly Target", f"{current_user['Target_WU']}.0 WU")
col2.metric("Scheduled Capacity", f"{min(current_user['Target_WU'], 30)}.0 WU")
col3.metric("Protected Buffer", f"{max(0, current_user['Target_WU'] - 30)}.0 WU")
col4.metric("Domain Status", "Verified BAA ✅")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📋 My Task Queue", "🔍 WT13 Clinical QA Queue", "💼 WT19 Medicaid Billing Queue"])

with tab1:
    st.markdown(f"### Active Task Queue for **{current_user['Name']}**")
    tasks_data = [
        {"Task ID": "TSK-1001", "Provider Agency": "HOUSE OF ANGELS", "Individual": "Asia Marsh", "Work Type": "WT1 — Annual ISP", "WU Weight": 3.0, "Deadline": "2026-10-12", "Status": "In Progress"},
        {"Task ID": "TSK-1002", "Provider Agency": "HOUSE OF ANGELS", "Individual": "Charlie Rollins", "Work Type": "WT2 — Quarterly Review", "WU Weight": 1.5, "Deadline": "2026-10-15", "Status": "Ready for Review"}
    ]
    st.dataframe(pd.DataFrame(tasks_data), use_container_width=True)

with tab2:
    st.markdown("### WT13 — Clinical Quality Assurance Review Queue")
    qa_data = [
        {"Task ID": "TSK-1002", "Staff Writer": "Ashley Shilo", "Provider": "HOUSE OF ANGELS", "Deliverable": "Quarterly Review — Charlie Rollins", "Submitted Date": "2026-10-05"}
    ]
    st.table(pd.DataFrame(qa_data))

with tab3:
    st.markdown("### WT19 — Medicaid Billing Reconciliation Queue")
    billing_data = [
        {"Task ID": "TSK-1003", "Individual": "Ahmad Wallace", "Provider": "EXTRAORDINARY CHANGES", "Service Auth #": "SA-998412", "Billing Specialist": "Denna Smith"}
    ]
    st.table(pd.DataFrame(billing_data))
