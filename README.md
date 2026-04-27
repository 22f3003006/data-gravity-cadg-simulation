# Carbon-Aware Data Gravity (CADG) — Simulation Code

Reproducibility code for *"Data Gravity in Multi-Cloud Architecture: A Green Computing Perspective"* (Malhotra, Anand, Joshi 2026).

## Files

| File | Purpose |
|------|---------|
| `montecarlo_cs1.py` | Monte-Carlo sensitivity analysis for Case Study 1 (1000 trials, joint perturbation of Ec, Ci, Tr, compute and storage coefficients) |
| `cadg_policy_cs2.py` | CADG decision-engine and 12-month workload-trace simulation for Case Study 2 (480 candidate migration events on a four-region multi-cloud topology) |

## Requirements

- Python ≥ 3.8
- numpy

```bash
pip install numpy
```

## Reproducing the results

```bash
python3 montecarlo_cs1.py
python3 cadg_policy_cs2.py
```

Random seeds are fixed (`np.random.seed(42)` for CS1, `np.random.seed(7)` for CS2) so results are bit-exact reproducible.

## Data sources for coefficients

- Network energy intensity Ec ∈ [0.006, 0.060] kWh/GB — Aslan, Mayers, Koomey & France, *Electricity Intensity of Internet Data Transmission*, J. Industrial Ecology, 2017.
- Per-region grid carbon intensity Ci — electricityMaps 2024 annual averages.
- Compute energy 140–260 kWh/TB/yr — AWS Sustainability Report 2024 (mid-range).
- Storage energy 20–40 kWh/TB/yr — Backblaze 2023 + Seagate sustainability disclosures.
- Path-weighted transit Ci — Coroamă & Mattern, *Energy intensity of internet data transmission*, 2020.
- Workload predictor accuracy (15–25% RMS) — Cortez et al., *Resource Central*, SOSP 2017.

## Citation

If you use this code, please cite the paper.
