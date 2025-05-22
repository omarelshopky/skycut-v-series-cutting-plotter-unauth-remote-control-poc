# Module: hpgl_converter.py
# Part of the Skycut V Series Cutting Plotter Unauthenticated Remote Control
# Author: Omar Elshopky (omarelshopky.com)
#
# Full Write-up: https://medium.com/@omarelshopky/wireless-weapons-turning-skycut-plotters-into-physical-dangers-9f29e0cd357a
# Advisory: https://github.com/omarelshopky/skycut-v-series-cutting-plotter-unauth-remote-control-poc

from fontTools.ttLib import TTFont
from config import COMMON_FONT_PATHS, DEFAULT_FONT_SIZE, DEFAULT_PLOT_WIDTH, DEFAULT_PLOT_HEIGHT
from .hpgl_pen import HPGLPen
from .hpgl_optimizer import HPGLOptimizer


class HPGLConverter:
    """Converts font outlines to HPGL commands"""

    def __init__(self):
        self._load_font()

    def _load_font(self):
        """Load the font file"""
        try:
            for font_path in COMMON_FONT_PATHS:
                try:
                    self.font = TTFont(font_path)
                    break
                except:
                    continue
        except Exception as e:
            raise Exception("Could not find a suitable font. Please specify a font file path.")

    def text_to_hpgl(self, text, font_size=DEFAULT_FONT_SIZE, plot_width=DEFAULT_PLOT_WIDTH, plot_height=DEFAULT_PLOT_HEIGHT):
        """Convert text to HPGL commands"""
        try:
            # Get single-line paths
            hpgl_raw = self._create_single_line_paths(text, font_size)

            # Scale to fit plot dimensions
            commands_data = self._parse_commands(hpgl_raw)

            # Scale and center the drawing
            scaled_commands = self._scale_and_center(commands_data, plot_width, plot_height)

            # Optimize the final output
            return HPGLOptimizer.optimize(''.join(scaled_commands)) + "IN;"

        except Exception as e:
            # Return a simple diagonal line pattern if there's an error
            return "IN;PU0,0;PD1000,1000;PU2000,2000;PD3000,3000;PU4000,4000;PD5000,5000;PA;"

    def _create_single_line_paths(self, text, font_size):
        """Create single-line paths for text characters"""
        # Get font metadata
        cmap = self.font.getBestCmap()
        hmtx = self.font["hmtx"]
        units_per_em = self.font["head"].unitsPerEm
        scale_factor = font_size / units_per_em
        
        # Process each character
        x_offset = 0
        all_commands = ["IN;"]  # Initialize plotter
        
        for char in text:
            if char == " ":
                # Handle space character
                x_offset += font_size * 0.5
                continue
                
            # Get glyph name and data
            if ord(char) not in cmap:
                continue  # Skip characters not in font
                
            glyph_name = cmap[ord(char)]
            glyph_set = self.font.getGlyphSet()
            glyph = glyph_set[glyph_name]
            
            # Create path for glyph
            pen = HPGLPen(glyph_set)
            glyph.draw(pen)
            
            # Scale and offset the commands
            for cmd in pen.commands:
                if cmd.startswith("PU") or cmd.startswith("PD"):
                    cmd_type = cmd[:2]
                    coords = cmd[2:-1]  # Remove command and semicolon
                    
                    # Process coordinate pairs
                    coord_pairs = coords.split(',')
                    new_coords = []
                    
                    for i in range(0, len(coord_pairs), 2):
                        if i+1 < len(coord_pairs):
                            x = float(coord_pairs[i])
                            y = float(coord_pairs[i+1])
                            
                            # Scale and properly orient y (no need to flip)
                            x = int((x * scale_factor) + x_offset)
                            y = int(y * scale_factor)  # Changed: No more flipping the y coordinate
                            
                            new_coords.extend([str(x), str(y)])
                    
                    all_commands.append(f"{cmd_type}{','.join(new_coords)};")
                else:
                    all_commands.append(cmd)
            
            # Update position for next character
            advance_width, _ = hmtx[glyph_name]
            x_offset += advance_width * scale_factor
        
        return ''.join(all_commands)
    
    def _parse_commands(self, hpgl_commands):
        """Parse HPGL commands and extract coordinates"""
        parsed_commands = []
        points = []
        
        for cmd in hpgl_commands.split(";"):
            if not cmd:
                continue
                
            if cmd.startswith("PU") or cmd.startswith("PD"):
                cmd_type = cmd[:2]
                coords = cmd[2:]
                if coords:
                    coord_pairs = coords.split(',')
                    point_pairs = []
                    
                    for i in range(0, len(coord_pairs), 2):
                        if i+1 < len(coord_pairs):
                            x = int(coord_pairs[i])
                            y = int(coord_pairs[i+1])
                            points.append((x, y))
                            point_pairs.append((x, y))
                    
                    parsed_commands.append((cmd_type, point_pairs))
            else:
                parsed_commands.append((cmd, None))
        
        return {"commands": parsed_commands, "points": points}
    
    def _scale_and_center(self, commands_data, plot_width, plot_height):
        """Scale and center the drawing to fit the plot dimensions"""
        parsed_commands = commands_data["commands"]
        points = commands_data["points"]
        
        if not points:
            return []
            
        # Find bounding box
        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)
        
        width = max_x - min_x
        height = max_y - min_y
        
        # Calculate scaling to fit plot with margins
        x_scale = (plot_width * 0.8) / width if width > 0 else 1
        y_scale = (plot_height * 0.8) / height if height > 0 else 1
        scale = min(x_scale, y_scale)
        
        # Center the drawing
        x_offset = (plot_width - width * scale) / 2 - min_x * scale
        y_offset = (plot_height - height * scale) / 2 - min_y * scale
        
        # Apply scaling and offset
        scaled_commands = []  # Initialize plotter
        
        for cmd_type, coords in parsed_commands:
            if coords:
                scaled_points = []
                for x, y in coords:
                    x_scaled = int(x * scale + x_offset)
                    y_scaled = int(y * scale + y_offset)
                    scaled_points.extend([str(x_scaled), str(y_scaled)])
                
                scaled_commands.append(f"{cmd_type}{','.join(scaled_points)};")
            else:
                scaled_commands.append(f"{cmd_type};")
        
        return scaled_commands