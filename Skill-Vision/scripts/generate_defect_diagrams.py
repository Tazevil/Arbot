#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Animated Diagrams for Common Bathroom Defects
Creates visual explanations of defect progression and identification
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, Wedge, Rectangle, FancyArrowPatch
from matplotlib.path import Path
import matplotlib.patches as patches
import numpy as np
from pathlib import Path as PathLib

# Color palette
COLORS = {
    'healthy': '#2ecc71',      # Green
    'warning': '#f39c12',      # Orange
    'critical': '#e74c3c',     # Red
    'water': '#3498db',        # Blue
    'mold': '#34495e',         # Dark gray
    'crack': '#c0392b',        # Dark red
    'tile': '#ecf0f1',         # Light gray
    'grout': '#95a5a6',        # Gray
    'silicone': '#bdc3c7',     # Silver
    'membrane': '#16a085'      # Teal
}

def create_defect_progression_diagram(output_path='training_catalog/diagrams/defect_progression.png'):
    """Create diagram showing defect progression over time."""

    fig, axes = plt.subplots(1, 4, figsize=(16, 4), dpi=150)
    fig.patch.set_facecolor('white')

    stages = [
        ("Stade 1\nDébut", COLORS['healthy'], "Installation\ncorrecte"),
        ("Stade 2\nAvertissement", COLORS['warning'], "Premiers\nsignes"),
        ("Stade 3\nDégradation", COLORS['critical'], "Défaut\nmajeur"),
        ("Stade 4\nCritique", '#8e44ad', "Intervention\nurgente")
    ]

    for idx, (ax, (title, color, desc)) in enumerate(zip(axes, stages)):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')

        # Main circle
        circle = Circle((5, 6), 2.5, facecolor=color, edgecolor='black', linewidth=3, alpha=0.7)
        ax.add_patch(circle)

        # Title
        ax.text(5, 9.5, title, fontsize=14, fontweight='bold', ha='center', va='top')

        # Description
        ax.text(5, 6, desc, fontsize=10, ha='center', va='center', color='white', fontweight='bold')

        # Severity indicator
        severity = idx + 1
        for i in range(4):
            bar_color = color if i < severity else '#ecf0f1'
            rect = Rectangle((2.5 + i*1.3, 1.5), 1, 0.5, facecolor=bar_color, edgecolor='black', linewidth=1)
            ax.add_patch(rect)

        ax.text(5, 0.8, f'Gravité: {severity}/4', fontsize=9, ha='center', style='italic')

        # Arrow to next stage
        if idx < 3:
            ax.annotate('', xy=(10.5, 5), xytext=(9.5, 5),
                       arrowprops=dict(arrowstyle='->', lw=3, color='#2c3e50'))

    plt.tight_layout()
    PathLib(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    print(f"[OK] Defect progression diagram: {output_path}")
    plt.close()

def create_waterproofing_layers_diagram(output_path='training_catalog/diagrams/waterproofing_layers.png'):
    """Create cross-section diagram of waterproofing layers."""

    fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
    fig.patch.set_facecolor('white')
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(6, 9.5, 'Coupe Transversale - Étanchéité Salle de Bain (DTU 52.2)',
           fontsize=16, fontweight='bold', ha='center')

    # Layers (from bottom to top)
    layers = [
        (1, 1.2, '#8b4513', 'Support béton/maçonnerie'),
        (2.2, 0.8, '#d2b48c', 'Enduit de ragréage'),
        (3, 0.4, '#e67e22', 'Primaire d\'accrochage'),
        (3.4, 0.5, COLORS['membrane'], 'Membrane étanchéité'),
        (3.9, 0.3, '#95a5a6', 'Colle carrelage C2'),
        (4.2, 1, COLORS['tile'], 'Carrelage céramique'),
        (5.2, 0.2, COLORS['grout'], 'Joint ciment'),
        (5.4, 0.3, COLORS['silicone'], 'Joint silicone périphérique')
    ]

    x_start = 2
    total_height = sum(h for _, h, _, _ in layers)
    current_y = 2

    for y_offset, height, color, label in layers:
        # Layer rectangle
        rect = Rectangle((x_start, current_y), 6, height,
                        facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(rect)

        # Label with arrow
        ax.annotate(label,
                   xy=(x_start + 6.1, current_y + height/2),
                   xytext=(9, current_y + height/2),
                   fontsize=10,
                   va='center',
                   arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))

        current_y += height

    # Dimensions
    ax.plot([1.5, 1.5], [2, current_y], 'k-', lw=2)
    ax.plot([1.3, 1.7], [2, 2], 'k-', lw=2)
    ax.plot([1.3, 1.7], [current_y, current_y], 'k-', lw=2)
    ax.text(0.8, (2 + current_y)/2, f'{total_height:.1f}cm',
           fontsize=10, ha='center', va='center', rotation=90, fontweight='bold')

    # Key points
    ax.text(6, 1.2, '✓ CONFORME DTU 52.2', fontsize=12, ha='center',
           color=COLORS['healthy'], fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor=COLORS['healthy'], lw=2))

    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    print(f"[OK] Waterproofing layers diagram: {output_path}")
    plt.close()

