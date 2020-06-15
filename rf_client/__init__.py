import logging
from logging import NullHandler

from rf_client.tree_wrapper import TreeWrapper
from rf_client.wrapper import Wrapper

from .map_wrapper import MapWrapper
from . import abc


logging.getLogger(__name__).addHandler(NullHandler())
