import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="IROS Operating System", layout="wide")

# Baseline Launch Date: Week 1 Starts Sunday, Nov 1, 2026
LAUNCH_DATE = datetime(2026, 11, 1)

# Staff Roster Capacities & Role Definitions
STAFF_ROSTER = {
    "Rebecca Neill": {"target_wu": 0, "role": "Executive Director"},
    "Cara Neill": {"target_wu": 0, "role": "Administrative Director"},
    "Latoya Smith": {"target_wu": 30, "role": "Clinical Director"},
    "Stephanie Eatton-Johnson": {"target_wu": 30, "role": "Clinical Director"},
    "Ayaat Albayati": {"target_wu": 30, "role": "Clinical Operations Director"},
    "Ashley Shilo": {"target_wu": 30, "role": "DDA"},
    "Shalette Shaw": {"target_wu": 30, "role": "DDS 2"},
    "Jerry Burton": {"target_wu": 10, "role": "Audit Support Specialist"},
    "Ondrea Wilson": {"target_wu": 30, "role": "DDA"},
    "Terri Thomasson": {"target_wu": 10, "role": "Audit Support Specialist"},
    "Denna Smith": {"target_wu": 40, "role": "Business Support Specialist"},
    "Kristin Williams": {"target_wu": 40, "role": "DDS 2"},
    "Mohammed": {"target_wu": 30, "role": "QDDP (Start 10/19, Reports 10/26)"}
}

@st.cache_data(ttl=0)
def load_data():
    workload_df = pd.read_csv("Master_Workload.csv")
    try:
        note_df = pd.read_csv("Note_Report_Master.csv")
    except:
        note_df = pd.DataFrame()

    def get_sortable_date(row):
        w_type = str(row.get("Work Type", "")).strip().upper()
        week_num = row.get("Week Number", None)
        
        if pd.notnull(week_num) and str(week_num).isdigit():
            w_int = int(week_num)
            target_friday = LAUNCH_DATE + timedelta(weeks=w_int - 1, days=5)
        else:
            target_friday = LAUNCH_DATE + timedelta(days=5)

        base_date_str = row.get("ISP End Date") or row.get("Quarter End Date") or row.get("Target Date")
        parsed_base = None
        if pd.notnull(base_date_str):
            for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m-%d-%Y"):
                try:
                    parsed_base = datetime.strptime(str(base_date_str).strip(), fmt)
                    break
                except ValueError:
                    pass

        if "WT1" in w_type or "ANNUAL" in w_type:
            due_date = parsed_base - timedelta(days=14) if parsed_base else target_friday
            display_str = f"Due: {due_date.strftime('%m/%d/%Y')} (WT1 - Annual ISP)"

        elif "WT2" in w_type or "QUARTERLY" in w_type:
            if parsed_base:
                due_date = parsed_base + timedelta(days=1)
                display_str = f"Window: {due_date.strftime('%m/%d/%Y')} – {(parsed_base + timedelta(days=10)).strftime('%m/%d/%Y')}"
            else:
                due_date = target_friday
                display_str = f"Due: {due_date.strftime('%m/%d/%Y')} (WT2 - Quarterly)"

        elif any(k in w_type for k in ["WT5", "WT6", "NOTE"]):
            due_date = target_friday
            display_str = f"Due: {due_date.strftime('%m/%d/%Y')} @ 5:00 PM"

        else:
            due_date = target_friday
            display_str = f"Due: {due_date.strftime('%m/%d/%Y')}"

        return pd.Series([due_date, display_str])

    if "Work Type" in workload_df.columns:
        workload_df[["_sort_date", "Controlling Due Date"]] = workload_df.apply(get_sortable_date, axis=1)

    return workload_df, note_df

try:
    workload_df, note_df = load_data()
except Exception as e:
    st.error(f"Error loading CSV files: {e}")
    st.stop()

# Initialize session state for interactive status changes
if "workload_data" not in st.session_state:
    st.session_state.workload_data = workload_df.copy()

# Sidebar Staff Selection
st.sidebar.title("⚡ IROS Operating System")
staff_list = sorted(list(st.session_state.workload_data["Assigned Staff"].dropna().unique()))

if "Unassigned" in staff_list:
    staff_list.remove("Unassigned")

selected_staff = st.sidebar.selectbox("Select Active Staff Account:", staff_list)

# Staff Details from Roster
staff_info = STAFF_ROSTER.get(selected_staff, {"target_wu": 30, "role": "Staff Member"})

# Filter tasks for selected staff
user_tasks = st.session_state.workload_data[st.session_state.workload_data["Assigned Staff"] == selected_staff].copy()

if "_sort_date" in user_tasks.columns:
    user_tasks = user_tasks.sort_values(by="_sort_date", ascending=True)