def create_joint_failure_diagram(output_path='training_catalog/diagrams/joint_failure.png'):
    """Create diagram showing joint failure mechanisms."""

    fig, axes = plt.subplots(2, 2, figsize=(12, 10), dpi=150)
    fig.patch.set_facecolor('white')
    fig.suptitle('Modes de Défaillance des Joints', fontsize=18, fontweight='bold', y=0.98)

    scenarios = [
        ("Joint Silicone Dégradé", "Moisissure + Perte d'adhérence"),
        ("Joint Ciment Fissuré", "Infiltration d'eau"),
        ("Absence de Joint d'Angle", "Zone non protégée"),
        ("Joint Mal Lissé", "Rétention d'eau + Salissures")
    ]

    for idx, (ax, (title, issue)) in enumerate(zip(axes.flat, scenarios)):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')

        # Title
        ax.text(5, 9.5, title, fontsize=13, fontweight='bold', ha='center')

        if idx == 0:  # Silicone dégradé
            # Tiles
            for i in range(2):
                rect = Rectangle((1 + i*4, 3), 3.8, 3, facecolor=COLORS['tile'],
                               edgecolor='black', linewidth=2)
                ax.add_patch(rect)

            # Degraded joint
            joint_x = [4.8, 5, 5.2, 5, 4.8]
            joint_y = [6, 6.5, 6, 5.5, 6]
            ax.fill(joint_x, joint_y, color=COLORS['mold'], alpha=0.8, edgecolor='black', linewidth=1.5)
            ax.scatter([4.9, 5.1, 5.0], [5.8, 6.2, 5.6], s=30, c='black', alpha=0.5)

            ax.text(5, 1.5, issue, fontsize=10, ha='center', style='italic', color=COLORS['critical'])

        elif idx == 1:  # Ciment fissuré
            # Tiles
            rect1 = Rectangle((2, 4), 3, 3, facecolor=COLORS['tile'], edgecolor='black', linewidth=2)
            rect2 = Rectangle((5.2, 4), 3, 3, facecolor=COLORS['tile'], edgecolor='black', linewidth=2)
            ax.add_patch(rect1)
            ax.add_patch(rect2)

            # Cracked grout
            ax.plot([5, 5.2], [7, 4], 'r-', linewidth=4, alpha=0.7)
            ax.plot([5.05, 5.15], [6.5, 5], 'r--', linewidth=2)

            # Water droplets
            for y_pos in [6.5, 5.5, 4.5]:
                circle = Circle((5.1, y_pos), 0.15, facecolor=COLORS['water'], edgecolor='black', linewidth=1)
                ax.add_patch(circle)

            ax.text(5, 1.5, issue, fontsize=10, ha='center', style='italic', color=COLORS['critical'])

        elif idx == 2:  # Absence joint d'angle
            # Wall 1
            rect1 = Rectangle((2, 2), 0.5, 6, facecolor='#d3d3d3', edgecolor='black', linewidth=2)
            ax.add_patch(rect1)
            # Wall 2
            rect2 = Rectangle((2, 2), 5, 0.5, facecolor='#d3d3d3', edgecolor='black', linewidth=2)
            ax.add_patch(rect2)

            # Missing joint indicator
            ax.plot([2.5, 2.5], [2.5, 4], 'r--', linewidth=3, alpha=0.8)
            ax.text(3.5, 3.5, '❌ JOINT\nMANQUANT', fontsize=11, ha='center',
                   color=COLORS['critical'], fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor='white', edgecolor='red', lw=2))

            ax.text(5, 1, issue, fontsize=10, ha='center', style='italic', color=COLORS['critical'])

        else:  # Joint mal lissé
            # Tile
            rect = Rectangle((2, 4), 6, 3, facecolor=COLORS['tile'], edgecolor='black', linewidth=2)
            ax.add_patch(rect)

            # Irregular joint profile
            x = np.linspace(2.5, 7.5, 100)
            y = 3.7 + 0.3 * np.sin(10 * x) + 0.1 * np.random.randn(100)
            ax.fill_between(x, y, 4, color=COLORS['silicone'], alpha=0.7, edgecolor='black', linewidth=1)

            # Water retention zones
            ax.scatter([3.5, 5, 6.5], [3.85, 3.75, 3.9], s=80, c=COLORS['water'],
                      alpha=0.6, edgecolors='black', linewidths=1)

            ax.text(5, 1.5, issue, fontsize=10, ha='center', style='italic', color=COLORS['warning'])

    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    print(f"[OK] Joint failure diagram: {output_path}")
    plt.close()

