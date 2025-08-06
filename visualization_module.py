"""
Professional visualization tools for F1 telemetry data
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Optional, Dict, Any
from matplotlib.ticker import FuncFormatter


class F1PlotStyle:
    """
    Professional F1 styling for telemetry visualizations
    """
    
    # F1 team colors (approximate)
    TEAM_COLORS = {
        'VER': '#1E41FF',  # Red Bull - Blue
        'PER': '#1E41FF',  # Red Bull - Blue
        'HAM': '#00D2BE',  # Mercedes - Teal
        'RUS': '#00D2BE',  # Mercedes - Teal
        'LEC': '#DC143C',  # Ferrari - Red
        'SAI': '#DC143C',  # Ferrari - Red
        'NOR': '#FF8700',  # McLaren - Orange
        'PIA': '#FF8700',  # McLaren - Orange
        'ALO': '#006F62',  # Aston Martin - Green
        'STR': '#006F62',  # Aston Martin - Green
    }
    
    # Default colors for unknown drivers
    DEFAULT_COLORS = ['#4A9EFF', '#00D4AA', '#FF6B6B', '#4ECDC4', '#45B7D1']
    
    @staticmethod
    def get_driver_color(driver: str, index: int = 0) -> str:
        """Get color for a specific driver"""
        if driver in F1PlotStyle.TEAM_COLORS:
            return F1PlotStyle.TEAM_COLORS[driver]
        return F1PlotStyle.DEFAULT_COLORS[index % len(F1PlotStyle.DEFAULT_COLORS)]
    
    @staticmethod
    def setup_dark_theme():
        """Setup dark theme for professional look"""
        plt.style.use('dark_background')
        plt.rcParams.update({
            'figure.facecolor': '#1a1a1a',
            'axes.facecolor': '#1a1a1a',
            'axes.edgecolor': '#666666',
            'axes.labelcolor': 'white',
            'xtick.color': 'white',
            'ytick.color': 'white',
            'text.color': 'white',
            'grid.color': '#333333',
            'grid.alpha': 0.7
        })
    
    @staticmethod
    def reset_style():
        """Reset to default matplotlib style"""
        plt.style.use('default')
        plt.rcParams.update(plt.rcParamsDefault)


def plot_delta_comparison(
    delta: np.ndarray,
    distances: np.ndarray,
    driver1: str,
    driver2: str,
    laptime1: float,
    laptime2: float,
    reference_delta: Optional[np.ndarray] = None,
    style: str = 'f1insights',
    title: Optional[str] = None,
    save_path: Optional[str] = None
) -> None:
    """
    Create professional delta comparison plot
    
    Args:
        delta: Delta time array
        distances: Distance array
        driver1: First driver code
        driver2: Second driver code  
        laptime1: First driver lap time
        laptime2: Second driver lap time
        reference_delta: Optional reference delta for comparison
        style: Plot style ('f1insights', 'broadcast', or 'technical')
        title: Custom title
        save_path: Path to save the plot
    """
    
    if style == 'f1insights':
        _plot_f1insights_style(delta, distances, driver1, driver2, laptime1, laptime2, 
                              reference_delta, title, save_path)
    elif style == 'broadcast':
        _plot_broadcast_style(delta, distances, driver1, driver2, laptime1, laptime2,
                             reference_delta, title, save_path)
    elif style == 'technical':
        _plot_technical_style(delta, distances, driver1, driver2, laptime1, laptime2,
                              reference_delta, title, save_path)
    else:
        raise ValueError(f"Unknown style: {style}")


def _plot_f1insights_style(
    delta: np.ndarray,
    distances: np.ndarray, 
    driver1: str,
    driver2: str,
    laptime1: float,
    laptime2: float,
    reference_delta: Optional[np.ndarray] = None,
    title: Optional[str] = None,
    save_path: Optional[str] = None
) -> None:
    """F1InsightsHub-style delta plot"""
    F1PlotStyle.setup_dark_theme()
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 6))
    fig.patch.set_facecolor('#1a1a1a')
    ax.set_facecolor('#1a1a1a')
    
    # Get driver colors
    color1 = F1PlotStyle.get_driver_color(driver1, 0)
    color2 = F1PlotStyle.get_driver_color(driver2, 1)
    
    # Plot delta line
    if reference_delta is not None:
        ax.plot(distances, reference_delta, color='#888888', linewidth=2, alpha=0.7, label='Reference')
    
    ax.plot(distances, delta, color=color2, linewidth=3)
    ax.axhline(y=0, color=color1, linewidth=2, alpha=0.8)
    
    # Styling
    ax.set_xlabel('')
    ax.set_ylabel('Delta', fontsize=12, color='white', rotation=90, labelpad=20)
    ax.grid(True, color='#333333', linewidth=0.5, alpha=0.7)
    ax.set_axisbelow(True)
    
    # Format lap times for title
    laptime1_str = f"{int(laptime1//60)}:{laptime1%60:06.3f}"
    laptime2_str = f"{int(laptime2//60)}:{laptime2%60:06.3f}"
    
    if title is None:
        title = f"● {driver1} - {laptime1_str}    ● {driver2} - {laptime2_str}"
    
    ax.set_title(title, fontsize=14, color='white', pad=20, loc='center')
    
    # Set limits and formatting
    y_max = max(abs(delta.min()), abs(delta.max()))
    ax.set_ylim(-y_max * 1.1, y_max * 1.1)
    ax.set_xlim(distances[0], distances[-1])
    
    # Format axes
    ax.tick_params(axis='both', colors='white', labelsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#666666')
    ax.spines['bottom'].set_color('#666666')
    
    # Format y-axis
    def format_delta(x, p):
        return f'{x:.3f}'
    ax.yaxis.set_major_formatter(FuncFormatter(format_delta))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='#1a1a1a')
    
    plt.show()
    F1PlotStyle.reset_style()


def _plot_broadcast_style(
    delta: np.ndarray,
    distances: np.ndarray,
    driver1: str,
    driver2: str, 
    laptime1: float,
    laptime2: float,
    reference_delta: Optional[np.ndarray] = None,
    title: Optional[str] = None,
    save_path: Optional[str] = None
) -> None:
    """Broadcast-style delta plot with additional information"""
    F1PlotStyle.setup_dark_theme()
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), height_ratios=[3, 1])
    fig.patch.set_facecolor('#1a1a1a')
    
    # Main delta plot
    color1 = F1PlotStyle.get_driver_color(driver1, 0)
    color2 = F1PlotStyle.get_driver_color(driver2, 1)
    
    ax1.plot(distances, delta, color=color2, linewidth=4, label=f'{driver2} vs {driver1}')
    ax1.axhline(y=0, color=color1, linewidth=2, alpha=0.8, label=f'{driver1} Reference')
    
    if reference_delta is not None:
        ax1.plot(distances, reference_delta, color='white', linewidth=2, alpha=0.5, linestyle='--', label='Reference Delta')
    
    # Fill areas
    ax1.fill_between(distances, delta, 0, where=(delta >= 0), alpha=0.3, color=color2, label=f'{driver2} Behind')
    ax1.fill_between(distances, delta, 0, where=(delta < 0), alpha=0.3, color=color1, label=f'{driver1} Behind')
    
    ax1.set_ylabel('Gap (seconds)', fontsize=14, color='white')
    ax1.grid(True, color='#333333', linewidth=0.5, alpha=0.7)
    ax1.legend(loc='upper right', facecolor='#2a2a2a', edgecolor='white')
    
    # Gap evolution plot
    gap_evolution = np.abs(delta)
    ax2.plot(distances, gap_evolution, color='yellow', linewidth=2)
    ax2.fill_between(distances, gap_evolution, alpha=0.3, color='yellow')
    ax2.set_ylabel('Absolute Gap', fontsize=12, color='white')
    ax2.set_xlabel('Distance (m)', fontsize=12, color='white')
    ax2.grid(True, color='#333333', linewidth=0.5, alpha=0.7)
    
    # Format both axes
    for ax in [ax1, ax2]:
        ax.set_facecolor('#1a1a1a')
        ax.tick_params(axis='both', colors='white', labelsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#666666')
        ax.spines['bottom'].set_color('#666666')
    
    if title is None:
        laptime1_str = f"{int(laptime1//60)}:{laptime1%60:06.3f}"
        laptime2_str = f"{int(laptime2//60)}:{laptime2%60:06.3f}"
        title = f"Telemetry Comparison: {driver1} ({laptime1_str}) vs {driver2} ({laptime2_str})"
    
    fig.suptitle(title, fontsize=16, color='white', y=0.95)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='#1a1a1a')
    
    plt.show()
    F1PlotStyle.reset_style()


def _plot_technical_style(
    delta: np.ndarray,
    distances: np.ndarray,
    driver1: str, 
    driver2: str,
    laptime1: float,
    laptime2: float,
    reference_delta: Optional[np.ndarray] = None,
    title: Optional[str] = None,
    save_path: Optional[str] = None
) -> None:
    """Technical analysis style with detailed metrics"""
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    fig.patch.set_facecolor('white')
    
    # Main delta plot
    ax1 = axes[0, 0]
    ax1.plot(distances, delta, 'b-', linewidth=2, label='Calculated Delta')
    if reference_delta is not None:
        ax1.plot(distances, reference_delta, 'r--', linewidth=2, label='Reference Delta')
        diff = delta - reference_delta
        ax1.fill_between(distances, delta, reference_delta, alpha=0.3, color='orange')
    
    ax1.axhline(y=0, color='k', linestyle='-', alpha=0.5)
    ax1.set_xlabel('Distance (m)')
    ax1.set_ylabel('Delta (s)')
    ax1.set_title('Delta Analysis')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Delta gradient
    ax2 = axes[0, 1]
    delta_gradient = np.gradient(delta, distances)
    ax2.plot(distances, delta_gradient * 1000, 'g-', linewidth=2)  # Convert to ms/m
    ax2.axhline(y=0, color='k', linestyle='-', alpha=0.5)
    ax2.set_xlabel('Distance (m)')
    ax2.set_ylabel('Delta Gradient (ms/m)')
    ax2.set_title('Delta Rate of Change')
    ax2.grid(True, alpha=0.3)
    
    # Statistics panel
    ax3 = axes[1, 0]
    ax3.axis('off')
    
    stats_text = f"""
