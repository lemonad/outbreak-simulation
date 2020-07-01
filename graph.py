"""
Jonas Nockert (2020)

TODO Prune closer contacts less than those far away?
TODO Use overlapping leaves to degree of contactness (c).
     That is, something like at level N, c=1, at level N-1, c=0.5,
     where contacts at level N-1 exclude those at level N.
TODO Model difference in latent period and incubation period (e.g. presymptomatic
     infectiousness seems to be on the scale of multiple days in the case of COVID-19")
TODO Model severity of symptoms with more severe cases limiting their contacts
     more than milder cases.
TODO Estimate R0 using the initial data (for checking that parameters are set ok)
TODO Contacts further away could be seen as going to the store and someone travelling
     being there — but then this type of contacts should be random and not constant
     over time. In this case it would be okay with a high transmission probability.
TODO Transmission probability should be probably be random, especially for intermittent
     contacts further away in the graph. Generally low but sometimes very high.
TODO Metrics? When implementing changes, the result should preferably become better
     according to some metric (more interesting, more accurate, more realistic,
     faster, etc.)
TODO Model reporting times in order to have something to test nowcasting and
     back-projection on.
TODO Estimate generation times.
"""
from enum import Enum
import math
import numpy as np
from PIL import Image, ImageColor, ImageDraw
import random
from scipy import stats
import time

import matplotlib
matplotlib.use("MacOSX")
import matplotlib.pyplot as plt

from bsp import BSP_Tree
from geometry import Point, Rect


class NodeState(Enum):
    SUSCEPTIBLE = 1
    INFECTED_LATENT = 2
    INFECTIOUS = 3
    RECOVERED = 4


class GraphState(Enum):
    NORMAL = 1
    PHYSICAL_DISTANCING = 2
    OPENING_UP = 3


class Node:
    # TODO Use duration/period random distributions.
    # infectious_durations = stats.norm(loc=7, scale=2)
    # latent_periods = stats.norm(loc=4, scale=1)
    # infectious_durations = stats.norm(loc=7, scale=1.5)

    def __init__(self, bsp_node, point):
        self.bsp_node = bsp_node
        self.counter = 0
        self.id = id(point)
        self.infection_rate = 0.01
        self.point = point
        self.state = NodeState.SUSCEPTIBLE

    def is_infected(self):
        return (
            self.state == NodeState.INFECTED_LATENT
            or self.state == NodeState.INFECTIOUS
        )

    def is_latent(self):
        return self.state == NodeState.INFECTED_LATENT

    def is_infectious(self):
        return self.state == NodeState.INFECTIOUS

    def is_recovered(self):
        return self.state == NodeState.RECOVERED

    def is_susceptible(self):
        return self.state == NodeState.SUSCEPTIBLE

    def infect(self):
        self.state = NodeState.INFECTED_LATENT
        self.counter = 7

    def infectious(self, infectious=False):
        self.state = NodeState.INFECTIOUS
        self.counter = 7

    def recover(self):
        self.state = NodeState.RECOVERED
        self.counter = 0

    def pre_step(self):
        if self.is_recovered():
            return

        if self.is_latent() and self.counter <= 0:
            self.infectious()
        elif self.is_infectious() and self.counter <= 0:
            self.recover()
        elif self.counter > 0:
            self.counter -= 1

    def step(self, contact_ids, nodes):
        if self.is_recovered():
            return

        for cid in contact_ids:
            contact = nodes[cid]
            # Do nothing if both infected or neither infected.
            if (
                (self.is_infectious() and contact.is_susceptible())
                or (self.is_susceptible() and contact.is_infectious())
            ) and random.random() < self.infection_rate:
                if self.is_susceptible():
                    self.infect()
                else:
                    contact.infect()
                    break

    def post_step(self):
        pass