def create_tile_defects_diagram(output_path='training_catalog/diagrams/tile_defects.png'):
    """Create diagram showing common tile installation defects."""

    fig, axes = plt.subplots(2, 2, figsize=(12, 10), dpi=150)
    fig.patch.set_facecolor('white')
    fig.suptitle('Défauts Courants de Pose Carrelage', fontsize=18, fontweight='bold', y=0.98)

    scenarios = [
        ("Désalignement", "Joints irréguliers"),
        ("Planéité Défectueuse", "Niveau inégal"),
        ("Décollement", "Son creux"),
        ("Fissuration", "Contraintes mécaniques")
    ]

    for idx, (ax, (title, desc)) in enumerate(zip(axes.flat, scenarios)):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')

        ax.text(5, 9.5, title, fontsize=13, fontweight='bold', ha='center')

        if idx == 0:  # Désalignement
            # Misaligned tiles
            tiles = [
                (1, 4, 2.5, 2.5, 0),
                (3.6, 4.2, 2.5, 2.5, 5),  # Rotated
                (6.1, 3.8, 2.5, 2.5, -3),
            ]
            for x, y, w, h, angle in tiles:
                from matplotlib.transforms import Affine2D
                t = Affine2D().rotate_deg(angle) + ax.transData
                rect = Rectangle((x, y), w, h, facecolor=COLORS['tile'],
                               edgecolor='black', linewidth=2, transform=t)
                ax.add_patch(rect)

            # Irregular joints highlighted
            ax.plot([3.5, 3.7], [6.7, 4], 'r-', linewidth=3, alpha=0.8)
            ax.plot([6, 6.2], [6.3, 3.8], 'r-', linewidth=3, alpha=0.8)

        elif idx == 1:  # Planéité
            # Tiles at different levels
            tiles_data = [(1.5, 4, 0), (4, 4.3, 0.3), (6.5, 3.7, -0.3)]
            for x, y, offset in tiles_data:
                color_shade = int(240 - abs(offset) * 100)  # Darker if more offset
                rect = Rectangle((x, y), 2.3, 2.3,
                               facecolor=f'#{color_shade:02x}{color_shade:02x}{color_shade:02x}',
                               edgecolor='black', linewidth=2)
                ax.add_patch(rect)
                # Level indicator
                ax.plot([x + 1.15, x + 1.15], [y + 2.3, y + 2.3 + abs(offset)*2],
                       'r-', linewidth=2, alpha=0.7)
                ax.text(x + 1.15, y + 2.5 + abs(offset)*2, f'{offset:+.1f}mm',
                       fontsize=8, ha='center', color='red', fontweight='bold')

        elif idx == 2:  # Décollement
            # Tile with void underneath
            rect = Rectangle((2.5, 4), 5, 3, facecolor=COLORS['tile'],
                           edgecolor='black', linewidth=2)
            ax.add_patch(rect)

            # Void area (hatched)
            void = Rectangle((3.5, 2.5), 3, 1.5, facecolor='white',
                           edgecolor=COLORS['critical'], linewidth=2,
                           hatch='///', alpha=0.5)
            ax.add_patch(void)

            # Sound wave indicators
            for i in range(3):
                circle = Circle((5, 5.5), 0.5 + i*0.4, facecolor='none',
                              edgecolor=COLORS['warning'], linewidth=2, linestyle='--')
                ax.add_patch(circle)

            ax.text(5, 1.5, '🔊 Son creux au tape test', fontsize=10, ha='center',
                   color=COLORS['critical'], fontweight='bold')

        else:  # Fissuration
            # Tile with crack
            rect = Rectangle((2, 3), 6, 4, facecolor=COLORS['tile'],
                           edgecolor='black', linewidth=2)
            ax.add_patch(rect)

            # Crack pattern
            crack_x = [3, 4.5, 6, 7.5]
            crack_y = [3.5, 5, 6, 6.5]
            ax.plot(crack_x, crack_y, 'r-', linewidth=4, alpha=0.8)
            ax.plot(crack_x, crack_y, 'k-', linewidth=2, linestyle='--', alpha=0.5)

            # Stress indicators (arrows)
            ax.annotate('', xy=(2.5, 5), xytext=(1.5, 5),
                       arrowprops=dict(arrowstyle='->', lw=2, color='red'))
            ax.annotate('', xy=(7.5, 5), xytext=(8.5, 5),
                       arrowprops=dict(arrowstyle='->', lw=2, color='red'))
            ax.text(5, 1.5, 'Contraintes ↔', fontsize=10, ha='center',
                   color=COLORS['critical'], fontweight='bold')

        ax.text(5, 0.8, desc, fontsize=9, ha='center', style='italic', color='#666')

    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    print(f"[OK] Tile defects diagram: {output_path}")
    plt.close()

