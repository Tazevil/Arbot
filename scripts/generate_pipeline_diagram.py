#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Visual Pipeline Diagram for ArBot-MiniDB
Creates a professional flowchart visualization of the vision analysis pipeline
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import json
from pathlib import Path

# Color scheme (professional, accessible)
COLORS = {
    'ingestion': '#3498db',      # Blue
    'vision': '#9b59b6',         # Purple
    'defect': '#e74c3c',         # Red
    'norm': '#f39c12',           # Orange
    'reporting': '#2ecc71',      # Green
    'data': '#34495e',           # Dark gray
    'output': '#16a085',         # Teal
    'background': '#ecf0f1',     # Light gray
    'text': '#2c3e50'            # Dark blue-gray
}

def create_pipeline_diagram(output_path='pipeline_diagram.png'):
    """Create comprehensive pipeline visualization."""

    # Create figure with high DPI for clarity
    fig, ax = plt.subplots(figsize=(16, 12), dpi=150)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 14)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    # Title
    ax.text(5, 13.2, 'ArBot Vision Analysis Pipeline v0.7.1',
            fontsize=24, fontweight='bold', ha='center', color=COLORS['text'])
    ax.text(5, 12.7, 'Construction Defect Detection & Assessment System',
            fontsize=14, ha='center', style='italic', color=COLORS['text'])

    # Helper functions
    def add_box(x, y, width, height, text, color, subtitle=''):
        """Add a rounded box with text."""
        box = FancyBboxPatch((x, y), width, height,
                            boxstyle="round,pad=0.1",
                            edgecolor=color, facecolor=color,
                            linewidth=2, alpha=0.85)
        ax.add_patch(box)

        # Main text
        ax.text(x + width/2, y + height/2 + 0.15, text,
               fontsize=13, fontweight='bold', ha='center', va='center',
               color='white')

        # Subtitle
        if subtitle:
            ax.text(x + width/2, y + height/2 - 0.2, subtitle,
                   fontsize=9, ha='center', va='center',
                   color='white', style='italic')

    def add_data_box(x, y, width, height, text, details=''):
        """Add a data storage box."""
        box = mpatches.Rectangle((x, y), width, height,
                                edgecolor=COLORS['data'],
                                facecolor='white',
                                linewidth=2, linestyle='--')
        ax.add_patch(box)
        ax.text(x + width/2, y + height/2 + 0.1, text,
               fontsize=10, fontweight='bold', ha='center', va='center',
               color=COLORS['data'])
        if details:
            ax.text(x + width/2, y + height/2 - 0.2, details,
                   fontsize=8, ha='center', va='center',
                   color=COLORS['data'])

    def add_arrow(x1, y1, x2, y2, label='', color='#7f8c8d', style='->'):
        """Add arrow between components."""
        arrow = FancyArrowPatch((x1, y1), (x2, y2),
                              arrowstyle=style, mutation_scale=25,
                              linewidth=2.5, color=color, alpha=0.7)
        ax.add_patch(arrow)

        if label:
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mid_x + 0.2, mid_y, label,
                   fontsize=8, ha='center',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                            edgecolor='none', alpha=0.8))

    # === INPUT DATA (Top) ===
    add_data_box(0.5, 11, 1.8, 0.8, '94 Images', 'images_db.json')
    add_data_box(2.8, 11, 1.8, 0.8, '16 Documents', 'docs_index.json')
    add_data_box(5.1, 11, 2.3, 0.8, 'ArBot-Core v1.4', '70 analysis files')
    add_data_box(7.9, 11, 1.8, 0.8, 'Knowledge Base', '15 JSON files')

    # === PHASE 1: INGESTION ===
    add_box(1.5, 9.2, 2.5, 0.9, 'PHASE 1', COLORS['ingestion'], 'INGESTION')

    # Details for ingestion
    ax.text(2.75, 8.9, '• Validate files\n• Load metadata\n• Apply filters',
           fontsize=8, ha='center', color=COLORS['text'])

    # Arrows from inputs to Phase 1
    add_arrow(1.4, 11, 2, 10.1, '', COLORS['ingestion'])
    add_arrow(3.7, 11, 3, 10.1, '', COLORS['ingestion'])
    add_arrow(6.25, 11, 3.5, 10.1, '', COLORS['ingestion'])

    # === PHASE 2: VISION_ANALYSIS ===
    add_box(1.5, 7.3, 2.5, 0.9, 'PHASE 2', COLORS['vision'], 'VISION_ANALYSIS')

    ax.text(2.75, 7, '• Image processing\n• ROI extraction\n• Feature detection',
           fontsize=8, ha='center', color=COLORS['text'])

    add_arrow(2.75, 9.2, 2.75, 8.2, '94 images', COLORS['vision'])

    # === PHASE 3: DEFECT_DETECTION ===
    add_box(5.5, 7.3, 2.5, 0.9, 'PHASE 3', COLORS['defect'], 'DEFECT_DETECTION')

    ax.text(6.75, 7, '• Pattern recognition\n• Severity assessment\n• Classification',
           fontsize=8, ha='center', color=COLORS['text'])

    add_arrow(4, 7.75, 5.5, 7.75, '', COLORS['defect'])

    # Defect stats box
    add_data_box(5.5, 5.8, 2.5, 0.8, '204 Defects', '6 categories')
    add_arrow(6.75, 7.3, 6.75, 6.6, '', COLORS['defect'])

    # === PHASE 4: NORM_REFERENCE_LINK ===
    add_box(1.5, 4.5, 2.5, 0.9, 'PHASE 4', COLORS['norm'], 'NORM_REFERENCE')

    ax.text(2.75, 4.2, '• Standards lookup\n• DTU validation\n• Compliance check',
           fontsize=8, ha='center', color=COLORS['text'])

    # Arrow from defects to norm linking
    add_arrow(6.75, 5.8, 4, 4.95, '+ DTU docs', COLORS['norm'])

    # Technical standards reference
    add_data_box(0.2, 3.5, 1.5, 1.2, 'DTU Standards',
                'DTU 25.41\nDTU 52.2\nDTU 60.1')
    add_arrow(1.5, 4.2, 1.5, 4.7, '', COLORS['norm'], style='<-')

    # === PHASE 5: REPORTING ===
    add_box(5.5, 4.5, 2.5, 0.9, 'PHASE 5', COLORS['reporting'], 'REPORTING')

    ax.text(6.75, 4.2, '• Generate JSON\n• Create summaries\n• Export results',
           fontsize=8, ha='center', color=COLORS['text'])

    add_arrow(4, 4.95, 5.5, 4.95, '', COLORS['reporting'])

    # === OUTPUTS ===
    # Main outputs
    add_data_box(5, 2.5, 1.5, 0.8, 'pipeline_summary', '.json')
    add_data_box(6.8, 2.5, 1.5, 0.8, 'def_all.json', '204 defects')
    add_data_box(5, 1.4, 1.5, 0.8, 'Analysis Reports', '70 files')
    add_data_box(6.8, 1.4, 1.5, 0.8, 'Defect Catalog', 'by category')

    # Arrows to outputs
    add_arrow(6.75, 4.5, 5.75, 3.3, '', COLORS['reporting'])
    add_arrow(6.75, 4.5, 7.55, 3.3, '', COLORS['reporting'])
    add_arrow(6.75, 4.5, 5.75, 2.2, '', COLORS['reporting'])
    add_arrow(6.75, 4.5, 7.55, 2.2, '', COLORS['reporting'])

    # === SIDE PANEL: Pipeline Configuration ===
    config_x, config_y = 8.5, 9.2
    ax.add_patch(mpatches.Rectangle((config_x, config_y - 2.5), 1.3, 3.3,
                                   facecolor=COLORS['background'],
                                   edgecolor=COLORS['text'],
                                   linewidth=2, alpha=0.5))

    ax.text(config_x + 0.65, config_y + 0.6, 'Configuration',
           fontsize=11, fontweight='bold', ha='center', color=COLORS['text'])

    config_text = """Control Panel
v0.7.1

Modules:
• Schemas
• Prompts
• Runtime

Outputs:
• JSON
• Reports
• Manifests"""

    ax.text(config_x + 0.65, config_y - 0.5, config_text,
           fontsize=8, ha='center', va='top', color=COLORS['text'],
           linespacing=1.5)

    # === SIDE PANEL: Statistics ===
    stats_x, stats_y = 8.5, 5.5
    ax.add_patch(mpatches.Rectangle((stats_x, stats_y - 2.2), 1.3, 2.5,
                                   facecolor='#fff9e6',
                                   edgecolor=COLORS['output'],
                                   linewidth=2))

    ax.text(stats_x + 0.65, stats_y + 0.1, 'Pipeline Stats',
           fontsize=11, fontweight='bold', ha='center', color=COLORS['text'])

    stats_text = """Images: 94
Documents: 16
Defects: 204
Frames: 70
Categories: 6
Zones: 3

Status: ✓ Ready"""

    ax.text(stats_x + 0.65, stats_y - 0.4, stats_text,
           fontsize=8, ha='center', va='top', color=COLORS['text'],
           linespacing=1.6, family='monospace')

    # === LEGEND ===
    legend_elements = [
        mpatches.Patch(color=COLORS['ingestion'], label='Data Loading', alpha=0.85),
        mpatches.Patch(color=COLORS['vision'], label='Vision Processing', alpha=0.85),
        mpatches.Patch(color=COLORS['defect'], label='Defect Detection', alpha=0.85),
        mpatches.Patch(color=COLORS['norm'], label='Standards Compliance', alpha=0.85),
        mpatches.Patch(color=COLORS['reporting'], label='Report Generation', alpha=0.85),
        mpatches.Patch(facecolor='white', edgecolor=COLORS['data'],
                      label='Data Storage', linestyle='--', linewidth=2)
    ]

    ax.legend(handles=legend_elements, loc='lower left',
             fontsize=9, framealpha=0.9, ncol=3)

    # === FOOTER ===
    ax.text(5, 0.3, 'ArBot-MiniDB | Case #25-001508-RLY-M1 | Water Damage Assessment',
           fontsize=9, ha='center', style='italic', color=COLORS['text'])
    ax.text(5, 0.05, 'Generated by Vision Boost Pro Plus',
           fontsize=8, ha='center', color='gray')

    # Save with high quality
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight',
               facecolor='white', edgecolor='none')
    print(f"[OK] Pipeline diagram saved: {output_path}")

    # Also save as SVG for scalability
    svg_path = output_path.replace('.png', '.svg')
    plt.savefig(svg_path, format='svg', bbox_inches='tight',
               facecolor='white', edgecolor='none')
    print(f"[OK] Vector version saved: {svg_path}")

    return output_path


