from matplotlib.patches import Circle, RegularPolygon, Rectangle, Polygon
from matplotlib.collections import PatchCollection
import numpy as np


class Marker:
    def __init__(self, x: list = None, y: list = None, size: int = 2,
                 facecolor="white", edgecolor="black", linewidth=1, alpha=1, cmap="viridis"):
        """
        Initialize the Marker class.

        :param x: List of X-coordinates of the markers. Defaults to an empty list if not provided.
        :param y: List of Y-coordinates of the markers. Defaults to an empty list if not provided.
        :param size: Size of the markers. Default is 2.
        :param facecolor: Face color of the markers. Default is 'white'.
        :param edgecolor: Edge color of the markers. Default is 'black'.
        :param linewidth: Width of the marker edges. Default is 1.
        :param alpha: Transparency of the markers. Default is 1.

        """
        self.x = x if x is not None else []
        self.y = y if y is not None else []
        self.size = size
        self.facecolor = facecolor
        self.edgecolor = edgecolor
        self.linewidth = linewidth
        self.alpha = alpha
        self.patch_collection = None
        self.marker = None
        self.cmap = cmap

    def simpleMarker(self, ax, marker='o'):
        """
        Create simple matplotlib.pyplot markers.

        :param ax: matplotlib subplot in which markers are plotted.
        :param marker: string indicating the marker type.
        :return: matplotlib.lines.Line2D object that represents the plotted markers.

        """
        if len(self.x) == 0:
            return None
        else:
            plot = ax.scatter(self.x, self.y,
                              s=self.size,
                              c=self.facecolor,
                              edgecolors=self.edgecolor,
                              linewidths=self.linewidth,
                              alpha=self.alpha,
                              marker=marker)
            plot.set_cmap(self.cmap)
            return plot

    def markerCross(self):
        """
        Create a list of cross-shaped markers.

        :return: List of markers.

        """
        self.marker = [Polygon(np.array([[xi, yi],
                                          [xi + self.size / 4, yi],
                                          [xi - self.size / 4, yi],
                                          [xi, yi],
                                          [xi, yi - self.size / 4],
                                          [xi, yi + self.size / 4]], ), closed=True) for xi, yi in zip(self.x, self.y)]
        self._createPatchCollection()
        return self.patch_collection

    def markerX(self):
        """
        Create a list of X-shaped markers.

        :return: List of markers.

        """
        size = self.size
        self.marker = [Polygon(np.array([[xi, yi],
                                          [xi + size / 4, yi - size / 4],
                                          [xi - size / 4, yi + size / 4],
                                          [xi, yi],
                                          [xi - size / 4, yi - size / 4],
                                          [xi + size / 4, yi + size / 4],
                                          ]), closed=True) for xi, yi in zip(self.x, self.y)]
        self._createPatchCollection()
        return self.patch_collection

    def markerCircle(self):
        """
        Create a list of circle markers.

        :return: List of markers.

        """
        self.marker = [Circle(xy=(xi, yi), radius=self.size / 2) for xi, yi in zip(self.x, self.y)]
        self._createPatchCollection()
        return self.patch_collection

    def markerSquare(self):
        """
        Create a list of square markers.

        :return: List of Polygon markers.

        """
        self.marker = [Rectangle((xi - self.size/2,
                                     yi - self.size/2),
                                 self.size, self.size) for xi, yi in zip(self.x, self.y)]
        self._createPatchCollection()
        return self.patch_collection

    def _createPatchCollection(self):
        """
        Create a PatchCollection from the self.marker.

        Uses instance attributes for marker properties such as facecolor, edgecolor, linewidth, and alpha.

        """
        self.patch_collection = PatchCollection(self.marker,
                                                facecolors=self.facecolor,
                                                edgecolors=self.edgecolor,
                                                linewidths=self.linewidth,
                                                alpha=self.alpha)


class LineMarker:
    def __init__(self, x1: list = None, y1: list = None, x2: list = None, y2: list = None,
                 linecolor="white", linewidth=1, alpha=1):
        """

        """
        self.x1 = x1 if x1 is not None else []
        self.y1 = y1 if y1 is not None else []
        self.x2 = x2 if x2 is not None else []
        self.y2 = y2 if y2 is not None else []
        self.linecolor = linecolor
        self.linewidth = linewidth
        self.alpha = alpha

    def simpleMarker(self, ax, style="--"):
        """
        Create simple matplotlib.pyplot line.

        :param ax: matplotlib subplot in which markers are plotted.
        :param style: string indicating the line type.
        :return: matplotlib.lines.Line2D object that represents the plotted markers.

        """
        if len(self.x1) == 0:
            return None
        else:
            return ax.plot([self.x1, self.x2],
                           [self.y1, self.y2],
                           linestyle=style,
                           color=self.linecolor,
                           linewidth=self.linewidth,
                           alpha=self.alpha)
