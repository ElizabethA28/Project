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
        # Ensure numeric grades
        for df in [self.math_df, self.por_df]:
            for col in ["G1","G2","G3","absences"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            if "school" in df.columns:
                df["school"] = df["school"].str.upper()

        # Rename grade columns to distinguish subjects
        self.math_df = self.math_df.rename(columns={"G1":"G1_math","G2":"G2_math","G3":"G3_math"})
        self.por_df  = self.por_df.rename(columns={"G1":"G1_por","G2":"G2_por","G3":"G3_por"})

        # Attendance cleaning
        if "Date" in self.attendance_df.columns:
            self.attendance_df["Date"] = pd.to_datetime(self.attendance_df["Date"], errors="coerce")
        if "Present" in self.attendance_df.columns and "Enrolled" in self.attendance_df.columns:
            self.attendance_df["attendance_rate"] = self.attendance_df["Present"] / self.attendance_df["Enrolled"]

        # Aggregate attendance by school
        if "school" in self.attendance_df.columns and "attendance_rate" in self.attendance_df.columns:
            self.school_attendance = (
                self.attendance_df.groupby("school")["attendance_rate"].mean().reset_index()
            )

    # MERGING
    def merge_data(self):
        merge_keys = ["school","sex","age","address","famsize","Pstatus","Medu","Fedu","Mjob","Fjob","reason","guardian"]
        merged = pd.merge(self.math_df, self.por_df, on=merge_keys, suffixes=("_math","_por"), how="inner")

        if self.school_attendance is not None:
            merged = merged.merge(self.school_attendance, on="school", how="left")

        # Derived columns
        merged["avg_grade"] = merged[["G3_math","G3_por"]].mean(axis=1)

        # Guarantee attendance_rate exists
        if "attendance_rate" not in merged.columns:
            if "absences" in merged.columns:
                merged["attendance_rate"] = 1 - (merged["absences"] / merged["absences"].max())
            else:
                merged["attendance_rate"] = 1.0
        
        # Create a combined absences column
        if "absences_math" in merged.columns and "absences_por" in merged.columns:
            merged["total_absences"] = merged[["absences_math","absences_por"]].mean(axis=1)
        elif "absences" in merged.columns:
            merged["total_absences"] = merged["absences"]
        else:
            merged["total_absences"] = 0

        self.merged_df = merged
        return merged

    
    #Grade Distribution
    def plot_grade_distribution(self, group_by="subject"):
        df = self.merged_df.copy()
        fig, ax = plt.subplots(figsize=(8,5))

        if group_by == "subject":
            # Compute average final grade per subject
            subject_means = {
                "Math": df["G3_math"].mean(),
                "Portuguese": df["G3_por"].mean()
            }
            subjects = list(subject_means.keys())
            grades = list(subject_means.values())

            sns.barplot(x=subjects, y=grades, palette="Set2", ax=ax)
            ax.set_title("Average Final Grade by Subject")
            ax.set_ylabel("Average Grade")

        elif group_by == "semester":
            sem_avgs = df[[
            "G1_math","G2_math","G3_math",
            "G1_por","G2_por","G3_por"
            ]].melt(var_name="Semester", value_name="Grade")

            sns.barplot(data=sem_avgs, x="Semester", y="Grade", ci=None, palette="muted", ax=ax)
            ax.set_title("Average Grade by Semester")
            ax.set_ylabel("Average Grade")

        else:
            sns.histplot(df["avg_grade"], bins=20, kde=True, ax=ax)
            ax.set_title("Overall Grade Distribution")
            ax.set_xlabel("Average Grade")
            ax.set_ylabel("Number of Students")
        return fig

    # 2. Attendance correlation
    def plot_attendance_vs_performance(self):
        df = self.merged_df.copy()
        # Defensive check
        for col in ["attendance_rate","avg_grade","school"]:
            if col not in df.columns:
                raise ValueError(f"Required column '{col}' not found in merged_df")
        fig, ax = plt.subplots(figsize=(8,5))
        sns.scatterplot(data=df, x="attendance_rate", y="avg_grade", hue="school", ax=ax)
        sns.regplot(data=df, x="attendance_rate", y="avg_grade", scatter=False, ax=ax, color="black")
        ax.set_title("Attendance vs Performance")
        return fig

    # 3. At-risk students
    def detect_at_risk(self, grade_threshold=10, attendance_threshold=0.9):
        df = self.merged_df.copy()
        df["at_risk"] = (df["avg_grade"] < grade_threshold) | (df["attendance_rate"] < attendance_threshold)
        return df[df["at_risk"]]

    def plot_at_risk(self, grade_threshold=10, attendance_threshold=0.9):
        df = self.detect_at_risk(grade_threshold, attendance_threshold)
        fig, ax = plt.subplots(figsize=(8,5))
        sns.scatterplot(data=df, x="attendance_rate", y="avg_grade", hue="school", ax=ax)
        ax.set_title("At-Risk Students: Attendance vs Grade")
        return fig

    # 4. School comparison
    def plot_school_comparison(self):
        df = self.merged_df.groupby("school")[["G3_math","G3_por","avg_grade"]].mean().reset_index()
        fig, ax = plt.subplots(figsize=(10,6))
        df.plot(x="school", y=["G3_math","G3_por","avg_grade"], kind="bar", ax=ax)
        ax.set_ylabel("Average Grade")
        ax.set_title("Average Performance by School")
        plt.xticks(rotation=45)
        return fig

    # 5. Performance trends
    def plot_performance_trends(self):
        df = self.merged_df.copy()
        trend_df = pd.DataFrame({
            "Semester":["G1","G2","G3"],
            "Math":[df["G1_math"].mean(), df["G2_math"].mean(), df["G3_math"].mean()],
            "Portuguese":[df["G1_por"].mean(), df["G2_por"].mean(), df["G3_por"].mean()]
        })
        fig, ax = plt.subplots(figsize=(8,5))
        sns.lineplot(data=trend_df, x="Semester", y="Math", marker="o", ax=ax)
        sns.lineplot(data=trend_df, x="Semester", y="Portuguese", marker="o", ax=ax)
        ax.set_title("Performance Trends Across Semesters")
        ax.set_ylabel("Average Grade")
        return fig

    # Gender comparison
    def plot_gender_comparison(self):
        df = self.merged_df.copy()
        fig, ax = plt.subplots(figsize=(8,5))
        sns.barplot(data=df, x="sex", y="avg_grade", ci=None, ax=ax, palette="Set2")
        ax.set_title("Average Grade by Gender")
        ax.set_ylabel("Average Grade")
        return fig

    # Grade vs Age
    def plot_grade_vs_age(self):
        df = self.merged_df.copy()
        fig, ax = plt.subplots(figsize=(8,5))
        sns.boxplot(data=df, x="age", y="avg_grade", ax=ax, palette="coolwarm")
        ax.set_title("Grade Distribution by Age")
        ax.set_ylabel("Average Grade")
        return fig

#heatmap

