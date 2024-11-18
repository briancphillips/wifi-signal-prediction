import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from poor_deployment import run_poor_deployment
from optimal_deployment import run_optimal_deployment
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def create_comparison_report():
    """Create a comprehensive comparison between poor and optimal deployments."""
    
    # Run both deployments
    print("Running poor deployment simulation...")
    poor_results_path = run_poor_deployment()
    
    print("\nRunning optimal deployment simulation...")
    optimal_results_path = run_optimal_deployment()
    
    # Create comparison directory
    comparison_dir = os.path.join('results', 'deployment_comparison')
    os.makedirs(comparison_dir, exist_ok=True)
    
    # Create comparison visualizations
    create_comparison_visualizations(poor_results_path, optimal_results_path, comparison_dir)
    
    # Generate comparison report
    report_path = generate_comparison_report(poor_results_path, optimal_results_path, comparison_dir)
    
    print(f"\nComparison report generated: {report_path}")
    return comparison_dir

def create_comparison_visualizations(poor_path, optimal_path, output_dir):
    """Create side-by-side comparison visualizations."""
    
    # Coverage comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    
    # Poor deployment coverage
    poor_coverage = plt.imread(os.path.join(poor_path, 'visualizations', 'coverage_combined.png'))
    ax1.imshow(poor_coverage)
    ax1.set_title('Poor Deployment Coverage')
    ax1.axis('off')
    
    # Optimal deployment coverage
    optimal_coverage = plt.imread(os.path.join(optimal_path, 'visualizations', 'coverage_combined.png'))
    ax2.imshow(optimal_coverage)
    ax2.set_title('Optimal Deployment Coverage')
    ax2.axis('off')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'coverage_comparison.png'))
    plt.close()
    
    # Interference comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    
    # Poor deployment interference
    poor_interference = plt.imread(os.path.join(poor_path, 'visualizations', 'interference_map.png'))
    ax1.imshow(poor_interference)
    ax1.set_title('Poor Deployment Interference')
    ax1.axis('off')
    
    # Optimal deployment interference
    optimal_interference = plt.imread(os.path.join(optimal_path, 'visualizations', 'interference_map.png'))
    ax2.imshow(optimal_interference)
    ax2.set_title('Optimal Deployment Interference')
    ax2.axis('off')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'interference_comparison.png'))
    plt.close()

def generate_comparison_report(poor_path, optimal_path, output_dir):
    """Generate a detailed comparison report."""
    
    report = []
    report.append("# WiFi Deployment Comparison Report\n")
    
    # Add introduction
    report.append("## Overview")
    report.append("This report compares two WiFi deployment scenarios:")
    report.append("1. Poor Deployment: Common mistakes and suboptimal choices")
    report.append("2. Optimal Deployment: Best practices and strategic planning\n")
    
    # Add deployment characteristics
    report.append("## Deployment Characteristics\n")
    report.append("### Poor Deployment")
    report.append("- Too few access points")
    report.append("- APs clustered in one area")
    report.append("- Overlapping channels causing interference")
    report.append("- Signal-blocking materials (metal walls)")
    report.append("- Large areas without coverage\n")
    
    report.append("### Optimal Deployment")
    report.append("- Strategic AP placement")
    report.append("- Non-overlapping channel assignment")
    report.append("- Signal-friendly materials")
    report.append("- Coverage optimized for different areas")
    report.append("- Redundancy in high-density areas\n")
    
    # Add coverage comparison
    report.append("## Coverage Comparison")
    report.append("![Coverage Comparison](coverage_comparison.png)\n")
    report.append("### Analysis")
    report.append("- Poor deployment shows significant dead zones and overlapping coverage")
    report.append("- Optimal deployment provides uniform coverage across the entire space")
    report.append("- Strategic AP placement ensures consistent signal strength\n")
    
    # Add interference comparison
    report.append("## Interference Analysis")
    report.append("![Interference Comparison](interference_comparison.png)\n")
    report.append("### Analysis")
    report.append("- Poor deployment shows high interference in areas with clustered APs")
    report.append("- Optimal deployment minimizes interference through:")
    report.append("  * Strategic channel assignment")
    report.append("  * Proper AP spacing")
    report.append("  * Consideration of building materials\n")
    
    # Add recommendations
    report.append("## Recommendations")
    report.append("1. **AP Placement**")
    report.append("   - Distribute APs evenly across the space")
    report.append("   - Consider user density in different areas")
    report.append("   - Account for building materials\n")
    
    report.append("2. **Channel Assignment**")
    report.append("   - Use non-overlapping channels (1, 6, 11 for 2.4GHz)")
    report.append("   - Plan channel reuse carefully")
    report.append("   - Consider interference from neighboring networks\n")
    
    report.append("3. **Coverage Planning**")
    report.append("   - Ensure minimum signal strength throughout")
    report.append("   - Plan for redundancy in critical areas")
    report.append("   - Account for different device types\n")
    
    report.append("4. **Material Considerations**")
    report.append("   - Use signal-friendly materials where possible")
    report.append("   - Add additional APs near signal-blocking materials")
    report.append("   - Consider window placement for signal propagation\n")
    
    # Save report
    report_path = os.path.join(output_dir, 'comparison_report.md')
    with open(report_path, 'w') as f:
        f.write('\n'.join(report))
    
    return report_path

if __name__ == "__main__":
    create_comparison_report()
