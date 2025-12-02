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
        self.school_attendance = None

    
    #CLEANING

    def clean_data(self):
        # Clean math + Portuguese numeric columns
        numeric_cols = ["G1", "G2", "G3", "absences"]
        for df in [self.math_df, self.por_df]:
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            # Ensure school codes are uppercase (GP, MS)
            if "school" in df.columns:
                df["school"] = df["school"].str.upper()

        #CLEAN ATTENDANCE DATASET
        # Convert date column
        if "Date" in self.attendance_df.columns:
            self.attendance_df["Date"] = pd.to_datetime(
                self.attendance_df["Date"], errors="coerce"
            )

        # Convert Present/Enrolled if Status column exists
        if "Status" in self.attendance_df.columns:
            self.attendance_df["Present"] = (
                self.attendance_df["Status"].str.lower() == "present"
            ).astype(int)
            self.attendance_df["Enrolled"] = 1

        # Compute attendance rate
        self.attendance_df["attendance_rate"] = (
            self.attendance_df["Present"] / self.attendance_df["Enrolled"]
        )

        # Map DBN → school names
        school_map = {
            "01M015": "Winners High School",
            "01M019": "Marks High School",
            "01M020": "Liberty High School",
            "01M034": "Central High School",
            "01M063": "Unity High School",
            "02M531": "Harmony High School"
        }

        if "School DBN" in self.attendance_df.columns:
            self.attendance_df["school"] = (
                self.attendance_df["School DBN"].map(school_map)
            )
        plot_df = filtered.dropna(subset=["attendance_rate", "G3_math", "G3_por"])


        # Aggregate attendance by school
        self.school_attendance = (
            self.attendance_df.groupby("school")["attendance_rate"]
            .mean()
            .reset_index()
        )

    #MERGING
    def merge_data(self):
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

        # Warn if merge failed
        if merged.empty:
            print("Warning: merge produced an empty dataset")

        self.merged_df = merged
        return merged

    # 3AT-RISK DETECTION
    def detect_at_risk(self, grade_threshold=10, attendance_threshold=0.90):
        df = self.merged_df.copy()
        df["avg_grade"] = (df["G3_math"] + df["G3_por"]) / 2

        df["at_risk"] = (
            (df["avg_grade"] < grade_threshold) |
            (df["attendance_rate"] < attendance_threshold)
        )

        return df[df["at_risk"] == True]

    #SUMMARY STATISTICS
    def grade_summary(self):
        return self.merged_df[["G3_math", "G3_por"]].describe()

    def attendance_summary(self):
        return self.school_attendance

    #HEATMAPS
    def heatmap_by_school(self, school_name):
        df = self.merged_df[self.merged_df["school"] == school_name]
        df = df.select_dtypes(include="number")

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(df.corr(), annot=False, cmap="coolwarm", ax=ax)
        ax.set_title(f"Correlation Heatmap – {school_name}")
        fig.tight_layout()
        return fig

    def heatmap_math_vs_por(self):
        cols = ["G1_math", "G2_math", "G3_math", "G1_por", "G2_por", "G3_por"]
        df = self.merged_df[cols].dropna()

        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(df.corr(), annot=True, cmap="viridis", ax=ax)
        ax.set_title("Math vs Portuguese Grade Correlation")
        fig.tight_layout()
        return fig

    def attendance_heatmap(self):
        df = self.attendance_df.copy()

        if "Date" in df.columns:
            df["Month"] = df["Date"].dt.month
            df["Day"] = df["Date"].dt.day

        pivot = df.pivot_table(
            index="Month",
            columns="Day",
            values="attendance_rate"
        )

        fig, ax = plt.subplots(figsize=(14, 6))
        sns.heatmap(pivot, cmap="YlGnBu", ax=ax)
        ax.set_title("Attendance Rate Heatmap Over Time")
        fig.tight_layout()
        return fig
