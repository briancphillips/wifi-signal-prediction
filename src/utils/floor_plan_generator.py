import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
import random

class FloorPlanGenerator:
    def __init__(self, width=800, height=600):
        """Initialize the floor plan generator.
        
        Args:
            width (int): Width of the floor plan in pixels
            height (int): Height of the floor plan in pixels
        """
        self.width = width
        self.height = height
        self.rooms = []
        self.corridors = []
        self.walls = []
        
    def add_room(self, x, y, width, height, room_type="office"):
        """Add a room to the floor plan.
        
        Args:
            x (int): X coordinate of room's top-left corner
            y (int): Y coordinate of room's top-left corner
            width (int): Room width
            height (int): Room height
            room_type (str): Type of room (office, meeting, etc.)
        """
        self.rooms.append({
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'type': room_type
        })
        
    def add_corridor(self, x1, y1, x2, y2, width=40):
        """Add a corridor to the floor plan.
        
        Args:
            x1, y1 (int): Start coordinates
            x2, y2 (int): End coordinates
            width (int): Corridor width
        """
        self.corridors.append({
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2,
            'width': width
        })
        
    def generate_office_layout(self, num_rooms=10):
        """Generate a random office layout.
        
        Args:
            num_rooms (int): Number of rooms to generate
        """
        # Clear existing layout
        self.rooms = []
        self.corridors = []
        
        # Add main corridor
        corridor_y = self.height // 2
        self.add_corridor(0, corridor_y, self.width, corridor_y)
        
        # Add rooms on both sides of corridor
        room_types = ["office", "meeting", "open_space"]
        min_room_width = 100
        min_room_height = 80
        
        for _ in range(num_rooms):
            # Randomly choose side of corridor
            is_top = random.choice([True, False])
            
            # Generate room dimensions
            room_width = random.randint(min_room_width, min_room_width * 2)
            room_height = random.randint(min_room_height, min_room_height * 2)
            
            # Generate room position
            x = random.randint(0, self.width - room_width)
            if is_top:
                y = random.randint(0, corridor_y - room_height - 20)
            else:
                y = random.randint(corridor_y + 20, self.height - room_height)
            
            # Add room
            self.add_room(x, y, room_width, room_height, 
                         room_type=random.choice(room_types))
            
    def draw_floor_plan(self, output_path, show_grid=True):
        """Draw and save the floor plan.
        
        Args:
            output_path (str): Path to save the floor plan image
            show_grid (bool): Whether to show measurement grid
        """
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        
        # Draw rooms
        for room in self.rooms:
            rect = Rectangle((room['x'], room['y']), 
                           room['width'], room['height'],
                           facecolor='white',
                           edgecolor='black',
                           linewidth=2)
            ax.add_patch(rect)
            
            # Add room label
            ax.text(room['x'] + room['width']/2, 
                   room['y'] + room['height']/2,
                   room['type'],
                   horizontalalignment='center',
                   verticalalignment='center')
        
        # Draw corridors
        for corridor in self.corridors:
            if corridor['y1'] == corridor['y2']:  # Horizontal corridor
                rect = Rectangle((corridor['x1'], 
                                corridor['y1'] - corridor['width']/2),
                               corridor['x2'] - corridor['x1'],
                               corridor['width'],
                               facecolor='lightgray',
                               edgecolor='black',
                               linewidth=2)
                ax.add_patch(rect)
            else:  # Vertical corridor
                rect = Rectangle((corridor['x1'] - corridor['width']/2,
                                corridor['y1']),
                               corridor['width'],
                               corridor['y2'] - corridor['y1'],
                               facecolor='lightgray',
                               edgecolor='black',
                               linewidth=2)
                ax.add_patch(rect)
        
        # Add measurement grid
        if show_grid:
            grid_spacing = 100
            for x in range(0, self.width + 1, grid_spacing):
                ax.axvline(x=x, color='gray', linestyle=':', alpha=0.3)
            for y in range(0, self.height + 1, grid_spacing):
                ax.axhline(y=y, color='gray', linestyle=':', alpha=0.3)
        
        # Set aspect ratio and remove axes
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Save the floor plan
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        plt.close()
        
    def generate_multi_floor_plan(self, num_floors=3, output_prefix="floor"):
        """Generate multiple floor plans for a building.
        
        Args:
            num_floors (int): Number of floors to generate
            output_prefix (str): Prefix for output files
        """
        for floor in range(num_floors):
            self.generate_office_layout(num_rooms=random.randint(8, 12))
            self.draw_floor_plan(f"{output_prefix}_{floor+1}.png")
            
def create_example_floor_plan():
    """Create an example floor plan with typical office layout."""
    generator = FloorPlanGenerator(width=1000, height=800)
    
    # Generate random office layout
    generator.generate_office_layout(num_rooms=10)
    
    # Save the floor plan
    generator.draw_floor_plan("example_floor_plan.png")
    
    return "example_floor_plan.png"

if __name__ == "__main__":
    # Generate example floor plan
    output_path = create_example_floor_plan()
    print(f"Example floor plan generated: {output_path}")
