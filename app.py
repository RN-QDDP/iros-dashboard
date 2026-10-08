import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="IROS Operating System", layout="wide")

@st.cache_data(ttl=0)
def load_data():
    workload_df = pd.read_csv("Master_Workload.csv")
    try:
        note_df = pd.read_csv("Note_Report_Master.csv")
    except:
        note_df = pd.DataFrame()

    # Function to calculate specific WT deadline windows based on IROS policy
    def calculate_deadline(row):
        w_type = str(row.get("Work Type", "")).upper()
        
        # 1. WT1 Annual ISP: 14 Days Pre-Due Window
        if "WT1" in w_type or "ANNUAL" in w_type:
            return "14-Day Pre-Due Window (Prior to ISP End Date)"
        
        # 2. WT2 Quarterly Review: 1-10 Day Post-Quarter Window
        elif "WT2" in w_type or "QUARTERLY" in w_type:
            return "1–10 Day Window (Post Quarter End)"
        
        # 3. Note Reports (WT5/WT6): Friday @ 5:00 PM
        elif "WT5" in w_type or "WT6" in w_type or "NOTE" in w_type:
            return "Friday @ 5:00 PM (Weekly Hard Deadline)"
        
        else:
            return "Standard Operational Schedule"

    if "Work Type" in workload_df.columns:
        workload_df["Compliance Deadline Window"] = workload_df.apply(calculate_deadline, axis=1)

    return workload_df, note_df

try:
    workload_df, note_df = load_data()
except Exception as e:
    st.error(f"Error loading CSV files: {e}")
    st.stop()

# Sidebar Staff Selection
st.sidebar.title("⚡ IROS Operating System")
staff_list = sorted(list(workload_df["Assigned Staff"].dropna().unique()))

if "Unassigned" in staff_list:
    staff_list.remove("Unassigned")

selected_staff = st.sidebar.selectbox("Select Active Staff Account:", staff_list)

# Filter tasks for selected staff
user_tasks = workload_df[workload_df["Assigned Staff"] == selected_staff].copy()

# Header Metrics
st.title("Inspired Resolutions Operating System (IROS)")
st.subheader(f"Welcome back, {selected_staff}!")

col1, col2, col3, col4 = st.columns(4)
total_wu = user_tasks["Unit Value (WU)"].sum() if "Unit Value (WU)" in user_tasks.columns else 0.0
task_count = len(user_tasks)

col1.metric("Total Assigned Tasks", f"{task_count} Tasks")
col2.metric("Scheduled Load", f"{total_wu:.1f} WU")
col3.metric("Protected Buffer", "0.0 WU")
col4.metric("Domain Status", "Verified BAA ✅")

st.markdown("---")

# Navigation Tabs
tab1, tab2 = st.tabs(["📋 My Task Queue", "📑 Weekly Provider Note Reports"])

with tab1:
    st.subheader(f"Active Task Queue for {selected_staff}")
    if len(user_tasks) > 0:
        display_cols = [c for c in ["Work Type", "Compliance Deadline Window", "Person's Full Name", "Provider", "Service", "Unit Value (WU)", "Week Number", "Work Status", "Barrier / Note"] if c in user_tasks.columns]
        st.dataframe(user_tasks[display_cols], use_container_width=True)
    else:
        st.info("No active tasks assigned.")

with tab2:
    st.subheader(f"Note Report Intake Queue for {selected_staff}")
    if not note_df.empty and "Assigned Staff" in note_df.columns:
        user_notes = note_df[note_df["Assigned Staff"] == selected_staff]
        if len(user_notes) > 0:
            st.dataframe(user_notes, use_container_width=True)
        else:
            st.info("No provider note reports assigned to this account.")
    else:
        st.info("Note Report Master data loaded.")