# Header Metrics
st.title("Inspired Resolutions Operating System (IROS)")
st.subheader(f"Welcome back, {selected_staff} ({staff_info['role']})!")

col1, col2, col3, col4 = st.columns(4)
total_wu = user_tasks["Unit Value (WU)"].sum() if "Unit Value (WU)" in user_tasks.columns else 0.0
task_count = len(user_tasks)

nov_tasks = user_tasks[(user_tasks["_sort_date"] >= datetime(2026, 11, 1)) & (user_tasks["_sort_date"] <= datetime(2026, 11, 30))]

col1.metric("Weekly Target Capacity", f"{staff_info['target_wu']} WU / Week")
col2.metric("Total Annual Tasks", f"{task_count} Tasks")
col3.metric("Nov 2026 Immediate Load", f"{len(nov_tasks)} Tasks")
col4.metric("Domain Status", "Verified BAA ✅")

st.markdown("---")

# Navigation Tabs
tab1, tab2 = st.tabs(["📋 My Task Queue", "📑 Weekly Provider Note Reports"])

with tab1:
    st.subheader(f"Active Task Queue for {selected_staff}")
    
    # Timeframe Selector including Custom Date Range
    view_filter = st.radio(
        "Select Timeframe View:",
        ["📅 Week 1 (Nov 1 – Nov 7, 2026)", "🗓️ Month of November 2026", "📆 Full 52-Week Year", "🔍 Custom Date Range"],
        horizontal=True
    )
    
    filtered_tasks = user_tasks.copy()
    
    if view_filter == "📅 Week 1 (Nov 1 – Nov 7, 2026)":
        filtered_tasks = user_tasks[(user_tasks["_sort_date"] >= datetime(2026, 11, 1)) & (user_tasks["_sort_date"] <= datetime(2026, 11, 7))]
    elif view_filter == "🗓️ Month of November 2026":
        filtered_tasks = user_tasks[(user_tasks["_sort_date"] >= datetime(2026, 11, 1)) & (user_tasks["_sort_date"] <= datetime(2026, 11, 30))]
    elif view_filter == "🔍 Custom Date Range":
        col_start, col_end = st.columns(2)
        with col_start:
            start_date = st.date_input("Start Date:", value=datetime(2026, 11, 1))
        with col_end:
            end_date = st.date_input("End Date:", value=datetime(2026, 11, 30))
            
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        filtered_tasks = user_tasks[(user_tasks["_sort_date"] >= start_datetime) & (user_tasks["_sort_date"] <= end_datetime)]

    if len(filtered_tasks) > 0:
        display_cols = [c for c in ["Controlling Due Date", "Work Type", "Person's Full Name", "Provider", "Service", "Unit Value (WU)", "Week Number", "Work Status", "Barrier / Note"] if c in filtered_tasks.columns]
        
        st.dataframe(filtered_tasks[display_cols], use_container_width=True)
        st.caption(f"Showing {len(filtered_tasks)} task(s) for this selected view.")

        # Interactive Status Update Form
        st.markdown("### ✏️ Update Task Status")
        
        task_options = [f"{row['Person\'s Full Name']} - {row['Work Type']} ({row['Controlling Due Date']})" for idx, row in filtered_tasks.iterrows()]
        selected_task_str = st.selectbox("Select a task to update:", task_options)
        
        if selected_task_str:
            selected_idx = filtered_tasks.index[task_options.index(selected_task_str)]
            current_status = filtered_tasks.loc[selected_idx, "Work Status"] if "Work Status" in filtered_tasks.columns else "Scheduled"
            current_note = filtered_tasks.loc[selected_idx, "Barrier / Note"] if "Barrier / Note" in filtered_tasks.columns else ""

            with st.form("status_update_form"):
                status_choices = ["Scheduled", "In Progress", "Ready for Review", "Completed", "Pending QA", "Barrier Tagged"]
                default_idx = status_choices.index(current_status) if current_status in status_choices else 0
                
                new_status = st.selectbox("Update Work Status:", status_choices, index=default_idx)
                new_note = st.text_input("Barrier / Action Note:", value=str(current_note) if pd.notnull(current_note) else "")
                submit_button = st.form_submit_button("Save Status Update")

                if submit_button:
                    st.session_state.workload_data.loc[selected_idx, "Work Status"] = new_status
                    st.session_state.workload_data.loc[selected_idx, "Barrier / Note"] = new_note
                    st.success(f"Status updated to '{new_status}' for {filtered_tasks.loc[selected_idx, 'Person\'s Full Name']}!")
                    st.rerun()

    else:
        st.info("No active tasks due in this selected timeframe view.")

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
