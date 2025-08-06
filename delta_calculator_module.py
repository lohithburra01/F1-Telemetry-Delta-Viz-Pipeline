# This will contain your original F1TelemetryDeltaCalculator class
# Moving the content from your paste.txt file here with minor adjustments

import numpy as np
import pandas as pd
import fastf1
from scipy import interpolate
import matplotlib.pyplot as plt
from typing import Tuple, List, Dict, Optional
import warnings
from .visualization import plot_delta_comparison

warnings.filterwarnings('ignore')


class F1TelemetryDeltaCalculator:
    """
    Replicate F1InsightsHub's exact telemetry delta calculation methodology
    """
    
    def __init__(self, session_year: int, session_type: str, session_name: str):
        """Initialize with F1 session data"""
        self.session_year = session_year
        self.session_type = session_type
        self.session_name = session_name
        self.session = None
        self.load_session()
    
    def load_session(self):
        """Load F1 session data"""
        print(f"Loading {self.session_year} {self.session_name} {self.session_type}...")
        self.session = fastf1.get_session(self.session_year, self.session_name, self.session_type)
        self.session.load()
        print("Session loaded successfully!")
    
    def get_driver_telemetry(self, driver1: str, driver2: str, lap_type: str = 'fastest') -> Tuple[pd.DataFrame, pd.DataFrame, float, float]:
        """
        Extract telemetry for two drivers using FastF1 API
        Returns: tel1, tel2, real_laptime1, real_laptime2
        """
        if lap_type == 'fastest':
            lap1 = self.session.laps.pick_driver(driver1).pick_fastest()
            lap2 = self.session.laps.pick_driver(driver2).pick_fastest()
        else:
            # Could extend for other lap selection methods
            raise NotImplementedError("Only fastest lap supported currently")
        
        # Get raw telemetry - only Distance and Speed columns
        tel1_raw = lap1.get_telemetry()
        tel2_raw = lap2.get_telemetry()
        
        # Extract only Distance and Speed as per F1InsightsHub method
        tel1 = pd.DataFrame({
            'Distance': tel1_raw['Distance'].values,
            'Speed': tel1_raw['Speed'].values
        })
        
        tel2 = pd.DataFrame({
            'Distance': tel2_raw['Distance'].values,
            'Speed': tel2_raw['Speed'].values
        })
        
        # Get real lap times
        real_laptime1 = lap1['LapTime'].total_seconds()
        real_laptime2 = lap2['LapTime'].total_seconds()
        
        print(f"{driver1} lap time: {real_laptime1:.3f}s")
        print(f"{driver2} lap time: {real_laptime2:.3f}s")
        
        return tel1, tel2, real_laptime1, real_laptime2
    
    def calculate_custom_time(self, telemetry: pd.DataFrame, real_laptime: float) -> pd.DataFrame:
        """
        Step 1: Calculate custom time using integration method
        Ignore original timestamps completely
        """
        distances = telemetry['Distance'].values
        speeds_kmh = telemetry['Speed'].values
        
        # Calculate distance differentials
        ds = np.diff(distances)
        
        # Convert speed from km/h to m/s
        speeds_ms = speeds_kmh / 3.6
        
        # Calculate average speeds between points
        avg_speeds = (speeds_ms[:-1] + speeds_ms[1:]) / 2
        
        # Avoid division by zero
        avg_speeds = np.where(avg_speeds == 0, 0.001, avg_speeds)
        
        # Calculate time differentials
        dt = ds / avg_speeds
        
        # Calculate cumulative time starting from 0
        custom_time = np.cumsum(np.concatenate([[0], dt]))
        
        # Scale to real lap time
        if custom_time[-1] > 0:
            scaled_time = custom_time * (real_laptime / custom_time[-1])
        else:
            scaled_time = custom_time
        
        # Create result dataframe
        result = telemetry.copy()
        result['Time'] = scaled_time
        
        return result
    
    def windowed_mse_alignment(self, tel1: pd.DataFrame, tel2: pd.DataFrame, num_windows: int = 4) -> pd.DataFrame:
        """
        Step 2: Telemetry alignment using windowed MSE optimization
        """
        tel2_aligned = tel2.copy()
        
        # Get distance ranges
        min_dist = max(tel1['Distance'].min(), tel2['Distance'].min())
        max_dist = min(tel1['Distance'].max(), tel2['Distance'].max())
        
        # Create windows
        window_boundaries = np.linspace(min_dist, max_dist, num_windows + 1)
        
        print(f"Performing MSE alignment with {num_windows} windows...")
        
        for i in range(num_windows):
            window_start = window_boundaries[i]
            window_end = window_boundaries[i + 1]
            
            # Get data for this window
            mask1 = (tel1['Distance'] >= window_start) & (tel1['Distance'] <= window_end)
            mask2 = (tel2['Distance'] >= window_start) & (tel2['Distance'] <= window_end)
            
            window_tel1 = tel1[mask1].copy()
            window_tel2 = tel2[mask2].copy()
            
            if len(window_tel1) == 0 or len(window_tel2) == 0:
                continue
            
            # Test offsets from -15m to +15m
            best_offset = 0
            best_mse = float('inf')
            
            for offset in np.arange(-15, 16, 1):  # 1m steps
                # Apply offset to tel2 distances
                shifted_distances = window_tel2['Distance'].values + offset
                
                # Find common distance range
                common_min = max(window_tel1['Distance'].min(), shifted_distances.min())
                common_max = min(window_tel1['Distance'].max(), shifted_distances.max())
                
                if common_max <= common_min:
                    continue
                
                # Create interpolation grid
                common_grid = np.arange(common_min, common_max + 1, 1)
                
                # Interpolate speeds
                try:
                    speed1_interp = np.interp(common_grid, window_tel1['Distance'].values, window_tel1['Speed'].values)
                    speed2_interp = np.interp(common_grid, shifted_distances, window_tel2['Speed'].values)
                    
                    # Calculate MSE
                    mse = np.mean((speed1_interp - speed2_interp) ** 2)
                    
                    if mse < best_mse:
                        best_mse = mse
                        best_offset = offset
                        
                except:
                    continue
            
            # Apply best offset to this window
            window_mask = (tel2_aligned['Distance'] >= window_start) & (tel2_aligned['Distance'] <= window_end)
            tel2_aligned.loc[window_mask, 'Distance'] += best_offset
            
            print(f"Window {i+1}: offset = {best_offset}m, MSE = {best_mse:.2f}")
        
        return tel2_aligned
    
    def resample_on_common_grid(self, tel1: pd.DataFrame, tel2: pd.DataFrame, grid_step: float = 5.0) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Step 3: Resample both telemetries on common 5m grid
        """
        # Find common distance range
        common_min = max(tel1['Distance'].min(), tel2['Distance'].min())
        common_max = min(tel1['Distance'].max(), tel2['Distance'].max())
        
        # Generate uniform grid with 5m steps
        common_grid = np.arange(common_min, common_max + grid_step, grid_step)
        
        print(f"Resampling on common grid: {common_min:.1f}m to {common_max:.1f}m (step: {grid_step}m)")
        
        # Interpolate both telemetries onto common grid
        tel1_resampled = pd.DataFrame({
            'Distance': common_grid,
            'Speed': np.interp(common_grid, tel1['Distance'].values, tel1['Speed'].values),
            'Time': np.interp(common_grid, tel1['Distance'].values, tel1['Time'].values)
        })
        
        tel2_resampled = pd.DataFrame({
            'Distance': common_grid,
            'Speed': np.interp(common_grid, tel2['Distance'].values, tel2['Speed'].values),
            'Time': np.interp(common_grid, tel2['Distance'].values, tel2['Time'].values)
        })
        
        return tel1_resampled, tel2_resampled
    
    def calculate_integration_delta(self, tel1: pd.DataFrame, tel2: pd.DataFrame, time1_final: float, time2_final: float) -> np.ndarray:
        """
        Step 4: Delta calculation using segment-by-segment integration
        """
        # Convert speeds to m/s
        speed1 = tel1['Speed'].values / 3.6
        speed2 = tel2['Speed'].values / 3.6
        distances = tel1['Distance'].values
        
        # Calculate distance steps
        ds = np.diff(distances)
        
        # Determine reference driver (fastest)
        if time1_final < time2_final:
            ref_speed, slow_speed = speed1, speed2
            print("Driver 1 is reference (faster)")
        else:
            ref_speed, slow_speed = speed2, speed1
            print("Driver 2 is reference (faster)")
        
        # Integration method: calculate delta at each segment
        delta_cumulative = [0]  # Start at 0 seconds
        
        for i in range(len(ds)):
            # Average speeds over this segment
            avg_ref_speed = (ref_speed[i] + ref_speed[i+1]) / 2
            avg_slow_speed = (slow_speed[i] + slow_speed[i+1]) / 2
            
            # Avoid division by zero
            avg_ref_speed = max(avg_ref_speed, 0.001)
            avg_slow_speed = max(avg_slow_speed, 0.001)
            
            # Time for each driver over this segment
            dt_ref = ds[i] / avg_ref_speed
            dt_slow = ds[i] / avg_slow_speed
            
            # Delta for this segment
            dt_delta = dt_slow - dt_ref
            
            # Add to cumulative delta
            delta_cumulative.append(delta_cumulative[-1] + dt_delta)
        
        # Convert to numpy array
        delta_raw = np.array(delta_cumulative)
        
        # Scale final delta to match real lap time gap
        real_gap = abs(time1_final - time2_final)
        if abs(delta_raw[-1]) > 0:
            scale_factor = real_gap / abs(delta_raw[-1])
            delta_final = delta_raw * scale_factor
        else:
            delta_final = delta_raw
        
        print(f"Raw delta: {delta_raw[-1]:.3f}s")
        print(f"Real gap: {real_gap:.3f}s")
        print(f"Scale factor: {scale_factor:.3f}")
        print(f"Final delta: {delta_final[-1]:.3f}s")
        
        return delta_final
    
    def align_to_sector_times(self, delta: np.ndarray, distances: np.ndarray, 
                             sector_boundaries: Dict[str, float] = None) -> np.ndarray:
        """
        Step 5: Align delta to actual driven sector times (optional enhancement)
        """
        if sector_boundaries is None:
            print("No sector boundaries provided, skipping sector alignment")
            return delta
        
        # This would require sector time data and boundary positions
        # Implementation would depend on available sector timing data
        print("Sector alignment not implemented - would require sector timing data")
        return delta
    
    def calculate_delta(self, driver1: str, driver2: str, lap_type: str = 'fastest', 
                       num_windows: int = 4, grid_step: float = 5.0) -> Tuple[np.ndarray, np.ndarray, pd.DataFrame, float, float]:
        """
        Complete delta calculation pipeline following F1InsightsHub methodology
        """
        print(f"\n=== F1InsightsHub Delta Calculation: {driver1} vs {driver2} ===")
        
        # Step 1: Get raw telemetry
        print("\nStep 1: Raw Data Acquisition")
        tel1, tel2, real_laptime1, real_laptime2 = self.get_driver_telemetry(driver1, driver2, lap_type)
        
        # Calculate custom times
        print("\nCalculating custom times...")
        tel1_timed = self.calculate_custom_time(tel1, real_laptime1)
        tel2_timed = self.calculate_custom_time(tel2, real_laptime2)
        
        # Step 2: MSE Alignment
        print(f"\nStep 2: MSE Alignment ({num_windows} windows)")
        tel2_aligned = self.windowed_mse_alignment(tel1_timed, tel2_timed, num_windows)
        
        # Step 3: Resample on common grid
        print(f"\nStep 3: Resampling on {grid_step}m grid")
        tel1_final, tel2_final = self.resample_on_common_grid(tel1_timed, tel2_aligned, grid_step)
        
        # Step 4: Integration delta calculation
        print("\nStep 4: Integration Delta Calculation")
        delta = self.calculate_integration_delta(tel1_final, tel2_final, real_laptime1, real_laptime2)
        
        # Return results
        distances = tel1_final['Distance'].values
        
        # Create summary dataframe
        summary_df = pd.DataFrame({
            'Distance': distances,
            'Speed_Driver1': tel1_final['Speed'].values,
            'Speed_Driver2': tel2_final['Speed'].values,
            'Delta': delta
        })
        
        print(f"\n=== Calculation Complete ===")
        print(f"Final delta range: {delta.min():.3f}s to {delta.max():.3f}s")
        
        return delta, distances, summary_df, real_laptime1, real_laptime2
    
    def plot_comparison(self, delta: np.ndarray, distances: np.ndarray, 
                       driver1: str, driver2: str, laptime1: float, laptime2: float,
                       reference_delta: np.ndarray = None, style: str = 'f1insights',
                       save_path: Optional[str] = None):
        """
        Plot delta comparison using the visualization module
        """
        plot_delta_comparison(
            delta=delta,
            distances=distances,
            driver1=driver1,
            driver2=driver2,
            laptime1=laptime1,
            laptime2=laptime2,
            reference_delta=reference_delta,
            style=style,
            save_path=save_path
        )
    
    def get_session_info(self) -> Dict[str, any]:
        """Get session information for exports"""
        return {
            'year': self.session_year,
            'type': self.session_type,
            'name': self.session_name
        }
    
    def get_available_drivers(self) -> List[str]:
        """Get list of available drivers in the session"""
        if self.session is None:
            return []
        return self.session.laps['Driver'].unique().tolist()
    
    def export_data(self, delta: np.ndarray, distances: np.ndarray, 
                   summary_df: pd.DataFrame, driver1: str, driver2: str,
                   laptime1: float, laptime2: float, filename: str = None) -> str:
        """Export calculation results for 3D pipeline"""
        from .utils import export_for_3d_pipeline
        
        if filename is None:
            filename = f"telemetry_{driver1}_vs_{driver2}_{self.session_year}_{self.session_name}.json"
        
        session_info = self.get_session_info()
        
        export_for_3d_pipeline(
            delta=delta,
            distances=distances,
            summary_df=summary_df,
            driver1=driver1,
            driver2=driver2,
            laptime1=laptime1,
            laptime2=laptime2,
            session_info=session_info,
            output_file=filename
        )
        
        return filename