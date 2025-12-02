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
    x=filtered["attendance_rate"],
    y=(filtered["G3_math"] + filtered["G3_por"]) / 2,
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


#Grade Distribution by Class, Subject, or Semester
st.header("📘 Grade Distribution by Class, Subject, or Semester")

group_option = st.selectbox(
    "Group by:",
    ["school", "sex", "age", "reason", "guardian", "semester (G1/G2/G3)"]
)

fig, ax = plt.subplots(figsize=(10, 5))

if group_option == "semester (G1/G2/G3)":
    sns.histplot(filtered["G1_math"], kde=True, color="blue", label="G1 Math", ax=ax)
    sns.histplot(filtered["G2_math"], kde=True, color="green", label="G2 Math", ax=ax)
    sns.histplot(filtered["G3_math"], kde=True, color="red", label="G3 Math", ax=ax)
else:
    sns.histplot(filtered["G3_math"], kde=True, color="blue", label="Math", ax=ax)
    sns.histplot(filtered["G3_por"], kde=True, color="orange", label="Portuguese", ax=ax)

plt.legend()
st.pyplot(fig)


#Attendance vs Student Performance
st.header("Attendance vs Student Performance")

filtered["avg_grade"] = (filtered["G3_math"] + filtered["G3_por"]) / 2

fig, ax = plt.subplots(figsize=(8, 5))
sns.regplot(
    x=filtered["attendance_rate"],
    y=filtered["avg_grade"],
    scatter_kws={"alpha": 0.5},
    line_kws={"color": "red"},
    ax=ax
)

ax.set_xlabel("Attendance Rate")
ax.set_ylabel("Average Final Grade")
ax.set_title("Correlation Between Attendance and Performance")

st.pyplot(fig)

corr_value = filtered["attendance_rate"].corr(filtered["avg_grade"])
st.metric("Correlation Coefficient", f"{corr_value:.2f}")


#Students At Risk of Failing or Dropping Out
st.header("Students At Risk of Failing or Dropping Out")

at_risk_df = analyzer.detect_at_risk()

st.write(f"Total At-Risk Students: {len(at_risk_df)}")
st.dataframe(at_risk_df[["school", "sex", "age", "G3_math", "G3_por", "attendance_rate"]])

fig, ax = plt.subplots(figsize=(8, 5))
sns.scatterplot(
    data=at_risk_df,
    x="attendance_rate",
    y="avg_grade",
    hue="school",
    ax=ax
)
ax.set_title("At-Risk Students: Attendance vs Grade")
st.pyplot(fig)

#Performance Comparison Between Schools
st.header("Compare Performance Between Schools")

school_perf = (
    merged_df.groupby("school")[["G3_math", "G3_por"]]
    .mean()
    .reset_index()
)

fig, ax = plt.subplots(figsize=(10, 5))
school_perf.plot(
    x="school",
    y=["G3_math", "G3_por"],
    kind="bar",
    ax=ax
)

ax.set_ylabel("Average Final Grade")
ax.set_title("Average Performance by School")
plt.xticks(rotation=45)
st.pyplot(fig)

#Trends Over Semesters
st.header("Performance Trends Over Semesters")

trend_df = pd.DataFrame({
    "Semester": ["G1", "G2", "G3"],
    "Math": [
        merged_df["G1_math"].mean(),
        merged_df["G2_math"].mean(),
        merged_df["G3_math"].mean()
    ],
    "Portuguese": [
        merged_df["G1_por"].mean(),
        merged_df["G2_por"].mean(),
        merged_df["G3_por"].mean()
    ]
})

fig, ax = plt.subplots(figsize=(8, 5))
sns.lineplot(data=trend_df, x="Semester", y="Math", marker="o", ax=ax)
sns.lineplot(data=trend_df, x="Semester", y="Portuguese", marker="o", ax=ax)

ax.set_title("Performance Trends Across Semesters")
ax.set_ylabel("Average Grade")
st.pyplot(fig)
