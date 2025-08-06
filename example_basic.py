"""
Basic usage example for F1 Telemetry Delta Calculator
"""

from f1_telemetry import F1TelemetryDeltaCalculator

def main():
    # Initialize calculator for 2024 Bahrain Qualifying
    calculator = F1TelemetryDeltaCalculator(2024, 'Q', 'BAHRAIN')
    
    # Show available drivers
    drivers = calculator.get_available_drivers()
    print(f"Available drivers: {drivers}")
    
    # Calculate delta between Verstappen and Hamilton
    delta, distances, summary_df, laptime1, laptime2 = calculator.calculate_delta('VER', 'HAM')
    
    # Create professional F1InsightsHub-style visualization
    calculator.plot_comparison(
        delta=delta,
        distances=distances, 
        driver1='VER',
        driver2='HAM',
        laptime1=laptime1,
        laptime2=laptime2,
        style='f1insights'
    )
    
    # Export data for 3D pipeline
    filename = calculator.export_data(
        delta=delta,
        distances=distances,
        summary_df=summary_df,
        driver1='VER',
        driver2='HAM',
        laptime1=laptime1,
        laptime2=laptime2
    )
    
    print(f"Data exported to: {filename}")
    print(f"Ready for 3D visualization pipeline!")
    
    # Print summary statistics
    print("\n=== Summary Statistics ===")
    print(f"Maximum gap: {max(abs(delta.min()), abs(delta.max())):.3f}s")
    print(f"Average delta: {delta.mean():.3f}s")
    print(f"Total distance: {distances[-1] - distances[0]:.1f}m")
    print(f"Data points: {len(distances)}")

if __name__ == "__main__":
    main()
