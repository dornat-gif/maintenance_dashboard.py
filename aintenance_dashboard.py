
import streamlit as st
import json
import re
from collections import defaultdict
import plotly.express as px
from datetime import datetime
import csv
import os

# Title
st.title("Maintenance Reporting Dashboard")

# Text input for daily activity
daily_input = st.text_area("Paste today's technician activity update here:", height=300)

if st.button("Generate Report"):
    # Initialize data structures
    technicians = defaultdict(list)
    contractors = []
    suspended = []
    pto = []
    training = []
    material_notes = []
    contractor_flag = False

    # Normalize input
    lines = daily_input.split('\n')
    current_tech = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Match technician name
        match = re.match(r"^([A-Z][a-z]+)\\s", line)
        if match:
            current_tech = match.group(1)
            if "Suspended" in line:
                suspended.append(current_tech)
            elif "PTO" in line:
                pto.append(current_tech)
            elif "training" in line.lower() or "tests" in line.lower():
                training.append(current_tech)
            else:
                task = line[len(current_tech):].strip()
                technicians[current_tech].append(task)
        elif "Marshall" in line or "contractor" in line.lower() or "SSI" in line or "Tencarva" in line or "A&H" in line:
            contractors.append(line)
            contractor_flag = True
        elif "material" in line.lower() or "need" in line.lower():
            material_notes.append(line)
        elif current_tech:
            technicians[current_tech].append(line)

    # Generate Email 1
    email1 = "Subject: Technician Activity Report\n\nHi Bryan,\n\nHere’s today’s breakdown of technician activity:\n\n"
    for tech, tasks in technicians.items():
        email1 += f"{tech}\n"
        if tasks:
            for task in tasks:
                email1 += f"• {task}\n"
        else:
            email1 += "• No tasks recorded.\n"
        email1 += "\n"
    for tech in suspended:
        email1 += f"{tech}\n• Suspended\n\n"
    for tech in pto:
        email1 += f"{tech}\n• PTO\n\n"
    for tech in training:
        email1 += f"{tech}\n• Completed training or tests\n\n"
    email1 += "Contractor Updates:\n"
    if contractor_flag:
        for c in contractors:
            email1 += f"• {c}\n"
    else:
        email1 += "• No contractor updates today.\n"
    email1 += "\nBest,\nDaniel"

    # Generate Email 2
    email2 = "Subject: Maintenance Department Update\n\nHello Team,\n\n"
    email2 += "Today’s work focused on system reliability and operational improvements. "
    email2 += "Tasks included water sampling, equipment troubleshooting, electrical checks, air system work, piping changes, and filter installations. "
    email2 += "Material planning and valve replacements were also completed. "
    email2 += "Training and onboarding progressed with new hire check-offs and scheduled equipment certifications.\n\n"
    if contractor_flag:
        email2 += "Contractor support included:\n"
        for c in contractors:
            email2 += f"• {c}\n"
    email2 += "\nGreat job by the maintenance team for staying focused and collaborating across departments to keep operations running smoothly.\n\n"
    email2 += "Best regards,\nDaniel Ornat"

    # Display emails
    st.subheader("Email 1: Technician Activity Report")
    st.text_area("Email to Bryan Weiss", value=email1, height=400)

    st.subheader("Email 2: Maintenance Department Update")
    st.text_area("Email to Upper Management & Peers", value=email2, height=400)

    # Technician productivity chart
    task_counts = {tech: len(tasks) for tech, tasks in technicians.items()}
    if task_counts:
        fig = px.bar(x=list(task_counts.keys()), y=list(task_counts.values()),
                     labels={'x': 'Technician', 'y': 'Number of Tasks'},
                     title='Technician Productivity for Today')
        st.plotly_chart(fig)

    # Save structured data
    report_data = {
        "date": datetime.today().strftime("%Y-%m-%d"),
        "technicians": dict(technicians),
        "suspended": suspended,
        "pto": pto,
        "training": training,
        "contractors": contractors,
        "material_notes": material_notes,
        "email1": email1,
        "email2": email2
    }

    with open("maintenance_dashboard_data.json", "w") as f:
        json.dump(report_data, f, indent=2)

    # Append metrics to CSV for continuous tracking
    csv_file = "technician_metrics.csv"
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Date", "Technician", "TaskCount"])
        for tech, count in task_counts.items():
            writer.writerow([datetime.today().strftime("%Y-%m-%d"), tech, count])

    st.success("Report generated, saved to JSON, and metrics appended to CSV.")
``