def create_electrical_volumes_diagram(output_path='training_catalog/diagrams/electrical_volumes.png'):
    """Create diagram of electrical safety volumes in bathroom."""

    fig, ax = plt.subplots(figsize=(14, 10), dpi=150)
    fig.patch.set_facecolor('white')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(7, 9.5, 'Volumes Électriques Salle de Bain (NF C 15-100)',
           fontsize=18, fontweight='bold', ha='center')

    # Shower/bathtub (Volume 0)
    bathtub = Rectangle((3, 1), 3, 1.5, facecolor='#3498db',
                       edgecolor='black', linewidth=3, alpha=0.3)
    ax.add_patch(bathtub)
    ax.text(4.5, 1.75, 'Volume 0\nBaignoire', fontsize=10, ha='center',
           fontweight='bold', color='white')

    # Volume 1 (above bathtub, 2.25m height)
    vol1 = Rectangle((3, 2.5), 3, 3.5, facecolor='#e74c3c',
                    edgecolor='black', linewidth=3, alpha=0.2)
    ax.add_patch(vol1)
    ax.text(4.5, 4.25, 'Volume 1\n2.25m', fontsize=11, ha='center',
           fontweight='bold', color='#c0392b')

    # Volume 2 (60cm around Volume 1)
    vol2_left = Rectangle((2.4, 2.5), 0.6, 3.5, facecolor='#f39c12',
                         edgecolor='black', linewidth=2, alpha=0.2)
    vol2_right = Rectangle((6, 2.5), 0.6, 3.5, facecolor='#f39c12',
                          edgecolor='black', linewidth=2, alpha=0.2)
    ax.add_patch(vol2_left)
    ax.add_patch(vol2_right)
    ax.text(1.8, 4.25, 'Vol. 2\n60cm', fontsize=9, ha='center',
           fontweight='bold', color='#d35400', rotation=90)

    # Hors volumes (outside)
    ax.text(9, 4, 'Hors Volumes\n(> 60cm du Vol. 2)', fontsize=12, ha='center',
           fontweight='bold', color='#27ae60',
           bbox=dict(boxstyle='round,pad=0.8', facecolor='#2ecc71',
                    edgecolor='black', lw=2, alpha=0.3))

    # Equipment examples
    equipment = [
        # (x, y, name, volume, allowed, ip_rating)
        (4.5, 1.2, '💧 Pomme douche', '0', '✓ TBTS 12V', 'IPX7'),
        (4.5, 3.5, '💡 Spot', '1', '✓ Classe II', 'IPX5'),
        (2.2, 3.5, '🌀 Extracteur', '2', '✓ IPX4', 'IPX4'),
        (9, 3, '🔌 Prise 16A', 'Hors', '✓ + 30mA', 'IP21'),
        (5.2, 4.8, '❌ Prise', '1', '❌ INTERDIT', '--'),
    ]

    for x, y, name, vol, allowed, ip in equipment:
        color = '#2ecc71' if '✓' in allowed else '#e74c3c'
        symbol = '✓' if '✓' in allowed else '❌'

        ax.text(x, y, name, fontsize=9, ha='center', fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.4', facecolor=color,
                        edgecolor='black', lw=1.5, alpha=0.6))
        ax.text(x, y - 0.4, f'{allowed} | {ip}', fontsize=7, ha='center', style='italic')

    # Legend
    legend_y = 0.5
    legend_items = [
        ('Volume 0', '#3498db', 'Aucun appareil (sauf TBTS 12V)'),
        ('Volume 1', '#e74c3c', 'Chauffe-eau instantané IPX5'),
        ('Volume 2', '#f39c12', 'Luminaires, extracteur IPX4'),
        ('Hors volumes', '#2ecc71', 'Appareils standards IP21 + 30mA')
    ]

    for i, (label, color, desc) in enumerate(legend_items):
        x_pos = 1 + i * 3
        rect = Rectangle((x_pos, legend_y), 0.4, 0.3, facecolor=color,
                        edgecolor='black', linewidth=1, alpha=0.5)
        ax.add_patch(rect)
        ax.text(x_pos + 0.6, legend_y + 0.15, f'{label}:', fontsize=8,
               va='center', fontweight='bold')
        ax.text(x_pos + 0.6, legend_y - 0.1, desc, fontsize=7, va='top', style='italic')

    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    print(f"[OK] Electrical volumes diagram: {output_path}")
    plt.close()

def main():
    """Generate all defect diagrams."""
    print("=== Defect Diagrams Generator ===\n")

    output_dir = PathLib("training_catalog/diagrams")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("[1/5] Generating defect progression diagram...")
    create_defect_progression_diagram()

    print("[2/5] Generating waterproofing layers diagram...")
    create_waterproofing_layers_diagram()

    print("[3/5] Generating joint failure modes...")
    create_joint_failure_diagram()

    print("[4/5] Generating tile defects diagram...")
    create_tile_defects_diagram()

    print("[5/5] Generating electrical safety volumes...")
    create_electrical_volumes_diagram()

    print("\n✅ All diagrams generated successfully!")
    print(f"Location: {output_dir.absolute()}/")
    print("\nGenerated files:")
    for file in sorted(output_dir.glob("*.png")):
        size_kb = file.stat().st_size / 1024
        print(f"  - {file.name} ({size_kb:.1f} KB)")

if __name__ == "__main__":
    main()
