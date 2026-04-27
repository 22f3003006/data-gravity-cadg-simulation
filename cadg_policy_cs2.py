"""
CADG Policy Engine + Workload Trace Simulator (Case Study 2)
============================================================
Implements the Three-Weight Gravity Model and Carbon Proximity Constraint
from the paper, then simulates a 12-month synthetic workload trace and
evaluates two policies:
  - TCP baseline:   migrate if destination is cheaper or "greener-labelled"
  - CADG:           migrate iff Delta C_ops > C_move (Carbon Proximity Constraint)

Decision accuracy is reported as F1 score against an oracle that has full
lifecycle-carbon knowledge.

All assumptions are documented inline. Random seed fixed for reproducibility.
"""
import numpy as np

np.random.seed(7)

# ---------- Region topology ----------
# Ci values from electricityMaps 2024 annual averages
# Egress prices from provider list pages (2025)
REGIONS = {
    "us-east-1":   {"provider": "AWS",   "Ci": 0.380, "egress": 0.090, "compute_cost_hr": 0.096},
    "eu-north-1":  {"provider": "AWS",   "Ci": 0.050, "egress": 0.090, "compute_cost_hr": 0.114},
    "westeurope":  {"provider": "Azure", "Ci": 0.210, "egress": 0.087, "compute_cost_hr": 0.110},
    "asia-south1": {"provider": "GCP",   "Ci": 0.708, "egress": 0.080, "compute_cost_hr": 0.082},
}

PRIMARY = "us-east-1"          # primary data hub (where data originally lives)
Ec      = 0.022                # kWh/GB transit energy (Aslan 2017)
Ci_path = 0.275                # path-weighted transit Ci, kg/kWh

# ---------- Workload trace generator ----------
def generate_trace(n_events=480, seed=7):
    """480 candidate migrations over 12 months, Pareto-distributed sizes."""
    rng = np.random.default_rng(seed)
    # Pareto sizes, capped at 500 TB
    sizes_TB = np.minimum(rng.pareto(1.5, n_events) * 5 + 1, 500)
    durations_days = rng.uniform(3, 60, n_events)
    compute_kW    = rng.uniform(20, 250, n_events)
    candidate_targets = rng.choice(
        [r for r in REGIONS if r != PRIMARY], size=n_events
    )
    access_freq_per_hr = rng.uniform(5, 200, n_events)
    return list(zip(sizes_TB, durations_days, compute_kW,
                    candidate_targets, access_freq_per_hr))

# ---------- Carbon and cost computation ----------
def C_move(size_TB):
    """Migration carbon for moving size_TB across cloud boundary."""
    return size_TB * 1000 * Ec * Ci_path  # kg CO2e

def C_ops(compute_kW, duration_days, region):
    """Operational carbon for running the workload at `region`."""
    hours = duration_days * 24
    energy_kWh = compute_kW * hours
    return energy_kWh * REGIONS[region]["Ci"]  # kg CO2e

def egress_cost(size_TB, region):
    """One-time egress cost when moving out of a region."""
    return size_TB * 1000 * REGIONS[region]["egress"]

def compute_cost(compute_kW, duration_days, region):
    """Compute cost for running workload at region."""
    hours = duration_days * 24
    return compute_kW * hours * REGIONS[region]["compute_cost_hr"]

# ---------- The three policies ----------
def oracle_decision(event):
    """Ground truth: migrate iff total lifecycle carbon at target < at primary."""
    size, dur, kW, target, _ = event
    home_total   = C_ops(kW, dur, PRIMARY)
    target_total = C_ops(kW, dur, target) + C_move(size)
    return target_total < home_total

def tcp_decision(event):
    """Traditional Cost-Performance baseline: migrate if target offers
    lower compute cost OR is labelled 'green' (Ci < 100 gCO2e/kWh).
    Crucially, it ignores migration carbon C_move entirely - this is the
    bug that creates the Green Migration Paradox.
    """
    _, dur, kW, target, _ = event
    home_compute_cost   = compute_cost(kW, dur, PRIMARY)
    target_compute_cost = compute_cost(kW, dur, target)
    cheaper = target_compute_cost < home_compute_cost
    labelled_green = REGIONS[target]["Ci"] < 0.100  # the "100% renewable" label
    return cheaper or labelled_green

def cadg_decision(event, rng=None):
    """CADG: migrate iff estimated Delta_C_ops > C_move.
    In production, compute_kW and duration are forecasted, not known.
    We model 15% RMS prediction error on both, consistent with reported
    accuracy of cloud-workload predictors (Cortez et al., SOSP 2017).
    """
    if rng is None:
        rng = np.random.default_rng(99)
    size, dur, kW, target, _ = event
    kW_est  = max(1.0, kW  * rng.normal(1.0, 0.25))
    dur_est = max(0.1, dur * rng.normal(1.0, 0.25))
    delta_ops = C_ops(kW_est, dur_est, PRIMARY) - C_ops(kW_est, dur_est, target)
    move      = C_move(size)
    return delta_ops > move

