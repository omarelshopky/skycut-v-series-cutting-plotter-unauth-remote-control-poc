# Module: hpgl_pen.py
# Part of the Skycut V Series Cutting Plotter Unauthenticated Remote Control
# Author: Omar Elshopky (omarelshopky.com)
#
# Full Write-up: https://medium.com/@omarelshopky/wireless-weapons-turning-skycut-plotters-into-physical-dangers-9f29e0cd357a
# Advisory: https://github.com/omarelshopky/skycut-v-series-cutting-plotter-unauth-remote-control-poc

import math
import numpy as np
from fontTools.pens.basePen import BasePen


class HPGLPen(BasePen):
    """A pen that converts font outlines to ultra-smooth HPGL commands"""

    def __init__(self, glyphSet):
        super().__init__(glyphSet)
        self.commands = []
        self.current_point = None
        self.start_point = None

    def _moveTo(self, pt):
        x, y = pt
        self.commands.append(f"PU{int(x)},{int(y)};")
        self.current_point = pt

    def _lineTo(self, pt):
        x, y = pt
        if self.current_point:
            self.commands.append(f"PD{int(x)},{int(y)};")
        else:
            self.commands.append(f"PU{int(x)},{int(y)};")
        self.current_point = pt

    def _curveToOne(self, pt1, pt2, pt3):
        """Convert cubic Bezier curve to line segments for smoother curves"""
        if not self.current_point:
            self._moveTo(pt1)

        # Determine optimal number of segments for curve quality
        num_segments = self._adaptive_curve_sampling(self.current_point, pt1, pt2, pt3)

        # Generate points along the curve
        points = self._generate_bezier_points(self.current_point, pt1, pt2, pt3, num_segments)

        # Output as a single PD command for efficiency
        if points:
            coords = ",".join(f"{x},{y}" for x, y in points)
            self.commands.append(f"PD{coords};")
            self.current_point = points[-1]

    def _qCurveToOne(self, pt1, pt2):
        """Convert quadratic Bezier curve to line segments"""
        if not self.current_point:
            self._moveTo(pt1)

        # Use 40 segments for quadratic curves
        num_segments = 40
        t_points = np.linspace(0, 1, num_segments)
        start_point = self.current_point

        # Generate points along the curve
        points = []
        for t in t_points[1:]:  # Skip first point (already there)
            x = (1-t)**2 * start_point[0] + 2*(1-t)*t * pt1[0] + t**2 * pt2[0]
            y = (1-t)**2 * start_point[1] + 2*(1-t)*t * pt1[1] + t**2 * pt2[1]
            points.append((int(x), int(y)))

        # Output as a single PD command
        if points:
            coords = ",".join(f"{x},{y}" for x, y in points)
            self.commands.append(f"PD{coords};")
            self.current_point = points[-1]

    def _closePath(self):
        """Close the current path smoothly"""
        if not self.current_point or not self.start_point:
            return

        # Calculate distance between current point and start point
        dist_squared = ((self.current_point[0] - self.start_point[0])**2 +
                        (self.current_point[1] - self.start_point[1])**2)

        if dist_squared > 400:  # Use a threshold for smooth closing
            # Create a simple curve to close the path smoothly
            mid_x = (self.current_point[0] + self.start_point[0]) / 2
            mid_y = (self.current_point[1] + self.start_point[1]) / 2
            self._qCurveToOne((mid_x, mid_y), self.start_point)
        else:
            # Direct line for close points
            x, y = self.start_point
            self.commands.append(f"PD{int(x)},{int(y)};")

        self.current_point = None

    def _adaptive_curve_sampling(self, p0, p1, p2, p3, tolerance=1.0):
        """Determine optimal number of segments for a curve based on curvature"""
        # Start with a reasonable number of segments
        num_segments = 12

        # Calculate maximum deviation from linear approximation
        max_deviation = self._compute_curve_deviation(p0, p1, p2, p3)

        # Adjust segments based on deviation
        if max_deviation > tolerance * 3:
            num_segments = 50
        elif max_deviation > tolerance * 2:
            num_segments = 30
        elif max_deviation > tolerance:
            num_segments = 20

        return min(num_segments, 60)  # Cap at 60 segments

    def _compute_curve_deviation(self, p0, p1, p2, p3):
        """Compute maximum deviation of a cubic Bezier curve from linear approximation"""
        # Sample curve at midpoint (t=0.5)
        t = 0.5
        # Calculate point on curve at t=0.5
        p_curve_x = (1-t)**3 * p0[0] + 3*(1-t)**2*t * p1[0] + 3*(1-t)*t**2 * p2[0] + t**3 * p3[0]
        p_curve_y = (1-t)**3 * p0[1] + 3*(1-t)**2*t * p1[1] + 3*(1-t)*t**2 * p2[1] + t**3 * p3[1]

        # Linear approximation between endpoints
        p_linear_x = (p0[0] + p3[0]) / 2
        p_linear_y = (p0[1] + p3[1]) / 2

        # Distance from curve to linear approximation
        return math.sqrt((p_curve_x - p_linear_x)**2 + (p_curve_y - p_linear_y)**2)

    def _generate_bezier_points(self, p0, p1, p2, p3, num_segments):
        """Generate points along a cubic Bezier curve"""
        t_points = np.linspace(0, 1, num_segments)
        points = []

        for t in t_points[1:]:  # Skip first point (already there)
            # Cubic bezier formula
            x = (1-t)**3 * p0[0] + 3*(1-t)**2*t * p1[0] + 3*(1-t)*t**2 * p2[0] + t**3 * p3[0]
            y = (1-t)**3 * p0[1] + 3*(1-t)**2*t * p1[1] + 3*(1-t)*t**2 * p2[1] + t**3 * p3[1]
            points.append((int(x), int(y)))

        return points

    def moveTo(self, pt):
        self.start_point = pt
        super().moveTo(pt)