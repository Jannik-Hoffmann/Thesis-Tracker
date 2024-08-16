import asyncio
import json
import os
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# File to store the data
DATA_FILE = "thesis_data.json"

# Emojis for categories and priority levels
CATEGORY_EMOJIS = {
    "Introduction": "📝",
    "Literature Review": "📚",
    "Methodology": "🔬",
    "Results": "📊",
    "Discussion": "💬",
    "Conclusion": "🏁",
    "Writing": "✍️",
    "Research": "🔎",
    "Data Analysis": "📈",
    "Meetings": "👥",
    "Other": "🔧",
}
PRIORITY_EMOJIS = {"High": "🔴", "Medium": "🟠", "Low": "🟢"}


# Function to load data
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
            for report in data.get("reports", []):
                if isinstance(report["date"], str):
                    report["date"] = datetime.fromisoformat(report["date"])
            for todo in data.get("todo", []):
                if "due_date" in todo and isinstance(todo["due_date"], str):
                    todo["due_date"] = datetime.strptime(
                        todo["due_date"], "%Y-%m-%d"
                    ).date()
        except json.JSONDecodeError:
            data = {
                "progress": {},
                "reports": [],
                "categories": [],
                "tasks": [],
                "todo": [],
                "tags": [],
            }
    else:
        data = {
            "progress": {},
            "reports": [],
            "categories": [],
            "tasks": [],
            "todo": [],
            "tags": [],
        }
    return data


# Function to save data
def save_data(data):
    with open(DATA_FILE, "w") as f:
        data_to_save = data.copy()
        for report in data_to_save.get("reports", []):
            if isinstance(report["date"], datetime):
                report["date"] = report["date"].isoformat()
        for todo in data_to_save.get("todo", []):
            if "due_date" in todo and isinstance(todo["due_date"], datetime):
                todo["due_date"] = todo["due_date"].isoformat()
        json.dump(data_to_save, f, default=str, indent=4)


# Load data
if "data" not in st.session_state:
    st.session_state.data = load_data()

# Ensure all necessary keys exist
for key in ["progress", "reports", "categories", "tasks", "todo", "tags"]:
    if key not in st.session_state.data:
        st.session_state.data[key] = []

# Initial categories and tags
if not st.session_state.data["categories"]:
    st.session_state.data["categories"] = list(CATEGORY_EMOJIS.keys())
if not st.session_state.data["tags"]:
    st.session_state.data["tags"] = ["Important", "Urgent", "Long-term"]

# Set page config
st.set_page_config(page_title="Thesis Manager", page_icon="🎓", layout="wide")