DELTA STATISTICS
────────────────────
Max Gap: {max(abs(delta.min()), abs(delta.max())):.3f}s
Mean Delta: {np.mean(delta):.3f}s
Std Deviation: {np.std(delta):.3f}s
Total Distance: {distances[-1] - distances[0]:.1f}m
Data Points: {len(distances)}

LAP TIMES
────────────────────
{driver1}: {laptime1:.3f}s
{driver2}: {laptime2:.3f}s
Real Gap: {abs(laptime2 - laptime1):.3f}s
"""
    
    if reference_delta is not None:
        diff = delta - reference_delta
        stats_text += f"""
ACCURACY METRICS
────────────────────
Mean Error: {np.mean(diff):.4f}s
MAE: {np.mean(np.abs(diff)):.4f}s
RMSE: {np.sqrt(np.mean(diff**2)):.4f}s
Max Error: {np.max(np.abs(diff)):.4f}s
"""
    
    ax3.text(0.05, 0.95, stats_text, transform=ax3.transAxes, fontsize=11,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    # Error analysis (if reference available)
    ax4 = axes[1, 1]
    if reference_delta is not None:
        diff = delta - reference_delta
        ax4.plot(distances, diff, 'purple', linewidth=2)
        ax4.fill_between(distances, diff, 0, alpha=0.3, color='purple')
        ax4.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        ax4.set_xlabel('Distance (m)')
        ax4.set_ylabel('Error (s)')
        ax4.set_title('Calculation Error vs Reference')
        ax4.grid(True, alpha=0.3)
    else:
        ax4.axis('off')
        ax4.text(0.5, 0.5, 'No Reference\nData Available', 
                transform=ax4.transAxes, ha='center', va='center',
                fontsize=14, alpha=0.5)
    
    if title is None:
        title = f"Technical Analysis: {driver1} vs {driver2}"
    
    fig.suptitle(title, fontsize=16, y=0.95)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def plot_speed_comparison(
    summary_df,
    driver1: str,
    driver2: str,
    style: str = 'overlay',
    save_path: Optional[str] = None
) -> None:
    """
    Plot speed comparison between two drivers
    
    Args:
        summary_df: DataFrame with Distance, Speed_Driver1, Speed_Driver2 columns
        driver1: First driver code
        driver2: Second driver code
        style: 'overlay', 'difference', or 'both'
        save_path: Path to save the plot
    """
    F1PlotStyle.setup_dark_theme()
    
    distances = summary_df['Distance'].values
    speed1 = summary_df['Speed_Driver1'].values
    speed2 = summary_df['Speed_Driver2'].values
    
    color1 = F1PlotStyle.get_driver_color(driver1, 0)
    color2 = F1PlotStyle.get_driver_color(driver2, 1)
    
    if style == 'both':
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))
        fig.patch.set_facecolor('#1a1a1a')
        
        # Speed overlay
        ax1.plot(distances, speed1, color=color1, linewidth=2, label=driver1)
        ax1.plot(distances, speed2, color=color2, linewidth=2, label=driver2)
        ax1.set_ylabel('Speed (km/h)', color='white')
        ax1.set_title('Speed Comparison', color='white')
        ax1.legend()
        ax1.grid(True, color='#333333', alpha=0.7)
        
        # Speed difference
        speed_diff = speed1 - speed2
        ax2.plot(distances, speed_diff, color='yellow', linewidth=2)
        ax2.fill_between(distances, speed_diff, 0, where=(speed_diff >= 0), 
                        alpha=0.3, color=color1, label=f'{driver1} Faster')
        ax2.fill_between(distances, speed_diff, 0, where=(speed_diff < 0),
                        alpha=0.3, color=color2, label=f'{driver2} Faster')
        ax2.axhline(y=0, color='white', linewidth=1, alpha=0.8)
        ax2.set_xlabel('Distance (m)', color='white')
        ax2.set_ylabel('Speed Difference (km/h)', color='white')
        ax2.set_title('Speed Advantage', color='white')
        ax2.legend()
        ax2.grid(True, color='#333333', alpha=0.7)
        
        for ax in [ax1, ax2]:
            ax.set_facecolor('#1a1a1a')
            ax.tick_params(axis='both', colors='white')
            for spine in ax.spines.values():
                spine.set_color('#666666')
    
    else:
        fig, ax = plt.subplots(1, 1, figsize=(16, 6))
        fig.patch.set_facecolor('#1a1a1a')
        ax.set_facecolor('#1a1a1a')
        
        if style == 'overlay':
            ax.plot(distances, speed1, color=color1, linewidth=2, label=driver1)
            ax.plot(distances, speed2, color=color2, linewidth=2, label=driver2)
            ax.set_ylabel('Speed (km/h)', color='white')
            ax.set_title('Speed Comparison', color='white')
        
        elif style == 'difference':
            speed_diff = speed1 - speed2
            ax.plot(distances, speed_diff, color='yellow', linewidth=2)
            ax.fill_between(distances, speed_diff, 0, alpha=0.3, color='yellow')
            ax.axhline(y=0, color='white', linewidth=1, alpha=0.8)
            ax.set_ylabel('Speed Difference (km/h)', color='white')
            ax.set_title(f'Speed Advantage: {driver1} vs {driver2}', color='white')
        
        ax.set_xlabel('Distance (m)', color='white')
        ax.legend()
        ax.grid(True, color='#333333', alpha=0.7)
        ax.tick_params(axis='both', colors='white')
        
        for spine in ax.spines.values():
            spine.set_color('#666666')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='#1a1a1a')
    
    plt.show()
    F1PlotStyle.reset_style()


def create_dashboard(
    delta: np.ndarray,
    distances: np.ndarray,
    summary_df,
    driver1: str,
    driver2: str,
    laptime1: float,
    laptime2: float,
    save_path: Optional[str] = None
) -> None:
    """
    Create comprehensive dashboard with multiple analysis panels
    """
    F1PlotStyle.setup_dark_theme()
    
    fig = plt.figure(figsize=(20, 12))
    fig.patch.set_facecolor('#1a1a1a')
    
    # Create grid layout
    gs = fig.add_gridspec(3, 3, height_ratios=[2, 2, 1], width_ratios=[2, 2, 1])
    
    # Main delta plot
    ax1 = fig.add_subplot(gs[0, :2])
    color1 = F1PlotStyle.get_driver_color(driver1, 0)
    color2 = F1PlotStyle.get_driver_color(driver2, 1)
    
    ax1.plot(distances, delta, color=color2, linewidth=3)
    ax1.axhline(y=0, color=color1, linewidth=2, alpha=0.8)
    ax1.set_ylabel('Delta (s)', color='white', fontsize=12)
    ax1.set_title('Lap Time Delta Analysis', color='white', fontsize=14)
    ax1.grid(True, color='#333333', alpha=0.7)
    
    # Speed comparison
    ax2 = fig.add_subplot(gs[1, :2])
    speed1 = summary_df['Speed_Driver1'].values
    speed2 = summary_df['Speed_Driver2'].values
    
    ax2.plot(distances, speed1, color=color1, linewidth=2, label=driver1)
    ax2.plot(distances, speed2, color=color2, linewidth=2, label=driver2)
    ax2.set_ylabel('Speed (km/h)', color='white', fontsize=12)
    ax2.set_xlabel('Distance (m)', color='white', fontsize=12)
    ax2.set_title('Speed Comparison', color='white', fontsize=14)
    ax2.legend()
    ax2.grid(True, color='#333333', alpha=0.7)
    
    # Statistics panel
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.axis('off')
    
    laptime1_str = f"{int(laptime1//60)}:{laptime1%60:06.3f}"
    laptime2_str = f"{int(laptime2//60)}:{laptime2%60:06.3f}"
    
    stats_text = f"""
