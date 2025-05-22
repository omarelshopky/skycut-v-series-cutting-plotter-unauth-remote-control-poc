# Module: hpgl_optimizer.py
# Part of the Skycut V Series Cutting Plotter Unauthenticated Remote Control
# Author: Omar Elshopky (omarelshopky.com)
#
# Full Write-up: https://medium.com/@omarelshopky/wireless-weapons-turning-skycut-plotters-into-physical-dangers-9f29e0cd357a
# Advisory: https://github.com/omarelshopky/skycut-v-series-cutting-plotter-unauth-remote-control-poc

class HPGLOptimizer:
    """Optimizes HPGL commands for efficient plotting"""

    @staticmethod
    def optimize(commands):
        """Optimize HPGL commands by combining consecutive commands and removing redundancy"""
        optimized = []
        current_cmd = None
        current_points = []

        for cmd in commands.split(';'):
            if not cmd:
                continue

            if cmd.startswith("PD") or cmd.startswith("PU"):
                cmd_type = cmd[:2]
                coords = cmd[2:].split(',')

                # Process coordinate pairs
                point_pairs = []
                for i in range(0, len(coords), 2):
                    if i+1 < len(coords):
                        x, y = int(coords[i]), int(coords[i+1])
                        point_pairs.append((x, y))

                # Start new command or append to existing
                if current_cmd != cmd_type or not current_points:
                    # Finish previous command if any
                    HPGLOptimizer._append_command(optimized, current_cmd, current_points)

                    # Start new command
                    current_cmd = cmd_type
                    current_points = point_pairs
                else:
                    # Append to existing command - skip redundant points
                    for point in point_pairs:
                        if not current_points or point != current_points[-1]:
                            current_points.append(point)
            else:
                # Non-coordinate command
                HPGLOptimizer._append_command(optimized, current_cmd, current_points)
                optimized.append(f"{cmd};")
                current_cmd = None
                current_points = []

        # Add final command if any
        HPGLOptimizer._append_command(optimized, current_cmd, current_points)

        return ''.join(optimized)

    @staticmethod
    def _append_command(commands_list, cmd_type, points):
        """Append a command with its points to the command list"""
        if cmd_type and points:
            flat_points = []
            for x, y in points:
                flat_points.extend([str(x), str(y)])
            commands_list.append(f"{cmd_type}{','.join(flat_points)};")