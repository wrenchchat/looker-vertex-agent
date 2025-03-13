#!/usr/bin/env python3
"""
Vertex AI Agent Test Results Dashboard

An interactive dashboard built with Streamlit and Plotly to visualize
the performance metrics of the Vertex AI Agent.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import glob
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Vertex AI Agent Analytics", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #4285F4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #5F6368;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .card {
        background-color: #F8F9FA;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-container {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
    }
    .metric-card {
        background-color: #fff;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        min-width: 200px;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #4285F4;
    }
    .metric-label {
        font-size: 1rem;
        color: #5F6368;
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
@st.cache_data
def load_all_data():
    """Load all test results CSV files and combine them into a single DataFrame."""
    # Look for CSV files in the data/results directory relative to the script
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    results_dir = os.path.join(project_root, 'data', 'results')
    
    # Check if the directory exists
    if not os.path.exists(results_dir):
        st.error(f"Results directory not found: {results_dir}")
        return None
        
    # Get all CSV files in the results directory
    csv_files = glob.glob(os.path.join(results_dir, "*test_results*.csv"))
    
    if not csv_files:
        st.error(f"No test result files found in {results_dir}. Please make sure CSV files with 'test_results' in the name exist.")
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
    
    with col1:
        # Response time distribution
        fig = px.histogram(
            df, 
            x="response_time_ms",
            nbins=20,
            title="Response Time Distribution",
            labels={"response_time_ms": "Response Time (ms)"},
            color_discrete_sequence=["#4285F4"]
        )
        fig.update_layout(
            xaxis_title="Response Time (ms)",
            yaxis_title="Number of Questions",
            plot_bgcolor="white",
            margin=dict(l=20, r=20, t=40, b=20),
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
                color_discrete_sequence=["#34A853"]
            )
            fig.update_layout(
                xaxis_title="Category",
                yaxis_title="Avg Response Time (ms)",
                plot_bgcolor="white",
                margin=dict(l=20, r=20, t=40, b=20),
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
                color_discrete_sequence=["#FBBC05"]
            )
            fig.update_layout(
                xaxis_title="Difficulty",
                yaxis_title="Avg Response Time (ms)",
                plot_bgcolor="white",
                margin=dict(l=20, r=20, t=40, b=20),
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
                color_discrete_sequence=["#EA4335"]
            )
            fig.update_layout(
                xaxis_title="Category",
                yaxis_title="Count",
                plot_bgcolor="white",
                margin=dict(l=20, r=20, t=40, b=20),
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
                }
            )
            fig.update_layout(
                xaxis_title="Question Number",
                yaxis_title="Response Time (ms)",
                plot_bgcolor="white",
                margin=dict(l=20, r=20, t=40, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Moving average trend
            window_size = min(10, len(df_sorted))
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
                color_discrete_sequence=["#4285F4"]
            )
            fig.update_layout(
                xaxis_title="Question Number",
                yaxis_title="Response Time (ms)",
                plot_bgcolor="white",
                margin=dict(l=20, r=20, t=40, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)
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
            if 'question_number' in filtered_df.columns:
                question_numbers = sorted(filtered_df['question_number'].unique())
                selected_q_idx = st.slider(
                    "Select Question", 
                    0, len(question_numbers)-1, 
                    0
                )
                selected_q_num = question_numbers[selected_q_idx]
                selected_row = filtered_df[filtered_df['question_number'] == selected_q_num].iloc[0]
            else:
                selected_q_idx = st.slider(
                    "Select Question", 
                    0, len(filtered_df)-1, 
                    0
                )
                selected_row = filtered_df.iloc[selected_q_idx]
            
            # Display question details
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
                    st.markdown(f"**Timestamp:** {selected_row['timestamp']}")
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
<div style="text-align: center; color: #5F6368; font-size: 0.8rem;">
    Vertex AI Agent Performance Dashboard | Created on {date}
</div>
""".format(date=datetime.now().strftime("%Y-%m-%d")), unsafe_allow_html=True) 