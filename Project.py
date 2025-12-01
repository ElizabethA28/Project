import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


class StudentAnalyzer:
    def __init__(self, math_df, por_df, attendance_df):
        self.math_df = math_df.copy()
        self.por_df = por_df.copy()
        self.attendance_df = attendance_df.copy()
        self.merged_df = None

    # ---------------------------------------------------------
    # 1. CLEANING
    # ---------------------------------------------------------
    def clean_data(self):
        # Convert numeric columns
        numeric_cols = ["G1", "G2", "G3", "absences"]
        for df in [self.math_df, self.por_df]:
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Clean attendance
        self.attendance_df["attendance_rate"] = (
            self.attendance_df["Present"] / self.attendance_df["Enrolled"]
        )

        # Map DBN → UCI school codes
        school_map = {
            "01M015": "GP",
            "01M019": "MS"
        }
        self.attendance_df["school"] = self.attendance_df["School DBN"].map(school_map)

        # Aggregate attendance by school
        self.school_attendance = (
            self.attendance_df.groupby("school")["attendance_rate"]
            .mean()
            .reset_index()
        )

    # ---------------------------------------------------------
    # 2. MERGING
    # ---------------------------------------------------------
    def merge_data(self):
        # Merge math + Portuguese on student attributes
        merge_keys = [
            "school", "sex", "age", "address", "famsize", "Pstatus",
            "Medu", "Fedu", "Mjob", "Fjob", "reason", "guardian"
        ]

        merged = pd.merge(
            self.math_df,
            self.por_df,
            on=merge_keys,
            suffixes=("_math", "_por"),
            how="inner"
        )

        # Merge attendance
        merged = merged.merge(self.school_attendance, on="school", how="left")

        self.merged_df = merged
        return merged

    # ---------------------------------------------------------
    # 3. AT-RISK DETECTION
    # ---------------------------------------------------------
    def detect_at_risk(self, grade_threshold=10, attendance_threshold=0.90):
        df = self.merged_df.copy()
        df["avg_grade"] = (df["G3_math"] + df["G3_por"]) / 2

        df["at_risk"] = (
            (df["avg_grade"] < grade_threshold) |
            (df["attendance_rate"] < attendance_threshold)
        )

        return df[df["at_risk"] == True]

    # ---------------------------------------------------------
    # 4. SUMMARY STATISTICS
    # ---------------------------------------------------------
    def grade_summary(self):
        return self.merged_df[["G3_math", "G3_por"]].describe()

    def attendance_summary(self):
        return self.school_attendance
    


    def clean_data(self):
        # Convert grade columns to numeric
        grade_cols = ["G1_x", "G2_x", "G3_x", "G1_y", "G2_y", "G3_y"]
        for col in grade_cols:
            if col in self.merged_df.columns:
                self.merged_df[col] = pd.to_numeric(self.merged_df[col], errors="coerce")

        # Convert attendance date
        self.attendance_df["Date"] = pd.to_datetime(self.attendance_df["Date"], format="%Y%m%d")

        # Compute attendance rate
        self.attendance_df["AttendanceRate"] = (
            self.attendance_df["Present"] / self.attendance_df["Enrolled"]
        )

    def heatmap_by_school(self, school_name):
        df = self.merged_df[self.merged_df["school"] == school_name]
        corr = df.select_dtypes(include="number").corr()

        plt.figure(figsize=(10, 6))
        sns.heatmap(corr, annot=False, cmap="coolwarm")
        plt.title(f"Correlation Heatmap – {school_name}")
        plt.tight_layout()
        return plt

    def heatmap_math_vs_por(self):
        cols = ["G1_x", "G2_x", "G3_x", "G1_y", "G2_y", "G3_y"]
        df = self.merged_df[cols]
        corr = df.corr()

        plt.figure(figsize=(8, 6))
        sns.heatmap(corr, annot=True, cmap="viridis")
        plt.title("Math vs Portuguese Grade Correlation")
        plt.tight_layout()
        return plt

    def attendance_heatmap(self):
        df = self.attendance_df.copy()
        df["Month"] = df["Date"].dt.month
        df["Day"] = df["Date"].dt.day

        pivot = df.pivot_table(
            index="Month",
            columns="Day",
            values="AttendanceRate"
        )

        plt.figure(figsize=(14, 6))
        sns.heatmap(pivot, cmap="YlGnBu")
        plt.title("Attendance Rate Heatmap Over Time")
        plt.tight_layout()
        return plt




