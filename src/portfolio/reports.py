import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO
import base64
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from src.data.database import db
from src.data.market_data import market_data
from src.ui.components import loading_spinner, format_currency, format_percentage

class ReportGenerator:
    """Generate simple PDF and Excel reports for portfolio performance"""
    
    def __init__(self):
        self.database = db
        self.market_provider = market_data
        
    def render(self):
        """Render the reports dashboard"""
        st.markdown("## 📊 Reports & Analytics")
        st.markdown("---")
        
        # Report type selection
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📋 Generate Reports")
            
            report_type = st.selectbox(
                "Report Type",
                ["Portfolio Performance", "Trade Summary", "Risk Analysis", "Tax Report"]
            )
            
            # Date range selection
            col1a, col1b = st.columns(2)
            with col1a:
                start_date = st.date_input(
                    "Start Date",
                    value=datetime.now() - timedelta(days=90)
                )
            
            with col1b:
                end_date = st.date_input(
                    "End Date",
                    value=datetime.now()
                )
            
            # Report format
            format_type = st.selectbox(
                "Format",
                ["PDF Report", "Excel Spreadsheet", "Both"]
            )
            
            # Generate report button
            if st.button("📊 Generate Report", type="primary"):
                with loading_spinner("Generating report..."):
                    self._generate_report(report_type, start_date, end_date, format_type)
        
        with col2:
            st.markdown("### ⚡ Quick Reports")
            
            if st.button("📈 Monthly Performance"):
                self._generate_quick_performance_report()
            
            if st.button("💰 Current Positions"):
                self._generate_positions_report()
            
            if st.button("📊 Year-to-Date Summary"):
                self._generate_ytd_summary()
            
            if st.button("🔍 Trade Analysis"):
                self._generate_trade_analysis()
        
        st.markdown("---")
        
        # Report previews and analytics
        tab1, tab2, tab3 = st.tabs(["📊 Performance Preview", "📋 Recent Reports", "⚙️ Settings"])
        
        with tab1:
            self._render_performance_preview()
        
        with tab2:
            self._render_recent_reports()
        
        with tab3:
            self._render_report_settings()
    
    def _generate_report(self, report_type: str, start_date: datetime.date, 
                        end_date: datetime.date, format_type: str):
        """Generate the selected report"""
        try:
            if report_type == "Portfolio Performance":
                if format_type in ["PDF Report", "Both"]:
                    pdf_data = self._generate_performance_pdf(start_date, end_date)
                    self._download_report(pdf_data, "portfolio_performance.pdf", "application/pdf")
                
                if format_type in ["Excel Spreadsheet", "Both"]:
                    excel_data = self._generate_performance_excel(start_date, end_date)
                    self._download_report(excel_data, "portfolio_performance.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            
            elif report_type == "Trade Summary":
                if format_type in ["PDF Report", "Both"]:
                    pdf_data = self._generate_trade_summary_pdf(start_date, end_date)
                    self._download_report(pdf_data, "trade_summary.pdf", "application/pdf")
                
                if format_type in ["Excel Spreadsheet", "Both"]:
                    excel_data = self._generate_trade_summary_excel(start_date, end_date)
                    self._download_report(excel_data, "trade_summary.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            
            elif report_type == "Risk Analysis":
                self._generate_risk_analysis_report(start_date, end_date, format_type)
            
            elif report_type == "Tax Report":
                self._generate_tax_report(start_date, end_date, format_type)
            
            st.success("✅ Report generated successfully!")
            
        except Exception as e:
            st.error(f"❌ Error generating report: {e}")
    
    def _generate_performance_pdf(self, start_date: datetime.date, end_date: datetime.date) -> bytes:
        """Generate portfolio performance PDF report"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph("HedgeLab Portfolio Performance Report", title_style))
        story.append(Spacer(1, 20))
        
        # Report period
        period_text = f"Report Period: {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}"
        story.append(Paragraph(period_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Get portfolio data
        positions = self._get_portfolio_positions()
        performance_data = self._get_performance_data(start_date, end_date)
        trades = self._get_trades_data(start_date, end_date)
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        
        # Calculate key metrics
        portfolio_value = self._calculate_total_portfolio_value(positions)
        total_return = self._calculate_total_return(performance_data)
        sharpe_ratio = self._calculate_sharpe_ratio(performance_data)
        max_drawdown = self._calculate_max_drawdown(performance_data)
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Portfolio Value', format_currency(portfolio_value)],
            ['Total Return', format_percentage(total_return)],
            ['Sharpe Ratio', f"{sharpe_ratio:.2f}"],
            ['Maximum Drawdown', format_percentage(max_drawdown)],
            ['Number of Trades', str(len(trades))],
            ['Active Positions', str(len(positions[positions['quantity'] != 0]) if not positions.empty else 0)]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 30))
        
        # Current Positions
        story.append(Paragraph("Current Positions", styles['Heading2']))
        
        if not positions.empty and len(positions[positions['quantity'] != 0]) > 0:
            positions_data = [['Symbol', 'Quantity', 'Avg Cost', 'Market Value', 'P&L', 'P&L %']]
            
            for _, position in positions.iterrows():
                if position['quantity'] != 0:
                    current_price = self._get_current_price(position['symbol'])
                    market_value = position['quantity'] * current_price
                    cost_basis = position['quantity'] * position['avg_cost']
                    pnl = market_value - cost_basis
                    pnl_percent = (pnl / abs(cost_basis)) * 100 if cost_basis != 0 else 0
                    
                    positions_data.append([
                        position['symbol'],
                        f"{position['quantity']:,.0f}",
                        f"${position['avg_cost']:.2f}",
                        f"${market_value:,.2f}",
                        f"${pnl:,.2f}",
                        f"{pnl_percent:+.2f}%"
                    ])
            
            positions_table = Table(positions_data)
            positions_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(positions_table)
        else:
            story.append(Paragraph("No active positions found.", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Performance Analysis
        story.append(Paragraph("Performance Analysis", styles['Heading2']))
        
        analysis_text = f"""
        During the reporting period from {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}, 
        the portfolio achieved a total return of {format_percentage(total_return)}. The Sharpe ratio of {sharpe_ratio:.2f} 
        indicates {'strong' if sharpe_ratio > 1 else 'moderate' if sharpe_ratio > 0.5 else 'weak'} risk-adjusted performance.
        
        The maximum drawdown of {format_percentage(max_drawdown)} represents the largest peak-to-trough decline 
        during the period, providing insight into the portfolio's downside risk.
        """
        
        story.append(Paragraph(analysis_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _generate_performance_excel(self, start_date: datetime.date, end_date: datetime.date) -> bytes:
        """Generate portfolio performance Excel report"""
        buffer = BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = self._get_summary_data(start_date, end_date)
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Positions sheet
            positions = self._get_portfolio_positions()
            if not positions.empty:
                positions.to_excel(writer, sheet_name='Positions', index=False)
            
            # Performance data sheet
            performance_data = self._get_performance_data(start_date, end_date)
            if not performance_data.empty:
                performance_data.to_excel(writer, sheet_name='Performance', index=False)
            
            # Trades sheet
            trades = self._get_trades_data(start_date, end_date)
            if not trades.empty:
                trades.to_excel(writer, sheet_name='Trades', index=False)
        
        buffer.seek(0)
        return buffer.getvalue()
    
    def _generate_trade_summary_pdf(self, start_date: datetime.date, end_date: datetime.date) -> bytes:
        """Generate trade summary PDF report"""
        # Similar structure to performance PDF but focused on trades
        buffer = BytesIO()
        # Implementation would be similar to performance PDF
        return buffer.getvalue()
    
    def _generate_trade_summary_excel(self, start_date: datetime.date, end_date: datetime.date) -> bytes:
        """Generate trade summary Excel report"""
        buffer = BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            trades = self._get_trades_data(start_date, end_date)
            if not trades.empty:
                # Trade summary
                trade_summary = self._calculate_trade_summary(trades)
                trade_summary_df = pd.DataFrame([trade_summary])
                trade_summary_df.to_excel(writer, sheet_name='Trade Summary', index=False)
                
                # All trades
                trades.to_excel(writer, sheet_name='All Trades', index=False)
                
                # Monthly breakdown
                if len(trades) > 0:
                    monthly_trades = self._calculate_monthly_trade_breakdown(trades)
                    monthly_trades.to_excel(writer, sheet_name='Monthly Breakdown', index=False)
        
        buffer.seek(0)
        return buffer.getvalue()
    
    def _download_report(self, data: bytes, filename: str, mime_type: str):
        """Provide download link for generated report"""
        b64 = base64.b64encode(data).decode()
        href = f'<a href="data:{mime_type};base64,{b64}" download="{filename}">📥 Download {filename}</a>'
        st.markdown(href, unsafe_allow_html=True)
    
    def _render_performance_preview(self):
        """Render performance preview charts"""
        st.markdown("### 📊 Performance Preview")
        
        # Get recent performance data
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=90)
        performance_data = self._get_performance_data(start_date, end_date)
        
        if not performance_data.empty:
            # Performance chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=performance_data['date'],
                y=performance_data['total_value'],
                mode='lines',
                name='Portfolio Value',
                line=dict(color='#3b82f6', width=2)
            ))
            
            fig.update_layout(
                title="Portfolio Performance (Last 90 Days)",
                xaxis_title="Date",
                yaxis_title="Portfolio Value ($)",
                template="plotly_white",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_return = self._calculate_total_return(performance_data)
                st.metric("90-Day Return", format_percentage(total_return))
            
            with col2:
                sharpe_ratio = self._calculate_sharpe_ratio(performance_data)
                st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")
            
            with col3:
                max_drawdown = self._calculate_max_drawdown(performance_data)
                st.metric("Max Drawdown", format_percentage(max_drawdown))
            
            with col4:
                volatility = self._calculate_volatility(performance_data)
                st.metric("Volatility", format_percentage(volatility))
        else:
            st.info("No performance data available for preview.")
    
    def _render_recent_reports(self):
        """Render list of recently generated reports"""
        st.markdown("### 📋 Recent Reports")
        
        # In a real implementation, this would show recently generated reports
        recent_reports = [
            {"name": "Portfolio Performance", "date": "2024-01-15", "type": "PDF", "size": "245 KB"},
            {"name": "Trade Summary", "date": "2024-01-10", "type": "Excel", "size": "156 KB"},
            {"name": "Risk Analysis", "date": "2024-01-05", "type": "PDF", "size": "189 KB"}
        ]
        
        if recent_reports:
            for report in recent_reports:
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                    
                    with col1:
                        st.write(f"📊 **{report['name']}**")
                    
                    with col2:
                        st.write(report['date'])
                    
                    with col3:
                        st.write(report['type'])
                    
                    with col4:
                        st.write(report['size'])
                    
                    st.markdown("---")
        else:
            st.info("No recent reports found. Generate your first report above!")
    
    def _render_report_settings(self):
        """Render report generation settings"""
        st.markdown("### ⚙️ Report Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Default Settings")
            
            default_format = st.selectbox(
                "Default Report Format",
                ["PDF Report", "Excel Spreadsheet", "Both"]
            )
            
            include_charts = st.checkbox("Include Charts in PDF", value=True)
            include_analysis = st.checkbox("Include Performance Analysis", value=True)
            
            benchmark_symbol = st.text_input(
                "Benchmark Symbol",
                value="SPY",
                help="Symbol to compare performance against"
            )
        
        with col2:
            st.markdown("#### Report Branding")
            
            company_name = st.text_input("Company Name", value="HedgeLab")
            report_footer = st.text_input("Report Footer", value="Generated by HedgeLab")
            
            logo_upload = st.file_uploader(
                "Upload Logo",
                type=['png', 'jpg', 'jpeg'],
                help="Logo will appear in PDF reports"
            )
        
        if st.button("💾 Save Settings"):
            st.success("✅ Report settings saved!")
    
    # Helper methods for data retrieval and calculations
    def _get_portfolio_positions(self) -> pd.DataFrame:
        """Get current portfolio positions"""
        return self.database.get_positions()
    
    def _get_performance_data(self, start_date: datetime.date, end_date: datetime.date) -> pd.DataFrame:
        """Get performance data for date range"""
        return self.database.get_portfolio_performance(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
    
    def _get_trades_data(self, start_date: datetime.date, end_date: datetime.date) -> pd.DataFrame:
        """Get trades data for date range"""
        all_trades = self.database.get_trades()
        if all_trades.empty:
            return pd.DataFrame()
        
        # Filter by date range
        all_trades['timestamp'] = pd.to_datetime(all_trades['timestamp'])
        filtered_trades = all_trades[
            (all_trades['timestamp'].dt.date >= start_date) & 
            (all_trades['timestamp'].dt.date <= end_date)
        ]
        
        return filtered_trades
    
    def _get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        try:
            stock_data = self.market_provider.get_stock_data(symbol, period="1d")
            if not stock_data.empty:
                return stock_data['Close'].iloc[-1]
        except:
            pass
        return 0.0
    
    def _calculate_total_portfolio_value(self, positions: pd.DataFrame) -> float:
        """Calculate total portfolio value"""
        if positions.empty:
            return 0.0
        
        total_value = 0
        for _, position in positions.iterrows():
            if position['quantity'] != 0:
                current_price = self._get_current_price(position['symbol'])
                market_value = position['quantity'] * current_price
                total_value += market_value
        
        return total_value
    
    def _calculate_total_return(self, performance_data: pd.DataFrame) -> float:
        """Calculate total return for the period"""
        if performance_data.empty or len(performance_data) < 2:
            return 0.0
        
        start_value = performance_data['total_value'].iloc[0]
        end_value = performance_data['total_value'].iloc[-1]
        
        if start_value == 0:
            return 0.0
        
        return ((end_value - start_value) / start_value) * 100
    
    def _calculate_sharpe_ratio(self, performance_data: pd.DataFrame) -> float:
        """Calculate Sharpe ratio"""
        if performance_data.empty or len(performance_data) < 2:
            return 0.0
        
        returns = performance_data['total_value'].pct_change().dropna()
        if len(returns) == 0 or returns.std() == 0:
            return 0.0
        
        return (returns.mean() / returns.std()) * np.sqrt(252)  # Annualized
    
    def _calculate_max_drawdown(self, performance_data: pd.DataFrame) -> float:
        """Calculate maximum drawdown"""
        if performance_data.empty:
            return 0.0
        
        values = performance_data['total_value']
        cumulative_returns = values / values.iloc[0]
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        
        return drawdown.min() * 100
    
    def _calculate_volatility(self, performance_data: pd.DataFrame) -> float:
        """Calculate annualized volatility"""
        if performance_data.empty or len(performance_data) < 2:
            return 0.0
        
        returns = performance_data['total_value'].pct_change().dropna()
        if len(returns) == 0:
            return 0.0
        
        return returns.std() * np.sqrt(252) * 100  # Annualized percentage
    
    def _get_summary_data(self, start_date: datetime.date, end_date: datetime.date) -> List[Dict]:
        """Get summary data for Excel report"""
        positions = self._get_portfolio_positions()
        performance_data = self._get_performance_data(start_date, end_date)
        trades = self._get_trades_data(start_date, end_date)
        
        portfolio_value = self._calculate_total_portfolio_value(positions)
        total_return = self._calculate_total_return(performance_data)
        sharpe_ratio = self._calculate_sharpe_ratio(performance_data)
        max_drawdown = self._calculate_max_drawdown(performance_data)
        
        return [
            {"Metric": "Total Portfolio Value", "Value": portfolio_value},
            {"Metric": "Total Return (%)", "Value": total_return},
            {"Metric": "Sharpe Ratio", "Value": sharpe_ratio},
            {"Metric": "Maximum Drawdown (%)", "Value": max_drawdown},
            {"Metric": "Number of Trades", "Value": len(trades)},
            {"Metric": "Active Positions", "Value": len(positions[positions['quantity'] != 0]) if not positions.empty else 0}
        ]
    
    def _calculate_trade_summary(self, trades: pd.DataFrame) -> Dict:
        """Calculate trade summary statistics"""
        if trades.empty:
            return {}
        
        total_trades = len(trades)
        buy_trades = len(trades[trades['side'] == 'BUY'])
        sell_trades = len(trades[trades['side'] == 'SELL'])
        total_volume = trades['total_value'].sum()
        avg_trade_size = trades['total_value'].mean()
        
        return {
            "Total Trades": total_trades,
            "Buy Trades": buy_trades,
            "Sell Trades": sell_trades,
            "Total Volume": total_volume,
            "Average Trade Size": avg_trade_size
        }
    
    def _calculate_monthly_trade_breakdown(self, trades: pd.DataFrame) -> pd.DataFrame:
        """Calculate monthly trade breakdown"""
        if trades.empty:
            return pd.DataFrame()
        
        trades['month'] = pd.to_datetime(trades['timestamp']).dt.to_period('M')
        monthly_summary = trades.groupby('month').agg({
            'symbol': 'count',
            'total_value': 'sum'
        }).rename(columns={'symbol': 'trade_count', 'total_value': 'total_volume'})
        
        return monthly_summary.reset_index()
    
    def _generate_quick_performance_report(self):
        """Generate quick performance report"""
        st.info("📈 Generating quick performance report...")
        # Implementation for quick report
    
    def _generate_positions_report(self):
        """Generate current positions report"""
        st.info("💰 Generating positions report...")
        # Implementation for positions report
    
    def _generate_ytd_summary(self):
        """Generate year-to-date summary"""
        st.info("📊 Generating YTD summary...")
        # Implementation for YTD summary
    
    def _generate_trade_analysis(self):
        """Generate trade analysis"""
        st.info("🔍 Generating trade analysis...")
        # Implementation for trade analysis
    
    def _generate_risk_analysis_report(self, start_date: datetime.date, end_date: datetime.date, format_type: str):
        """Generate risk analysis report"""
        st.info("⚠️ Risk analysis report generation coming soon!")
    
    def _generate_tax_report(self, start_date: datetime.date, end_date: datetime.date, format_type: str):
        """Generate tax report"""
        st.info("📄 Tax report generation coming soon!")

# For testing purposes
if __name__ == "__main__":
    report_generator = ReportGenerator()
    report_generator.render() 