LAP TIMES
─────────────
{driver1}: {laptime1_str}
{driver2}: {laptime2_str}
Gap: {abs(laptime2-laptime1):.3f}s

DELTA STATS
─────────────
Max: {delta.max():.3f}s
Min: {delta.min():.3f}s
Range: {delta.max()-delta.min():.3f}s
Avg: {np.mean(delta):.3f}s

DISTANCE
─────────────
Total: {distances[-1]-distances[0]:.0f}m
Points: {len(distances)}
Resolution: {distances[1]-distances[0]:.1f}m
"""
    
    ax3.text(0.05, 0.95, stats_text, transform=ax3.transAxes, fontsize=11,
             verticalalignment='top', fontfamily='monospace', color='white',
             bbox=dict(boxstyle='round', facecolor='#2a2a2a', alpha=0.8))
    
    # Speed statistics
    ax4 = fig.add_subplot(gs[1, 2])
    ax4.axis('off')
    
    speed_stats = f"""
SPEED STATS
─────────────
{driver1}:
  Max: {speed1.max():.1f} km/h
  Min: {speed1.min():.1f} km/h
  Avg: {speed1.mean():.1f} km/h

{driver2}:
  Max: {speed2.max():.1f} km/h
  Min: {speed2.min():.1f} km/h
  Avg: {speed2.mean():.1f} km/h