def create_defect_distribution_chart(output_path='defect_distribution.png'):
    """Create defect category distribution visualization."""

    # Load defect data
    try:
        with open('pipeline_output/def_all.json', 'r', encoding='utf-8') as f:
            defects_data = json.load(f)
            defects = defects_data.get('defects', [])
    except FileNotFoundError:
        print("[WARNING] def_all.json not found, using sample data")
        defects = []

    # Count by category
    categories = {}
    severities = {}

    for defect in defects:
        cat = defect.get('category', 'UNKNOWN')
        sev = defect.get('severity', 'UNKNOWN')
        categories[cat] = categories.get(cat, 0) + 1
        severities[sev] = severities.get(sev, 0) + 1

    if not categories:
        # Sample data for demonstration
        categories = {
            'CARRELAGE': 82,
            'JOINTS': 45,
            'PLOMBERIE': 31,
            'ETANCHEITE': 28,
            'REVETEMENTS': 12,
            'ELECTRICITE': 6
        }
        severities = {
            'CRITIQUE': 15,
            'MAJEUR': 89,
            'MINEUR': 76,
            'OBSERVATION': 24
        }

    # Create subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), dpi=150)
    fig.patch.set_facecolor('white')

    # Chart 1: Categories
    cats = list(categories.keys())
    counts = list(categories.values())
    colors_cat = ['#e74c3c', '#3498db', '#9b59b6', '#f39c12', '#2ecc71', '#1abc9c']

    bars1 = ax1.barh(cats, counts, color=colors_cat[:len(cats)], alpha=0.8, edgecolor='black', linewidth=1.5)
    ax1.set_xlabel('Number of Defects', fontsize=12, fontweight='bold')
    ax1.set_title('Defects by Category', fontsize=14, fontweight='bold', pad=20)
    ax1.grid(axis='x', alpha=0.3, linestyle='--')

    # Add value labels
    for i, (bar, count) in enumerate(zip(bars1, counts)):
        ax1.text(count + 1, i, str(count), va='center', fontweight='bold', fontsize=11)

    # Chart 2: Severities
    sevs = list(severities.keys())
    sev_counts = list(severities.values())
    colors_sev = ['#c0392b', '#e67e22', '#f1c40f', '#95a5a6']

    wedges, texts, autotexts = ax2.pie(sev_counts, labels=sevs, autopct='%1.1f%%',
                                       colors=colors_sev[:len(sevs)], startangle=90,
                                       textprops={'fontsize': 11, 'fontweight': 'bold'},
                                       wedgeprops={'edgecolor': 'white', 'linewidth': 2})

    ax2.set_title('Defects by Severity', fontsize=14, fontweight='bold', pad=20)

    # Make percentage text white for better contrast
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[OK] Defect distribution chart saved: {output_path}")

    return output_path


if __name__ == "__main__":
    print("=== ArBot Pipeline Diagram Generator ===\n")

    # Create output directory
    output_dir = Path("visualizations")
    output_dir.mkdir(exist_ok=True)

    # Generate diagrams
    pipeline_path = output_dir / "pipeline_architecture.png"
    defect_path = output_dir / "defect_distribution.png"

    create_pipeline_diagram(str(pipeline_path))
    create_defect_distribution_chart(str(defect_path))

    print(f"\n[SUCCESS] All visualizations generated in {output_dir}/")
    print("\nGenerated files:")
    print(f"  • {pipeline_path}")
    print(f"  • {pipeline_path.with_suffix('.svg')}")
    print(f"  • {defect_path}")
