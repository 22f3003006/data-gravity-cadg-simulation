"""
Figures:
  Fig 1 (CS1): Annual Total CO2 Emissions, Year 1-3
  Fig 2 (CS1): Year-3 Carbon Source Decomposition (compute + storage + transit)
  Fig 3 (CS2): Migration Target Distribution by Policy
  Fig 4 (CS2): Annual Lifecycle Carbon Comparison

Requirements:
  pip install matplotlib numpy
"""
import os
import matplotlib.pyplot as plt
import numpy as np

# Output directory
os.makedirs("figures", exist_ok=True)

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "legend.fontsize": 9,
    "legend.frameon": False,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.dpi": 100,
})

# Colour palette
COLOR_A       = "#2E7D32"   
COLOR_B       = "#C62828"   
COLOR_COMPUTE = "#1F4E79"   
COLOR_STORAGE = "#E68A00"   
COLOR_TRANSIT = "#A6192E"   


# Case Study 1: Annual Total CO2 Emissions
def fig1_annual_carbon():
    """Grouped bar chart, three years × two architectures."""
    years   = ["Year 1\n(50 TB)", "Year 2\n(150 TB)", "Year 3\n(400 TB)"]
    a_total = [617,   1850,  4934]    # Co. A (gravity-aware), kg
    b_total = [4657, 13972, 37259]    # Co. B (gravity-blind), kg

    x = np.arange(len(years))
    w = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    bars_a = ax.bar(x - w/2, a_total, w,
                    label="Co. A (Gravity-Aware)", color=COLOR_A,
                    edgecolor="black", linewidth=0.5)
    bars_b = ax.bar(x + w/2, b_total, w,
                    label="Co. B (Gravity-Blind)", color=COLOR_B,
                    edgecolor="black", linewidth=0.5)

    # Numeric labels on top of each bar
    for bar in list(bars_a) + list(bars_b):
        h = bar.get_height()
        ax.annotate(f"{h:,}",
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9)

    ax.set_xlabel("Year (Total Data Volume)")
    ax.set_ylabel("Total CO\u2082e Emissions (kg)")
    ax.set_title("Figure 1: Annual Total Lifecycle CO\u2082 Emissions by Architecture")
    ax.set_xticks(x)
    ax.set_xticklabels(years)
    ax.legend(loc="upper left")
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.set_ylim(0, max(b_total) * 1.15)

    plt.tight_layout()
    plt.savefig("figures/fig1_annual_carbon.png", dpi=300, bbox_inches="tight")
    plt.savefig("figures/fig1_annual_carbon.pdf", bbox_inches="tight")
    plt.close()


#  Case Study 1: Year-3 Carbon Source Decomposition
def fig2_carbon_decomposition():
    """Stacked bars: Compute + Storage + Transit, Year 3 (400 TB)."""
    companies = ["Co. A\n(Gravity-Aware)", "Co. B\n(Gravity-Blind)"]
    compute   = [4000, 30400]   # kg CO2e (Year 3)
    storage   = [ 600,  4560]
    transit   = [ 334,  2299]

    x = np.arange(len(companies))
    w = 0.55

    fig, ax = plt.subplots(figsize=(7, 5.5))
    p1 = ax.bar(x, compute, w,
                label="Compute", color=COLOR_COMPUTE,
                edgecolor="black", linewidth=0.5)
    p2 = ax.bar(x, storage, w, bottom=compute,
                label="Storage", color=COLOR_STORAGE,
                edgecolor="black", linewidth=0.5)
    p3 = ax.bar(x, transit, w,
                bottom=[c + s for c, s in zip(compute, storage)],
                label="Transit", color=COLOR_TRANSIT,
                edgecolor="black", linewidth=0.5)

    # Inline labels for compute (always large enough)
    for i in range(len(companies)):
        ax.text(x[i], compute[i] / 2, f"{compute[i]:,}",
                ha="center", va="center", color="white",
                fontsize=10, fontweight="bold")
        # Storage and transit only labelled when bar is tall enough
        if storage[i] > 1500:
            ax.text(x[i], compute[i] + storage[i] / 2,
                    f"{storage[i]:,}", ha="center", va="center",
                    color="white", fontsize=9, fontweight="bold")
        if transit[i] > 1500:
            ax.text(x[i], compute[i] + storage[i] + transit[i] / 2,
                    f"{transit[i]:,}", ha="center", va="center",
                    color="white", fontsize=9, fontweight="bold")

    # Totals on top
    totals = [c + s + t for c, s, t in zip(compute, storage, transit)]
    for i, total in enumerate(totals):
        ax.annotate(f"Total: {total:,} kg",
                    xy=(x[i], total),
                    xytext=(0, 6), textcoords="offset points",
                    ha="center", va="bottom",
                    fontsize=10, fontweight="bold")

    ax.set_xlabel("Architecture")
    ax.set_ylabel("CO\u2082e Emissions (kg)")
    ax.set_title("Figure 2: Year-3 Carbon Source Decomposition (400 TB)")
    ax.set_xticks(x)
    ax.set_xticklabels(companies)
    ax.legend(loc="upper left")
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.set_ylim(0, max(totals) * 1.18)

    plt.tight_layout()
    plt.savefig("figures/fig2_carbon_decomposition.png", dpi=300, bbox_inches="tight")
    plt.savefig("figures/fig2_carbon_decomposition.pdf", bbox_inches="tight")
    plt.close()


