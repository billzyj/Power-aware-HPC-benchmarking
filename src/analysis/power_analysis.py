#!/usr/bin/env python3

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dataclasses import dataclass
from ..power_profiling.monitors.base import PowerReading
import os
import json

@dataclass
class PowerAnalysisResult:
    """Container for power analysis results"""
    raw_data: pd.DataFrame
    statistics: Dict[str, float]
    plots: Dict[str, go.Figure]
    metadata: Dict[str, Any]

class PowerAnalyzer:
    def __init__(self, power_readings: List[PowerReading]):
        """Initialize the power analyzer with a list of power readings"""
        self.power_readings = power_readings
        self.df = self._create_dataframe()
    
    def _create_dataframe(self) -> pd.DataFrame:
        """Convert power readings to a pandas DataFrame"""
        data = []
        for reading in self.power_readings:
            row = {
                'timestamp': reading.timestamp,
                'power_watts': reading.power_watts,
                **reading.metadata
            }
            data.append(row)
        return pd.DataFrame(data)
    
    def calculate_statistics(self) -> Dict[str, float]:
        """Calculate comprehensive power statistics"""
        if self.df.empty:
            return {}
            
        stats = {
            'min_power': self.df['power_watts'].min(),
            'max_power': self.df['power_watts'].max(),
            'mean_power': self.df['power_watts'].mean(),
            'median_power': self.df['power_watts'].median(),
            'std_power': self.df['power_watts'].std(),
            'total_energy': (self.df['power_watts'] * self.df['power_watts'].index.to_series().diff()).sum(),
            'duration': (self.df['timestamp'].max() - self.df['timestamp'].min()).total_seconds()
        }
        
        # Calculate percentiles
        percentiles = [25, 50, 75, 90, 95, 99]
        for p in percentiles:
            stats[f'p{p}_power'] = self.df['power_watts'].quantile(p/100)
            
        return stats
    
    def create_power_time_plot(self) -> go.Figure:
        """Create an interactive power vs time plot"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=self.df['timestamp'],
            y=self.df['power_watts'],
            mode='lines',
            name='Power Consumption',
            line=dict(color='blue')
        ))
        
        # Add mean power line
        mean_power = self.df['power_watts'].mean()
        fig.add_hline(
            y=mean_power,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {mean_power:.2f}W",
            annotation_position="bottom right"
        )
        
        fig.update_layout(
            title='Power Consumption Over Time',
            xaxis_title='Time',
            yaxis_title='Power (Watts)',
            showlegend=True,
            hovermode='x unified'
        )
        
        return fig
    
    def create_power_distribution_plot(self) -> go.Figure:
        """Create a power distribution histogram"""
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=self.df['power_watts'],
            nbinsx=50,
            name='Power Distribution',
            histnorm='probability'
        ))
        
        # Add kernel density estimate
        kde = gaussian_kde(self.df['power_watts'])
        x_range = np.linspace(self.df['power_watts'].min(), self.df['power_watts'].max(), 100)
        y_range = kde(x_range)
        
        fig.add_trace(go.Scatter(
            x=x_range,
            y=y_range,
            mode='lines',
            name='KDE',
            line=dict(color='red')
        ))
        
        fig.update_layout(
            title='Power Consumption Distribution',
            xaxis_title='Power (Watts)',
            yaxis_title='Probability',
            showlegend=True
        )
        
        return fig
    
    def create_summary_plot(self) -> go.Figure:
        """Create a summary plot with multiple subplots"""
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Power Consumption Over Time', 'Power Distribution'),
            vertical_spacing=0.15
        )
        
        # Power vs time
        fig.add_trace(
            go.Scatter(
                x=self.df['timestamp'],
                y=self.df['power_watts'],
                mode='lines',
                name='Power'
            ),
            row=1, col=1
        )
        
        # Power distribution
        fig.add_trace(
            go.Histogram(
                x=self.df['power_watts'],
                nbinsx=50,
                name='Distribution'
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=800,
            showlegend=True,
            title_text="Power Analysis Summary"
        )
        
        return fig
    
    def analyze(self) -> PowerAnalysisResult:
        """Perform complete power analysis"""
        statistics = self.calculate_statistics()
        
        plots = {
            'power_time': self.create_power_time_plot(),
            'power_distribution': self.create_power_distribution_plot(),
            'summary': self.create_summary_plot()
        }
        
        metadata = {
            'start_time': self.df['timestamp'].min(),
            'end_time': self.df['timestamp'].max(),
            'sample_count': len(self.df),
            'monitor_type': self.df['monitor_type'].iloc[0] if 'monitor_type' in self.df.columns else None
        }
        
        return PowerAnalysisResult(
            raw_data=self.df,
            statistics=statistics,
            plots=plots,
            metadata=metadata
        )
    
    def export_results(self, output_dir: str):
        """Export analysis results to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Export raw data
        self.df.to_csv(os.path.join(output_dir, 'power_data.csv'), index=False)
        
        # Export statistics
        with open(os.path.join(output_dir, 'statistics.json'), 'w') as f:
            json.dump(self.calculate_statistics(), f, indent=2)
        
        # Export plots
        for name, fig in self.create_summary_plot().items():
            fig.write_html(os.path.join(output_dir, f'{name}_plot.html')) 