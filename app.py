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

# Grade Distribution
st.header("Grade Distribution")
st.pyplot(analyzer.plot_grade_distribution(group_by="subject"))
st.pyplot(analyzer.plot_grade_distribution(group_by="semester"))

# Attendance vs Performance
st.header("Attendance vs Performance")
st.pyplot(analyzer.plot_attendance_vs_performance())

# At-Risk Students
st.header("At-Risk Students")
at_risk_df = analyzer.detect_at_risk(grade_threshold, attendance_threshold)
st.write(f"Total At-Risk Students: {len(at_risk_df)}")
st.dataframe(at_risk_df[["school","sex","age","G3_math","G3_por","attendance_rate","avg_grade"]])
st.pyplot(analyzer.plot_at_risk(grade_threshold, attendance_threshold))

# School Comparison
st.header("Compare Performance Between Schools")
st.pyplot(analyzer.plot_school_comparison())

# Trends
st.header("Performance Trends Over Semesters")
st.pyplot(analyzer.plot_performance_trends())
