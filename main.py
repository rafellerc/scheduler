from os.path import dirname, abspath
from src.exchange_data import generate_forms, read_forms, write_sol
from src.optim import solve
from src.tests import *

import numpy as np
from random import randint


def main():
    root_dir = dirname(abspath(__file__))
    # generate_forms(root_dir) ?
    optim_params, names, slot_names, days = read_forms(root_dir)
    n_p, n_d, n_s, G, T, K, indisp, forced, slot_choice, demand = optim_params

    prob_status, sol, value = solve(n_p, n_d, n_s, G, T, K, indisp, forced,
                                    slot_choice, demand)
    print(prob_status)
    if sol is not None:
        write_sol(root_dir, sol, names, slot_names, days)

if __name__ == "__main__":
    main()
