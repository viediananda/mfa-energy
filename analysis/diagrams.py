"""Report diagrams: system boundary and method workflow (reports/figures/diagram_*.png)."""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from hallsta_mfa import plotstyle
from hallsta_mfa.model import BASE, run

C = plotstyle.CARRIER
INK, INK2, INK3 = plotstyle.INK, plotstyle.INK_2, plotstyle.INK_3
b = run(BASE)


def box(ax, x, y, w, h, text, fc='white', ec=INK3, fs=8.5, weight='normal', ls='-', tc=INK):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.02,rounding_size=0.08', fc=fc, ec=ec, lw=1.1, ls=ls))
    ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=fs, color=tc, weight=weight, linespacing=1.3)


def arrow(ax, p0, p1, color, lw=2.0, ls='-', rad=0.0, label=None, lpos=0.5, loff=(0, 0.12), fs=7.5):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle='-|>', mutation_scale=11, color=color, lw=lw, ls=ls,
                                 connectionstyle=f'arc3,rad={rad}', shrinkA=2, shrinkB=2))
    if label:
        x = p0[0] + (p1[0] - p0[0])*lpos + loff[0]; y = p0[1] + (p1[1] - p0[1])*lpos + loff[1]
        ax.text(x, y, label, ha='center', va='bottom', fontsize=fs, color=INK2)


def system_boundary():
    plotstyle.use()
    fig, ax = plt.subplots(figsize=(12.5, 6.6)); ax.set_xlim(0, 17.6); ax.set_ylim(0.2, 9); ax.axis('off')
    ax.add_patch(FancyBboxPatch((3.3, 0.75), 9.6, 7.55, boxstyle='round,pad=0.05,rounding_size=0.25', fc='#f6f7f5', ec=INK2, lw=1.4, ls=(0, (6, 3))))
    ax.text(3.55, 8.05, 'System boundary: Hallsta mill gate, 2023', fontsize=9.5, weight='bold', color=INK, va='top')
    # inputs
    box(ax, 0.1, 5.25, 2.8, 1.1, f'Purchased electricity\n{b["E_tot"]:,.0f} GWh/y', fc='#e5effb', ec=C['electricity'], weight='bold', fs=8.3)
    box(ax, 0.1, 0.85, 2.8, 0.9, f'Diesel\n{BASE["diesel"]:.1f} GWh/y', fc='#fdf3dc', ec=C['diesel'], fs=8.3)
    box(ax, 0.1, 2.9, 2.8, 1.15, 'Wood chips and logs\n(material input,\nenergy not counted)', ec=INK3, ls='--', tc=INK2, fs=7.8)
    # processes
    box(ax, 3.8, 5.6, 2.9, 1.35, f'TMP refining\nTMP3, TMP12\n{b["el_TMP"]:,.0f} GWh/y (70 %)', ec=INK2, weight='bold', fs=8.3)
    box(ax, 3.8, 3.2, 2.9, 1.15, f'Electric boilers\nEP1, EP2\n{b["el_EB"]:,.0f} GWh/y (10 %)', ec=INK2, fs=8.3)
    box(ax, 3.8, 1.35, 2.9, 1.3, 'Other users (5 %)\nbleaching, WWTP,\nwood handling, utilities', ec=INK2, fs=8)
    box(ax, 7.55, 4.2, 2.1, 1.2, f'Steam network\n{b["st_supply"]:,.0f} GWh/y', fc='#fdebe3', ec=C['steam'], weight='bold', fs=8.3)
    box(ax, 10.15, 5.6, 2.5, 1.35, f'Paper machines\nPM11, PM12\ndrying {b["st_PM"]:,.0f} GWh/y', ec=INK2, weight='bold', fs=8.3)
    box(ax, 10.15, 3.2, 2.5, 1.15, 'Hot water, heating,\nsummer venting', ec=INK2, fs=8.3)
    # internal flows
    arrow(ax, (2.9, 6.0), (3.8, 6.2), C['electricity'], lw=3)
    arrow(ax, (2.9, 5.6), (3.8, 3.8), C['electricity'], lw=1.8)
    arrow(ax, (2.9, 5.4), (3.8, 2.1), C['electricity'], lw=1.2)
    arrow(ax, (2.9, 6.25), (10.15, 6.75), C['electricity'], lw=1.6, rad=-0.2)
    ax.text(7.1, 7.55, f'electricity to paper machines {b["el_PM"]+b["el_bleach"]:,.0f} GWh/y (15 %)', fontsize=7.5, color=INK2, ha='center')
    arrow(ax, (6.7, 5.95), (7.65, 5.4), C['steam'], lw=2.6)
    ax.text(7.25, 6.05, f'recovered\nsteam {b["st_rec"]:,.0f}', fontsize=7.4, color=INK2, ha='left', va='bottom')
    arrow(ax, (6.7, 3.75), (7.65, 4.35), C['steam'], lw=1.6)
    ax.text(7.2, 3.55, f'steam {b["st_EB"]:,.0f}', fontsize=7.4, color=INK2, ha='left', va='top')
    arrow(ax, (9.65, 5.1), (10.15, 5.95), C['steam'], lw=2.4)
    arrow(ax, (9.65, 4.5), (10.15, 3.85), C['steam'], lw=1.4)
    box(ax, 10.15, 0.9, 2.5, 0.9, 'Wood-yard vehicles\n(heat to air)', ec=C['diesel'], fs=8)
    arrow(ax, (2.9, 1.05), (10.15, 1.05), C['diesel'], lw=1.2)
    # outputs
    outs = [(7.25, 'Paper 444,494 t/y (product)', INK, '-', 2.0),
            (6.05, 'Exhaust air and ventilation\n(heat, found by difference)', C['waste heat'], '-', 2.6),
            (4.85, f'Wastewater to Edeboviken\n{b["sink_water"]:,.0f} GWh/y', C['water'], '-', 1.8),
            (3.7, f'Cooling water, about 4 Mm³/y\n(estimated {b["sink_cool"]:,.0f} GWh/y)', C['water'], '-', 1.4),
            (2.55, f'District heat, Norrtälje Energi\n{b["sink_DH"]:.1f} GWh/y', '#008300', '-', 1.2),
            (1.3, 'Bark sold as fuel\n(about 204 GWh/y, not counted)', INK3, '--', 1.0)]
    for y, t, col, ls, lw in outs:
        arrow(ax, (12.9, y + 0.3), (13.7, y + 0.3), col, lw=lw, ls=ls)
        box(ax, 13.75, y - 0.12, 3.75, 0.85, t, ec=col if ls == '-' else INK3, ls=ls, fs=7.7, tc=INK if ls == '-' else INK2)
    ax.text(8.8, 0.35, 'Solid arrows cross the boundary and are counted. Dashed items are outside the energy analysis.', fontsize=7.6, color=INK2, ha='center')
    return plotstyle.save(fig, 'diagram_system_boundary')


