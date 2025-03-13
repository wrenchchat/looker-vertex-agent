#!/usr/bin/env python3
"""
Vertex AI Agent Test Results Dashboard (Dark Theme)

An interactive dashboard built with Streamlit and Plotly to visualize
the performance metrics of the Vertex AI Agent with a dark theme.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import glob
import os
from datetime import datetime

# Force disable caching
st.cache_data.clear()

# Page configuration
st.set_page_config(
    page_title="Vertex AI Agent Analytics", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling with dark theme
st.markdown("""
<style>
    /* Base theme overrides */
    .stApp {
        background-color: #121212;
        color: #F5F5F5;
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-1lcbmhc {
        background-color: #0F1111;
    }
    
    /* Widgets styling */
    .stSlider, .stCheckbox, .stRadio, .stSelectbox {
        background-color: #0F1111;
    }
    
    /* Text styling */
    p, .caption, label, stMarkdown {
        color: #F5F5F5;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #F5F5F5 !important;
    }
    
    /* Custom classes */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #F5F5F5 !important;
        margin-bottom: 1rem;
        text-shadow: 0 0 10px rgba(157, 0, 255, 0.5);
    }
    
    .sub-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #F5F5F5 !important;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    .card {
        background-color: #0F1111;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border: 1px solid #2C2F33;
    }
    
    .metric-container {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
    }
    
    .metric-card {
        background-color: #0F1111;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        min-width: 200px;
        border: 1px solid #2C2F33;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #F5F5F5 !important;
        text-shadow: 0 0 5px rgba(27, 3, 163, 0.5);
    }
    
    .metric-label {
        font-size: 1rem;
        color: #F5F5F5;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #0F1111;
        color: #F5F5F5;
        border: none;
    }
    
    .stButton>button:hover {
        background-color: #9D00FF;
    }
    
    /* Multiselect styling - fixing the red pills */
    .stMultiSelect div[data-baseweb="tag"] {
        background-color: #1B03A3 !important;
        color: #F5F5F5 !important;
    }
    
    .stMultiSelect div[data-baseweb="tag"]:hover {
        background-color: #9D00FF !important;
    }
    
    .stMultiSelect div[role="button"] {
        color: #F5F5F5 !important;
    }
    
    .stMultiSelect span[data-testid="stMultiSelectDelete"] {
        color: #F5F5F5 !important;
    }
    
    .stMultiSelect div[data-baseweb="select"] {
        background-color: #0F1111 !important;
        border-color: #2C2F33 !important;
    }
    
    .stMultiSelect div[data-baseweb="popover"] {
        background-color: #0F1111 !important;
    }
    
    .stMultiSelect ul {
        background-color: #0F1111 !important;
    }
    
    .stMultiSelect li:hover {
        background-color: #1B03A3 !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #0F1111;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #F5F5F5;
    }
    
    .stTabs [aria-selected="true"] {
        color: #F5F5F5 !important;
        background-color: #0F1111;
    }
    
    /* Dataframe styling */
    .dataframe {
        background-color: #0F1111 !important;
        color: #F5F5F5 !important;
    }
    
    .dataframe th {
        background-color: #0F1111 !important;
        color: #F5F5F5 !important;
    }
    
    /* Success/Info/Warning/Error message styling */
    .stSuccess, .stInfo, .stWarning, .stError {
        background-color: #0F1111;
        border: 1px solid;
    }
    
    .stSuccess {
        border-color: #39FF14;
        background-color: #0F1111 !important;
    }
    
    .stInfo {
        border-color: #00FFFF;
        background-color: #0F1111 !important;
    }
    
    .stWarning {
        border-color: #E9FF32;
        background-color: #0F1111 !important;
    }
    
    .stError {
        border-color: #FF3131;
        background-color: #0F1111 !important;
    }
    
    /* Override Streamlit's default styling for message containers */
    [data-testid="stCaptionContainer"] {
        background-color: #0F1111 !important;
        color: #F5F5F5 !important;
    }
    
    /* Target the specific success and info message boxes */
    .element-container [data-testid="stCaptionContainer"] {
        background-color: #0F1111 !important;
    }
    
    /* Target the specific message in the sidebar */
    .css-1d391kg [data-testid="stCaptionContainer"],
    .css-1lcbmhc [data-testid="stCaptionContainer"] {
        background-color: #0F1111 !important;
    }
    
    /* Override any remaining colored backgrounds */
    div.stAlert > div {
        background-color: #0F1111 !important;
    }
    
    /* Make sure text in alerts is visible */
    div.stAlert {
        background-color: #0F1111 !important;
        color: #F5F5F5 !important;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">Vertex AI Agent Performance Dashboard</div>', unsafe_allow_html=True)
st.markdown("""
This dashboard provides analytics and visualizations for the Vertex AI Agent test results, 
including response times, success rates, and performance by category and difficulty.
""")

# Load data
def load_all_data(merged_file_pattern="merged_test_results*.csv"):
    """
    Load test results data, prioritizing merged files if available.
    
    Args:
        merged_file_pattern (str): Pattern to identify merged data files
        
    Returns:
        pd.DataFrame: Combined dataframe with all test results
    """
    # First, look for merged data files
    merged_files = glob.glob(merged_file_pattern)
    
    if merged_files:
        # Sort by filename to get the most recent merged file (assuming timestamp in filename)
        merged_files.sort(reverse=True)
        latest_merged_file = merged_files[0]
        
        try:
            st.sidebar.success(f"Using merged data file: {os.path.basename(latest_merged_file)}")
            
            # Check if it's a symlink
            if os.path.islink(latest_merged_file):
                real_path = os.path.realpath(latest_merged_file)
                st.sidebar.info(f"This is a symlink pointing to: {real_path}")
                
                # Check if the target file exists
                if os.path.exists(real_path):
                    st.sidebar.success(f"Target file exists with size: {os.path.getsize(real_path)} bytes")
                    df = pd.read_csv(real_path)
                    st.sidebar.write(f"Loaded {len(df)} rows from target file")
                else:
                    st.sidebar.error(f"Target file does not exist!")
                    return None
            else:
                df = pd.read_csv(latest_merged_file)
                st.sidebar.write(f"Loaded {len(df)} rows from direct file")
            
            return df
        except Exception as e:
            st.warning(f"Could not load merged file {latest_merged_file}: {e}")
    
    # If no merged file or loading failed, fall back to individual files
    csv_files = glob.glob("*test_results*.csv")
    
    if not csv_files:
        st.error("No test result files found. Please make sure CSV files with 'test_results' in the name exist in the current directory.")
        return None
    
    dfs = []
    file_info = []
    
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            # Add file source column
            df['source_file'] = file
            
            # Extract timestamp from file if available
            timestamp = datetime.now()
            if '_' in file:
                try:
                    date_part = file.split('_')[-1].split('.')[0]
                    if len(date_part) == 14:  # Format: YYYYMMDD_HHMMSS
                        timestamp = datetime.strptime(date_part, '%Y%m%d_%H%M%S')
                except:
                    pass
            
            df['file_timestamp'] = timestamp
            
            dfs.append(df)
            file_info.append({
                'file': file,
                'questions': len(df),
                'timestamp': timestamp
            })
        except Exception as e:
            st.warning(f"Could not load file {file}: {e}")
    
    if not dfs:
        st.error("No valid data found in any files.")
        return None
    
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Add file information to session state
    st.session_state['file_info'] = file_info
    
    return combined_df

# Main content area
try:
    # Load data directly from the target file to bypass any caching or symlink issues
    target_file = "../tests/data/results/merged_test_results_20250313_023549.csv"
    if os.path.exists(target_file):
        df = pd.read_csv(target_file)
        st.sidebar.success(f"Directly loaded {len(df)} rows from {target_file}")
    else:
        df = load_all_data()
    
    if df is None:
        st.stop()
        
    # Ensure numeric types for calculations
    if 'response_time_ms' in df.columns:
        df['response_time_ms'] = pd.to_numeric(df['response_time_ms'], errors='coerce')
    
    # Check for success in answers
    if 'answer' in df.columns:
        df['is_error'] = df['answer'].astype(str).str.startswith('ERROR')
    elif 'success' in df.columns:
        df['is_error'] = ~df['success']
    else:
        df['is_error'] = False
        
    # Sidebar
    st.sidebar.title("Filters")
    
    # File selection
    if 'file_info' in st.session_state and len(st.session_state['file_info']) > 1:
        file_options = ["All Files"] + [fi['file'] for fi in st.session_state['file_info']]
        selected_file = st.sidebar.selectbox("Select Data Source", file_options)
        
        if selected_file != "All Files":
            df = df[df['source_file'] == selected_file]
    
    # Category filter
    if 'category' in df.columns:
        categories = sorted(df['category'].unique())
        selected_categories = st.sidebar.multiselect(
            "Select Categories", 
            options=categories,
            default=categories
        )
        if selected_categories:
            df = df[df['category'].isin(selected_categories)]
    
    # Difficulty filter
    if 'difficulty' in df.columns:
        difficulties = sorted(df['difficulty'].unique())
        selected_difficulties = st.sidebar.multiselect(
            "Select Difficulty Levels", 
            options=difficulties,
            default=difficulties
        )
        if selected_difficulties:
            df = df[df['difficulty'].isin(selected_difficulties)]
    
    # Time range filter if timestamps are available
    if 'timestamp' in df.columns:
        # Convert timestamp strings to datetime objects if they're not already
        if df['timestamp'].dtype == 'object':  # String type
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            
        min_date = df['timestamp'].min()
        max_date = df['timestamp'].max()
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date()
        )
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            df = df[(df['timestamp'].dt.date >= start_date) & 
                    (df['timestamp'].dt.date <= end_date)]
    
    # Advanced filters section
    with st.sidebar.expander("Advanced Filters"):
        # Response time range
        if 'response_time_ms' in df.columns:
            min_time = int(df['response_time_ms'].min())
            max_time = int(df['response_time_ms'].max())
            
            # Handle the case when min_time equals max_time
            if min_time == max_time:
                st.info(f"All response times are the same: {min_time} ms")
            else:
                time_range = st.slider(
                    "Response Time Range (ms)",
                    min_value=min_time,
                    max_value=max_time,
                    value=(min_time, max_time)
                )
                
                df = df[(df['response_time_ms'] >= time_range[0]) & 
                        (df['response_time_ms'] <= time_range[1])]
        
        # Text search in questions or answers
        search_text = st.text_input("Search in Questions/Answers")
        if search_text:
            text_query = search_text.lower()
            text_mask = (
                df['question'].astype(str).str.lower().str.contains(text_query) | 
                df['answer'].astype(str).str.lower().str.contains(text_query)
            )
            df = df[text_mask]
    
    # Main dashboard content
    if len(df) == 0:
        st.warning("No data matches the selected filters. Please adjust your filters.")
        st.stop()
    
    # Summary metrics
    st.markdown('<div class="sub-header">Summary Metrics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Questions", len(df))
    
    with col2:
        error_count = df['is_error'].sum()
        success_rate = ((len(df) - error_count) / len(df)) * 100 if len(df) > 0 else 0
        st.metric("Success Rate", f"{success_rate:.1f}%")
    
    with col3:
        avg_time = df['response_time_ms'].mean()
        st.metric("Avg Response Time", f"{avg_time:.1f} ms")
    
    with col4:
        median_time = df['response_time_ms'].median()
        st.metric("Median Response Time", f"{median_time:.1f} ms")
    
    # Response Time Analysis
    st.markdown('<div class="sub-header">Response Time Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    # Define dark theme for plotly
    dark_template = dict(
        layout=dict(
            paper_bgcolor="#121212",
            plot_bgcolor="#121212",
            font=dict(color="#F5F5F5"),
            title=dict(font=dict(color="#F5F5F5")),
            xaxis=dict(
                gridcolor="#0F1111",
                zerolinecolor="#0F1111",
                title=dict(font=dict(color="#F5F5F5"))
            ),
            yaxis=dict(
                gridcolor="#0F1111",
                zerolinecolor="#0F1111",
                title=dict(font=dict(color="#F5F5F5"))
            ),
            legend=dict(font=dict(color="#F5F5F5"))
        )
    )
    
    with col1:
        # Response time distribution
        fig = px.histogram(
            df, 
            x="response_time_ms",
            nbins=20,
            title="Response Time Distribution",
            labels={"response_time_ms": "Response Time (ms)"},
            color_discrete_sequence=["#1B03A3"]
        )
        fig.update_layout(
            xaxis_title="Response Time (ms)",
            yaxis_title="Number of Questions",
            margin=dict(l=20, r=20, t=40, b=20),
            **dark_template["layout"]
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Response time by category
        if 'category' in df.columns:
            category_stats = df.groupby('category')['response_time_ms'].mean().reset_index()
            category_stats = category_stats.sort_values('response_time_ms', ascending=False)
            
            fig = px.bar(
                category_stats,
                x="category",
                y="response_time_ms",
                title="Average Response Time by Category",
                labels={
                    "response_time_ms": "Avg Response Time (ms)",
                    "category": "Category"
                },
                color_discrete_sequence=["#9D00FF"]
            )
            fig.update_layout(
                xaxis_title="Category",
                yaxis_title="Avg Response Time (ms)",
                margin=dict(l=20, r=20, t=40, b=20),
                **dark_template["layout"]
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Category information not available in the dataset.")
    
    # Second row of charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Response time by difficulty
        if 'difficulty' in df.columns:
            difficulty_stats = df.groupby('difficulty')['response_time_ms'].mean().reset_index()
            
            # Sort by difficulty level if possible
            difficulty_order = ['Easy', 'Medium', 'Difficult', 'Extremely Difficult']
            difficulty_stats['difficulty_order'] = difficulty_stats['difficulty'].apply(
                lambda x: difficulty_order.index(x) if x in difficulty_order else 999
            )
            difficulty_stats = difficulty_stats.sort_values('difficulty_order')
            
            fig = px.bar(
                difficulty_stats,
                x="difficulty",
                y="response_time_ms",
                title="Average Response Time by Difficulty",
                labels={
                    "response_time_ms": "Avg Response Time (ms)",
                    "difficulty": "Difficulty"
                },
                color_discrete_sequence=["#FF10F0"]
            )
            fig.update_layout(
                xaxis_title="Difficulty",
                yaxis_title="Avg Response Time (ms)",
                margin=dict(l=20, r=20, t=40, b=20),
                **dark_template["layout"]
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Difficulty information not available in the dataset.")
    
    with col2:
        # Question count by category
        if 'category' in df.columns:
            category_counts = df['category'].value_counts().reset_index()
            category_counts.columns = ['category', 'count']
            
            fig = px.bar(
                category_counts,
                x="category",
                y="count",
                title="Question Count by Category",
                labels={
                    "count": "Number of Questions",
                    "category": "Category"
                },
                color_discrete_sequence=["#FF0090"]
            )
            fig.update_layout(
                xaxis_title="Category",
                yaxis_title="Count",
                margin=dict(l=20, r=20, t=40, b=20),
                **dark_template["layout"]
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Category information not available in the dataset.")
    
    # Detailed View
    st.markdown('<div class="sub-header">Detailed Analysis</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Response Time Trends", "Question Explorer", "Raw Data"])
    
    with tab1:
        # Response time by question number
        if 'question_number' in df.columns:
            df_sorted = df.sort_values('question_number')
            
            fig = px.scatter(
                df_sorted,
                x="question_number",
                y="response_time_ms",
                color="category" if 'category' in df.columns else None,
                size="response_time_ms",
                hover_data=["question", "response_time_ms"],
                title="Response Time by Question Number",
                labels={
                    "response_time_ms": "Response Time (ms)",
                    "question_number": "Question Number"
                },
                color_discrete_sequence=["#1B03A3", "#9D00FF", "#FF10F0", "#FF0090", "#C7EA46", "#39FF14"]
            )
            fig.update_layout(
                xaxis_title="Question Number",
                yaxis_title="Response Time (ms)",
                margin=dict(l=20, r=20, t=40, b=20),
                **dark_template["layout"]
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Moving average trend
            window_size = min(10, max(1, len(df_sorted)))
            if len(df_sorted) >= 2:  # Only show moving average if we have at least 2 data points
                df_sorted['moving_avg'] = df_sorted['response_time_ms'].rolling(window=window_size).mean()
                
                fig = px.line(
                    df_sorted,
                    x="question_number",
                    y="moving_avg",
                    title=f"Response Time Trend (Moving Average, Window Size: {window_size})",
                    labels={
                        "moving_avg": f"{window_size}-Question Moving Average (ms)",
                        "question_number": "Question Number"
                    },
                    color_discrete_sequence=["#FF10F0"]
                )
                fig.update_layout(
                    xaxis_title="Question Number",
                    yaxis_title="Response Time (ms)",
                    margin=dict(l=20, r=20, t=40, b=20),
                    **dark_template["layout"]
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Not enough data points to show a moving average trend.")
        else:
            st.info("Question number information not available in the dataset.")
    
    with tab2:
        # Interactive question explorer
        st.subheader("Question Explorer")
        
        # Category dropdown
        if 'category' in df.columns:
            selected_category = st.selectbox(
                "Select Category",
                options=["All Categories"] + sorted(df['category'].unique().tolist())
            )
            
            filtered_df = df
            if selected_category != "All Categories":
                filtered_df = df[df['category'] == selected_category]
        else:
            filtered_df = df
        
        # Question slider
        if len(filtered_df) > 0:
            # Display total questions in this category
            st.info(f"Showing {len(filtered_df)} questions in {selected_category if selected_category != 'All Categories' else 'all categories'}")
            
            if 'question_number' in filtered_df.columns:
                question_numbers = sorted(filtered_df['question_number'].unique())
                if len(question_numbers) == 1:
                    st.info(f"Only one question available: #{question_numbers[0]}")
                    selected_q_num = question_numbers[0]
                    selected_row = filtered_df[filtered_df['question_number'] == selected_q_num].iloc[0]
                else:
                    # Use a slider with a range from 0 to the number of questions - 1
                    selected_q_idx = st.slider(
                        "Select Question", 
                        0, len(question_numbers)-1, 
                        0,
                        format="%d"
                    )
                    selected_q_num = question_numbers[selected_q_idx]
                    # Display the question number in the UI
                    st.write(f"Question #{selected_q_idx + 1} of {len(question_numbers)}")
                    selected_row = filtered_df[filtered_df['question_number'] == selected_q_num].iloc[0]
            else:
                if len(filtered_df) == 1:
                    st.info("Only one question available")
                    selected_row = filtered_df.iloc[0]
                else:
                    # Use a slider with a range from 0 to the number of questions - 1
                    selected_q_idx = st.slider(
                        "Select Question", 
                        0, len(filtered_df)-1, 
                        0,
                        format="%d"
                    )
                    # Display the question number in the UI
                    st.write(f"Question #{selected_q_idx + 1} of {len(filtered_df)}")
                    selected_row = filtered_df.iloc[selected_q_idx]
            
            # Display question details
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown("### Question")
                    st.markdown(f"**{selected_row['question']}**")
                    
                    st.markdown("### Answer")
                    st.markdown(selected_row['answer'])
                
                with col2:
                    st.markdown("### Details")
                    if 'category' in selected_row:
                        st.markdown(f"**Category:** {selected_row['category']}")
                    
                    if 'difficulty' in selected_row:
                        st.markdown(f"**Difficulty:** {selected_row['difficulty']}")
                    
                    st.markdown(f"**Response Time:** {selected_row['response_time_ms']:.1f} ms")
                    
                    if 'session_id' in selected_row:
                        st.markdown(f"**Session ID:** {selected_row['session_id']}")
                    
                    if 'timestamp' in selected_row:
                        # Format timestamp for display
                        timestamp_value = selected_row['timestamp']
                        if isinstance(timestamp_value, str):
                            try:
                                # Try to parse and format the timestamp string
                                timestamp_value = pd.to_datetime(timestamp_value).strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                # If parsing fails, just display the original string
                                pass
                        st.markdown(f"**Timestamp:** {timestamp_value}")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("No questions available with the current filters.")
    
    with tab3:
        # Raw data table
        st.subheader("Raw Data")
        
        # Download button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download CSV",
            csv,
            "vertex_ai_agent_results.csv",
            "text/csv",
            key='download-csv'
        )
        
        # Display dataframe
        display_columns = [
            'question_number', 'category', 'difficulty', 'question', 
            'response_time_ms', 'is_error', 'source_file'
        ]
        display_columns = [col for col in display_columns if col in df.columns]
        
        st.dataframe(df[display_columns], use_container_width=True)

except Exception as e:
    st.error(f"An error occurred: {e}")
    import traceback
    st.code(traceback.format_exc())

# Footer
st.markdown("""
---
<div style="text-align: center; color: #7D8B99; font-size: 0.8rem;">
    Vertex AI Agent Performance Dashboard | Created on {date}
</div>
""".format(date=datetime.now().strftime("%Y-%m-%d")), unsafe_allow_html=True) 