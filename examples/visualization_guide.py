import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def generate_visualization_guide():
    """Generate a user-friendly guide to reading WiFi deployment visualizations."""
    
    guide = []
    guide.append("# How to Read WiFi Deployment Visualizations: A Simple Guide\n")
    
    # Introduction
    guide.append("## Introduction")
    guide.append("This guide will help you understand the WiFi deployment visualizations in simple terms. "
                "Think of it like a weather map, but for WiFi signals instead of rain!\n")
    
    # Signal Strength Colors
    guide.append("## Understanding the Colors")
    guide.append("The colors in our maps work like a temperature gauge:")
    guide.append("* 🔴 **Red** = Very Strong Signal (Like being right next to the router)")
    guide.append("* 🟡 **Yellow** = Good Signal (Perfect for most uses)")
    guide.append("* 🟢 **Green** = Okay Signal (Good enough for basic internet)")
    guide.append("* 🔵 **Blue** = Weak Signal (Might have connection issues)")
    guide.append("* 🟣 **Purple/Dark Blue** = Very Weak Signal (Probably won't connect)\n")
    
    # Access Points
    guide.append("## Access Points (APs)")
    guide.append("* Look for the red triangles (▲) on the maps - these are your WiFi routers")
    guide.append("* Each AP has a name like 'AP1_Ch1' where:")
    guide.append("  - 'AP1' is the router's name")
    guide.append("  - 'Ch1' means it's using Channel 1\n")
    
    # Coverage Maps
    guide.append("## Reading Coverage Maps")
    guide.append("![Coverage Map Example](coverage_example.png)")
    guide.append("* This map shows how strong your WiFi signal is in different areas")
    guide.append("* The brighter/redder the color, the stronger your WiFi signal")
    guide.append("* Dark blue areas = Weak or no WiFi signal")
    guide.append("* Think of it like a flashlight: bright near the source, dimmer as you move away\n")
    
    # Combined Coverage
    guide.append("## Combined Coverage Map")
    guide.append("![Combined Coverage Example](coverage_combined.png)")
    guide.append("* Shows all WiFi signals combined")
    guide.append("* Brighter areas = Good coverage from at least one AP")
    guide.append("* Dark areas = Poor coverage (WiFi dead zones)")
    guide.append("* Ideal map should be mostly yellow/green with minimal dark spots\n")
    
    # Interference Map
    guide.append("## Understanding Interference")
    guide.append("![Interference Map Example](interference_example.png)")
    guide.append("* Shows where WiFi signals might conflict with each other")
    guide.append("* Red areas = High interference (like radio stations overlapping)")
    guide.append("* Blue areas = Low interference (clean signal)")
    guide.append("* You want mostly blue/green colors here!\n")
    
    # Common Patterns
    guide.append("## Common Patterns to Look For")
    guide.append("### Good Signs:")
    guide.append("* Even, consistent colors across the space")
    guide.append("* Minimal dark blue areas in coverage maps")
    guide.append("* Mostly blue/green in interference maps")
    guide.append("* APs spread out evenly\n")
    
    guide.append("### Bad Signs:")
    guide.append("* Large dark blue areas (dead zones)")
    guide.append("* Too much red in interference maps")
    guide.append("* APs clustered together")
    guide.append("* Very uneven coloring\n")
    
    # Example Comparisons
    guide.append("## Example: Good vs Bad Deployment")
    guide.append("### Bad Deployment:")
    guide.append("![Bad Deployment Example](bad_deployment.png)")
    guide.append("* APs too close together")
    guide.append("* Large areas with no coverage")
    guide.append("* Lots of interference (red areas)\n")
    
    guide.append("### Good Deployment:")
    guide.append("![Good Deployment Example](good_deployment.png)")
    guide.append("* APs evenly spread out")
    guide.append("* Consistent coverage everywhere")
    guide.append("* Minimal interference\n")
    
    # Simple Tips
    guide.append("## Quick Tips for Reading Maps")
    guide.append("1. 👀 **First Look**: Check for dark spots in coverage maps")
    guide.append("2. 🎯 **AP Locations**: Should be spread out, not clustered")
    guide.append("3. 🌈 **Colors**: Want mostly yellow/green in coverage maps")
    guide.append("4. ⚠️ **Red Flags**: Large dark areas or too much interference")
    guide.append("5. 🎨 **Consistency**: Even coloring is better than patchy\n")
    
    # Save guide
    output_dir = os.path.join('results', 'visualization_guide')
    os.makedirs(output_dir, exist_ok=True)
    
    guide_path = os.path.join(output_dir, 'visualization_guide.md')
    with open(guide_path, 'w') as f:
        f.write('\n'.join(guide))
    
    print(f"Visualization guide generated: {guide_path}")
    return guide_path

if __name__ == "__main__":
    generate_visualization_guide()
