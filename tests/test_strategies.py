#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
# Copyright (c) 2020 ContinualAI Research                                      #
# Copyrights licensed under the CC BY 4.0 License.                             #
# See the accompanying LICENSE file for terms.                                 #
#                                                                              #
# Date: 1-06-2020                                                              #
# Author(s): Andrea Cossu                                                #
# E-mail: contact@continualai.org                                              #
# Website: clair.continualai.org                                               #
################################################################################

import unittest

import torch

from torchvision.datasets import MNIST
from torchvision.transforms import ToTensor, Compose
from torch.optim import SGD
from torch.nn import CrossEntropyLoss

from avalanche.extras.models import SimpleMLP
from avalanche.benchmarks.scenarios import DatasetPart
from avalanche.training.strategies import Naive, Replay, CWRStar
from avalanche.benchmarks import nc_scenario, NCStepInfo


class StrategyTest(unittest.TestCase):

    def test_naive(self):
        model = SimpleMLP()
        optimizer = SGD(model.parameters(), lr=1e-3)
        criterion = CrossEntropyLoss()
        mnist_train, mnist_test = self.load_dataset()
        my_nc_scenario = nc_scenario(
            mnist_train, mnist_test, 5, task_labels=False,
            shuffle=True, seed=1234)

        strategy = Naive(model, optimizer, criterion, train_mb_size=64)
        self.run_strategy(my_nc_scenario, strategy)

    def test_cwrstar(self):
        model = SimpleMLP()
        optimizer = SGD(model.parameters(), lr=1e-3)
        criterion = CrossEntropyLoss()
        mnist_train, mnist_test = self.load_dataset()
        my_nc_scenario = nc_scenario(
            mnist_train, mnist_test, 5, task_labels=False,
            shuffle=True, seed=1234)

        strategy = CWRStar(model, optimizer, criterion, 'features.0.bias',
                           train_mb_size=64)
        self.run_strategy(my_nc_scenario, strategy)

    def test_replay(self):
        model = SimpleMLP()
        optimizer = SGD(model.parameters(), lr=1e-3)
        criterion = CrossEntropyLoss()
        mnist_train, mnist_test = self.load_dataset()
        my_nc_scenario = nc_scenario(
            mnist_train, mnist_test, 5, task_labels=False, seed=1234)

        strategy = Replay(model, optimizer, criterion,
                          mem_size=200, train_mb_size=64)
        self.run_strategy(my_nc_scenario, strategy)

    def load_dataset(self):
        mnist_train = MNIST(
            './data/mnist', train=True, download=True, 
            transform=Compose([ToTensor()]))

        mnist_test = MNIST(
            './data/mnist', train=False, download=True,
            transform=Compose([ToTensor()]))
        return mnist_train, mnist_test

    def run_strategy(self, scenario, cl_strategy):
        print('Starting experiment...')
        results = []
        batch_info: NCStepInfo
        for batch_info in scenario:
            print("Start of step ", batch_info.current_step)

            cl_strategy.train(batch_info, num_workers=4)
            print('Training completed')

            print('Computing accuracy on the current test set')
            results.append(cl_strategy.test(batch_info, DatasetPart.CURRENT,
                                            num_workers=4))


if __name__ == '__main__':
    unittest.main()