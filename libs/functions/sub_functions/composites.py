""" composite functions """
from libs.metrics import (
    market_composite_index, bond_composite_index, correlation_composite_index, type_composite_index
)


def mci_function(config: dict):
    """market composite index function

    Args:
        config (dict): configuration dictionary
    """
    config['properties'] = config.get('properties', {})
    config['properties']['Indexes'] = config['properties'].get('Indexes', {})
    config['properties']['Indexes']['Market Sector'] = config['properties']['Indexes'].get(
        'Market Sector', True)
    market_composite_index(config=config, plot_output=True)


def bci_function(config: dict):
    """bond composite index function

    Args:
        config (dict): configuration dictionary
    """
    config['properties'] = config.get('properties', {})
    config['properties']['Indexes'] = config['properties'].get('Indexes', {})
    config['properties']['Indexes']['Treasury Bond'] = True
    config['properties']['Indexes']['Corporate Bond'] = True
    config['properties']['Indexes']['International Bond'] = True
    bond_composite_index(config, plot_output=True)


def tci_function(config: dict):
    """type composite index function

    Args:
        config (dict): configuration dictionary
    """
    config['properties'] = config.get('properties', {})
    config['properties']['Indexes'] = config['properties'].get('Indexes', {})
    config['properties']['Indexes']['Type Sector'] = config['properties']['Indexes'].get(
        'Type Sector', True)
    type_composite_index(config=config, plot_output=True)


def correlation_index_function(config: dict):
    """correlation composite index function

    Args:
        config (dict): configuration dictionary
    """
    config['properties'] = config.get('properties', {})
    config['properties']['Indexes'] = config['properties'].get('Indexes', {})

    timeframe = config.get('duration', 'short')
    temp = {"run": True, "type": timeframe}
    config['properties']['Indexes']['Correlation'] = config['properties']['Indexes'].get(
        'Correlation', temp)
    correlation_composite_index(config=config)
