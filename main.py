"""
Jonas Nockert (2020)

Epidemiological SIR model simulation created for fun/learning during the course
"The Mathematics and Statistics of Infectious Disease Outbreaks" (MT3002)
at Stockholm University, Summer 2020.

Probably not very interesting or useful.

"""
import glob
from pathlib import Path
import sys

from graph import Graph


g = Graph(100, 100)
g.adjacency_matrix()
initially_infected = g.infect_random(n=1)
social_distancing = False

for p in Path("./images").glob("image-*.png"):
    p.unlink()
for p in Path("./images").glob("plot-*.png"):
    p.unlink()

for i in range(250):
    g.step()

    n_susceptible = g.stats[-1]["S"]
    n_infected = g.stats[-1]["I"]
    n_recovered = g.stats[-1][3]

    # Stop early if epidemic is over.
    if n_infected == 0:
        break

    # TODO Social distancing only when we have a large amount of
    # simultaneous infections? The number of cumulative infections would
    # not count into the decision, right?
    if not social_distancing and (n_infected / n_susceptible) > 0.1:
        social_distancing = True
        g.social_distancing(rate=0.1)
    # elif social_distancing and (n_infected / n_susceptible) > 0.1:
    # simulate opening up.

    g.plot(filename=f"images/plot-{i:03d}.png")
    g.image(filename=f"images/image-{i:03d}.png")

print(g.stats)

# Uncomment to show connection graph of the first initially infected person.
# g.image(adj_id=initially_infected[0])