class Graph:
    def __init__(self, n1, n2):
        self.N = n1 * n2
        self.n1 = n1
        self.n2 = n2
        self.tree = BSP_Tree(n1, n2)
        self.nodes = {}
        self.adj = {}
        self.stats = []
        self.t = 0
        self.state = GraphState.NORMAL
        self.physical_distancing_t = None

    def infect_random(self, n=1):
        assert self.nodes
        node_ids = random.choices(list(self.nodes), k=n)
        for node_id in node_ids:
            self.nodes[node_id].infectious()
        return node_ids

    def physical_distancing(self, rate=0.5):
        self.state = GraphState.PHYSICAL_DISTANCING
        self.physical_distancing_t = self.t
        for node_id in self.adj:
            contact_ids = self.adj[node_id]
            n_ids = len(contact_ids)
            self.adj[node_id] = random.sample(contact_ids, int(n_ids * rate))

    def step(self):
        assert self.nodes
        assert self.adj
        self.t += 1
        print(f"Stepping to time t={self.t}")

        for node_id in self.nodes:
            self.nodes[node_id].pre_step()
        for node_id in self.nodes:
            self.nodes[node_id].step(self.adj[node_id], self.nodes)

        n_susceptible = 0
        n_infected = 0
        n_recovered = 0
        for node_id in self.nodes:
            node = self.nodes[node_id]
            if node.is_infected():
                n_infected += 1
            elif node.is_recovered():
                n_recovered += 1
            else:
                n_susceptible += 1
        assert self.N == n_susceptible + n_infected + n_recovered

        if self.t > 1:
            # Note: the below assumes that S->I and I->R is always at least one
            # time step each.

            # S is a decreasing function (so delta is <= 0).
            delta_susceptible = n_susceptible - self.stats[-1]["S"]
            # R is an increasing function (so delta is >= 0).
            delta_recovered = n_recovered - self.stats[-1]["R"]
            delta_infected = n_infected - self.stats[-1]["I"]

            new_infected = -delta_susceptible
            n_infected_cumulative = self.stats[-1]["ICUM"] + new_infected
        else:
            n_infected_cumulative = n_infected

        self.stats.append(
            {
                "t": self.t,
                "S": n_susceptible,
                "I": n_infected,
                "R": n_recovered,
                "ICUM": n_infected_cumulative,
            }
        )

    def plot(self, show=True, filename=None):
        t = list(map(lambda x: x["t"], self.stats))
        susceptible = list(map(lambda x: x["S"], self.stats))
        infected = list(map(lambda x: x["I"], self.stats))
        recovered = list(map(lambda x: x["R"], self.stats))
        infected_cumulative = list(map(lambda x: x["ICUM"], self.stats))

        fig = plt.figure(1, clear=True)
        plt.plot(t, susceptible, color="blue", label="S")
        plt.plot(t, infected_cumulative, color="orange", label="I (cumul.)")
        plt.plot(t, recovered, color="green", label="R")
        plt.plot(t, infected, color="red", label="I")
        if self.physical_distancing_t:
            plt.axvline(
                x=self.physical_distancing_t,
                linestyle=":",
                color="gray",
                label="physical dist.",
            )
        fig.legend()
        if show:
            plt.pause(0.1)
        if filename:
            plt.savefig(filename)

    def image(self, adj_id=None, show=True, filename=None, modal=False):
        assert self.nodes
        image = Image.new("RGB", (self.n1, self.n2))
        for node in self.nodes.values():
            if node.is_latent():
                color = (255, 255, 0)
            elif node.is_infectious():
                color = (255, 0, 0)
            elif node.is_recovered():
                color = (0, 255, 0)
            else:
                color = (
                    int(node.bsp_node.color[0] * 255),
                    int(node.bsp_node.color[1] * 255),
                    int(node.bsp_node.color[2] * 255),
                )
            image.putpixel((node.point.x, node.point.y), color)

        if adj_id:
            node = self.nodes[adj_id]
            draw = ImageDraw.Draw(image)
            for node_id in self.adj[adj_id]:
                contact = self.nodes[node_id]
                draw.line(
                    [
                        node.bsp_node.rect.center.as_tuple(),
                        contact.bsp_node.rect.center.as_tuple(),
                    ],
                    (255, 255, 255, 128),
                )
            for node_id in self.back_adj[adj_id]:
                contact = self.nodes[node_id]
                draw.line(
                    [
                        node.bsp_node.rect.center.as_tuple(),
                        contact.bsp_node.rect.center.as_tuple(),
                    ],
                    (255, 255, 255, 128),
                )
        if show:
            plt.figure(2)
            plt.imshow(image)
            if modal:
                plt.show()
            else:
                plt.pause(0.1)
        if filename:
            image.save(filename)

    def adjacency_matrix(self):
        self.nodes = {}
        self.adj = {}
        self.back_adj = {}
        leaf_points = {}
        leaves = self.tree.leaves()
        n_leaves = len(leaves)

        print("Creating internal leaf connections")
        prev_percent = 0
        for i in range(n_leaves):
            percent = int(100 * i / (n_leaves - 1))
            if percent > prev_percent:
                print("{:.2f} %".format(percent))
                prev_percent = percent
            points = leaves[i].get_points()
            leaf_points[i] = points
            n_points = len(points)

            for p in points:
                node = Node(leaves[i], p)
                self.nodes[node.id] = node
                self.adj[node.id] = set()
                self.back_adj[node.id] = set()

            for pi in range(n_points - 1):
                for pj in range(pi + 1, n_points):
                    id1 = id(points[pi])
                    id2 = id(points[pj])
                    self.adj[id1].add(id2)
                    self.back_adj[id2].add(id1)

        print("Creating external leaf connections")
        prev_percent_int = 0
        start_timestamp = time.time()
        for i in range(n_leaves - 1):
            percent = i / (n_leaves - 2)
            percent_int = int(100 * percent)
            if percent_int > prev_percent_int:
                ts = time.time()
                delta_t = ts - start_timestamp
                print(
                    "{:d} % ({:.0f} s, {:.0f}s remaining)".format(
                        percent_int,
                        round(delta_t),
                        round((delta_t / percent - delta_t) / 2),
                    )
                )
                prev_percent_int = percent_int
            points = leaf_points[i]

            for j in range(i + 1, n_leaves):
                other_points = leaf_points[j]
                n_other_points = len(other_points)
                d = self.tree.relative_distance(leaves[i], leaves[j])
                # n_connections = int(np.random.exponential(1 / d))
                n_connections = int(
                    n_other_points * 0.2 * np.random.exponential(2 * (1 - d) / 3)
                )
                p1s = random.choices(points, k=n_connections)
                p2s = random.choices(other_points, k=n_connections)

                for z1, z2 in zip(p1s, p2s):
                    self.adj[id(z1)].add(id(z2))
                    self.back_adj[id(z2)].add(id(z1))
