"""Shared figure style for the report. Import and call `use()` before plotting.

Colours follow a validated colour-blind-safe categorical order; assign series in
SERIES order and keep the carrier colours fixed across every figure.
"""
from pathlib import Path

import matplotlib as mpl

SERIES = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#4a3aa7', '#e34948']
CARRIER = {'electricity': '#2a78d6', 'steam': '#eb6834', 'water': '#1baf7a',
           'diesel': '#eda100', 'waste heat': '#8a8984', 'exergy destroyed': '#e34948'}
INK, INK_2, INK_3, GRID = '#0b0b0b', '#52514e', '#8a8984', '#e4e3df'
SEQ = ['#cde2fb', '#9ec5f4', '#6da7ec', '#3987e5', '#256abf', '#184f95', '#0d366b']

FIG_DIR = Path(__file__).resolve().parents[2] / 'reports' / 'figures'


def use():
    mpl.rcParams.update({
        'figure.dpi': 110, 'savefig.dpi': 200, 'savefig.bbox': 'tight',
        'figure.facecolor': 'white', 'axes.facecolor': 'white',
        'font.size': 9, 'axes.titlesize': 10, 'axes.titleweight': 'bold', 'axes.titlelocation': 'left',
        'axes.labelsize': 9, 'axes.labelcolor': INK_2, 'text.color': INK,
        'xtick.color': INK_2, 'ytick.color': INK_2, 'xtick.labelsize': 8, 'ytick.labelsize': 8,
        'axes.edgecolor': INK_3, 'axes.linewidth': 0.6,
        'axes.spines.top': False, 'axes.spines.right': False,
        'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.6, 'axes.axisbelow': True,
        'axes.prop_cycle': mpl.cycler(color=SERIES),
        'lines.linewidth': 2, 'lines.markersize': 6,
        'legend.frameon': False, 'legend.fontsize': 8,
    })


def save(fig, name):
    """Save to reports/figures/<name>.png and return the path."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / f'{name}.png'
    fig.savefig(path)
    return path
