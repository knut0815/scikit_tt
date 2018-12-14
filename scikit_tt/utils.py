#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import time as _time
import sys
from scikit_tt.tensor_train import TT
import matplotlib.pyplot as plt


def header(title=None, subtitle=None):
    """Print scikit_tt header

    Parameters
    ----------
    title: string
        title or name of the procedure
    subtitle: string
        subtitle of the procedure
    """

    print('                                               ')
    print('.  __    __               ___    ___ ___       ')
    print('. /__`  /  `  |  |__/  |   |      |   |        ')
    print('| .__/  \__,  |  |  \  |   |      |   |        ')
    print('o ─────────── o ────── o ─ o ──── o ─ o ── ─  ─')
    if title is not None:
        print('|')
        print('o ─ ' + title)
    if subtitle is not None:
        print('    ' + subtitle)
    print(' ')
    print(' ')


def mean_concentrations(series):
    """Mean concentrations of TT series

    Compute mean concentrations of a given time series in TT format representing probability distributions of, e.g., a
    chemical reaction network..

    Parameters
    ----------
    series: list of instances of TT class

    Returns
    -------
    mean: ndarray(#time_steps,#species)
        mean concentrations of the species over time
    """

    # define array
    mean = np.zeros([len(series), series[0].order])

    # loop over time steps
    for i in range(len(series)):

        # loop over species
        for j in range(series[0].order):
            # define tensor train to compute mean concentration of jth species
            cores = [np.ones([1, series[0].row_dims[k], 1, 1]) for k in range(series[0].order)]
            cores[j] = np.zeros([1, series[0].row_dims[j], 1, 1])
            cores[j][0, :, 0, 0] = np.arange(series[0].row_dims[j])
            tensor_mean = TT(cores)

            # define entry of mean
            mean[i, j] = (series[i].transpose() @ tensor_mean).element([0] * 2 * series[0].order)

    return mean


def plot_parameters(font_size=14):
    """Customized plot parameters

    Parameters
    ----------
    font_size: int
        default font size for title, labels, etc.
    """

    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
    plt.rcParams["mathtext.fontset"] = "cm"
    plt.rcParams.update({'font.size': font_size})
    plt.rcParams.update({'figure.autolayout': True})
    plt.rcParams.update({'axes.grid': True})


def progress(text, percent, dots=3):
    """Show progress in percent

    Print strings of the form, e.g., 'Running ... 10%' etc., without line breaks.

    Parameters
    ----------
    text: string
        string to print
    percent: float
        current progress
    dots: int, optional
        number of dots to print, default is 3
    """

    sys.stdout.write('\r' + text + ' ' + dots * '.' + ' ' + str("%.1f" % percent) + '%')

    if percent == 100:
        sys.stdout.write('\n')


class Timer(object):
    """Measure CPU time

    Can be executed using the 'with' statement in order to measure the CPU time needed for calculations.
    """

    def __enter__(self):
        self.start_time = _time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.elapsed = _time.time() - self.start_time


def unit_vector(dimension, index):
    """Canonical unit vector

    Return specific canonical unit vector in a given given dimension.

    Parameters
    ----------
    dimension: int
        dimension of the unit vector
    index: int
        position of the 1

    Returns
    -------
    v: ndarray
        unit vector
    """
    v = np.zeros(dimension)
    v[index] = 1

    return v
