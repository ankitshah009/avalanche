#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
# Copyright (c) 2020 ContinualAI                                               #
# Copyrights licensed under the MIT License.                                   #
# See the accompanying LICENSE file for terms.                                 #
#                                                                              #
# Date: 20-11-2020                                                             #
# Author(s): Vincenzo Lomonaco                                                 #
# E-mail: contact@continualai.org                                              #
# Website: clair.continualai.org                                               #
################################################################################

"""
This is a simple example on the Permuted MNIST benchmark.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import torch
from torch.nn import CrossEntropyLoss
from torch.optim import SGD

from avalanche.benchmarks.classic import PermutedMNIST
from avalanche.models import SimpleMLP
from avalanche.training.strategies import Naive
from avalanche.evaluation.metrics import TaskForgetting, accuracy_metrics, \
    loss_metrics, timing_metrics, cpu_usage_metrics
from avalanche.logging import InteractiveLogger
from avalanche.training.plugins import EvaluationPlugin

def main():

    # Config
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    # model
    model = SimpleMLP(num_classes=10)

    # CL Benchmark Creation
    scenario = PermutedMNIST(n_steps=5, seed=1)
    train_stream = scenario.train_stream
    test_stream = scenario.test_stream

    # Prepare for training & testing
    optimizer = SGD(model.parameters(), lr=0.001, momentum=0.9)
    criterion = CrossEntropyLoss()

    # choose some metrics and evaluation method
    interactive_logger = InteractiveLogger()

    eval_plugin = EvaluationPlugin(
        accuracy_metrics(minibatch=True, epoch=True, task=True),
        loss_metrics(minibatch=True, epoch=True, task=True),
        timing_metrics(epoch=True, epoch_average=True, test=False),
        cpu_usage_metrics(step=True),
        TaskForgetting(),
        loggers=[interactive_logger])

    # Continual learning strategy
    cl_strategy = Naive(
        model, optimizer, criterion, train_mb_size=32, train_epochs=2,
        test_mb_size=32, device=device, evaluator=eval_plugin)

    # train and test loop
    results = []
    for train_task in train_stream:
        print("Current Classes: ", train_task.classes_in_this_step)
        cl_strategy.train(train_task)
        results.append(cl_strategy.test(test_stream))

if __name__ == '__main__':
    main()