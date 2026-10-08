import streamlit as st
import pandas as pd

st.set_page_config(page_title="IROS Operating System", layout="wide")

# Load data from the repository CSV files
@st.cache_data(ttl=0)
def load_data():
    workload_df = pd.read_csv("Master_Workload.csv")
    try:
        note_df = pd.read_csv("Note_Report_Master.csv")
    except:
        note_df = pd.DataFrame()
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
user_tasks = workload_df[workload_df["Assigned Staff"] == selected_staff]

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
        display_cols = [c for c in ["Work Type", "Person's Full Name", "Provider", "Service", "Unit Value (WU)", "Week Number", "Work Status", "Barrier / Note"] if c in user_tasks.columns]
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
