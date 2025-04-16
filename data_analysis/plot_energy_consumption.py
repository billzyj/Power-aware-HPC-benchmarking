import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set style
plt.style.use('default')
sns.set_theme()

def load_data(input_dir):
    data = []
    for filename in os.listdir(input_dir):
        if filename.endswith('.json') and not filename.startswith('.'):
            with open(os.path.join(input_dir, filename), 'r') as f:
                json_data = json.load(f)
                
                # Extract framework and model from filename
                # Format: final_[framework]_models--models--meta-llama--[model]_[date].json
                parts = filename.split('_')
                framework = parts[1]  # deepspeed, transformers, or vllm
                
                # Extract model name - it's between "meta-llama--" and the date
                model_part = filename.split('meta-llama--')[1]
                model = model_part.split('_')[0]  # Llama-3.1-8B, Llama-3.2-1B, or Llama-3.2-3B
                
                # Process each batch size entry
                for entry in json_data[list(json_data.keys())[0]]:
                    entry['framework'] = framework
                    entry['model'] = model
                    data.append(entry)
    
    return pd.DataFrame(data)

def plot_energy_comparison(df, metric, title, output_dir):
    """Create grouped bar plots comparing energy consumption across frameworks"""
    plt.figure(figsize=(12, 6))
    
    # Group data by framework and model
    grouped = df.groupby(['framework', 'model'])[metric].mean().unstack()
    
    # Create bar plot
    ax = grouped.plot(kind='bar', width=0.8)
    
    plt.title(title)
    plt.xlabel('Framework')
    plt.ylabel('Energy Consumption')
    plt.xticks(rotation=45)
    plt.legend(title='Model', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    # Save plot
    plt.savefig(os.path.join(output_dir, f'energy_comparison_{metric}.png'), 
                bbox_inches='tight', dpi=300)
    plt.close()

def plot_batch_size_scaling(df, component, output_dir):
    """Create line plots showing energy consumption scaling with batch size"""
    plt.figure(figsize=(10, 6))
    
    for framework in df['framework'].unique():
        for model in df['model'].unique():
            subset = df[(df['framework'] == framework) & (df['model'] == model)]
            plt.plot(subset['batch_size'], 
                    subset[f'{component}_energy_per_second'],
                    marker='o',
                    label=f'{framework}-{model}')
    
    plt.title(f'{component} Energy Consumption vs Batch Size')
    plt.xlabel('Batch Size')
    plt.ylabel('Energy per Second (Joules)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    plt.tight_layout()
    
    plt.savefig(os.path.join(output_dir, f'batch_size_scaling_{component}.png'),
                bbox_inches='tight', dpi=300)
    plt.close()

def plot_energy_heatmap(df, metric, output_dir):
    """Create heatmap showing energy consumption patterns"""
    plt.figure(figsize=(12, 8))
    
    # Pivot data for heatmap
    pivot_data = df.pivot_table(
        values=metric,
        index='framework',
        columns='model',
        aggfunc='mean'
    )
    
    # Create heatmap
    sns.heatmap(pivot_data, annot=True, fmt='.2f', cmap='YlOrRd')
    plt.title(f'Energy Consumption Heatmap ({metric})')
    plt.tight_layout()
    
    plt.savefig(os.path.join(output_dir, f'energy_heatmap_{metric}.png'),
                bbox_inches='tight', dpi=300)
    plt.close()

def plot_comprehensive_heatmap(df, metric, output_dir):
    """Create a comprehensive heatmap that integrates batch size information"""
    plt.figure(figsize=(15, 10))
    
    # Create a multi-index for the heatmap
    # Format: (framework, model, batch_size)
    df['combined_index'] = df.apply(
        lambda row: f"{row['framework']}-{row['model']}-bs{row['batch_size']}", 
        axis=1
    )
    
    # Pivot the data for the heatmap
    pivot_data = df.pivot_table(
        values=metric,
        index='framework',
        columns=['model', 'batch_size'],
        aggfunc='mean'
    )
    
    # Flatten the column multi-index for better visualization
    pivot_data.columns = [f"{col[0]}-bs{col[1]}" for col in pivot_data.columns]
    
    # Create heatmap
    sns.heatmap(pivot_data, annot=True, fmt='.2f', cmap='YlOrRd', 
                cbar_kws={'label': f'Energy Consumption ({metric})'})
    
    plt.title(f'Comprehensive Energy Consumption Heatmap ({metric})')
    plt.xlabel('Model and Batch Size')
    plt.ylabel('Framework')
    plt.tight_layout()
    
    plt.savefig(os.path.join(output_dir, f'comprehensive_heatmap_{metric}.png'),
                bbox_inches='tight', dpi=300)
    plt.close()

def plot_component_breakdown(df, output_dir):
    """Create stacked bar plots showing component contribution to total energy"""
    plt.figure(figsize=(12, 6))
    
    # Calculate average energy consumption for each component
    components = ['gpu', 'cpu', 'dram']
    energy_data = []
    
    for framework in df['framework'].unique():
        for model in df['model'].unique():
            subset = df[(df['framework'] == framework) & (df['model'] == model)]
            row = {'framework': framework, 'model': model}
            for comp in components:
                row[f'{comp}_energy'] = subset[f'{comp}_energy_per_second'].mean()
            energy_data.append(row)
    
    energy_df = pd.DataFrame(energy_data)
    
    # Create stacked bar plot
    bottom = np.zeros(len(energy_df))
    for comp in components:
        plt.bar(range(len(energy_df)), 
                energy_df[f'{comp}_energy'],
                bottom=bottom,
                label=comp.upper())
        bottom += energy_df[f'{comp}_energy']
    
    plt.title('Component-wise Energy Consumption Breakdown')
    plt.xlabel('Framework-Model Combination')
    plt.ylabel('Energy per Second (Joules)')
    plt.xticks(range(len(energy_df)), 
               [f"{row['framework']}-{row['model']}" for _, row in energy_df.iterrows()],
               rotation=45)
    plt.legend()
    plt.tight_layout()
    
    plt.savefig(os.path.join(output_dir, 'component_breakdown.png'),
                bbox_inches='tight', dpi=300)
    plt.close()

def plot_stacked_bars_by_batch_size(df, output_dir):
    """Create stacked bar graphs for each batch size showing component breakdown"""
    # Define components and their colors
    components = ['gpu', 'cpu', 'dram']
    colors = ['#FF9999', '#66B2FF', '#99FF99']  # Red, Blue, Green
    
    # Get unique batch sizes
    batch_sizes = sorted(df['batch_size'].unique())
    
    # For each batch size, create a separate plot
    for batch_size in batch_sizes:
        plt.figure(figsize=(15, 8))
        
        # Filter data for this batch size
        batch_data = df[df['batch_size'] == batch_size]
        
        # Create a list of framework-model combinations
        combinations = []
        for framework in batch_data['framework'].unique():
            for model in batch_data['model'].unique():
                combinations.append((framework, model))
        
        # Set up the x-axis positions
        x = np.arange(len(combinations))
        width = 0.8
        
        # Initialize the bottom array for stacking
        bottom = np.zeros(len(combinations))
        
        # Create stacked bars for each component
        for i, comp in enumerate(components):
            values = []
            for framework, model in combinations:
                subset = batch_data[(batch_data['framework'] == framework) & 
                                   (batch_data['model'] == model)]
                if not subset.empty:
                    values.append(subset[f'{comp}_energy_per_second'].mean())
                else:
                    values.append(0)
            
            plt.bar(x, values, width, bottom=bottom, label=comp.upper(), color=colors[i])
            bottom += values
        
        # Add total energy line on top
        total_values = []
        for framework, model in combinations:
            subset = batch_data[(batch_data['framework'] == framework) & 
                               (batch_data['model'] == model)]
            if not subset.empty:
                total_values.append(subset['total_energy_per_second'].mean())
            else:
                total_values.append(0)
        
        plt.plot(x, total_values, 'ko-', label='Total', linewidth=2)
        
        # Customize the plot
        plt.title(f'Energy Consumption Breakdown by Component (Batch Size: {batch_size})')
        plt.xlabel('Framework-Model Combination')
        plt.ylabel('Energy per Second (Joules)')
        plt.xticks(x, [f"{fw}-{md}" for fw, md in combinations], rotation=45)
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Save the plot
        plt.savefig(os.path.join(output_dir, f'stacked_bars_batch_{batch_size}.png'),
                    bbox_inches='tight', dpi=300)
        plt.close()

def plot_consolidated_stacked_bars(df, output_dir):
    """Create a single stacked bar graph with all batch sizes grouped together"""
    plt.figure(figsize=(20, 10))
    
    # Define components and their colors (in stacking order)
    colors = ['#FF4444', '#4444FF', '#44FF44', '#FFB000']  # Red, Blue, Green, Orange
    components_with_other = ['gpu', 'cpu', 'dram', 'other']
    legend_labels = ['GPU', 'CPU', 'MEM', 'Other']
    
    # Get unique values and sort them in desired order
    batch_sizes = sorted(df['batch_size'].unique())
    frameworks = sorted(df['framework'].unique())
    # Sort models in order of size
    models = sorted(df['model'].unique(), 
                   key=lambda x: float(x.split('-')[-1].replace('B', '')))
    
    # Calculate the number of groups and bars
    n_combinations = len(frameworks) * len(models)  # 9 combinations
    n_groups = len(batch_sizes)  # 5 batch sizes
    bar_width = 0.8
    group_width = n_combinations + 2  # Add some space between groups
    
    # Create positions for bars
    positions = []
    gpu_data_by_batch = {batch_size: {'positions': [], 'values': [], 'valid_indices': []} 
                        for batch_size in batch_sizes}
    
    for i in range(n_groups):
        group_start = i * group_width
        for j in range(n_combinations):
            positions.append(group_start + j)
    
    # Prepare data
    data = []
    labels = []
    total_values = []  # Store total energy values for markers
    
    # First, collect all data in order
    for batch_size in batch_sizes:
        batch_positions = []
        batch_gpu_values = []
        valid_indices = []  # Track valid data points for this batch size
        idx = 0
        
        for framework in frameworks:
            for model in models:
                subset = df[(df['batch_size'] == batch_size) & 
                          (df['framework'] == framework) & 
                          (df['model'] == model)]
                
                current_position = positions[len(data)]
                
                if not subset.empty:
                    row = {
                        'position': current_position,
                        'batch_size': batch_size,
                        'framework': framework,
                        'model': model
                    }
                    # Calculate components
                    row['gpu'] = subset['gpu_energy_per_second'].mean()
                    row['cpu'] = subset['cpu_energy_per_second'].mean()
                    row['dram'] = subset['dram_energy_per_second'].mean()
                    row['total'] = subset['total_energy_per_second'].mean()
                    # Calculate 'other' as the difference between total and sum of components
                    components_sum = row['gpu'] + row['cpu'] + row['dram']
                    row['other'] = max(0, row['total'] - components_sum)  # Ensure non-negative
                    
                    data.append(row)
                    total_values.append((current_position, row['total']))
                    
                    # Store GPU data for trend lines only if data exists
                    batch_positions.append(current_position)
                    batch_gpu_values.append(row['gpu'])
                    valid_indices.append(idx)
                else:
                    # Add placeholder for missing data
                    data.append({
                        'position': current_position,
                        'batch_size': batch_size,
                        'framework': framework,
                        'model': model,
                        'gpu': 0,
                        'cpu': 0,
                        'dram': 0,
                        'other': 0,
                        'total': 0
                    })
                    total_values.append((current_position, 0))
                
                labels.append(f"{framework}-{model}")
                idx += 1
        
        # Store the batch data in order
        gpu_data_by_batch[batch_size] = {
            'positions': batch_positions,
            'values': batch_gpu_values,
            'valid_indices': valid_indices
        }
    
    # Convert to DataFrame for easier plotting
    plot_df = pd.DataFrame(data)
    
    # Create stacked bars in specified order: GPU, CPU, MEM, Other
    bottom = np.zeros(len(plot_df))
    
    # Create patches for legend
    patches = []
    for i, (comp, label, color) in enumerate(zip(components_with_other, legend_labels, colors)):
        bar = plt.bar(plot_df['position'], plot_df[comp], 
                     bar_width, bottom=bottom, 
                     color=color)
        bottom += plot_df[comp]
        patches.append(plt.Rectangle((0,0), 1, 1, fc=color, label=label))
    
    # Add GPU trend lines at half height
    for batch_size in batch_sizes:
        batch_data = gpu_data_by_batch[batch_size]
        if batch_data['positions'] and batch_data['values']:  # Only plot if we have data
            positions = batch_data['positions']
            # Calculate the center point (half of GPU value)
            gpu_centers = [value/2 for value in batch_data['values']]
            
            # Add line plot for GPU values
            line = plt.plot(positions, gpu_centers, 'k-', linewidth=2, zorder=5)
            # Add markers at each point
            plt.plot(positions, gpu_centers, 'ko', markersize=4, zorder=5)
            
            if batch_size == batch_sizes[0]:  # Add to legend only once
                patches.append(plt.Line2D([0], [0], color='black', linewidth=2, 
                                        label='GPU Center Trend'))
    
    # Add total energy markers on top of bars
    for pos, total in total_values:
        if total > 0:  # Only add markers for non-zero values
            plt.plot(pos, total, 'ko', markersize=6, zorder=5)
    
    # Add marker to legend
    patches.append(plt.Line2D([0], [0], color='black', marker='o', linestyle='None',
                             markersize=6, label='Total Energy'))
    
    # Customize the plot
    plt.title('Energy Consumption Breakdown by Component and Batch Size', fontsize=14)
    plt.xlabel('Framework-Model Combinations', fontsize=12)
    plt.ylabel('Energy per Second (Joules)', fontsize=12)
    
    # Set x-ticks at the center of each group
    group_centers = []
    group_labels = []
    for i in range(n_groups):
        center = i * group_width + (n_combinations - 1) / 2
        group_centers.append(center)
        group_labels.append(f'Batch Size {batch_sizes[i]}')
    
    # Add two sets of x-ticks
    ax = plt.gca()
    ax.set_xticks(plot_df['position'])
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=10)
    
    # Add batch size labels
    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())
    ax2.set_xticks(group_centers)
    ax2.set_xticklabels(group_labels, fontsize=12)
    
    # Add grid and legend
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Create legend with custom patches
    plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), 
              loc='upper left', fontsize=12)
    
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(os.path.join(output_dir, 'consolidated_stacked_bars.png'),
                bbox_inches='tight', dpi=300)
    plt.close()

def main():
    # Create output directory
    output_dir = Path('data_analysis/output')
    output_dir.mkdir(exist_ok=True)
    
    # Load data
    df = load_data('data_analysis/input')
    
    # Generate plots
    metrics = ['gpu_energy_per_second', 'cpu_energy_per_second', 
               'dram_energy_per_second', 'total_energy_per_second']
    
    for metric in metrics:
        plot_energy_comparison(df, metric, 
                             f'Energy Consumption Comparison ({metric})',
                             output_dir)
        plot_energy_heatmap(df, metric, output_dir)
        plot_comprehensive_heatmap(df, metric, output_dir)
    
    components = ['gpu', 'cpu', 'dram']
    for component in components:
        plot_batch_size_scaling(df, component, output_dir)
    
    plot_component_breakdown(df, output_dir)
    plot_stacked_bars_by_batch_size(df, output_dir)
    plot_consolidated_stacked_bars(df, output_dir)

if __name__ == "__main__":
    main() 