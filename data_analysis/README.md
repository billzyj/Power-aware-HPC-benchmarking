## INPUT
- Data under /input folder
- Three frameworks are used: deepspeed, transformers and vllm
- Three models are used for each framework Llama-3.1-8B Llama-3.2-1B Llama-3.2-3B
- In total: 3 * 3 =  9 json files
- In each json file, five batch sizes are used: 1, 2, 4, 8, 16 
- For each batch size, the object contains the metric energy/sec energy/token energy/response for GPU, CPU, RAM and TOTAL separately

## OUTPUT
The script `plot_energy_consumption.py` generates several types of visualizations to analyze energy consumption patterns:

### 1. Energy Comparison Plots
- Individual bar plots comparing energy consumption across frameworks for each model
- Generated for GPU, CPU, RAM, and total energy consumption
- Output files: `energy_comparison_*_energy_per_second.png`

### 2. Batch Size Scaling Plots
- Line plots showing how energy consumption scales with batch size
- Separate plots for each component (GPU, CPU, RAM)
- Helps visualize efficiency trends across different batch sizes
- Output files: `batch_size_scaling_*.png`

### 3. Energy Heatmaps
- Basic heatmaps showing energy consumption patterns across frameworks and models
- Generated for each energy metric (GPU, CPU, RAM, total)
- Output files: `energy_heatmap_*_energy_per_second.png`

### 4. Comprehensive Heatmaps
- Detailed heatmaps integrating batch size information
- Shows complete energy consumption patterns across all variables
- Output files: `comprehensive_heatmap_*_energy_per_second.png`

### 5. Component Breakdown Plot
- Stacked bar plot showing the contribution of each component to total energy
- Helps understand the distribution of energy consumption
- Output file: `component_breakdown.png`

### 6. Consolidated Stacked Bar Plot
- Single comprehensive visualization showing all data aspects:
  - X-axis: Framework-Model combinations grouped by batch size
  - Y-axis: Energy per Second (Joules)
  - Stacked components in order (bottom to top):
    1. GPU (Red)
    2. CPU (Blue)
    3. Memory (Green)
    4. Other (Orange)
  - Special features:
    - Black trend line showing GPU energy center values within each batch size group
    - Black dots marking total energy consumption on top of each bar
    - Handles missing data points gracefully (e.g., transformers Llama-3.1-8B for batch sizes 2, 8, and 16)
    - Models ordered by size (1B, 3B, 8B)
    - Clear batch size labels on top axis
    - Comprehensive legend showing all components and indicators
- Output file: `consolidated_stacked_bars.png`

## Usage
To generate all visualizations:
```bash
python data_analysis/plot_energy_consumption.py
```

All plots will be saved in the `data_analysis/output` directory.

## Plot Details
### Consolidated Stacked Bar Plot Features
1. **Component Stacking**:
   - Components are stacked in a consistent order
   - Each component has a distinct color for easy identification
   - "Other" component calculated as (Total - (GPU + CPU + Memory))

2. **GPU Trend Visualization**:
   - Black line connecting GPU center points within each batch size
   - Line drawn at half height of GPU component
   - Trend lines do not connect across missing data points

3. **Total Energy Indicators**:
   - Black dots on top of each bar showing total energy consumption
   - Only shown for bars with non-zero values
   - Helps quick comparison of total energy across configurations

4. **Data Organization**:
   - Batch sizes: 1, 2, 4, 8, 16
   - Nine bars per batch size (when data available)
   - Models sorted by size for consistent ordering
   - Clear spacing between batch size groups

### Energy Metrics
The visualizations cover the following metrics:
- `gpu_energy_per_second`: GPU energy consumption
- `cpu_energy_per_second`: CPU energy consumption
- `dram_energy_per_second`: Memory energy consumption
- `total_energy_per_second`: Total system energy consumption
- "Other" component: Calculated as (Total - (GPU + CPU + Memory))