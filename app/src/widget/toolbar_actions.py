
from app.src.widget import screenshot


def conncetToolbar(main_window):
    main_window.ui.toolbar_action_screenshot.triggered.connect(
        lambda: screenshot.screenShot(main_window))
    main_window.ui.toolbar_action_pretty_screenshot.triggered.connect(
        lambda: screenshot.screenShotPretty(main_window))
