"""
Utility functions for F1 telemetry processing and 3D pipeline integration
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
import fastf1


def export_for_3d_pipeline(
    delta: np.ndarray,
    distances: np.ndarray, 
    summary_df: pd.DataFrame,
    driver1: str,
    driver2: str,
    laptime1: float,
    laptime2: float,
    session_info: Dict[str, Any],
    output_file: str = "telemetry_data.json"
) -> Dict[str, Any]:
    """
    Export processed telemetry data for 3D visualization pipeline
    
    Args:
        delta: Delta array from calculation
        distances: Distance array 
        summary_df: Summary dataframe with speeds
        driver1: First driver code
        driver2: Second driver code
        laptime1: First driver lap time
        laptime2: Second driver lap time
        session_info: Session metadata
        output_file: Output filename
        
    Returns:
        Dictionary containing all export data
    """
    
    # Create comprehensive export data structure
    export_data = {
        "metadata": {
            "session_year": session_info.get("year"),
            "session_type": session_info.get("type"), 
            "session_name": session_info.get("name"),
            "drivers": [driver1, driver2],
            "lap_times": [laptime1, laptime2],
            "total_distance": float(distances[-1] - distances[0]),
            "data_points": len(distances),
            "grid_resolution": float(distances[1] - distances[0]) if len(distances) > 1 else 5.0,
            "max_delta": float(max(abs(delta.min()), abs(delta.max()))),
            "export_timestamp": pd.Timestamp.now().isoformat()
        },
        "telemetry": {
            "distances": distances.tolist(),
            "delta": delta.tolist(),
            "speed_driver1": summary_df['Speed_Driver1'].tolist(),
            "speed_driver2": summary_df['Speed_Driver2'].tolist()
        },
        "animation_data": {
            # Pre-calculated data for smooth animations
            "position_markers": create_position_markers(distances, delta),
            "speed_zones": identify_speed_zones(summary_df),
            "overtaking_zones": find_overtaking_zones(delta, distances),
            "camera_waypoints": generate_camera_waypoints(distances, delta)
        }
    }
    
    # Save to file
    with open(output_file, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"Data exported to {output_file} for 3D pipeline")
    print(f"Total data points: {len(distances)}")
    print(f"Distance range: {distances[0]:.1f}m to {distances[-1]:.1f}m")
    
    return export_data


def create_position_markers(distances: np.ndarray, delta: np.ndarray, 
                           interval: float = 100.0) -> List[Dict]:
    """
    Create position markers for 3D animation at regular intervals
    """
    markers = []
    for dist in np.arange(distances[0], distances[-1], interval):
        idx = np.argmin(np.abs(distances - dist))
        markers.append({
            "distance": float(dist),
            "delta": float(delta[idx]),
            "position_advantage": "driver1" if delta[idx] > 0 else "driver2"
        })
    return markers


def identify_speed_zones(summary_df: pd.DataFrame) -> List[Dict]:
    """
    Identify high and low speed zones for visualization emphasis
    """
    speed1 = summary_df['Speed_Driver1'].values
    speed2 = summary_df['Speed_Driver2'].values
    distances = summary_df['Distance'].values
    
    avg_speed = (speed1 + speed2) / 2
    high_speed_threshold = np.percentile(avg_speed, 75)
    low_speed_threshold = np.percentile(avg_speed, 25)
    
    zones = []
    current_zone = None
    
    for i, speed in enumerate(avg_speed):
        if speed > high_speed_threshold:
            zone_type = "high_speed"
        elif speed < low_speed_threshold:
            zone_type = "low_speed"
        else:
            zone_type = "medium_speed"
        
        if current_zone is None or current_zone["type"] != zone_type:
            if current_zone is not None:
                current_zone["end_distance"] = float(distances[i-1])
                zones.append(current_zone)
            
            current_zone = {
                "type": zone_type,
                "start_distance": float(distances[i]),
                "avg_speed": float(speed)
            }
    
    if current_zone is not None:
        current_zone["end_distance"] = float(distances[-1])
        zones.append(current_zone)
    
    return zones


def find_overtaking_zones(delta: np.ndarray, distances: np.ndarray, 
                         threshold: float = 0.1) -> List[Dict]:
    """
    Find zones where the delta changes significantly (potential overtaking zones)
    """
    delta_gradient = np.gradient(delta, distances)
    significant_changes = np.abs(delta_gradient) > threshold / 1000  # Convert to per-meter
    
    overtaking_zones = []
    in_zone = False
    zone_start = None
    
    for i, is_significant in enumerate(significant_changes):
        if is_significant and not in_zone:
            in_zone = True
            zone_start = distances[i]
        elif not is_significant and in_zone:
            in_zone = False
            overtaking_zones.append({
                "start_distance": float(zone_start),
                "end_distance": float(distances[i]),
                "delta_change": float(delta[i] - delta[np.argmin(np.abs(distances - zone_start))]),
                "intensity": float(np.max(np.abs(delta_gradient[
                    np.logical_and(distances >= zone_start, distances <= distances[i])
                ])))
            })
    
    return overtaking_zones


def generate_camera_waypoints(distances: np.ndarray, delta: np.ndarray,
                             num_waypoints: int = 20) -> List[Dict]:
    """
    Generate camera waypoints for optimal viewing angles during 3D animation
    """
    waypoints = []
    indices = np.linspace(0, len(distances)-1, num_waypoints, dtype=int)
    
    for idx in indices:
        # Determine optimal camera angle based on delta magnitude
        delta_magnitude = abs(delta[idx])
        
        if delta_magnitude > 0.5:
            camera_style = "close_comparison"
            camera_distance = 15.0
        elif delta_magnitude > 0.2:
            camera_style = "medium_view" 
            camera_distance = 25.0
        else:
            camera_style = "wide_view"
            camera_distance = 40.0
        
        waypoints.append({
            "distance": float(distances[idx]),
            "delta": float(delta[idx]),
            "camera_style": camera_style,
            "camera_distance": camera_distance,
            "focus_point": "leader" if delta[idx] < 0 else "follower"
        })
    
    return waypoints


def validate_session(year: int, session_type: str, session_name: str) -> bool:
    """
    Validate that a session exists and can be loaded
    """
    try:
        session = fastf1.get_session(year, session_name, session_type)
        # Don't fully load, just check if it's valid
        return True
    except Exception as e:
        print(f"Invalid session: {year} {session_name} {session_type}")
        print(f"Error: {e}")
        return False


def get_available_drivers(year: int, session_type: str, session_name: str) -> List[str]:
    """
    Get list of available drivers for a session
    """
    try:
        session = fastf1.get_session(year, session_name, session_type)
        session.load()
        return session.laps['Driver'].unique().tolist()
    except Exception as e:
        print(f"Error loading session: {e}")
        return []


def calculate_sector_boundaries(distances: np.ndarray) -> Dict[str, float]:
    """
    Estimate sector boundaries based on track distance (rough approximation)
    """
    total_distance = distances[-1] - distances[0]
    
    return {
        "sector1_end": float(distances[0] + total_distance * 0.3),
        "sector2_end": float(distances[0] + total_distance * 0.65),
        "sector3_end": float(distances[-1])
    }


def smooth_delta(delta: np.ndarray, window_size: int = 5) -> np.ndarray:
    """
    Apply smoothing to delta for animation purposes
    """
    from scipy.ndimage import uniform_filter1d
    return uniform_filter1d(delta, size=window_size, mode='nearest')


def create_batch_export(calculator, driver_pairs: List[Tuple[str, str]], 
                       output_dir: str = "batch_exports") -> None:
    """
    Export multiple driver comparisons for batch processing
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    for i, (driver1, driver2) in enumerate(driver_pairs):
        try:
            delta, distances, summary_df, t1, t2 = calculator.calculate_delta(driver1, driver2)
            
            session_info = {
                "year": calculator.session_year,
                "type": calculator.session_type,
                "name": calculator.session_name
            }
            
            filename = f"{output_dir}/telemetry_{driver1}_vs_{driver2}.json"
            export_for_3d_pipeline(delta, distances, summary_df, driver1, driver2, 
                                 t1, t2, session_info, filename)
            
            print(f"Exported {i+1}/{len(driver_pairs)}: {driver1} vs {driver2}")
            
        except Exception as e:
            print(f"Error processing {driver1} vs {driver2}: {e}")