#Case Study 2: Migration Target Distribution
def fig4_migration_targets():
    """Horizontal grouped bars: where each policy sends migrations."""
    regions = [
        "eu-north-1\nCi = 50  (clean)",
        "westeurope\nCi = 210 (moderate)",
        "asia-south1\nCi = 708 (dirty)",
    ]
    tcp  = [156,   0, 155]
    cadg = [156, 169,   0]

    y = np.arange(len(regions))
    h = 0.36

    fig, ax = plt.subplots(figsize=(9, 5.5))
    bars_tcp  = ax.barh(y - h/2, tcp,  h,
                        label="TCP Baseline (Cost-Driven)", color=COLOR_B,
                        edgecolor="black", linewidth=0.5)
    bars_cadg = ax.barh(y + h/2, cadg, h,
                        label="CADG (Carbon-Aware)", color=COLOR_A,
                        edgecolor="black", linewidth=0.5)

    for bar in list(bars_tcp) + list(bars_cadg):
        v = bar.get_width()
        ax.annotate(f"{int(v)}",
                    xy=(v, bar.get_y() + bar.get_height() / 2),
                    xytext=(4, 0), textcoords="offset points",
                    ha="left", va="center", fontsize=10, fontweight="bold")

    ax.set_xlabel("Number of Migration Events")
    ax.set_ylabel("Target Region (Carbon Intensity, gCO\u2082e/kWh)")
    ax.set_title("Figure 4: Migration Target Distribution \u2014 TCP vs CADG (n = 480 events)")
    ax.set_yticks(y)
    ax.set_yticklabels(regions)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2)
    ax.grid(axis="x", alpha=0.3, linestyle="--")
    ax.set_xlim(0, 230)

    plt.tight_layout()
    plt.savefig("figures/fig4_migration_targets.png", dpi=300, bbox_inches="tight")
    plt.savefig("figures/fig4_migration_targets.pdf", bbox_inches="tight")
    plt.close()

# Case Study 2: Annual Lifecycle Carbon Comparison
def fig3_lifecycle_carbon():
    """Two-bar comparison with reduction annotation."""
    policies = ["TCP Baseline\n(Cost-Driven)", "CADG\n(Carbon-Aware)"]
    totals   = [18316, 10284]    # metric tons CO2e per year
    colors   = [COLOR_B, COLOR_A]

    fig, ax = plt.subplots(figsize=(7, 5.5))
    bars = ax.bar(policies, totals, color=colors, width=0.5,
                  edgecolor="black", linewidth=0.5)

    # Value label on top of each bar
    for bar, total in zip(bars, totals):
        ax.annotate(f"{total:,} t",
                    xy=(bar.get_x() + bar.get_width() / 2, total),
                    xytext=(0, 5), textcoords="offset points",
                    ha="center", va="bottom",
                    fontsize=12, fontweight="bold")

    # Reduction arrow + annotation between bars
    arrow_y = (totals[0] + totals[1]) / 2
    ax.annotate("",
                xy=(1, totals[1] + 800),
                xytext=(0, totals[0] - 800),
                arrowprops=dict(arrowstyle="->", color="black", lw=2))
    ax.annotate("\u221243.9%\n(8,032 t saved)",
                xy=(0.5, arrow_y + 1000),
                ha="center", va="center",
                fontsize=12, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.4",
                          facecolor="#FFF3CD",
                          edgecolor="black", linewidth=0.5))

    ax.set_ylabel("Annual Lifecycle CO\u2082e Emissions (metric tons)")
    ax.set_title("Figure 3: Annual Lifecycle Carbon \u2014 TCP Baseline vs CADG")
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.set_ylim(0, max(totals) * 1.18)

    plt.tight_layout()
    plt.savefig("figures/fig3_lifecycle_carbon.png", dpi=300, bbox_inches="tight")
    plt.savefig("figures/fig3_lifecycle_carbon.pdf", bbox_inches="tight")
    plt.close()


# main
if __name__ == "__main__":
    print("Generating figures for the paper...")
    fig1_annual_carbon();        print("  [OK] figures/fig1_annual_carbon.{png,pdf}")
    fig2_carbon_decomposition(); print("  [OK] figures/fig2_carbon_decomposition.{png,pdf}")
    fig3_lifecycle_carbon();     print("  [OK] figures/fig3_lifecycle_carbon.{png,pdf}")
    fig4_migration_targets();    print("  [OK] figures/fig4_migration_targets.{png,pdf}")
    print()
    print("Done. 4 figures x 2 formats = 8 files in figures/")
    print("Use the .pdf versions for IEEE/Springer submission (vector format).")
    print("Use the .png versions for previews and Word/Google Docs drafts.")
