"""
Advanced usage examples for F1 Telemetry Delta Calculator
Including batch processing, different visualization styles, and 3D pipeline integration
"""

from f1_telemetry import F1TelemetryDeltaCalculator, export_for_3d_pipeline
from f1_telemetry.visualization import plot_speed_comparison, create_dashboard
from f1_telemetry.utils import create_batch_export, smooth_delta
import numpy as np

def advanced_delta_analysis():
    """Advanced delta analysis with multiple visualization styles"""
    
    # Initialize calculator
    calculator = F1TelemetryDeltaCalculator(2024, 'Q', 'SILVERSTONE')
    
    # High-precision calculation with more windows and finer grid
    delta, distances, summary_df, t1, t2 = calculator.calculate_delta(
        driver1='VER',
        driver2='NOR',
        num_windows=8,      # More precise alignment
        grid_step=2.5       # Higher resolution
    )
    
    print("=== Advanced Visualization Styles ===")
    
    # 1. F1InsightsHub style
    print("1. Creating F1InsightsHub-style plot...")
    calculator.plot_comparison(delta, distances, 'VER', 'NOR', t1, t2, 
                              style='f1insights', save_path='plots/f1insights_style.png')
    
    # 2. Broadcast style
    print("2. Creating broadcast-style plot...")
    calculator.plot_comparison(delta, distances, 'VER', 'NOR', t1, t2,
                              style='broadcast', save_path='plots/broadcast_style.png')
    
    # 3. Technical analysis style
    print("3. Creating technical analysis plot...")
    calculator.plot_comparison(delta, distances, 'VER', 'NOR', t1, t2,
                              style='technical', save_path='plots/technical_style.png')
    
    # 4. Speed comparison
    print("4. Creating speed comparison...")
    plot_speed_comparison(summary_df, 'VER', 'NOR', style='both',
                         save_path='plots/speed_comparison.png')
    
    # 5. Comprehensive dashboard
    print("5. Creating comprehensive dashboard...")
    create_dashboard(delta, distances, summary_df, 'VER', 'NOR', t1, t2,
                    save_path='plots/dashboard.png')
    
    return delta, distances, summary_df, t1, t2

def batch_processing_example():
    """Process multiple driver comparisons for comprehensive analysis"""
    
    calculator = F1TelemetryDeltaCalculator(2024, 'Race', 'MONACO')
    
    # Define driver pairs for comparison
    driver_pairs = [
        ('VER', 'LEC'),
        ('HAM', 'RUS'),
        ('NOR', 'PIA'),
        ('ALO', 'STR')
    ]
    
    print("=== Batch Processing Multiple Comparisons ===")
    
    # Process all pairs
    create_batch_export(calculator, driver_pairs, output_dir='batch_output')
    
    print("Batch processing complete! Check 'batch_output' directory.")

def pipeline_integration_example():
    """Example of integrating with 3D visualization pipeline"""
    
    calculator = F1TelemetryDeltaCalculator(2024, 'Q', 'BAHRAIN')
    
    # Calculate delta with optimal settings for 3D animation
    delta, distances, summary_df, t1, t2 = calculator.calculate_delta(
        'VER', 'HAM',
        num_windows=6,      # Good precision
        grid_step=5.0       # Smooth animation
    )
    
    # Apply smoothing for animation
    delta_smooth = smooth_delta(delta, window_size=3)
    
    # Export with enhanced metadata for 3D pipeline
    session_info = calculator.get_session_info()
    
    export_data = export_for_3d_pipeline(
        delta=delta_smooth,
        distances=distances,
        summary_df=summary_df,
        driver1='VER',
        driver2='HAM',
        laptime1=t1,
        laptime2=t2,
        session_info=session_info,
        output_file='3d_pipeline_data.json'
    )
    
    print("=== 3D Pipeline Integration ===")
    print(f"Data exported with {len(export_data['animation_data']['position_markers'])} position markers")
    print(f"Speed zones identified: {len(export_data['animation_data']['speed_zones'])}")
    print(f"Overtaking zones: {len(export_data['animation_data']['overtaking_zones'])}")
    print(f"Camera waypoints: {len(export_data['animation_data']['camera_waypoints'])}")
    
    # Show how to use the exported data
    print("\n=== How to use in 3D Pipeline ===")
    print("1. Load the JSON file in your 3D application")
    print("2. Use 'telemetry.distances' and 'telemetry.delta' for car positioning")
    print("3. Use 'animation_data.position_markers' for key animation points")
    print("4. Use 'animation_data.camera_waypoints' for optimal camera angles")
    print("5. Reference: https://github.com/lohithburra01/F1-3D-VISUALIZATION")

def custom_analysis_example():
    """Custom analysis with validation and error checking"""
    
    # Validate session before processing
    from f1_telemetry.utils import validate_session
    
    if not validate_session(2024, 'Q', 'MONACO'):
        print("Invalid session specified!")
        return
    
    calculator = F1TelemetryDeltaCalculator(2024, 'Q', 'MONACO')
    
    # Get available drivers and validate
    available_drivers = calculator.get_available_drivers()
    print(f"Available drivers: {available_drivers}")
    
    if 'VER' not in available_drivers or 'LEC' not in available_drivers:
        print("Required drivers not available in this session")
        return
    
    # Perform calculation with error handling
    try:
        delta, distances, summary_df, t1, t2 = calculator.calculate_delta('VER', 'LEC')
        
        # Custom analysis
        max_gap = max(abs(delta.min()), abs(delta.max()))
        avg_gap = np.mean(np.abs(delta))
        
        print(f"\n=== Custom Analysis Results ===")
        print(f"Maximum gap: {max_gap:.3f}s")
        print(f"Average gap: {avg_gap:.3f}s")
        print(f"Gap variability: {np.std(delta):.3f}s")
        
        # Find biggest advantages
        ver_advantage_max = np.min(delta)  # Most negative = VER ahead
        lec_advantage_max = np.max(delta)  # Most positive = LEC ahead
        
        print(f"VER maximum advantage: {abs(ver_advantage_max):.3f}s")
        print(f"LEC maximum advantage: {lec_advantage_max:.3f}s")
        
        # Find distance where advantages occur
        ver_distance = distances[np.argmin(delta)]
        lec_distance = distances[np.argmax(delta)]
        
        print(f"VER advantage at: {ver_distance:.0f}m")
        print(f"LEC advantage at: {lec_distance:.0f}m")
        
    except Exception as e:
        print(f"Error in calculation: {e}")

def main():
    """Run all advanced examples"""
    
    import os
    
    # Create output directories
    os.makedirs('plots', exist_ok=True)
    os.makedirs('batch_output', exist_ok=True)
    
    print("F1 Telemetry Delta Calculator - Advanced Examples")
    print("=" * 50)
    
    try:
        # Run examples
        print("\n1. Advanced Delta Analysis...")
        advanced_delta_analysis()
        
        print("\n2. Batch Processing...")
        batch_processing_example()
        
        print("\n3. 3D Pipeline Integration...")
        pipeline_integration_example()
        
        print("\n4. Custom Analysis...")
        custom_analysis_example()
        
        print("\n=== All Examples Complete! ===")
        print("Check the output files and plots directory.")
        print("Data is ready for 3D visualization pipeline integration.")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure you have a stable internet connection for F1 data access.")

if __name__ == "__main__":
    main()
