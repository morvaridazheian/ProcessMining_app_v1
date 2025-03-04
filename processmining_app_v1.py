from datetime import datetime, timedelta  
import random
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, dash_table
from flask import Flask
import base64
import io
import os  # Added for dynamic port setting

# =============== Generate a Simple Event Log for Testing =============== #
def generate_sample_event_log():
    cases = [f"Case_{i}" for i in range(1, 6)]  # 5 cases
    activities = ["Start", "Review", "Approve", "End"]
    data = []

    for case in cases:
        start_time = datetime.now() - timedelta(days=random.randint(1, 30))
        for activity in activities:
            data.append({
                "case_id": case,
                "activity": activity,
                "timestamp": start_time.strftime("%Y-%m-%d %H:%M:%S")
            })
            start_time += timedelta(minutes=random.randint(5, 60))  # Random delay

    return pd.DataFrame(data)

# =============== Data Validation Function =============== #
def validate_data(df):
    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    except Exception as e:
        raise ValueError(f"Timestamp column conversion failed: {str(e)}")

    if df[['activity', 'case_id', 'timestamp']].isnull().any().any():
        raise ValueError("Missing values in required columns: 'activity', 'case_id', or 'timestamp'")

    return df

# =============== Decode File Function =============== #
def decode_file(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    return io.StringIO(decoded.decode('utf-8'))

# Generate sample event log
event_log = generate_sample_event_log()

# =============== Flask + Dash App Setup =============== #
server = Flask(__name__)  # Create Flask app
app = Dash(__name__, server=server)  # Dash app inside Flask

# =============== Dash Layout (User Interface) =============== #
app.layout = html.Div([
    html.H1("Process Mining Dashboard", style={'textAlign': 'center'}),
    dcc.Upload(id='upload-data', children=html.Button('Upload CSV File'), multiple=False),
    html.Hr(),
    html.Div(id='data-overview'),
    html.Hr(),
    dcc.Tabs([
        dcc.Tab(label='Process Bottlenecks', children=[dcc.Graph(id='bottleneck-graph')]),
        dcc.Tab(label='Process Loops', children=[html.Div(id='loop-summary')]),
        dcc.Tab(label='Process Variants', children=[html.Div(id='variant-summary')]),
        dcc.Tab(label='Compliance Analysis', children=[html.Div(id='compliance-summary')])
    ])
])

# =============== Callbacks for Data Processing =============== #
@app.callback(Output('data-overview', 'children'), Input('upload-data', 'contents'))
def update_data_overview(contents):
    df = event_log if contents is None else pd.read_csv(decode_file(contents))

    try:
        df = validate_data(df)
    except ValueError as e:
        return html.Div([html.H3(f"Error: {str(e)}")])

    return html.Div([
        html.H3("Data Overview"),
        html.P(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}"),
        html.P(f"Number of Cases: {df['case_id'].nunique()}"),
        html.P(f"Number of Activities: {df['activity'].nunique()}"),
        dash_table.DataTable(data=df.head(5).to_dict('records'), page_size=5)
    ])

@app.callback(Output('bottleneck-graph', 'figure'), Input('upload-data', 'contents'))
def detect_bottlenecks(contents):
    df = event_log if contents is None else pd.read_csv(decode_file(contents))

    try:
        df = validate_data(df)
    except ValueError as e:
        return px.bar([], x=[], y=[], title=f"Error: {str(e)}")

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['time_diff'] = df.groupby('case_id')['timestamp'].diff().dt.total_seconds()
    df['time_diff_minutes'] = df['time_diff'] / 60
    avg_times = df.groupby('activity')['time_diff_minutes'].mean().reset_index()

    return px.bar(avg_times, x='activity', y='time_diff_minutes', title="Average Time Spent Per Activity")

@app.callback(Output('loop-summary', 'children'), Input('upload-data', 'contents'))
def detect_loops(contents):
    df = event_log if contents is None else pd.read_csv(decode_file(contents))

    try:
        df = validate_data(df)
    except ValueError as e:
        return html.Div([html.H3(f"Error: {str(e)}")])

    df = df.sort_values(by=['case_id', 'timestamp'])
    loop_counts = df.groupby(['case_id', 'activity']).size().reset_index(name='count')
    loop_counts = loop_counts[loop_counts['count'] > 1] 

    if loop_counts.empty:
        return html.Div([html.H3("No Loops Detected")])

    loop_details = [html.Div([html.H4(f"Case: {case}"), html.P(f"Involved Activities: {', '.join(loop['activity'].unique())}")])
                    for case, loop in loop_counts.groupby('case_id')]

    return html.Div([html.H3("Process Loops"), *loop_details])

@app.callback(Output('variant-summary', 'children'), Input('upload-data', 'contents'))
def analyze_variants(contents):
    df = event_log if contents is None else pd.read_csv(decode_file(contents))

    try:
        df = validate_data(df)
    except ValueError as e:
        return html.Div([html.H3(f"Error: {str(e)}")])

    variants = df.groupby('case_id')['activity'].apply(tuple).value_counts()
    if variants.empty:
        return html.Div([html.H3("No Process Variants Found")])

    top_10_variants = pd.DataFrame(variants).reset_index().rename(columns={'activity': 'Process Variant', 0: 'Count'}).head(10)
    variant_details = [html.Div([html.H4(f"✅ Variant {idx + 1}: {' → '.join(row['Process Variant'])} (Count: {row['Count']})")])
                       for idx, row in top_10_variants.iterrows()]

    return html.Div([html.H3("Top 10 Process Variants"), *variant_details])

@app.callback(Output('compliance-summary', 'children'), Input('upload-data', 'contents'))
def compliance_analysis(contents):
    df = event_log if contents is None else pd.read_csv(decode_file(contents))

    try:
        df = validate_data(df)
    except ValueError as e:
        return html.Div([html.H3(f"Error: {str(e)}")])

    expected_sequence = ["Start", "Review", "Approve", "End"]
    df['process_sequence'] = df.groupby('case_id')['activity'].transform(lambda x: tuple(x))
    compliance_issues = df[~df['process_sequence'].isin([tuple(expected_sequence)])]

    return html.Div([
        html.H3("Compliance Issues"),
        html.P(f"Non-compliant cases: {compliance_issues['case_id'].nunique()}"),
        dash_table.DataTable(data=compliance_issues[['case_id', 'process_sequence']].drop_duplicates().to_dict('records'), page_size=5)
    ])

# =============== Run the App with Dynamic Port =============== #
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Get Render-assigned port or default to 10000
    app.run_server(debug=True, port=port, host='0.0.0.0')
