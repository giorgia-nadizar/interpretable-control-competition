from beluga_lib import BelugaProblem
import numpy as np
from importlib import resources
from . import configuration
import json
from typing import Iterable
import copy

def add_reference_arrivals(prb : BelugaProblem,
                           seed : int,
                           prec : int = 2):
    # Load rates from the included file
    rates_file = resources.files(configuration) / 'hourly_rates.json'
    with rates_file.open() as fp:
        rates = json.load(fp)
        rates = {int(k) : v for k, v in rates.items()}
    # Build and seed an RNG
    rng = np.random.default_rng(seed)
    # Prepare all flights for processing
    queue = prb.flights.copy()
    # flight_times = []
    now = 0
    period = max(rates.keys()) + 1
    while len(queue) > 0:
        # Draw a number of flights for this time
        n_flight_per_step = rng.poisson(rates[now % period])
        # Draw arrivals times uniformly within the hour
        offsets = rng.uniform(size=n_flight_per_step)
        offsets = np.round(offsets, decimals=prec)
        # Sort these local arrival times
        offsets = np.sort(offsets)
        for k, offset in enumerate(offsets):
            # Assign the scheduled arrival time
            queue[0].scheduled_arrival = now + offset
            # Remove the flight from the queue
            queue.pop(0)
            # Early stop
            if len(queue) == 0:
                break
        # Advance time
        now += 1



class ArrivalSampler:

    def __init__(self):
        self.support = None
        self.probs = None
        self.period = None
        pass

    def setup(self):
        # Load the delay distribution
        delay_file = resources.files(configuration) / 'delay_distribution.json'
        with delay_file.open() as fp:
            data = json.load(fp)
            # Load support and probabilities
            support = []
            probs = []
            for k in sorted(data, key=lambda k: float(k)):
                support.append(float(k))
                probs.append(data[k])
            self.support = np.array(support)
            self.probs = np.array(probs)
        # Load the rates to determine the period
        rates_file = resources.files(configuration) / 'hourly_rates.json'
        with rates_file.open() as fp:
            rates = json.load(fp)
            rates = {int(k) : v for k, v in rates.items()}
        self.period = max(rates.keys()) + 1

    def sample_arrivals_times(self,
                        scheduled_arrivals : Iterable[float],
                        size : int = None,
                        seed : int = None,
                        rebase : bool = True):
        assert(size is None or size > 0)
        # Build and seed an RNG
        rng = np.random.default_rng(seed)
        # Convert scheduled_arrivals to an array
        scheduled_arrivals = np.array(scheduled_arrivals)
        # Determine the number of samples
        nsamples = 1 if size is None else size
        # Sample delay vectors
        delays = rng.choice(self.support,
                            size=(nsamples, scheduled_arrivals.shape[0]),
                            p=self.probs)
        # Combine delays and scheduled_arrivals
        times = scheduled_arrivals + delays
        # Rebase, if requested
        if rebase:
            new_bases = np.min(times, axis=1).reshape(-1, 1)
            new_bases = np.floor(new_bases / 24) * 24
            times -= new_bases
        # Return the result
        if size is None:
            return times.ravel()
        else:
            return times


    def sample_id_sequences(self,
                        scheduled_arrivals : Iterable[float],
                        size : int = None,
                        seed : int = None,
                        rebase : bool = True):
        # Start by sampling arrivals
        times = self.sample_arrivals_times(scheduled_arrivals, size, seed, rebase)
        # Return position
        if size is None:
            sequence = np.argsort(times)
            return sequence, times[sequence]
        else:
            sequences = np.argsort(times)
            sorted_times = np.vstack([times[k, sequences[k]] for k in range(sequences.shape[0])])
            return sequences, sorted_times


    def sample_flight_sequences(self,
                        prb : BelugaProblem,
                        size : int = None,
                        seed : int = None,
                        rebase : bool = True):
        assert(size is None or size > 0)
        # Obtain a list with the scheduled arrivals
        scheduled_arrivals = [f.scheduled_arrival for f in prb.flights]
        # Sample sequences
        sequences, times = self.sample_id_sequences(scheduled_arrivals,
                                                           size, seed, rebase)
        # Replace sequences with flights
        if size is not None:
            flight_seq = [[prb.flights[k] for k in sequences[i, :]]
                          for i in range(sequences.shape[0])]
        else:
            flight_seq = [prb.flights[k] for k in sequences]
        # Return the result
        return flight_seq, times

    def sample_scenarios_as_problems(self,
                        prb : BelugaProblem,
                        size : int = None,
                        seed : int = None,
                        rebase : bool = True):
        assert(size is None or size > 0)
        # Sample sequences of flights
        flight_seq, times = self.sample_flight_sequences(prb, size, seed, rebase)
        # Use the sequeces to initialize multiple copies of the original problem
        prb_seq = [copy.deepcopy(prb) for s in flight_seq]
        for p, s in zip(prb_seq, flight_seq):
            p.flights = s
        # Return results
        return prb_seq, times


