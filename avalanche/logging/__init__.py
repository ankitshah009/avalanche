"""
The :py:mod:`logging` module provides a set of utilities that can be used for
logging your experiment metrics results  on stdout, logfile and browser-based
dashboard such as "Tensorboard" and "Weights & Biases". These resources are
provided in :py:mod:`interactive_logging`, :py:mod:`text_logging` and
:py:mod:`tensorboard_logger` respectively.
"""

from .strategy_logger import *
from .tensorboard_logger import *
from .text_logging import TextLogger
from .interactive_logging import InteractiveLogger

from avalanche.logging import InteractiveLogger
from avalanche.training.plugins import EvaluationPlugin
from avalanche.evaluation.metrics import accuracy_metrics, loss_metrics

default_logger = EvaluationPlugin(
    accuracy_metrics(minibatch=False, epoch=True, experience=True, stream=True),
    loss_metrics(minibatch=False, epoch=True, experience=True, stream=True),
    loggers=[InteractiveLogger()])
