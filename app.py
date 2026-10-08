import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="IROS Operating System", layout="wide")

# Baseline Launch Date: Week 1 Starts Sunday, Nov 1, 2026
LAUNCH_DATE = datetime(2026, 11, 1)

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
        
        # Calculate Friday of assigned week number starting from Nov 1, 2026
        if pd.notnull(week_num) and str(week_num).isdigit():
            w_int = int(week_num)
            target_friday = LAUNCH_DATE + timedelta(weeks=w_int - 1, days=5)
        else:
            target_friday = LAUNCH_DATE + timedelta(days=5)

        # Parse base date (ISP End Date or Quarter End Date)
        base_date_str = row.get("ISP End Date") or row.get("Quarter End Date") or row.get("Target Date")
        parsed_base = None
        if pd.notnull(base_date_str):
            for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m-%d-%Y"):
                try:
                    parsed_base = datetime.strptime(str(base_date_str).strip(), fmt)
                    break
                except ValueError:
                    pass

        # WT1 — Annual ISP: Due 14 Days Pre-Due Window prior to ISP End Date
        if "WT1" in w_type or "ANNUAL" in w_type:
            if parsed_base:
                due_date = parsed_base - timedelta(days=14)
            else:
                due_date = target_friday
            display_str = f"Due: {due_date.strftime('%m/%d/%Y')} (WT1 - Annual ISP)"

        # WT2 — Quarterly Review: 1-10 Day Window Post Quarter End
        elif "WT2" in w_type or "QUARTERLY" in w_type:
            if parsed_base:
                start_w = parsed_base + timedelta(days=1)
                due_date = start_w
                end_w = parsed_base + timedelta(days=10)
                display_str = f"Window: {start_w.strftime('%m/%d/%Y')} – {end_w.strftime('%m/%d/%Y')}"
            else:
                due_date = target_friday
                display_str = f"Due: {due_date.strftime('%m/%d/%Y')} (WT2 - Quarterly)"

        # WT5 / WT6 — Note Reports: Friday @ 5:00 PM
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

# Sidebar Staff Selection
st.sidebar.title("⚡ IROS Operating System")
staff_list = sorted(list(workload_df["Assigned Staff"].dropna().unique()))

if "Unassigned" in staff_list:
    staff_list.remove("Unassigned")

selected_staff = st.sidebar.selectbox("Select Active Staff Account:", staff_list)

# Filter tasks for selected staff
user_tasks = workload_df[workload_df["Assigned Staff"] == selected_staff].copy()

# STRICT CHRONOLOGICAL SORTING (Earliest November 2026 dates at the very top)
if "_sort_date" in user_tasks.columns:
    user_tasks = user_tasks.sort_values(by="_sort_date", ascending=True)

# Header Metrics
st.title("Inspired Resolutions Operating System (IROS)")
st.subheader(f"Welcome back, {selected_staff}!")

col1, col2, col3, col4 = st.columns(4)
total_wu = user_tasks["Unit Value (WU)"].sum() if "Unit Value (WU)" in user_tasks.columns else 0.0
task_count = len(user_tasks)

# November 2026 Immediate Focus Metrics
nov_tasks = user_tasks[(user_tasks["_sort_date"] >= datetime(2026, 11, 1)) & (user_tasks["_sort_date"] <= datetime(2026, 11, 30))]
nov_count = len(nov_tasks)

col1.metric("Total Assigned Tasks", f"{task_count} Tasks")
col2.metric("Nov 2026 Immediate Tasks", f"{nov_count} Due in Nov")
col3.metric("Scheduled Load", f"{total_wu:.1f} WU")
col4.metric("Domain Status", "Verified BAA ✅")

st.markdown("---")

# Navigation Tabs
tab1, tab2 = st.tabs(["📋 My Task Queue (Nov 2026 Testing Focus)", "📑 Weekly Provider Note Reports"])

with tab1:
    st.subheader(f"Active Task Queue for {selected_staff} (Sorted by Due Date)")
    if len(user_tasks) > 0:
        display_cols = [c for c in ["Controlling Due Date", "Work Type", "Person's Full Name", "Provider", "Service", "Unit Value (WU)", "Week Number", "Work Status", "Barrier / Note"] if c in user_tasks.columns]
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
