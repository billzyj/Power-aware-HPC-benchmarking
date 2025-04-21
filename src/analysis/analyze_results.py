from pathlib import Path

def run_analysis_pipeline(data_dir='results/raw', output_dir='results/processed'):
    """Run the complete analysis pipeline."""
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all data files
    power_files = list(Path(data_dir).glob('power_data_*.json'))
    benchmark_files = list(Path(data_dir).glob('*.txt'))

    # ... existing code ... 