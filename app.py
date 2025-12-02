import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from student_analyzer import StudentAnalyzer

st.title("📊 Student Performance & Attendance Dashboard")

# --- Load raw datasets ---
math_df = pd.read_csv("student-mat.csv", sep=";")
por_df = pd.read_csv("student-por.csv", sep=";")
attendance_df = pd.read_csv("attendance.csv")

# --- Instantiate analyzer with all three datasets ---
analyzer = StudentAnalyzer(math_df, por_df, attendance_df)
analyzer.clean_data()
merged_df = analyzer.merge_data()

# --- Sidebar filters ---
school_filter = st.sidebar.selectbox("Select School", merged_df["school"].unique())
grade_threshold = st.sidebar.slider("Grade Threshold", 0, 20, 10)
attendance_threshold = st.sidebar.slider("Attendance Threshold", 0.0, 1.0, 0.9)

# --- Filtered data ---
filtered = merged_df[merged_df["school"] == school_filter].copy()

# --- Grade Distribution ---
st.header("Grade Distribution by Subject")
fig, ax = plt.subplots()
sns.histplot(filtered["G3_math"], kde=True, color="blue", label="Math", ax=ax)
sns.histplot(filtered["G3_por"], kde=True, color="orange", label="Portuguese", ax=ax)
plt.legend()
st.pyplot(fig)

# --- Attendance vs Performance ---
st.header("Attendance vs Performance")
fig, ax = plt.subplots()
sns.scatterplot(data=filtered, x="attendance_rate", y="avg_grade", ax=ax)
ax.set_xlabel("Attendance Rate")
ax.set_ylabel("Average Final Grade")
st.pyplot(fig)

# --- At-Risk Students ---
st.header("At-Risk Students")
at_risk_df = analyzer.detect_at_risk(
    grade_threshold=grade_threshold,
    attendance_threshold=attendance_threshold
)
st.write(f"Total At-Risk Students: {len(at_risk_df)}")
st.dataframe(at_risk_df[["school","sex","age","G3_math","G3_por","attendance_rate","avg_grade"]])

# Download button
st.download_button(
    label="Download At-Risk Students as CSV",
    data=at_risk_df.to_csv(index=False),
    file_name="at_risk_students.csv",
    mime="text/csv"
)

fig, ax = plt.subplots()
sns.scatterplot(data=at_risk_df, x="attendance_rate", y="avg_grade", hue="school", ax=ax)
ax.set_title("At-Risk Students: Attendance vs Grade")
st.pyplot(fig)

# --- Performance Comparison Between Schools ---
st.header("Compare Performance Between Schools")
school_perf = merged_df.groupby("school")[["G3_math","G3_por"]].mean().reset_index()
fig, ax = plt.subplots()
school_perf.plot(x="school", y=["G3_math","G3_por"], kind="bar", ax=ax)
ax.set_ylabel("Average Final Grade")
ax.set_title("Average Performance by School")
plt.xticks(rotation=45)
st.pyplot(fig)

# --- Trends Over Semesters ---
st.header("Performance Trends Over Semesters")
trend_df = pd.DataFrame({
    "Semester":["G1","G2","G3"],
    "Math":[merged_df["G1_math"].mean(), merged_df["G2_math"].mean(), merged_df["G3_math"].mean()],
    "Portuguese":[merged_df["G1_por"].mean(), merged_df["G2_por"].mean(), merged_df["G3_por"].mean()]
})
fig, ax = plt.subplots()
sns.lineplot(data=trend_df, x="Semester", y="Math", marker="o", ax=ax)
sns.lineplot(data=trend_df, x="Semester", y="Portuguese", marker="o", ax=ax)
ax.set_title("Performance Trends Across Semesters")
ax.set_ylabel("Average Grade")
st.pyplot(fig)

# --- Heatmaps ---
st.header("Correlation Heatmap by School")
fig1 = analyzer.heatmap_by_school(school_filter)
st.pyplot(fig1)

st.header("Math vs Portuguese Grade Correlation")
fig2 = analyzer.heatmap_math_vs_por()
st.pyplot(fig2)

st.header("Attendance Trend Heatmap")
fig3 = analyzer.attendance_heatmap()
st.pyplot(fig3)
