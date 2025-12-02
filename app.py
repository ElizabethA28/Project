import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from student_analyzer import StudentAnalyzer

st.title("📊 Student Performance & Attendance Dashboard")

# Load data (must exist in repo)
math_df = pd.read_csv("student-mat.csv", sep=";")
por_df = pd.read_csv("student-por.csv", sep=";")
attendance_df = pd.read_csv("attendance.csv")

st.sidebar.header("Data upload")

grades_file = st.sidebar.file_uploader("Upload Grades CSV", type=["csv"])
attendance_file = st.sidebar.file_uploader("Upload Attendance CSV", type=["csv"])

# Analyzer
analyzer = StudentAnalyzer(math_df, por_df, attendance_df)
analyzer.clean_data()
merged_df = analyzer.merge_data()

# Sidebar filters
school_filter = st.sidebar.selectbox("Select School", merged_df["school"].unique())
filtered = merged_df[merged_df["school"] == school_filter]

# Grade Distribution
st.header("Grade Distribution by Subject")
fig, ax = plt.subplots()
sns.histplot(filtered["G3_math"], kde=True, color="blue", label="Math", ax=ax)
sns.histplot(filtered["G3_por"], kde=True, color="orange", label="Portuguese", ax=ax)
plt.legend()
st.pyplot(fig)

# Attendance vs Performance
st.header("Attendance vs Performance")
fig, ax = plt.subplots()
sns.scatterplot(
    x=filtered["avg_attendance_rate"],
    y=(filtered["g3_math"] + filtered["g3_por"]) / 2,
    ax=ax
)
ax.set_xlabel("Average Attendance Rate")
ax.set_ylabel("Average Final Grade")
st.pyplot(fig)

# At-Risk Students
st.header("At-Risk Students")
at_risk = analyzer.detect_at_risk()
st.dataframe(at_risk)

# Heatmaps
st.header("🏫 Heatmap by School")
school_choice = st.selectbox("Select School", merged_df["school"].unique())
fig1 = analyzer.heatmap_by_school(school_choice)
st.pyplot(fig1)

st.header("📘 Math vs Portuguese Correlation")
fig2 = analyzer.heatmap_math_vs_por()
st.pyplot(fig2)

st.header("📅 Attendance Trend Heatmap")
fig3 = analyzer.attendance_heatmap()
st.pyplot(fig3)