def _cartesian_product(arrays):
    la = len(arrays)
    dtype = np.result_type(*arrays)
    arr = np.empty([len(a) for a in arrays] + [la], dtype=dtype)
    for i, a in enumerate(np.ix_(*arrays)):
        arr[...,i] = a
    return arr.reshape(-1, la)

def _remove_replicated(cprod):
    mask = [np.unique(a, return_counts=True)[1].max() == 1 for a in cprod]
    return cprod[mask]


def _build_tt_support(nflights, history_len):
    # Build the cartesian product of all flights
    flight_choices = np.arange(nflights)
    transition_support = _cartesian_product([flight_choices] * (history_len+1))
    transition_support = _remove_replicated(transition_support)
    # Add starting transitions
    for k in range(history_len):
        tail = _cartesian_product([flight_choices] * (history_len-k))
        tail = _remove_replicated(tail)
        head = np.full(shape=(tail.shape[0], k+1), fill_value=-1)
        ext = np.hstack((head, tail))
        transition_support = np.vstack((ext, transition_support))
    # # Define the state support
    # state_support = np.unique(transition_support[:, :-1], axis=0)
    return set(tuple(t) for t in transition_support)


def _count_transitions(prb, history_len, nsamples, seed):
    # Sample multiple scenarios (i.e. flight arrival sequences)
    sampler = ArrivalSampler()
    sampler.setup()
    scheduled_arrivals = [f.scheduled_arrival for f in prb.flights]
    scenarios, _ = sampler.sample_id_sequences(scheduled_arrivals=scheduled_arrivals,
                                            size=nsamples, seed=seed, rebase=False)
    # Add starting elements
    base = np.full(shape=(scenarios.shape[0], history_len), fill_value=-1)
    scenarios = np.hstack((base, scenarios))
    # Build 3d tensor representation of the sequences
    # Subsequences include the state (history_len flights), plus the
    # next flight
    slen = scenarios.shape[1]
    subsequences = np.stack([
        scenarios[:, k:slen-(history_len-k)] for k in range(history_len+1)
        ], axis=-1)
    # Count the occurrences of each subsequence
    flat_subsequences = subsequences.reshape(subsequences.shape[0] * subsequences.shape[1], history_len+1)
    seqs, counts = np.unique(flat_subsequences, axis=0, return_counts=True)
    cmap = {tuple(k): v for k, v in zip(seqs, counts)}
    return cmap


def _add_missing_transition(tt_counts, tt_support):
    for tt in tt_support:
        if tt not in tt_counts:
            tt_counts[tt] = 1


def _normalize_counts(tt_counts, prec):
    # Compute the normalization constants
    z_map = {}
    cur_state = None
    cur_ccount = 0
    last_tt = None
    last_tt_map = {}
    for tt in sorted(tt_counts):
        stt = tuple(tt[:-1])
        cnt = tt_counts[tt]
        if cur_state is None:
            cur_state = stt
        if stt != cur_state:
            # Othewise, store the prob. mass
            z_map[cur_state] = cur_ccount
            # Mark the last transition for such state
            last_tt_map[cur_state] = last_tt
            # Then reset the accumulation fields
            cur_state = stt
            cur_ccount = 0
        # Update the count
        cur_ccount += cnt
        # Update the last transition
        last_tt = tt
    # Store the mass for the last state
    z_map[cur_state] = cur_ccount
    last_tt_map[cur_state] = tt

    # Normalize the counts
    cur_pmass = 0
    for tt in sorted(tt_counts):
        stt = tuple(tt[:-1])
        if tt != last_tt_map[stt]:
            # If this is not the last transition for this state,
            # apply a typical normalization
            val = np.round(tt_counts[tt] / z_map[stt], prec)
            tt_counts[tt] = val
            # Update the probability mass
            cur_pmass += val
        else:
            # Otherwise, normalize by complement
            tt_counts[tt] = np.round(1 - cur_pmass, prec)
            # Reset the probability mass
            cur_pmass = 0

    return tt_counts


def add_abstract_uncertainty_model(prb : BelugaProblem,
                                   history_len : int = 1,
                                   seed : int = None,
                                   nsamples : int = 10000):
    # Define the support for the transition table
    nflights = len(prb.flights)
    tt_support = _build_tt_support(nflights, history_len)
    # Compute transition counts via Monte-Carlo simulation
    tt_counts = _count_transitions(prb, history_len, nsamples, seed)
    # Add the missing probabilities
    _add_missing_transition(tt_counts, tt_support)
    # Normalize to obtain probabilities
    prec = int(np.ceil(np.log10(nsamples)))
    tt_probs = _normalize_counts(tt_counts, prec)
    # Write the transition table on the problem object
    tt_last = []
    tt_next = []
    tt_prob = []
    for tt in tt_probs:
        tt_last.append([prb.flights[int(v)].name if int(v) >= 0 else None for v in tt[:-1]])
        tt_next.append(prb.flights[int(tt[-1])].name)
        tt_prob.append(float(tt_probs[tt]))
    prb.tt_last = tt_last
    prb.tt_next = tt_next
    prb.tt_prob = tt_prob