# Custom CSS
st.markdown(
    """
<style>
    .stButton>button {
        border: 2px solid;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button[data-baseweb="button"]:nth-of-type(1) { border-color: #ff4b4b; }
    .stButton>button[data-baseweb="button"]:nth-of-type(2) { border-color: #4b8bff; }
    .stButton>button[data-baseweb="button"]:nth-of-type(3) { border-color: #4bff4b; }
    .stButton>button[data-baseweb="button"]:nth-of-type(4) { border-color: #ffbb4b; }
    .stButton>button[data-baseweb="button"]:nth-of-type(5) { border-color: #ff4bff; }
    .stButton>button[data-baseweb="button"]:nth-of-type(6) { border-color: #4bffff; }
    .stButton>button[data-baseweb="button"]:nth-of-type(7) { border-color: #ff8b4b; }
    .stButton>button[data-baseweb="button"]:nth-of-type(8) { border-color: #8b4bff; }
    .time {
        font-size: 48px !important;
        font-weight: 700 !important;
        color: #ec5953 !important;
        text-align: center;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.title("📚 Thesis Manager/Tracker 🎓")

# Sidebar navigation
pages = [
    "Home 🏠",
    "To-Do List 📋",
    "Tasks and Reports 📝",
    "Progress 📊",
    "Statistics 📈",
    "Manage Categories 🏷️",
    "Gantt Chart 📅",
    "Export/Import 💾",
]
col1, col2 = st.sidebar.columns(2)
for i, page in enumerate(pages):
    if i % 2 == 0:
        if col1.button(page, key=f"nav_{page}", use_container_width=True):
            st.session_state.page = page
    else:
        if col2.button(page, key=f"nav_{page}", use_container_width=True):
            st.session_state.page = page


# Timer function
async def run_timer(placeholder, duration, is_break=False):
    end_time = datetime.now() + timedelta(minutes=duration)
    while datetime.now() < end_time and st.session_state.timer_running:
        remaining = end_time - datetime.now()
        mins, secs = divmod(remaining.seconds, 60)
        placeholder.markdown(
            f'<p class="time">{mins:02d}:{secs:02d}</p>', unsafe_allow_html=True
        )
        await asyncio.sleep(1)

    if datetime.now() >= end_time:
        placeholder.markdown('<p class="time">00:00</p>', unsafe_allow_html=True)
        st.balloons()
        st.audio("https://www.soundjay.com/buttons/sounds/button-3.mp3", start_time=0)
        if not is_break:
            st.session_state.page = "Tasks and Reports 📝"
            st.rerun()
        else:
            st.session_state.timer_running = False
            st.rerun()


# Sidebar timer
st.sidebar.markdown("---")
st.sidebar.subheader("Work Timer")

if "timer_running" not in st.session_state:
    st.session_state.timer_running = False

timer_placeholder = st.sidebar.empty()

col1, col2 = st.sidebar.columns(2)
if col1.button("Start/Stop", key="sidebar_timer_startstop"):
    st.session_state.timer_running = not st.session_state.timer_running
    if st.session_state.timer_running:
        asyncio.run(run_timer(timer_placeholder, 25))  # 25-minute work session
    st.rerun()

if col2.button("Reset", key="sidebar_timer_reset"):
    st.session_state.timer_running = False
    timer_placeholder.markdown('<p class="time">25:00</p>', unsafe_allow_html=True)
    st.rerun()

# Display current to-do list in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("Current To-Do List")
for task in st.session_state.data["todo"]:
    st.sidebar.write(
        f"{PRIORITY_EMOJIS[task['priority']]} {task['name']} (Due: {task['due_date']})"
    )

# Main content
if "page" not in st.session_state:
    st.session_state.page = "Home 🏠"

if st.session_state.page == "Home 🏠":
    st.header("Welcome to the Thesis Manager/Tracker 🎓")

    st.subheader("Why This App Exists")
    st.write(
        """
    I created this Thesis Manager/Tracker for two main reasons:
    1. **Productive Procrastination**: Let's face it, sometimes we need a break from actual thesis writing. 
       What better way to procrastinate than by building a tool to manage your thesis? 😉
    2. **Genuine Productivity Boost**: Despite its origins, this app has become an invaluable tool for managing 
       my thesis progress, keeping track of tasks, and maintaining focus during work sessions.
    """
    )

    st.subheader("How to Use This App")
    st.write(
        """
    1. **To-Do List 📋**: Add and manage your thesis tasks. Break them down into steps, set priorities, and track progress.
    2. **Tasks and Reports 📝**: Log your work sessions and keep detailed reports of your progress.
    3. **Progress 📊**: Visualize your overall thesis progress across different sections.
    4. **Statistics 📈**: Analyze your productivity trends and time allocation.
    5. **Manage Categories 🏷️**: Customize categories to fit your thesis structure.
    6. **Gantt Chart 📅**: Get a timeline view of your tasks and deadlines.
    7. **Export/Import 💾**: Backup your data or transfer it between devices.
    """
    )

    st.subheader("Tips and Tricks")
    st.write(
        """
    - **Use the Work Timer**: Work in focused 25-minute sessions with short breaks in between.
    - **Regular Updates**: Keep your task list and progress up to date for better motivation.
    - **Analyze Your Stats**: Use the Statistics page to understand your productivity patterns.
    - **Break Down Tasks**: Use the steps feature in tasks to make large chunks of work more manageable.
    - **Celebrate Progress**: Don't forget to acknowledge your achievements, no matter how small!
    """
    )

    st.subheader("About the Developer")
    st.write(
        """
    This app was developed by [Your Name] as a side project while working on a thesis in [Your Field].
    If you're interested in the code or want to contribute, check out the project on GitHub:
    """
    )
    st.markdown("[GitHub Repository](https://github.com/yourusername/thesis-manager)")

    st.subheader("Feedback and Contributions")
    st.write(
        """
    Found a bug? Have a feature request? Feel free to open an issue or submit a pull request on GitHub.
    Your feedback and contributions are welcome!
    """
    )

    st.markdown("---")
    st.write("Now, let's get back to that thesis! 💪📚")

elif st.session_state.page == "To-Do List 📋":
    st.header("To-Do List 📋")

    # Add new task
    with st.form("new_todo"):
        st.subheader("Add New Task ✅")
        task_name = st.text_input("Task Name")
        category = st.selectbox(
            "Category",
            [
                f"{CATEGORY_EMOJIS[cat]} {cat}"
                for cat in st.session_state.data["categories"]
            ],
        )
        category = category.split(" ", 1)[1]
        priority = st.selectbox("Priority", list(PRIORITY_EMOJIS.keys()))
        due_date = st.date_input("Due Date")
        estimated_time = st.number_input(
            "Estimated Time (hours)", min_value=0.0, step=0.5
        )
        steps = st.text_area("Steps (one per line)")
        tags = st.multiselect(
            "Tags", options=st.session_state.data["tags"] + ["Add new tag..."]
        )
        if "Add new tag..." in tags:
            new_tag = st.text_input("New Tag")
            if new_tag and new_tag not in st.session_state.data["tags"]:
                st.session_state.data["tags"].append(new_tag)
                tags = [tag for tag in tags if tag != "Add new tag..."] + [new_tag]

        submitted = st.form_submit_button("Add Task")
        if submitted and task_name:
            new_task = {
                "name": task_name,
                "category": category,
                "priority": priority,
                "due_date": due_date,
                "estimated_time": estimated_time,
                "steps": [
                    {"step": step.strip(), "completed": False}
                    for step in steps.split("\n")
                    if step.strip()
                ],
                "tags": tags,
                "completed": False,
                "actual_time": 0,
                "notes": "",
            }
            st.session_state.data["todo"].append(new_task)
            if task_name not in st.session_state.data["tasks"]:
                st.session_state.data["tasks"].append(task_name)
            save_data(st.session_state.data)
            st.success(f"Task '{task_name}' added successfully! 🎉")

    # Display and manage tasks
    st.subheader("Current Tasks")

    # Filtering and sorting options
    filter_category = st.multiselect(
        "Filter by Category", options=st.session_state.data["categories"]
    )
    filter_priority = st.multiselect(
        "Filter by Priority", options=list(PRIORITY_EMOJIS.keys())
    )
    filter_tags = st.multiselect(
        "Filter by Tags", options=st.session_state.data["tags"]
    )
    sort_by = st.selectbox(
        "Sort by", options=["Due Date", "Priority", "Estimated Time"]
    )

    filtered_tasks = st.session_state.data["todo"]
    if filter_category:
        filtered_tasks = [
            task for task in filtered_tasks if task["category"] in filter_category
        ]
    if filter_priority:
        filtered_tasks = [
            task for task in filtered_tasks if task["priority"] in filter_priority
        ]
    if filter_tags:
        filtered_tasks = [
            task
            for task in filtered_tasks
            if any(tag in task["tags"] for tag in filter_tags)
        ]

    if sort_by == "Due Date":
        filtered_tasks.sort(key=lambda x: x["due_date"])
    elif sort_by == "Priority":
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        filtered_tasks.sort(key=lambda x: priority_order[x["priority"]])
    elif sort_by == "Estimated Time":
        filtered_tasks.sort(key=lambda x: x["estimated_time"], reverse=True)

    for i, task in enumerate(filtered_tasks):
        col1, col2, col3 = st.columns([0.5, 4, 0.5])
        with col1:
            completed = st.checkbox(
                "Complete", value=task["completed"], key=f"todo_{i}"
            )
        with col2:
            expander = st.expander(
                f"{PRIORITY_EMOJIS[task['priority']]} {CATEGORY_EMOJIS[task['category']]} {task['name']} "
                f"(Due: {task['due_date']})",
                expanded=True,
            )
            with expander:
                st.write(f"Estimated Time: {task['estimated_time']} hours")
                st.write(f"Actual Time: {task['actual_time']} hours")
                st.write("Steps:")
                for j, step in enumerate(task["steps"]):
                    step_completed = st.checkbox(
                        step["step"], step["completed"], key=f"step_{i}_{j}"
                    )
                    if step_completed != step["completed"]:
                        st.session_state.data["todo"][
                            st.session_state.data["todo"].index(task)
                        ]["steps"][j]["completed"] = step_completed
                        save_data(st.session_state.data)
                st.write(f"Tags: {', '.join(task['tags'])}")
                notes = st.text_area("Notes", task["notes"], key=f"notes_{i}")
                if notes != task["notes"]:
                    st.session_state.data["todo"][
                        st.session_state.data["todo"].index(task)
                    ]["notes"] = notes
                    save_data(st.session_state.data)
        with col3:
            if st.button("Delete", key=f"delete_todo_{i}"):
                st.session_state.data["todo"].remove(task)
                save_data(st.session_state.data)
                st.rerun()

        if completed != task["completed"]:
            st.session_state.data["todo"][st.session_state.data["todo"].index(task)][
                "completed"
            ] = completed
            if completed:
                # Create a report when task is completed
                st.session_state.data["reports"].append(
                    {
                        "date": datetime.now(),
                        "category": task["category"],
                        "task": task["name"],
                        "time_spent": task["actual_time"],
                        "result_rating": 5,  # Default value, can be adjusted
                        "focus_rating": 5,  # Default value, can be adjusted
                        "note": f"Task completed: {task['name']}",
                    }
                )
            save_data(st.session_state.data)
            st.rerun()

elif st.session_state.page == "Tasks and Reports 📝":
    st.header("Tasks and Reports 📝")

    # Add new report
    with st.form("new_report"):
        st.subheader("Add New Report ✍️")
        category = st.selectbox(
            "Category",
            [
                f"{CATEGORY_EMOJIS[cat]} {cat}"
                for cat in st.session_state.data["categories"]
            ],
        )
        category = category.split(" ", 1)[1]  # Remove emoji from category
        task = st.selectbox(
            "Task",
            ["New task..."]
            + st.session_state.data["tasks"]
            + [t["name"] for t in st.session_state.data["todo"]],
        )
        if task == "New task...":
            task = st.text_input("New task")
        time_spent = st.number_input("Time spent (hours) ⏱️", min_value=0.0, step=0.5)
        result_rating = st.slider("Result rating ⭐", 0, 5, 3)
        focus_rating = st.slider("Focus rating 🎯", 0, 5, 3)
        note = st.text_area("Notes 📌")
        submitted = st.form_submit_button("Submit Report 📤")
        if submitted:
            if task not in st.session_state.data["tasks"]:
                st.session_state.data["tasks"].append(task)
            st.session_state.data["reports"].append(
                {
                    "date": datetime.now(),
                    "category": category,
                    "task": task,
                    "time_spent": time_spent,
                    "result_rating": result_rating,
                    "focus_rating": focus_rating,
                    "note": note,
                }
            )
            # Update actual time for the corresponding todo item
            for todo_item in st.session_state.data["todo"]:
                if todo_item["name"] == task:
                    todo_item["actual_time"] += time_spent
                    break
            save_data(st.session_state.data)
            st.success("Report added successfully! 🎉")

    # Display reports
    st.subheader("Reports 📋")
    reports = sorted(
        st.session_state.data["reports"],
        key=lambda x: (
            x["date"]
            if isinstance(x["date"], datetime)
            else datetime.fromisoformat(x["date"])
        ),
        reverse=True,
    )

    # Group reports by week
    week_reports = {}
    for report in reports:
        report_date = (
            report["date"]
            if isinstance(report["date"], datetime)
            else datetime.fromisoformat(report["date"])
        )
        week_start = (report_date - timedelta(days=report_date.weekday())).date()
        if week_start not in week_reports:
            week_reports[week_start] = []
        week_reports[week_start].append(report)

    for week_start, week_data in week_reports.items():
        with st.expander(f"Week of {week_start} 📅"):
            for i, report in enumerate(week_data):
                report_date = (
                    report["date"]
                    if isinstance(report["date"], datetime)
                    else datetime.fromisoformat(report["date"])
                )
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.write(
                        f"**{report_date.strftime('%Y-%m-%d %H:%M')}** - {CATEGORY_EMOJIS[report['category']]} {report['category']}: {report['task']}"
                    )
                    st.write(f"⏱️ Time spent: {report['time_spent']} hours")
                    st.write(f"⭐ Result rating: {'⭐' * report['result_rating']}")
                    st.write(f"🎯 Focus rating: {'🎯' * report['focus_rating']}")
                    st.write(f"📌 Note: {report['note']}")
                with col2:
                    if st.button("Delete 🗑️", key=f"delete_{week_start}_{i}"):
                        st.session_state.data["reports"].remove(report)
                        save_data(st.session_state.data)
                        st.rerun()
                st.write("---")

elif st.session_state.page == "Progress 📊":
    st.header("Thesis Progress 📊")

    sections = [
        "Introduction",
        "Literature Review",
        "Methodology",
        "Results",
        "Discussion",
        "Conclusion",
    ]
    colors = ["#FF9999", "#66B2FF", "#99FF99", "#FFCC99", "#FF99CC", "#99CCFF"]

    # Circle diagram
    values = [st.session_state.data["progress"].get(section, 0) for section in sections]
    fig = go.Figure(
        data=[
            go.Pie(
                labels=[f"{CATEGORY_EMOJIS[s]} {s}" for s in sections],
                values=values,
                hole=0.3,
                marker_colors=colors,
            )
        ]
    )
    fig.update_layout(title_text="Overall Progress")
    st.plotly_chart(fig)

    # Progress bars
    for section in sections:
        st.write(f"{CATEGORY_EMOJIS[section]} **{section}**")
        progress = st.slider(
            f"{section} Progress",
            0,
            100,
            st.session_state.data["progress"].get(section, 0),
            key=section,
        )
        st.progress(progress)
        st.session_state.data["progress"][section] = progress

    save_data(st.session_state.data)

elif st.session_state.page == "Statistics 📈":
    st.header("Statistics 📈")

    reports = st.session_state.data["reports"]

    if reports:
        # Time spent over time
        df_time = pd.DataFrame(
            [
                (
                    (
                        datetime.fromisoformat(r["date"]).date()
                        if isinstance(r["date"], str)
                        else r["date"].date()
                    ),
                    r["time_spent"],
                )
                for r in reports
            ],
            columns=["Date", "Time Spent"],
        )
        df_time = df_time.groupby("Date").sum().reset_index()
        st.subheader("Time Spent Over Time ⏱️")
        st.line_chart(df_time.set_index("Date"))

        # Average ratings over time
        df_ratings = pd.DataFrame(
            [
                (
                    (
                        datetime.fromisoformat(r["date"]).date()
                        if isinstance(r["date"], str)
                        else r["date"].date()
                    ),
                    r["result_rating"],
                    r["focus_rating"],
                )
                for r in reports
            ],
            columns=["Date", "Result Rating", "Focus Rating"],
        )
        df_ratings = df_ratings.groupby("Date").mean().reset_index()
        st.subheader("Average Ratings Over Time 📊")
        st.line_chart(df_ratings.set_index("Date"))

        # Total time spent
        total_time = sum(r["time_spent"] for r in reports)
        st.subheader(f"Total Time Spent: {total_time:.1f} hours ⌛")

        # Average ratings
        avg_result = sum(r["result_rating"] for r in reports) / len(reports)
        avg_focus = sum(r["focus_rating"] for r in reports) / len(reports)
        st.subheader(f"Average Result Rating: {avg_result:.2f} ⭐")
        st.subheader(f"Average Focus Rating: {avg_focus:.2f} 🎯")

        # Time spent by category
        df_category = pd.DataFrame(
            [(r["category"], r["time_spent"]) for r in reports],
            columns=["Category", "Time Spent"],
        )
        df_category = df_category.groupby("Category").sum().reset_index()
        st.subheader("Time Spent by Category")
        fig = px.pie(
            df_category,
            values="Time Spent",
            names="Category",
            title="Time Distribution Across Categories",
        )
        st.plotly_chart(fig)

        # Productivity score over time (combination of result and focus ratings)
        df_productivity = pd.DataFrame(
            [
                (
                    (
                        datetime.fromisoformat(r["date"]).date()
                        if isinstance(r["date"], str)
                        else r["date"].date()
                    ),
                    (r["result_rating"] + r["focus_rating"]) / 2,
                )
                for r in reports
            ],
            columns=["Date", "Productivity Score"],
        )
        df_productivity = df_productivity.groupby("Date").mean().reset_index()
        st.subheader("Productivity Score Over Time")
        st.line_chart(df_productivity.set_index("Date"))
    else:
        st.write("No reports available yet. Add some reports to see statistics. 📊")

elif st.session_state.page == "Manage Categories 🏷️":
    st.header("Manage Categories 🏷️")

    # Display current categories
    st.subheader("Current Categories 📂")
    for category in st.session_state.data["categories"]:
        st.write(f"{CATEGORY_EMOJIS.get(category, '🔹')} {category}")

    # Add new category
    new_category = st.text_input("New Category 🆕")
    if st.button("Add Category ➕"):
        if new_category and new_category not in st.session_state.data["categories"]:
            st.session_state.data["categories"].append(new_category)
            save_data(st.session_state.data)
            st.success(f"Added new category: {new_category} 🎉")
        else:
            st.error("Please enter a unique category name. ❌")

    # Remove category
    category_to_remove = st.selectbox(
        "Select Category to Remove", st.session_state.data["categories"]
    )
    if st.button("Remove Category ➖"):
        if category_to_remove in st.session_state.data["categories"]:
            st.session_state.data["categories"].remove(category_to_remove)
            save_data(st.session_state.data)
            st.success(f"Removed category: {category_to_remove} 🗑️")
        else:
            st.error("Category not found. ❌")

elif st.session_state.page == "Gantt Chart 📅":
    st.header("Gantt Chart 📅")

    tasks = st.session_state.data["todo"]
    if tasks:
        df = pd.DataFrame(
            [
                dict(
                    Task=task["name"],
                    Start=task["due_date"]
                    - timedelta(days=int(task["estimated_time"] / 8)),
                    Finish=task["due_date"],
                    Resource=task["category"],
                )
                for task in tasks
            ]
        )

        fig = px.timeline(
            df, x_start="Start", x_end="Finish", y="Task", color="Resource"
        )
        fig.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig)
    else:
        st.write("No tasks available to display in the Gantt chart.")

elif st.session_state.page == "Export/Import 💾":
    st.header("Export/Import Data 💾")

    # Export data
    if st.button("Export Data"):
        json_string = json.dumps(st.session_state.data, default=str, indent=4)
        st.download_button(
            label="Download JSON",
            file_name="thesis_data.json",
            mime="application/json",
            data=json_string,
        )
        st.success(
            "Data exported successfully! Click the 'Download JSON' button to save the file."
        )

    # Import data
    uploaded_file = st.file_uploader("Choose a JSON file to import", type="json")
    if uploaded_file is not None:
        try:
            imported_data = json.load(uploaded_file)
            if st.button("Import Data"):
                st.session_state.data = imported_data
                save_data(st.session_state.data)
                st.success("Data imported successfully!")
                st.rerun()
        except json.JSONDecodeError:
            st.error("Invalid JSON file. Please upload a valid thesis_data.json file.")

st.sidebar.markdown("---")
st.sidebar.write("Remember to take breaks and stay hydrated! 💧☕")