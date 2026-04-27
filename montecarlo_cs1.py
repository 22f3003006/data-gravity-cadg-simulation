"""
Monte-Carlo Sensitivity Analysis for Case Study 1
=================================================
Tests the robustness of the gravity-aware carbon advantage under joint
perturbation of the principal coefficients across published ranges.

Parameters and ranges:
  Ec  : Network energy intensity, kWh/GB
        Range: 0.006 - 0.060  (Aslan et al., J. Industrial Ecology, 2017)
  Ci  : Regional grid carbon intensity, kg CO2e/kWh
        Co. A range: 0.05 - 0.40 (anchored, biased green but not always)
        Co. B range: 0.15 - 0.50 (scattered, biased higher-Ci)
        Source: electricityMaps 2024 annual averages
  Tr  : Cross-cloud transit ratio
        Co. A: 0.05 - 0.12  (gravity-aware policy)
        Co. B: 0.45 - 0.65  (gravity-blind policy)
  Compute: 140 - 260 kWh per TB processed per year
        Source: AWS Sustainability Report 2024 (mid-range)
  Storage: 20 - 40 kWh per TB stored per year
        Source: Backblaze 2023 + Seagate sustainability disclosures

Output:
  Percentage of trials in which Co. A's total lifecycle carbon is lower,
  mean delta, and 95% confidence interval.

Reproducibility:
  numpy random seed fixed at 42.
"""
import numpy as np

np.random.seed(42)
N_TRIALS = 1000
DATA_TB = 400              # Year-3 data volume
DATA_GB = DATA_TB * 1000

a_wins = 0
deltas = []
totals_A = []
totals_B = []

for _ in range(N_TRIALS):
    # Coefficients sampled per trial
    Ec        = np.random.uniform(0.006, 0.060)
    Ci_A      = np.random.uniform(0.05,  0.40)
    Ci_B      = np.random.uniform(0.15,  0.50)
    Tr_A      = np.random.uniform(0.05,  0.12)
    Tr_B      = np.random.uniform(0.45,  0.65)
    compute_e = np.random.uniform(140,   260)   # kWh/TB/yr
    storage_e = np.random.uniform(20,    40)    # kWh/TB/yr
    Ci_path   = np.random.uniform(0.20,  0.40)  # path-weighted transit Ci

    # Co. A total (compute + storage + transit)
    A = (DATA_TB * compute_e * Ci_A
         + DATA_TB * storage_e * Ci_A
         + DATA_GB * Tr_A * Ec * Ci_path)

    # Co. B total
    B = (DATA_TB * compute_e * Ci_B
         + DATA_TB * storage_e * Ci_B
         + DATA_GB * Tr_B * Ec * Ci_path)

    if A < B:
        a_wins += 1
    deltas.append(B - A)
    totals_A.append(A)
    totals_B.append(B)

deltas = np.array(deltas)
print("=" * 60)
print("MONTE-CARLO SENSITIVITY: CASE STUDY 1 (n=1000, Year 3)")
print("=" * 60)
print(f"Trials where Co. A is lower-carbon: {a_wins}/{N_TRIALS} = {a_wins/N_TRIALS*100:.1f}%")
print(f"Mean delta (Co. B - Co. A):   {np.mean(deltas):>10,.0f} kg CO2e")
print(f"Median delta:                 {np.median(deltas):>10,.0f} kg CO2e")
print(f"95% CI:                       [{np.percentile(deltas, 2.5):,.0f}, {np.percentile(deltas, 97.5):,.0f}] kg")
print(f"Mean Co. A total:             {np.mean(totals_A):>10,.0f} kg")
print(f"Mean Co. B total:             {np.mean(totals_B):>10,.0f} kg")

# One-at-a-time sensitivity sweeps
print()
print("ONE-AT-A-TIME SWEEPS (other params fixed at midpoints)")
print("-" * 60)

def fixed_run(Ec=0.022, Ci_A=0.225, Ci_B=0.325, Tr_A=0.08, Tr_B=0.55,
              compute_e=200, storage_e=30, Ci_path=0.30):
    A = (DATA_TB * compute_e * Ci_A + DATA_TB * storage_e * Ci_A
         + DATA_GB * Tr_A * Ec * Ci_path)
    B = (DATA_TB * compute_e * Ci_B + DATA_TB * storage_e * Ci_B
         + DATA_GB * Tr_B * Ec * Ci_path)
    return B - A

for Ec_test in [0.006, 0.022, 0.060]:
    print(f"  Ec = {Ec_test:.3f} kWh/GB  ->  delta = {fixed_run(Ec=Ec_test):>9,.0f} kg")
print()
for Tr_B_test in [0.20, 0.35, 0.55, 0.70]:
    print(f"  Tr_B = {Tr_B_test:.2f}        ->  delta = {fixed_run(Tr_B=Tr_B_test):>9,.0f} kg")
