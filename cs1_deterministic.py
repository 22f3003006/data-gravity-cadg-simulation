"""
Case Study 1 - Deterministic per-year computation
==================================================
Produces all numbers in Tables 1 and 2 using fixed coefficients
sampled at the published-mean of each parameter range.

All sources cited inline.
"""

# ---------- Coefficients (single value, central estimate, sources cited) ----------
Ec          = 0.022   # kWh/GB - Aslan et al. 2017 (mid of 0.004-0.060)
compute_e   = 200     # kWh per TB processed per year - AWS Sustainability 2024
storage_e   = 30      # kWh per TB stored per year - Backblaze 2023

# Per-region Ci (kg CO2e/kWh) - electricityMaps 2024 annual averages
Ci_eu_north = 0.050   # gravity-aware company anchors here
Ci_us_east  = 0.380
Ci_ap_south = 0.708

# Path-weighted transit Ci - Coroamă & Mattern 2020
Ci_path     = 0.275

# Original-paper transit-only Ci (kept for backward comparability)
Ci_legacy   = 0.475

# Placement policy
Ci_A_avg    = Ci_eu_north                      # gravity-aware: anchored in greenest
Ci_B_avg    = (Ci_us_east + Ci_ap_south) / 2   # gravity-blind: scattered ~ 0.544
                                                # Use a more moderate weighted avg
Ci_B_avg    = 0.380   # weighted avg of scattered placement, dominated by us-east-1

Tr_A        = 0.08
Tr_B        = 0.55

# ---------- Per-year computation ----------
def carbon(data_TB, Tr, Ci_compute):
    data_GB    = data_TB * 1000
    e_compute  = data_TB * compute_e        # kWh/yr
    e_storage  = data_TB * storage_e        # kWh/yr
    e_transit  = data_GB * Tr * Ec          # kWh/yr

    c_compute  = e_compute * Ci_compute
    c_storage  = e_storage * Ci_compute
    c_transit_legacy = e_transit * Ci_legacy   # for "transit only" column
    c_transit_path   = e_transit * Ci_path     # for "total" column

    total = c_compute + c_storage + c_transit_path
    return {
        "data_GB": data_GB,
        "transit_TB": data_TB * Tr,
        "transit_kWh": e_transit,
        "transit_CO2_legacy": c_transit_legacy,
        "transit_CO2_path":   c_transit_path,
        "compute_CO2": c_compute,
        "storage_CO2": c_storage,
        "total_CO2":   total,
        "CEI":         total / data_TB,
    }

print("=" * 75)
print("CASE STUDY 1 - DETERMINISTIC PER-YEAR RESULTS")
print("=" * 75)
print()
print(f"  Coefficients used:")
print(f"    Ec  = {Ec} kWh/GB  (Aslan et al. 2017)")
print(f"    Compute = {compute_e} kWh/TB/yr  (AWS Sustainability 2024)")
print(f"    Storage = {storage_e} kWh/TB/yr  (Backblaze 2023)")
print(f"    Ci(Co. A) = {Ci_A_avg}  (anchored in eu-north-1, electricityMaps 2024)")
print(f"    Ci(Co. B) = {Ci_B_avg}  (weighted avg, scattered placement)")
print(f"    Ci(transit, path-weighted) = {Ci_path}  (Coroamă & Mattern 2020)")
print(f"    Ci(transit, legacy) = {Ci_legacy}  (kept for back-compat with transit-only col)")
print()
print("-" * 75)
print(f"{'Year':<8}{'TB':<6}{'Co.':<6}{'Tx_TB':<8}{'Tx_kWh':<10}{'Tx_CO2_lg':<11}{'Compute':<11}{'Storage':<11}{'Total':<11}{'CEI':<8}")
print("-" * 75)
for year, TB in [(1, 50), (2, 150), (3, 400)]:
    A = carbon(TB, Tr_A, Ci_A_avg)
    B = carbon(TB, Tr_B, Ci_B_avg)
    print(f"Y{year:<7}{TB:<6}{'A':<6}{A['transit_TB']:<8.1f}{A['transit_kWh']:<10.1f}{A['transit_CO2_legacy']:<11.1f}{A['compute_CO2']:<11.0f}{A['storage_CO2']:<11.0f}{A['total_CO2']:<11.0f}{A['CEI']:<8.2f}")
    print(f"{'':<8}{'':<6}{'B':<6}{B['transit_TB']:<8.1f}{B['transit_kWh']:<10.1f}{B['transit_CO2_legacy']:<11.1f}{B['compute_CO2']:<11.0f}{B['storage_CO2']:<11.0f}{B['total_CO2']:<11.0f}{B['CEI']:<8.2f}")
    print(f"{'':<8}{'':<6}{'Δ':<6}{'':<8}{'':<10}{B['transit_CO2_legacy']-A['transit_CO2_legacy']:<11.1f}{B['compute_CO2']-A['compute_CO2']:<11.0f}{B['storage_CO2']-A['storage_CO2']:<11.0f}{B['total_CO2']-A['total_CO2']:<11.0f}")
    print()

# Year-3 transit reduction
A3 = carbon(400, Tr_A, Ci_A_avg)
B3 = carbon(400, Tr_B, Ci_B_avg)
print()
print("Year-3 summary:")
print(f"  Total CO2 gap (Co. B - Co. A): {B3['total_CO2'] - A3['total_CO2']:,.0f} kg = {(B3['total_CO2'] - A3['total_CO2'])/1000:.2f} t")
print(f"  Co. A CEI: {A3['CEI']:.2f} kg/TB")
print(f"  Co. B CEI: {B3['CEI']:.2f} kg/TB")
print(f"  CEI advantage of Co. A: {(B3['CEI'] - A3['CEI'])/B3['CEI']*100:.1f}%")
print(f"  Transit-only carbon scaling Y1->Y3 (Co. B): {B3['transit_CO2_legacy']/carbon(50, Tr_B, Ci_B_avg)['transit_CO2_legacy']:.1f}x ({(B3['transit_CO2_legacy']/carbon(50, Tr_B, Ci_B_avg)['transit_CO2_legacy'] - 1)*100:.0f}% increase)")
