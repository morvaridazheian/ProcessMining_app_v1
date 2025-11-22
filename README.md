# ProcessMining_App_v1

## 🔎 How This Code Works

This Dash web app provides Process Mining analysis using an uploaded CSV file or a generated sample event log. It detects bottlenecks, loops, process variants, and compliance issues in event logs.

    - Upload a CSV file, or use the sample data if no file is provided.
    - The app validates the data and processes it in four key analyses:
        1. Process Bottlenecks: Shows average time spent per activity.
        2. Process Loops: Detects repeated activities within cases.
        3. Process Variants: Identifies the most common activity sequences.
        4. Compliance Analysis: Checks if cases follow the expected sequence.

## 📁 CSV File Format

For correct processing, the CSV file must have these three columns:


    1. case_id: Unique identifier for each process instance.
    2. activity: Name of the activity performed.
    3. timestamp: Date & time when the activity happened (format: YYYY-MM-DD HH:MM:SS).

💡 Make sure the CSV follows this format for accurate analysis! 🚀

## 🌐 Live Deployment

This version is deployed on **Render**:

🔗 https://processmining-app-v1.onrender.com

---

## 🚀 Newer Version Available

A more complete and enhanced version is also available:

- **Repository:** `ProcessMining_App_v2`
  
  🔗 https://github.com/morvaridazheian/ProcessMining_app_v2  
- **Live Deployment:**
  
  🔗 https://processmining-app-v2.onrender.com

---
