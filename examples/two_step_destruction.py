#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This is an example for the application of the QTT format to Markovian master equations of chemical reaction
networks. For more details, see [1]_.

References
----------
..[1] P. Gelß. "The Tensor-Train Format and Its Applications: Modeling and Analysis of Chemical Reaction
      Networks, Catalytic Processes, Fluid Flows, and Brownian Dynamics", Freie Universität Berlin, 2017
"""

import numpy as np
from scikit_tt.tensor_train import TT
import scikit_tt.models as mdl
import scikit_tt.subfunctions as sf
import scikit_tt.tools as tls
import matplotlib.pyplot as plt

# parameters
# ----------
from scikit_tt.solvers import ODE

m = 3
step_sizes = [0.001] * 100 + [0.1] * 9 + [1] * 9
qtt_rank = 10
max_rank = 30

# construct operator in TT format and convert to QTT format
# ---------------------------------------------------------

operator = mdl.two_step_destruction(1, 2, m).tt2qtt([[2] * m] + [[2] * (m + 1)] + [[2] * m] + [[2] * m],
                                                    [[2] * m] + [[2] * (m + 1)] + [[2] * m] + [[2] * m],
                                                    threshold=10 ** -14)

# initial distribution in TT format and convert to QTT format
# -----------------------------------------------------------

initial_distribution = TT.zeros([2 ** m, 2 ** (m + 1), 2 ** m, 2 ** m], [1] * 4)
initial_distribution.cores[0][0, -1, 0, 0] = 1
initial_distribution.cores[1][0, -2, 0, 0] = 1
initial_distribution.cores[2][0, 0, 0, 0] = 1
initial_distribution.cores[3][0, 0, 0, 0] = 1
initial_distribution = TT.tt2qtt(initial_distribution, [[2] * m] + [[2] * (m + 1)] + [[2] * m] + [[2] * m],
                                 [[1] * m] + [[1] * (m + 1)] + [[1] * m] + [[1] * m], threshold=0)

# initial guess in QTT format
# ---------------------------

initial_guess = TT.uniform([2] * (4 * m + 1), ranks=qtt_rank).ortho_right()

# solve Markovian master equation in QTT format
# ---------------------------------------------

print('\nQTT approach')
print('------------\n')
with tls.Timer() as time:
    solution, errors = ODE.implicit_euler_mals(operator, initial_distribution, initial_guess, step_sizes,
                                               threshold=1e-7, max_rank=max_rank, compute_errors=True)
print('CPU time ' + '.' * 22 + ' ' + str("%.2f" % time.elapsed) + 's')
print('Maximum error ' + '.' * 17 + ' ' + str("%.2e" % np.amax(errors)))

# convert to TT and compute mean concentrations
# ---------------------------------------------

for i in range(len(solution)):
    solution[i] = TT.qtt2tt(solution[i], [m, m + 1, m, m])
mean = sf.mean_concentrations(solution)

# plot mean concentrations
# ------------------------

plt.rc('text', usetex=True)
plt.rc('font', family='serif')
plt.rcParams["mathtext.fontset"] = "cm"
plt.rcParams.update({'font.size': 14})
plt.rcParams.update({'figure.autolayout': True})
plt.plot(np.insert(np.cumsum(step_sizes), 0, 0), mean)
plt.title('Mean concentrations', y=1.05)
plt.xlabel(r'$t$')
plt.ylabel(r'$\overline{x_i}(t)$')
plt.axis([0, 2, 0, 2 ** (m + 1) - 2])
plt.grid(which='major')
plt.legend(['species ' + str(i) for i in range(1, 5)], loc=1)
plt.show()