def method():
    plotstyle.use()
    fig, ax = plt.subplots(figsize=(12, 2.6)); ax.set_xlim(0, 24.2); ax.set_ylim(0.2, 4.9); ax.axis('off')
    steps = [('Sources', 'Miljörapport 2023,\nHolmen answers\n2019 and 2025'),
             ('Data screening', 'trends 2019-2023,\nconflicting values,\nchosen inputs'),
             ('Energy balance', 'electricity, steam,\nexits (GWh/y)'),
             ('Exergy analysis', 'where work potential\nis destroyed'),
             ('Monte Carlo', '10,000 runs,\nP5-P95 ranges,\nsensitivity'),
             ('Measures', 'savings against\nboiler electricity'),
             ('Screening LCA', 'qualitative\ntrade-offs')]
    w, gap = 3.05, 0.42
    for i, (h, t) in enumerate(steps):
        x = 0.2 + i*(w + gap)
        ax.add_patch(FancyBboxPatch((x, 1.2), w, 3.4, boxstyle='round,pad=0.02,rounding_size=0.12',
                                    fc='#e2eee9' if i in (2, 3, 4) else 'white', ec=INK3, lw=1.1))
        ax.text(x + w/2, 4.15, f'{i+1}', ha='center', va='center', fontsize=8, color=INK3, family='monospace')
        ax.text(x + w/2, 3.55, h, ha='center', va='center', fontsize=8.6, weight='bold', color=INK)
        ax.text(x + w/2, 2.3, t, ha='center', va='center', fontsize=7.4, color=INK2, linespacing=1.3)
        if i < len(steps) - 1:
            ax.add_patch(FancyArrowPatch((x + w + 0.03, 2.9), (x + w + gap - 0.03, 2.9), arrowstyle='-|>', mutation_scale=10, color=INK2, lw=1.2))
    ax.text(12.1, 0.55, 'Shaded steps are calculated by the model. Each step uses the results of the one before.', ha='center', fontsize=7.6, color=INK2)
    return plotstyle.save(fig, 'diagram_method')


if __name__ == '__main__':
    print(system_boundary()); print(method())
