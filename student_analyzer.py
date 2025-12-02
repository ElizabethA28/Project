import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class StudentAnalyzer:
    def __init__(self, math_df, por_df, attendance_df):
        self.math_df = math_df.copy()
        self.por_df = por_df.copy()
        self.attendance_df = attendance_df.copy()
        self.merged_df = None
        self.school_attendance = None

    # CLEANING
    def clean_data(self):
        # Clean math + Portuguese numeric columns
        numeric_cols = ["G1", "G2", "G3", "absences"]
        for df in [self.math_df, self.por_df]:
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            if "school" in df.columns:
                df["school"] = df["school"].str.upper()

        # Attendance cleaning
        if "Date" in self.attendance_df.columns:
            self.attendance_df["Date"] = pd.to_datetime(
                self.attendance_df["Date"], errors="coerce"
            )

        if "Status" in self.attendance_df.columns:
            self.attendance_df["Present"] = (
                self.attendance_df["Status"].str.lower() == "present"
            ).astype(int)
            self.attendance_df["Enrolled"] = 1

        if "Present" in self.attendance_df.columns and "Enrolled" in self.attendance_df.columns:
            self.attendance_df["attendance_rate"] = (
                self.attendance_df["Present"] / self.attendance_df["Enrolled"]
            )

        # Aggregate attendance by school
        if "school" in self.attendance_df.columns and "attendance_rate" in self.attendance_df.columns:
            self.school_attendance = (
                self.attendance_df.groupby("school")["attendance_rate"]
                .mean()
                .reset_index()
            )

    # MERGING
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
        if self.school_attendance is not None:
            merged = merged.merge(self.school_attendance, on="school", how="left")

        # Derived columns
        merged["avg_grade"] = (merged["G3_math"] + merged["G3_por"]) / 2
        if "attendance_rate" not in merged.columns and "absences" in merged.columns:
            merged["attendance_rate"] = 1 - (merged["absences"] / merged["absences"].max())

        self.merged_df = merged
        return merged

    # AT-RISK DETECTION
    def detect_at_risk(self, grade_threshold=10, attendance_threshold=0.90):
        df = self.merged_df.copy()
        df["at_risk"] = (
            (df["avg_grade"] < grade_threshold) |
            (df["attendance_rate"] < attendance_threshold)
        )
        return df[df["at_risk"]]

    # SUMMARY
    def grade_summary(self):
        return self.merged_df[["G3_math", "G3_por", "avg_grade"]].describe()

    def attendance_summary(self):
        return self.school_attendance

    # HEATMAPS
    def heatmap_by_school(self, school_name):
        df = self.merged_df[self.merged_df["school"] == school_name]
        df = df.select_dtypes(include="number")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(df.corr(), annot=False, cmap="coolwarm", ax=ax)
        ax.set_title(f"Correlation Heatmap – {school_name}")
        return fig

    def heatmap_math_vs_por(self):
        cols = ["G1_math", "G2_math", "G3_math", "G1_por", "G2_por", "G3_por"]
        df = self.merged_df[cols].dropna()
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(df.corr(), annot=True, cmap="viridis", ax=ax)
        ax.set_title("Math vs Portuguese Grade Correlation")
        return fig

    def attendance_heatmap(self):
        df = self.attendance_df.copy()
        if "Date" in df.columns:
            df["Month"] = df["Date"].dt.month
            df["Day"] = df["Date"].dt.day
        if "attendance_rate" in df.columns:
            pivot = df.pivot_table(index="Month", columns="Day", values="attendance_rate")
            fig, ax = plt.subplots(figsize=(14, 6))
            sns.heatmap(pivot, cmap="YlGnBu", ax=ax)
            ax.set_title("Attendance Rate Heatmap Over Time")
            return fig
        else:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "No attendance_rate data available", ha="center")
            return fig
