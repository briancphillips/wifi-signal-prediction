import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, PathPatch
import matplotlib.path as mpath
from matplotlib.collections import PatchCollection
import random
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

@dataclass
class WallMaterial:
    name: str
    attenuation_db: float  # Signal attenuation in dB
    color: str
    pattern: Optional[str] = None

class BuildingMaterials:
    CONCRETE = WallMaterial("Concrete", 12.0, "gray", "//")
    DRYWALL = WallMaterial("Drywall", 3.5, "white")
    GLASS = WallMaterial("Glass", 2.0, "lightblue", None)
    METAL = WallMaterial("Metal", 15.0, "silver", "x")
    WOOD = WallMaterial("Wood", 2.5, "burlywood")

@dataclass
class Wall:
    x1: float
    y1: float
    x2: float
    y2: float
    material: WallMaterial
    thickness: float = 0.2  # meters

@dataclass
class Door:
    x: float
    y: float
    width: float = 1.0  # meters
    height: float = 2.1  # meters
    is_open: bool = True

@dataclass
class Window:
    x: float
    y: float
    width: float = 1.5  # meters
    height: float = 1.2  # meters

@dataclass
class Furniture:
    type: str
    x: float
    y: float
    width: float
    height: float
    rotation: float = 0.0  # degrees

