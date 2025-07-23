import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from pathlib import Path

class LogViewer:
    """Component for viewing HedgeLab logs"""
    
    def __init__(self):
        self.logs_dir = Path("logs")
    
    def render(self):
        """Render the log viewer interface"""
        st.header("📋 HedgeLab Log Viewer")
        st.markdown("Monitor application logs, API calls, and error tracking")
        
        # Log file selection
        log_files = self._get_log_files()
        
        if not log_files:
            st.warning("No log files found. Logs will appear here once the application generates them.")
            return
        
        # File selection
        selected_file = st.selectbox(
            "Select log file:",
            options=log_files,
            format_func=lambda x: x.replace('.log', '').replace('_', ' ').title()
        )
        
        if selected_file:
            self._display_log_file(selected_file)
    
    def _get_log_files(self) -> list:
        """Get available log files"""
        if not self.logs_dir.exists():
            return []
        
        log_files = []
        for file in self.logs_dir.glob("*.log"):
            log_files.append(file.name)
        
        return sorted(log_files, reverse=True)
    
    def _display_log_file(self, filename: str):
        """Display contents of a log file"""
        file_path = self.logs_dir / filename
        
        if not file_path.exists():
            st.error(f"Log file {filename} not found")
            return
        
        # Read log file
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            if not lines:
                st.info("Log file is empty")
                return
            
            # Parse log entries
            log_entries = []
            for line in lines:
                if line.strip():
                    entry = self._parse_log_line(line.strip())
                    if entry:
                        log_entries.append(entry)
            
            if not log_entries:
                st.info("No valid log entries found")
                return
            
            # Create DataFrame
            df = pd.DataFrame(log_entries)
            
            # Filter options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Level filter
                levels = ['ALL'] + list(df['level'].unique())
                selected_level = st.selectbox("Log Level:", levels)
            
            with col2:
                # Time filter
                time_filter = st.selectbox("Time Filter:", 
                    ['All Time', 'Last Hour', 'Last 24 Hours', 'Last 7 Days'])
            
            with col3:
                # Search
                search_term = st.text_input("Search:", placeholder="Enter search term...")
            
            # Apply filters
            filtered_df = df.copy()
            
            if selected_level != 'ALL':
                filtered_df = filtered_df[filtered_df['level'] == selected_level]
            
            if search_term:
                filtered_df = filtered_df[
                    filtered_df['message'].str.contains(search_term, case=False, na=False)
                ]
            
            # Apply time filter
            if time_filter != 'All Time':
                cutoff_time = self._get_cutoff_time(time_filter)
                filtered_df = filtered_df[filtered_df['timestamp'] >= cutoff_time]
            
            # Display statistics
            st.subheader("📊 Log Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Entries", len(df))
            with col2:
                st.metric("Filtered Entries", len(filtered_df))
            with col3:
                error_count = len(df[df['level'] == 'ERROR'])
                st.metric("Errors", error_count, delta=None)
            with col4:
                warning_count = len(df[df['level'] == 'WARNING'])
                st.metric("Warnings", warning_count, delta=None)
            
            # Display log entries
            st.subheader("📋 Log Entries")
            
            if len(filtered_df) > 100:
                st.warning(f"Showing first 100 of {len(filtered_df)} entries. Use filters to narrow down results.")
                filtered_df = filtered_df.head(100)
            
            # Format display
            for _, row in filtered_df.iterrows():
                self._display_log_entry(row)
    
    def _parse_log_line(self, line: str) -> dict:
        """Parse a log line into structured data"""
        try:
            # Expected format: timestamp - name - level - funcName:lineNo - message
            parts = line.split(' - ', 4)
            
            if len(parts) >= 5:
                timestamp_str = parts[0]
                name = parts[1]
                level = parts[2]
                location = parts[3]
                message = parts[4]
                
                # Parse timestamp
                try:
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                except ValueError:
                    try:
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        timestamp = datetime.now()
                
                return {
                    'timestamp': timestamp,
                    'name': name,
                    'level': level,
                    'location': location,
                    'message': message,
                    'raw': line
                }
            else:
                # Simple format: timestamp - level - message
                parts = line.split(' - ', 2)
                if len(parts) >= 3:
                    timestamp_str = parts[0]
                    level = parts[1]
                    message = parts[2]
                    
                    try:
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                    except ValueError:
                        try:
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            timestamp = datetime.now()
                    
                    return {
                        'timestamp': timestamp,
                        'name': 'hedgelab',
                        'level': level,
                        'location': '',
                        'message': message,
                        'raw': line
                    }
        
        except Exception:
            return None
    
    def _get_cutoff_time(self, time_filter: str) -> datetime:
        """Get cutoff time for time filter"""
        now = datetime.now()
        
        if time_filter == 'Last Hour':
            return now - timedelta(hours=1)
        elif time_filter == 'Last 24 Hours':
            return now - timedelta(days=1)
        elif time_filter == 'Last 7 Days':
            return now - timedelta(days=7)
        else:
            return datetime.min
    
    def _display_log_entry(self, entry: pd.Series):
        """Display a single log entry"""
        # Color coding based on level
        level_colors = {
            'ERROR': '🔴',
            'WARNING': '🟡',
            'INFO': '🔵',
            'DEBUG': '⚪'
        }
        
        icon = level_colors.get(entry['level'], '⚪')
        
        # Create expandable entry
        with st.expander(f"{icon} {entry['timestamp'].strftime('%H:%M:%S')} - {entry['level']} - {entry['message'][:100]}..."):
            st.text(f"Timestamp: {entry['timestamp']}")
            st.text(f"Level: {entry['level']}")
            st.text(f"Component: {entry['name']}")
            if entry['location']:
                st.text(f"Location: {entry['location']}")
            st.text(f"Message: {entry['message']}")
            
            # Special handling for API calls
            if 'API_CALL' in entry['message']:
                st.info("🔗 API Call detected")
            elif 'RATE_LIMIT' in entry['message']:
                st.warning("⚠️ Rate limiting detected")
            elif 'DATA_FALLBACK' in entry['message']:
                st.info("🔄 Data fallback used")
    
    def get_recent_errors(self, hours: int = 24) -> list:
        """Get recent errors for monitoring"""
        errors = []
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for log_file in self._get_log_files():
            if 'error' in log_file.lower():
                file_path = self.logs_dir / log_file
                try:
                    with open(file_path, 'r') as f:
                        for line in f:
                            entry = self._parse_log_line(line.strip())
                            if entry and entry['level'] == 'ERROR' and entry['timestamp'] >= cutoff_time:
                                errors.append(entry)
                except Exception:
                    continue
        
        return errors
    
    def get_api_call_stats(self, hours: int = 24) -> dict:
        """Get API call statistics"""
        stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'rate_limited_calls': 0,
            'avg_response_time': 0
        }
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        response_times = []
        
        for log_file in self._get_log_files():
            if 'api_calls' in log_file.lower():
                file_path = self.logs_dir / log_file
                try:
                    with open(file_path, 'r') as f:
                        for line in f:
                            if 'API_CALL' in line and cutoff_time <= datetime.now():
                                stats['total_calls'] += 1
                                
                                if 'SUCCESS' in line:
                                    stats['successful_calls'] += 1
                                elif 'FAILED' in line:
                                    stats['failed_calls'] += 1
                                
                                if 'RATE_LIMIT' in line:
                                    stats['rate_limited_calls'] += 1
                                
                                # Extract response time if available
                                if 's' in line:
                                    try:
                                        time_part = line.split(' - ')[-1]
                                        if 's' in time_part:
                                            time_str = time_part.split('s')[0].split()[-1]
                                            response_times.append(float(time_str))
                                    except (ValueError, IndexError):
                                        pass
                except Exception:
                    continue
        
        if response_times:
            stats['avg_response_time'] = sum(response_times) / len(response_times)
        
        return stats 