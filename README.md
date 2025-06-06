# SARPlotter

SARPlotter plots timeseries of deformation, temporal unwrapping and more for SARvey.

## Description
SARPlotter reads the files created by SARvey software to make the plots. It consists of a main window and several sub-windows to make

- timeseries plot
- temporal unwrapping plots


## Project Overview
SARPlotter consists of the following components:

- **Main Module:** [`main.py`](app/main.py) Located in the `app` directory. This is the entry point for the SARPlotter application.
- **Qt Designer UI Files:** Located in the `app/src/ui` directory. These files create th graphical user interface.
    - main window:
        - [`main_window.ui`](app/src/ui/main_window.ui) is the main application window responsible for displaying the primary user interface.
    - widgets that seat in different docks of the main window:
        - [`widget_setting.ui`](app/src/ui/widget_setting.ui) is the setting widget, providing different plot configurations.
        - [`widget_point_list.ui`](app/src/ui/widget_point_list.ui) is the point list widget displaying a list of clicked points.
- **Source Files:** The `app/src` directory contains Python files that implement the core functionality.
    - [`main_window.py`](app/src/main_window.py)
        - `MainWindow` class loads ui files from `app/src/ui/ to construct the main application window. This class inherits from PySide6 QMainWindow class.
    - [`data.py`](app/src/data.py)
        - `Data` class creates a structure for SAR/InSAR data and provides methods to read them. It includes the following methods.
            - `readAmplitude()`
            - `readTemporalCoherence()`
            - `readP1()`
            - `readP2()`
            - `updateP2File(index)` clears the old p2 information when p2 file selection index changes
            - `readIfgNetwork()`
            - `readDates()`
            - `readTsForIdx()`
    - [`plot_main.py`](app/src/plot_main.py)
        - `Plot` class creates the main plot for the SARPlotter application.
            - `initMainFigure()`
                - `onClickMap` and `onHoverMap` methods are called when main plot is clicked or hovered.
            - `plotAmplitude()`
            - `plotTemporalCoherence()`
            - `plotNoBackground()`
            - `plotAspect(status)`
            - `plotLabels(status)`
            - `plotCmap(cmap)`
            - `plotP1(status)`
            - `plotP2(status)`
            - `onClickMap(event)`
            - `onHoverMap(event)`
            - `plotTimeseriesList(selected_indices)`
            - `addLeftClickedMarkers(x: list, y: list, facecolor, edgecolor, size, alpha, linewidth)`
            - `addRightClickedMarkers(x: list, y: list, facecolor, edgecolor, size, alpha, linewidth)`
            - `clearP2Plots()`
    - [`plot_timeseries.py`](app/src/plot_timeseries.py)
        - `TimeseriesPlot` class
            - `plotTimeseries(idx: int, idx_ref: int)`
            - `clear()`
    - [`marker.py`](app/src/marker.py)
        - `Marker` class
            - `markerCross()`
            - `markerX()`
            - `circle()`
            - `square()`
        

## config file
The config file app/config/config.json contains the parameters of the app.
The widget parameters are handled in window_config.py.
When add/modify the components of the GUI, the config should be added to the config file and the relevant part should be
added to the window_config.py.





## Installation
...

## Usage
...

## Support
...

## Roadmap
...

## Contributing
...

## Authors and acknowledgment
...

## License
...

## Project status
...

## Acknowledgement
The following packages are used to develop SARPlotter

- [**Qt Designer**](https://doc.qt.io/qt-6/qtdesigner-manual.html): Used for designing the graphical user interface (GUI).
- [**PySide6**](https://doc.qt.io/qtforpython-6/index.html): Used for implementing the GUI.