class FloorPlanGenerator:
    def __init__(self, width=800, height=600, pixels_per_meter=20):
        """Initialize the floor plan generator.
        
        Args:
            width (int): Width of the floor plan in pixels
            height (int): Height of the floor plan in pixels
            pixels_per_meter (int): Pixels per meter for scale
        """
        self.width = width
        self.height = height
        self.pixels_per_meter = pixels_per_meter
        self.rooms = []
        self.corridors = []
        self.walls = []
        self.doors = []
        self.windows = []
        self.furniture = []
        
    def add_room(self, x, y, width, height, room_type="office"):
        """Add a room with walls, doors, and windows."""
        # Add room to list
        room = {
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'type': room_type
        }
        self.rooms.append(room)
        
        # Add walls
        walls = [
            Wall(x, y, x+width, y, BuildingMaterials.DRYWALL),  # Top wall
            Wall(x+width, y, x+width, y+height, BuildingMaterials.DRYWALL),  # Right wall
            Wall(x, y+height, x+width, y+height, BuildingMaterials.DRYWALL),  # Bottom wall
            Wall(x, y, x, y+height, BuildingMaterials.DRYWALL)  # Left wall
        ]
        self.walls.extend(walls)
        
        # Add door (randomly on one wall)
        door_wall = random.choice(range(4))
        if door_wall == 0:  # Top wall
            door_x = x + random.uniform(0.2 * width, 0.8 * width)
            self.doors.append(Door(door_x, y))
        elif door_wall == 1:  # Right wall
            door_y = y + random.uniform(0.2 * height, 0.8 * height)
            self.doors.append(Door(x + width, door_y))
        elif door_wall == 2:  # Bottom wall
            door_x = x + random.uniform(0.2 * width, 0.8 * width)
            self.doors.append(Door(door_x, y + height))
        else:  # Left wall
            door_y = y + random.uniform(0.2 * height, 0.8 * height)
            self.doors.append(Door(x, door_y))
            
        # Add windows (randomly on exterior walls)
        if x == 0 or x + width == self.width:  # Room on building edge
            window_y = y + random.uniform(0.2 * height, 0.8 * height)
            self.windows.append(Window(x if x == 0 else x + width, window_y))
            
        if y == 0 or y + height == self.height:  # Room on building edge
            window_x = x + random.uniform(0.2 * width, 0.8 * width)
            self.windows.append(Window(window_x, y if y == 0 else y + height))
            
        # Add furniture based on room type
        self.add_furniture_to_room(room)
        
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
        
        # Add walls along corridor
        if y1 == y2:  # Horizontal corridor
            self.walls.extend([
                Wall(x1, y1 - width/2, x2, y1 - width/2, BuildingMaterials.DRYWALL),  # Top wall
                Wall(x1, y1 + width/2, x2, y1 + width/2, BuildingMaterials.DRYWALL)   # Bottom wall
            ])
        else:  # Vertical corridor
            self.walls.extend([
                Wall(x1 - width/2, y1, x1 - width/2, y2, BuildingMaterials.DRYWALL),  # Left wall
                Wall(x1 + width/2, y1, x1 + width/2, y2, BuildingMaterials.DRYWALL)   # Right wall
            ])
        
    def add_furniture_to_room(self, room):
        """Add appropriate furniture based on room type."""
        if room['type'] == 'office':
            # Add desk
            desk_width = 1.6 * self.pixels_per_meter
            desk_height = 0.8 * self.pixels_per_meter
            desk_x = room['x'] + (room['width'] - desk_width) / 2
            desk_y = room['y'] + room['height'] * 0.2
            self.furniture.append(Furniture('desk', desk_x, desk_y, desk_width, desk_height))
            
            # Add chair
            chair_size = 0.6 * self.pixels_per_meter
            chair_x = desk_x + (desk_width - chair_size) / 2
            chair_y = desk_y + desk_height + 0.1 * self.pixels_per_meter
            self.furniture.append(Furniture('chair', chair_x, chair_y, chair_size, chair_size))
            
        elif room['type'] == 'meeting':
            # Add conference table
            table_width = min(room['width'], room['height']) * 0.6
            table_height = table_width * 0.4
            table_x = room['x'] + (room['width'] - table_width) / 2
            table_y = room['y'] + (room['height'] - table_height) / 2
            self.furniture.append(Furniture('table', table_x, table_y, table_width, table_height))
            
            # Add chairs around table
            chair_size = 0.6 * self.pixels_per_meter
            chairs_per_side = int(table_width / (chair_size * 1.5))
            for i in range(chairs_per_side):
                # Top side chairs
                chair_x = table_x + i * (table_width / (chairs_per_side - 1))
                chair_y = table_y - chair_size * 1.2
                self.furniture.append(Furniture('chair', chair_x, chair_y, chair_size, chair_size))
                
                # Bottom side chairs
                chair_y = table_y + table_height + chair_size * 0.2
                self.furniture.append(Furniture('chair', chair_x, chair_y, chair_size, chair_size))
                
        elif room['type'] == 'open_space':
            # Add multiple workstations
            desk_width = 1.2 * self.pixels_per_meter
            desk_height = 0.8 * self.pixels_per_meter
            spacing = 1.5 * self.pixels_per_meter
            
            rows = max(1, int(room['height'] / (desk_height + spacing)))
            cols = max(1, int(room['width'] / (desk_width + spacing)))
            
            for row in range(rows):
                for col in range(cols):
                    desk_x = room['x'] + col * (desk_width + spacing) + spacing
                    desk_y = room['y'] + row * (desk_height + spacing) + spacing
                    if desk_x + desk_width <= room['x'] + room['width'] and desk_y + desk_height <= room['y'] + room['height']:
                        self.furniture.append(Furniture('desk', desk_x, desk_y, desk_width, desk_height))
                        self.furniture.append(Furniture('chair', desk_x + desk_width/4, desk_y + desk_height + 0.1 * self.pixels_per_meter,
                                                     0.6 * self.pixels_per_meter, 0.6 * self.pixels_per_meter))
        
    def draw_floor_plan(self, output_path, show_grid=True):
        """Draw and save the floor plan with all elements."""
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        
        # Draw rooms (background)
        for room in self.rooms:
            rect = Rectangle((room['x'], room['y']), 
                           room['width'], room['height'],
                           facecolor='white',
                           edgecolor='none',
                           alpha=0.5)
            ax.add_patch(rect)
            
            # Add room label
            ax.text(room['x'] + room['width']/2, 
                   room['y'] + room['height']/2,
                   room['type'],
                   horizontalalignment='center',
                   verticalalignment='center',
                   alpha=0.5)
        
        # Draw walls
        for wall in self.walls:
            if wall.material.pattern:
                ax.fill_between([wall.x1, wall.x2], 
                              [wall.y1 - wall.thickness * self.pixels_per_meter/2, wall.y2 - wall.thickness * self.pixels_per_meter/2],
                              [wall.y1 + wall.thickness * self.pixels_per_meter/2, wall.y2 + wall.thickness * self.pixels_per_meter/2],
                              color=wall.material.color,
                              hatch=wall.material.pattern)
            else:
                ax.fill_between([wall.x1, wall.x2],
                              [wall.y1 - wall.thickness * self.pixels_per_meter/2, wall.y2 - wall.thickness * self.pixels_per_meter/2],
                              [wall.y1 + wall.thickness * self.pixels_per_meter/2, wall.y2 + wall.thickness * self.pixels_per_meter/2],
                              color=wall.material.color)
        
        # Draw doors
        for door in self.doors:
            door_patch = Rectangle((door.x - door.width * self.pixels_per_meter/2, door.y - door.height * self.pixels_per_meter/2),
                                 door.width * self.pixels_per_meter,
                                 door.height * self.pixels_per_meter,
                                 facecolor='brown' if not door.is_open else 'none',
                                 edgecolor='brown',
                                 alpha=0.7)
            ax.add_patch(door_patch)
            
        # Draw windows
        for window in self.windows:
            window_patch = Rectangle((window.x - window.width * self.pixels_per_meter/2, window.y - window.height * self.pixels_per_meter/2),
                                   window.width * self.pixels_per_meter,
                                   window.height * self.pixels_per_meter,
                                   facecolor=BuildingMaterials.GLASS.color,
                                   edgecolor='gray',
                                   alpha=0.3)
            ax.add_patch(window_patch)
            
        # Draw furniture
        for item in self.furniture:
            if item.type == 'desk':
                color = 'burlywood'
            elif item.type == 'chair':
                color = 'darkgray'
            elif item.type == 'table':
                color = 'burlywood'
            else:
                color = 'gray'
                
            furniture_patch = Rectangle((item.x, item.y),
                                     item.width,
                                     item.height,
                                     facecolor=color,
                                     edgecolor='black',
                                     alpha=0.7)
            if item.rotation != 0:
                furniture_patch.set_transform(plt.matplotlib.transforms.Affine2D().rotate_deg_around(
                    item.x + item.width/2, item.y + item.height/2, item.rotation) + ax.transData)
            ax.add_patch(furniture_patch)
        
        # Draw corridors
        for corridor in self.corridors:
            if corridor['y1'] == corridor['y2']:  # Horizontal corridor
                rect = Rectangle((corridor['x1'], 
                                corridor['y1'] - corridor['width']/2),
                               corridor['x2'] - corridor['x1'],
                               corridor['width'],
                               facecolor='lightgray',
                               edgecolor='black',
                               linewidth=2,
                               alpha=0.5)
                ax.add_patch(rect)
            else:  # Vertical corridor
                rect = Rectangle((corridor['x1'] - corridor['width']/2,
                                corridor['y1']),
                               corridor['width'],
                               corridor['y2'] - corridor['y1'],
                               facecolor='lightgray',
                               edgecolor='black',
                               linewidth=2,
                               alpha=0.5)
                ax.add_patch(rect)
        
        # Add measurement grid
        if show_grid:
            grid_spacing = self.pixels_per_meter  # 1 meter grid
            for x in range(0, self.width + 1, grid_spacing):
                ax.axvline(x=x, color='gray', linestyle=':', alpha=0.3)
            for y in range(0, self.height + 1, grid_spacing):
                ax.axhline(y=y, color='gray', linestyle=':', alpha=0.3)
                
            # Add scale bar
            scale_bar_length = 5 * self.pixels_per_meter  # 5 meters
            ax.plot([10, 10 + scale_bar_length], [10, 10], 'k-', linewidth=2)
            ax.text(10 + scale_bar_length/2, 15, '5 meters', 
                   horizontalalignment='center')
        
        # Set aspect ratio and remove axes
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Add legend for materials
        legend_elements = [
            plt.Rectangle((0, 0), 1, 1, facecolor=mat.color, hatch=mat.pattern if mat.pattern else None,
                         label=f"{mat.name} (-{mat.attenuation_db}dB)")
            for mat in [BuildingMaterials.CONCRETE, BuildingMaterials.DRYWALL, 
                       BuildingMaterials.GLASS, BuildingMaterials.METAL]
        ]
        ax.legend(handles=legend_elements, loc='upper right', title='Materials')
        
        # Save the floor plan
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        plt.close()
        
def create_example_floor_plan():
    """Create an example floor plan with typical office layout."""
    generator = FloorPlanGenerator(width=1000, height=800)
    
    # Generate random office layout
    generator.add_room(100, 100, 200, 200, 'office')
    generator.add_room(400, 100, 200, 200, 'meeting')
    generator.add_room(100, 400, 200, 200, 'open_space')
    
    # Save the floor plan
    generator.draw_floor_plan("example_floor_plan.png")
    
    return "example_floor_plan.png"

if __name__ == "__main__":
    # Generate example floor plan
    output_path = create_example_floor_plan()
    print(f"Example floor plan generated: {output_path}")
