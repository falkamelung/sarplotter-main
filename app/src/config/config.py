from .load_config import loadConfig
from .config_timeseries import configTimeseriesTab
from .config_temporal_unwrap import configTemporalUnwrapTab
from .config_network import configNetworkTab
from .config_map import configMapTab, configPointsTab

config = loadConfig("config.json")


def configApp(window):
    """
    set window parameters from config.json
    :param window:
    :return:
    """
    _configAppParameters(window)
    _configAppWidgets(window)


def _configAppParameters(window):
    """
    set parameters
    :param window:
    :return:
    """
    plot = window.plot
    _configObject(plot.plot_timeseries.parms, config["setting_widget"]["timeseries"])
    _configObject(plot.plot_temporal_unwrapping.parms, config["setting_widget"]["temporal_unwrap_plot"])
    _configObject(plot.plot_temporal_unwrapping.tu.parms, config["setting_widget"]["temporal_unwrap"])
    _configObject(plot.plot_network.parms, config["setting_widget"]["network"])
    _configObject(plot.parms, config["setting_widget"]["map"])


def _configAppWidgets(window):
    """
    set window settings
    :param window:
    :return:
    """
    plot = window.plot
    widget = window.setting_widget
    configNetworkTab(plot.plot_network.parms, widget)
    configTimeseriesTab(plot.plot_timeseries.parms, widget)
    configTemporalUnwrapTab(plot.plot_temporal_unwrapping.tu.parms,
                            plot.plot_temporal_unwrapping.parms, widget)

    configMapTab(plot.parms, widget)

    configPointsTab(plot.parms, window.points_widget)


def _configObject(obj: object, config: dict, lookup={}):
    """

    :param obj:
    :param config:
    :param lookup:
    :return:
    """
    # if the variable in Parms and config file are different, assign them in config file
    # lookup = {"key_in_Parm_class": "key_in_config.json"}
    # lookup = {"plot_enable": "plot"}
    for key in obj.__dict__.keys():
        if key in lookup.keys():
            key_in_config = lookup[key]
        else:
            key_in_config = key
        try:
            if key_in_config in config:
                setattr(obj, key, config[key_in_config])
            else:
                print(f"{key} not found in config file")
        except Warning:
            print(f"problem reading {key} from config and setting the attribute. Check the config file.")