# ---------- Simulation ----------
def run_simulation():
    trace = generate_trace()
    rng_cadg = np.random.default_rng(99)

    truth, tcp, cadg = [], [], []
    transit_TCP_TB = transit_CADG_TB = 0.0
    carbon_TCP = carbon_CADG = 0.0
    egress_TCP = egress_CADG = 0.0
    compute_TCP = compute_CADG = 0.0

    for event in trace:
        size, dur, kW, target, freq = event
        truth.append(oracle_decision(event))
        tcp.append(tcp_decision(event))
        cadg.append(cadg_decision(event, rng=rng_cadg))

        # Aggregate outcomes for each policy
        for policy_decision, transit_TB, carbon, egress, compute_c in [
            (tcp[-1],  "TCP",  None, None, None),
            (cadg[-1], "CADG", None, None, None),
        ]:
            pass  # unused, real aggregation below

        # TCP outcomes
        if tcp[-1]:
            transit_TCP_TB += size
            carbon_TCP     += C_ops(kW, dur, target) + C_move(size)
            egress_TCP     += egress_cost(size, PRIMARY)
            compute_TCP    += compute_cost(kW, dur, target)
        else:
            carbon_TCP     += C_ops(kW, dur, PRIMARY)
            compute_TCP    += compute_cost(kW, dur, PRIMARY)

        # CADG outcomes
        if cadg[-1]:
            transit_CADG_TB += size
            carbon_CADG     += C_ops(kW, dur, target) + C_move(size)
            egress_CADG     += egress_cost(size, PRIMARY)
            compute_CADG    += compute_cost(kW, dur, target)
        else:
            carbon_CADG     += C_ops(kW, dur, PRIMARY)
            compute_CADG    += compute_cost(kW, dur, PRIMARY)

    truth = np.array(truth); tcp = np.array(tcp); cadg = np.array(cadg)

    def f1(pred, true):
        tp = np.sum(pred & true)
        fp = np.sum(pred & ~true)
        fn = np.sum(~pred & true)
        prec = tp / (tp + fp) if (tp + fp) else 0
        rec  = tp / (tp + fn) if (tp + fn) else 0
        return 2 * prec * rec / (prec + rec) if (prec + rec) else 0

    print("=" * 60)
    print("CADG POLICY SIMULATION - 480 events, 12 months")
    print("=" * 60)
    print(f"Total events:                 {len(trace)}")
    print(f"Oracle says migrate:          {np.sum(truth)}  ({np.sum(truth)/len(trace)*100:.1f}%)")
    print(f"TCP baseline migrates:        {np.sum(tcp)}  ({np.sum(tcp)/len(trace)*100:.1f}%)")
    print(f"CADG migrates:                {np.sum(cadg)}  ({np.sum(cadg)/len(trace)*100:.1f}%)")
    print()
    print("DECISION ACCURACY (vs oracle)")
    print(f"  TCP F1:                     {f1(tcp, truth):.3f}")
    print(f"  CADG F1:                    {f1(cadg, truth):.3f}")
    print()
    print("ANNUAL OUTCOMES")
    print(f"  Transit volume - TCP:       {transit_TCP_TB/1000:>7,.2f} PB")
    print(f"  Transit volume - CADG:      {transit_CADG_TB/1000:>7,.2f} PB")
    if transit_TCP_TB > 0:
        print(f"  Transit reduction:          {(transit_TCP_TB - transit_CADG_TB)/transit_TCP_TB*100:.1f}%")
    print()
    print(f"  Total carbon  - TCP:        {carbon_TCP/1000:>7,.1f} t CO2e")
    print(f"  Total carbon  - CADG:       {carbon_CADG/1000:>7,.1f} t CO2e")
    if carbon_TCP > 0:
        print(f"  Carbon reduction:           {(carbon_TCP - carbon_CADG)/carbon_TCP*100:.1f}%")
    print()
    print(f"  Egress cost   - TCP:        ${egress_TCP/1000:>7,.0f}k")
    print(f"  Egress cost   - CADG:       ${egress_CADG/1000:>7,.0f}k")
    print(f"  Compute cost  - TCP:        ${compute_TCP/1000:>7,.0f}k")
    print(f"  Compute cost  - CADG:       ${compute_CADG/1000:>7,.0f}k")
    total_TCP  = egress_TCP + compute_TCP
    total_CADG = egress_CADG + compute_CADG
    print(f"  Total cost    - TCP:        ${total_TCP/1000:>7,.0f}k")
    print(f"  Total cost    - CADG:       ${total_CADG/1000:>7,.0f}k")
    if total_TCP > 0:
        print(f"  Cost change:                {(total_CADG - total_TCP)/total_TCP*100:+.1f}%")
    print()
    # Paradox migrations: TCP migrates but oracle says no
    paradox = tcp & ~truth
    cadg_blocks_paradox = paradox & ~cadg
    print(f"  Green Migration Paradox events (TCP migrates, oracle blocks): {np.sum(paradox)}")
    print(f"  CADG correctly blocks of those:                               {np.sum(cadg_blocks_paradox)}")

if __name__ == "__main__":
    run_simulation()
