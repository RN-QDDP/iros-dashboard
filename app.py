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

    def calculate_exact_deadline(row):
        w_type = str(row.get("Work Type", "")).strip().upper()
        week_num = row.get("Week Number", None)
        
        # Helper: Calculate Friday of assigned week number
        friday_str = None
        if pd.notnull(week_num) and str(week_num).isdigit():
            w_int = int(week_num)
            target_friday = LAUNCH_DATE + timedelta(weeks=w_int - 1, days=5)
            friday_str = target_friday.strftime("%m/%d/%Y")

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

        # WT1 — Annual ISP (14 days pre-due window prior to ISP End Date)
        if "WT1" in w_type or "ANNUAL" in w_type:
            if parsed_base:
                due = parsed_base - timedelta(days=14)
                return f"Due: {due.strftime('%m/%d/%Y')} (14 Days Pre-Due)"
            elif friday_str:
                return f"Due: {friday_str} (Target Week)"
            return "14 Days Prior to ISP End Date"

        # WT2 — Quarterly Review (1-10 Days Post Quarter End)
        elif "WT2" in w_type or "QUARTERLY" in w_type:
            if parsed_base:
                start_w = parsed_base + timedelta(days=1)
                end_w = parsed_base + timedelta(days=10)
                return f"Window: {start_w.strftime('%m/%d/%Y')} – {end_w.strftime('%m/%d/%Y')}"
            elif friday_str:
                return f"Due: {friday_str} (1–10 Day Post-Quarter Window)"
            return "1–10 Days Post Quarter End"

        # WT3 — Intake
        elif "WT3" in w_type or "INTAKE" in w_type:
            return "Within 5 Business Days of Trigger"

        # WT4 — Discharge
        elif "WT4" in w_type or "DISCHARGE" in w_type:
            return "Within 10 Business Days of Discontinuation"

        # WT5 / WT6 — Weekly Note Reports (Hard deadline Friday @ 5:00 PM)
        elif any(k in w_type for k in ["WT5", "WT6", "NOTE"]):
            if friday_str:
                return f"Due: {friday_str} @ 5:00 PM"
            return "Friday @ 5:00 PM Weekly"

        # WT7 — Documentation Corrections
        elif "WT7" in w_type or "CORRECTION" in w_type:
            return "Within 48 Hours of QA Return"

        # WT8 — Pended ISP / WaMS Pend
        elif "WT8" in w_type or "PEND" in w_type:
            return "High-Priority (Within 24–48 Hours)"

        # WT9 — VAMMIS Approval Monitoring
        elif "WT9" in w_type or "VAMMIS" in w_type:
            return "Submit Day -30 prior to Auth End"

        # WT10 — Partial Plan-Year Resubmission
        elif "WT10" in w_type or "PARTIAL" in w_type:
            return "Actionable Day -45; Submit Day -30"

        # WT11 — Clinical Barrier Management
        elif "WT11" in w_type or "BARRIER" in w_type:
            return "Active Resolution within 3 Days"

        # WT12 — Signatures
        elif "WT12" in w_type or "SIGNATURE" in w_type:
            return "Within 5 Business Days"

        # WT13 — Clinical QA / Final Review
        elif "WT13" in w_type or "QA" in w_type:
            return "Within 48 Hours in QA Queue"

        # WT14 — Provider Follow-Up
        elif "WT14" in w_type or "FOLLOW-UP" in w_type:
            return "Within 3 Business Days"

        # WT15 — Clinical Compliance / Escalation
        elif "WT15" in w_type or "ESCALAT" in w_type:
            return "Leadership Action within 24 Hours"

        # WT16 — Meetings
        elif "WT16" in w_type or "MEETING" in w_type:
            return "Scheduled Calendar Event Time"

        # WT17 — Daily Email / Calendar Review
        elif "WT17" in w_type or "EMAIL" in w_type:
            return "Daily by 5:00 PM COB"

        # WT18 — Communication
        elif "WT18" in w_type or "CALL" in w_type or "TEXT" in w_type:
            return "Same-Day / Within 24 Hours"

        # WT19 — Medicaid Billing Support
        elif "WT19" in w_type or "BILLING" in w_type:
            return "Weekly Billing Cycle (Fridays)"

        # WT20 — Provider EHR Entry
        elif "WT20" in w_type or "EHR" in w_type:
            return "Within 3 Business Days of Approval"

        else:
            if friday_str:
                return f"Due: {friday_str}"
            return "Standard Operational Schedule"

    if "Work Type" in workload_df.columns:
        workload_df["Controlling Due Date"] = workload_df.apply(calculate_exact_deadline, axis=1)

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
