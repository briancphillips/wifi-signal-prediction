import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.floor_plan_generator import FloorPlanGenerator

def generate_example_layouts():
    """Generate example floor plans with different layouts."""
    
    # Create output directory
    output_dir = "floor_plans"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate single floor office layout
    print("Generating single floor office layout...")
    generator = FloorPlanGenerator(width=1000, height=800)
    generator.generate_office_layout(num_rooms=10)
    generator.draw_floor_plan(os.path.join(output_dir, "office_layout.png"))
    
    # Generate multi-floor building
    print("\nGenerating multi-floor building layout...")
    generator = FloorPlanGenerator(width=1200, height=1000)
    generator.generate_multi_floor_plan(
        num_floors=3,
        output_prefix=os.path.join(output_dir, "floor")
    )
    
    print("\nFloor plans generated in the 'floor_plans' directory:")
    print("- office_layout.png: Single floor office layout")
    print("- floor_1.png: First floor of multi-floor building")
    print("- floor_2.png: Second floor of multi-floor building")
    print("- floor_3.png: Third floor of multi-floor building")

if __name__ == "__main__":
    generate_example_layouts()
