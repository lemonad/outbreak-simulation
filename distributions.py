"""

[1] Bar-On et al. "A quantitative compendium of COVID-19 epidemiology" (May 2020)
    (https://arxiv.org/pdf/2006.01283.pdf)

[2] Li et al. "Transmission characteristics of the COVID-19 outbreak in China: a study
    driven by data" (preprint, March 2020).
    [https://www.researchgate.net/publication/339620050_Transmission_characteristics_of_the_COVID-19_outbreak_in_China_a_study_driven_by_data)

"""
import matplotlib
import numpy as np
from scipy import stats

matplotlib.use("MacOSX")
import matplotlib.pyplot as plt


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class UnknownDistribution(Error):
    """Exception raised for unknown distribution name."""

    def __init__(self, name, message):
        self.name = name
        self.message = message


class Distributions:
    def __init__(self, name=None):
        if name == "covid-19":
            # Latent period distribution set to incubation time distribution given in
            # [2].
            #
            # TODO Check for newer research and possible pre-symptom infectiousness:
            # from [2]: "Since the mean generation time is smaller than the mean
            # incubation period, on average, a patient may become infectious 3.9 days
            # before showing major symptoms."
            #
            # [1] gives a median of 3-4 days for the latent period with incubation
            # period being longer with median 5.
            self.latent_period_dist = stats.gamma(3.07, scale=2.35)

            # [1] gives a median of 4-5 days with the caveat that this is the
            # population median and the "inter-individual variation is substantial".
            self.infectious_duration_dist = stats.gamma(3.5, scale=1.5)
        else:
            raise UnknownDistribution(name, "Only 'covid-19' is accepted for now.")

    def plot(self):
        N = 1000
        fig = plt.figure()
        plt.hist(self.latent_period_dist.rvs(N), density=True)
        x = np.linspace(
            self.latent_period_dist.ppf(0.001), self.latent_period_dist.ppf(0.999), 100
        )
        plt.plot(x, self.latent_period_dist.pdf(x))
        plt.title("Distribution of latent periods")

        fig = plt.figure()
        plt.hist(self.infectious_duration_dist.rvs(N), density=True)
        x = np.linspace(
            self.infectious_duration_dist.ppf(0.001),
            self.infectious_duration_dist.ppf(0.999),
            100,
        )
        plt.plot(x, self.infectious_duration_dist.pdf(x))
        plt.title("Distribution of infectious durations")

        plt.show()


if __name__ == "__main__":
    dist = Distributions("covid-19")
    dist.plot()