DIFFERENCE
─────────────
Max Diff: {np.max(np.abs(speed1-speed2)):.1f} km/h
Avg Diff: {np.mean(np.abs(speed1-speed2)):.1f} km/h
"""
    
    ax4.text(0.05, 0.95, speed_stats, transform=ax4.transAxes, fontsize=11,
             verticalalignment='top', fontfamily='monospace', color='white',
             bbox=dict(boxstyle='round', facecolor='#2a2a2a', alpha=0.8))
    
    # Summary bar chart
    ax5 = fig.add_subplot(gs[2, :])
    
    categories = ['Lap Time', 'Max Speed', 'Min Speed', 'Avg Speed']
    driver1_values = [laptime1, speed1.max(), speed1.min(), speed1.mean()]
    driver2_values = [laptime2, speed2.max(), speed2.min(), speed2.mean()]
    
    x = np.arange(len(categories))
    width = 0.35
    
    ax5.bar(x - width/2, driver1_values, width, label=driver1, color=color1, alpha=0.8)
    ax5.bar(x + width/2, driver2_values, width, label=driver2, color=color2, alpha=0.8)
    
    ax5.set_xticks(x)
    ax5.set_xticklabels(categories)
    ax5.legend()
    ax5.set_title('Performance Summary', color='white')
    ax5.grid(True, color='#333333', alpha=0.3, axis='y')
    
    # Style all axes
    for ax in [ax1, ax2, ax5]:
        ax.set_facecolor('#1a1a1a')
        ax.tick_params(axis='both', colors='white')
        for spine in ax.spines.values():
            spine.set_color('#666666')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='#1a1a1a')
    
    plt.show()
    F1PlotStyle.reset_style()