#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Professional Training Catalog Builder for ArBot-MiniDB
Analyzes all 94 images and creates comprehensive defect training materials
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any

# Defect taxonomy and learning objectives
DEFECT_TAXONOMY = {
    "CARRELAGE": {
        "name_fr": "Carrelage",
        "subcategories": {
            "DESALIGNEMENT": "Désalignement / Planéité",
            "FISSURE": "Fissures et cassures",
            "DECOLLEMENT": "Décollement / Délamination",
            "JOINT_INEGAL": "Joints irréguliers"
        },
        "severity_range": ["MINEUR", "MAJEUR", "CRITIQUE"],
        "dtu_refs": ["DTU 52.2", "DTU 25.41"],
        "learning_objectives": [
            "Identifier défauts de pose sur carrelage mural et sol",
            "Évaluer l'adhérence et la planéité",
            "Détecter signes avant-coureurs de délamination"
        ]
    },
    "JOINTS": {
        "name_fr": "Joints",
        "subcategories": {
            "SILICONE": "Joints silicone dégradés",
            "CIMENT": "Joints ciment fissurés",
            "ABSENCE": "Joints manquants",
            "MOISISSURE": "Joints moisis"
        },
        "severity_range": ["MINEUR", "MAJEUR", "CRITIQUE"],
        "dtu_refs": ["DTU 52.2", "DTU 59.1"],
        "learning_objectives": [
            "Différencier joints silicone vs ciment",
            "Identifier dégradations liées à l'humidité",
            "Évaluer nécessité de réfection"
        ]
    },
    "PLOMBERIE": {
        "name_fr": "Plomberie",
        "subcategories": {
            "FUITE": "Fuites et infiltrations",
            "CORROSION": "Corrosion des raccords",
            "EVACUATION": "Problèmes d'évacuation",
            "ALIMENTATION": "Défauts d'alimentation"
        },
        "severity_range": ["MAJEUR", "CRITIQUE"],
        "dtu_refs": ["DTU 60.1", "DTU 60.11"],
        "learning_objectives": [
            "Identifier signes de corrosion sur tuyauterie",
            "Évaluer conformité des raccords",
            "Détecter fuites actives vs anciennes"
        ]
    },
    "ETANCHEITE": {
        "name_fr": "Étanchéité",
        "subcategories": {
            "MEMBRANE": "Membrane déchirée/dégradée",
            "INFILTRATION": "Infiltrations d'eau",
            "SIPHON": "Siphon de sol défaillant",
            "ANGLE": "Angles non protégés"
        },
        "severity_range": ["MAJEUR", "CRITIQUE"],
        "dtu_refs": ["DTU 52.2 Art. 4", "DTU 25.41"],
        "learning_objectives": [
            "Reconnaître membranes d'étanchéité conformes",
            "Identifier zones à risque (angles, pénétrations)",
            "Évaluer impact sur structure bâtiment"
        ]
    },
    "REVETEMENTS": {
        "name_fr": "Revêtements",
        "subcategories": {
            "PEINTURE": "Peinture écaillée/dégradée",
            "ENDUIT": "Enduit décollé",
            "HUMIDITE": "Traces d'humidité",
            "MOISISSURE": "Moisissures visibles"
        },
        "severity_range": ["MINEUR", "MAJEUR"],
        "dtu_refs": ["DTU 59.3", "DTU 59.1"],
        "learning_objectives": [
            "Diagnostiquer causes de dégradation",
            "Distinguer problème esthétique vs structurel",
            "Identifier solutions de réparation adaptées"
        ]
    },
    "ELECTRICITE": {
        "name_fr": "Électricité",
        "subcategories": {
            "VOLUME": "Non-respect des volumes",
            "PROTECTION": "Protection IP insuffisante",
            "INSTALLATION": "Installation non conforme"
        },
        "severity_range": ["CRITIQUE"],
        "dtu_refs": ["NF C 15-100", "DTU 60.33"],
        "learning_objectives": [
            "Connaître volumes de sécurité (0, 1, 2)",
            "Identifier installations dangereuses",
            "Évaluer conformité NF C 15-100"
        ]
    }
}

# View types for pedagogical progression
VIEW_TYPES = {
    "GEN": {"name": "Vue Générale", "use": "Vision d'ensemble, contexte spatial"},
    "DET": {"name": "Vue Détail", "use": "Focus sur défaut spécifique"},
    "MAC": {"name": "Macro", "use": "Analyse microscopique du défaut"},
    "MGM": {"name": "Moyenne Macro", "use": "Détail intermédiaire"},
    "MGS": {"name": "Super Macro", "use": "Détail maximum"},
    "MGP": {"name": "Macro Panoramique", "use": "Large zone en détail"},
    "MGB": {"name": "Macro Basique", "use": "Détail simple"},
    "DEG": {"name": "Vue Dégagée", "use": "Vue dégagée sans obstacles"},
    "PAN": {"name": "Panoramique", "use": "Vue à 360°"}
}

def parse_filename(filename: str) -> Dict[str, str]:
    """Parse structured filename for metadata."""
    match = re.match(r'(\d{4})_([A-Z-]+)_(GEN|DET|MAC|MGM|MGS|MGP|MGB|DEG|PAN)(_\d{8})?\.jpg', filename)
    if match:
        return {
            "id": match.group(1),
            "zone": match.group(2),
            "view_type": match.group(3),
            "date": match.group(4)[1:] if match.group(4) else None
        }
    return {}

def categorize_images_by_content(images: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize images by their content keywords."""
    categorized = defaultdict(list)

    for img in images:
        filename = img['title'].upper()

        # Extract zone info
        parsed = parse_filename(img['title'])
        zone_name = parsed.get('zone', 'UNKNOWN')

        # Categorize by keywords in filename
        if 'JOINT' in zone_name:
            categorized['JOINTS'].append(img)
        elif 'CARRELAGE' in zone_name or 'DESALIGNEMENT' in zone_name:
            categorized['CARRELAGE'].append(img)
        elif 'EVACUATION' in zone_name or 'ALIMENTATION' in zone_name or 'SIPHON' in zone_name or 'MITIGEUR' in zone_name:
            categorized['PLOMBERIE'].append(img)
        elif 'BAIGNOIRE' in zone_name or 'VASQUE' in zone_name or 'APPUI' in zone_name:
            categorized['ETANCHEITE'].append(img)
        elif 'PEINTURE' in zone_name or 'BAGUETTE' in zone_name or 'DECOR' in zone_name:
            categorized['REVETEMENTS'].append(img)
        elif 'INTERRUPTEUR' in zone_name or 'PRISE' in zone_name or 'SPOT' in zone_name:
            categorized['ELECTRICITE'].append(img)
        elif parsed.get('view_type') == 'GEN':
            # General views go to overview
            categorized['OVERVIEW'].append(img)
        else:
            # Catch-all
            categorized['AUTRES'].append(img)

    return categorized

def select_best_examples(categorized: Dict[str, List], n_per_category: int = 6) -> Dict[str, List]:
    """Select most representative images from each category."""
    best_examples = {}

    for category, images in categorized.items():
        if category == 'OVERVIEW':
            # Keep all overview images
            best_examples[category] = images[:10]
            continue

        # Priority: DET > MAC > MGM > GEN
        view_priority = {'DET': 5, 'MAC': 4, 'MGM': 3, 'MGS': 3, 'MGP': 2, 'MGB': 2, 'GEN': 1, 'DEG': 1}

        scored = []
        for img in images:
            parsed = parse_filename(img['title'])
            view = parsed.get('view_type', 'GEN')
            score = view_priority.get(view, 0)
            scored.append((score, img))

        # Sort by score (highest first) and take top N
        scored.sort(key=lambda x: x[0], reverse=True)
        best_examples[category] = [img for score, img in scored[:n_per_category]]

    return best_examples

def generate_training_database(images_db: Dict, defects_db: Dict) -> Dict:
    """Generate comprehensive training database."""
    images = images_db['items']

    # Categorize all images
    categorized = categorize_images_by_content(images)

    # Select best examples
    best_examples = select_best_examples(categorized, n_per_category=8)

    # Build training database
    training_db = {
        "meta": {
            "name": "Catalogue de Formation - Défauts Rénovation Salle de Bain",
            "version": "1.0.0",
            "total_images": len(images),
            "selected_examples": sum(len(imgs) for imgs in best_examples.values()),
            "defect_categories": len(DEFECT_TAXONOMY),
            "pedagogical_progression": "Général → Détail → Macro",
            "target_audience": "Professionnels du bâtiment, experts sinistres, inspecteurs"
        },
        "taxonomy": DEFECT_TAXONOMY,
        "view_types": VIEW_TYPES,
        "categories": {},
        "statistics": {
            "images_by_category": {cat: len(imgs) for cat, imgs in categorized.items()},
            "selected_by_category": {cat: len(imgs) for cat, imgs in best_examples.items()},
            "images_by_view_type": defaultdict(int),
            "images_by_phase": {"chantier": 0, "sinistre": 0}
        }
    }

    # Populate categories with selected examples
    for category, images_list in best_examples.items():
        if category == 'OVERVIEW' or category == 'AUTRES':
            continue

        cat_info = DEFECT_TAXONOMY.get(category, {})

        training_db['categories'][category] = {
            "name": cat_info.get('name_fr', category),
            "subcategories": cat_info.get('subcategories', {}),
            "dtu_references": cat_info.get('dtu_refs', []),
            "learning_objectives": cat_info.get('learning_objectives', []),
            "severity_range": cat_info.get('severity_range', []),
            "images": []
        }

        for img in images_list:
            parsed = parse_filename(img['title'])

            # Count statistics
            view_type = parsed.get('view_type', 'UNKNOWN')
            training_db['statistics']['images_by_view_type'][view_type] += 1
            training_db['statistics']['images_by_phase'][img.get('phase', 'unknown')] += 1

            # Enhanced image entry
            training_db['categories'][category]['images'].append({
                "id": img['id'],
                "filename": img['title'],
                "url": img['url'],
                "url_preview": img['url_preview'],
                "view_type": view_type,
                "view_type_description": VIEW_TYPES.get(view_type, {}).get('use', ''),
                "zone": parsed.get('zone', 'UNKNOWN'),
                "phase": img.get('phase', ''),
                "date": parsed.get('date'),
                "roi_hints": img.get('roi_hints', []),
                "pedagogical_use": f"Exemple {view_type.lower()} de défaut {category.lower()}"
            })

    # Add overview section
    if 'OVERVIEW' in best_examples:
        training_db['overview_images'] = [{
            "id": img['id'],
            "filename": img['title'],
            "url": img['url'],
            "url_preview": img['url_preview'],
            "phase": img.get('phase'),
            "use": "Compréhension du contexte général du chantier/sinistre"
        } for img in best_examples.get('OVERVIEW', [])]

    return training_db

def generate_html_catalog(training_db: Dict, output_path: str):
    """Generate interactive HTML catalog."""

    html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catalogue de Formation - Défauts Rénovation Salle de Bain</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
        }}

        .header {{
            background: white;
            padding: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}

        .header h1 {{
            color: #667eea;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}

        .header p {{
            color: #666;
            font-size: 1.1rem;
        }}

        .stats {{
            background: white;
            margin: 2rem auto;
            max-width: 1200px;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
        }}

        .stat-card {{
            text-align: center;
            padding: 1.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
        }}

        .stat-card h3 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}

        .stat-card p {{
            font-size: 0.9rem;
            opacity: 0.9;
        }}

        .search-bar {{
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 2rem;
        }}

        .search-bar input {{
            width: 100%;
            padding: 1rem;
            font-size: 1.1rem;
            border: none;
            border-radius: 50px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            outline: none;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}

        .category-section {{
            background: white;
            margin-bottom: 3rem;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .category-header {{
            padding: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}

        .category-header h2 {{
            font-size: 2rem;
            margin-bottom: 1rem;
        }}

        .category-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            margin-top: 1rem;
        }}

        .meta-tag {{
            background: rgba(255,255,255,0.2);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
        }}

        .learning-objectives {{
            background: #f8f9fa;
            padding: 1.5rem 2rem;
            border-left: 4px solid #667eea;
        }}

        .learning-objectives h3 {{
            color: #667eea;
            margin-bottom: 1rem;
        }}

        .learning-objectives ul {{
            list-style-position: inside;
            color: #555;
        }}

        .learning-objectives li {{
            margin-bottom: 0.5rem;
        }}

        .image-gallery {{
            padding: 2rem;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 2rem;
        }}

        .image-card {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
            cursor: pointer;
        }}

        .image-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }}

        .image-card img {{
            width: 100%;
            height: 250px;
            object-fit: cover;
        }}

        .image-info {{
            padding: 1rem;
        }}

        .image-info h4 {{
            color: #667eea;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
        }}

        .image-info p {{
            color: #666;
            font-size: 0.85rem;
            margin-bottom: 0.3rem;
        }}

        .view-badge {{
            display: inline-block;
            padding: 0.3rem 0.8rem;
            background: #667eea;
            color: white;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: bold;
        }}

        .footer {{
            background: white;
            padding: 2rem;
            text-align: center;
            margin-top: 3rem;
        }}

        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
        }}

        .modal-content {{
            margin: auto;
            display: block;
            max-width: 90%;
            max-height: 90%;
            position: relative;
            top: 50%;
            transform: translateY(-50%);
        }}

        .close {{
            position: absolute;
            top: 15px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
        }}

        @media print {{
            body {{ background: white; }}
            .image-gallery {{ grid-template-columns: repeat(2, 1fr); }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📚 Catalogue de Formation Professionnel</h1>
        <p>Défauts de Rénovation en Salle de Bain - Guide Technique DTU</p>
        <p style="margin-top: 1rem; font-size: 0.9rem; color: #999;">
            ArBot-MiniDB | Case #25-001508-RLY-M1 | Version {version}
        </p>
    </div>

    <div class="stats">
        <div class="stat-card">
            <h3>{total_images}</h3>
            <p>Images Totales</p>
        </div>
        <div class="stat-card">
            <h3>{selected_examples}</h3>
            <p>Exemples Sélectionnés</p>
        </div>
        <div class="stat-card">
            <h3>{defect_categories}</h3>
            <p>Catégories de Défauts</p>
        </div>
        <div class="stat-card">
            <h3>DTU</h3>
            <p>Normes Référencées</p>
        </div>
    </div>

    <div class="search-bar">
        <input type="text" id="searchInput" placeholder="🔍 Rechercher un type de défaut, une zone, ou une référence DTU..." onkeyup="searchCatalog()">
    </div>

    <div class="container" id="catalogContent">
        {categories_html}
    </div>

    <div class="footer">
        <p><strong>ArBot Vision Boost Pro Plus</strong> | Généré le {date}</p>
        <p style="margin-top: 0.5rem; color: #999;">
            Document pédagogique pour formation professionnelle aux diagnostics de défauts en rénovation
        </p>
    </div>

    <!-- Modal for image zoom -->
    <div id="imageModal" class="modal" onclick="closeModal()">
        <span class="close">&times;</span>
        <img class="modal-content" id="modalImage">
    </div>

    <script>
        function openImage(url) {{
            document.getElementById('imageModal').style.display = 'block';
            document.getElementById('modalImage').src = url;
        }}

        function closeModal() {{
            document.getElementById('imageModal').style.display = 'none';
        }}

        function searchCatalog() {{
            const input = document.getElementById('searchInput').value.toLowerCase();
            const sections = document.querySelectorAll('.category-section');

            sections.forEach(section => {{
                const text = section.textContent.toLowerCase();
                section.style.display = text.includes(input) ? 'block' : 'none';
            }});
        }}

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'Escape') closeModal();
        }});
    </script>
</body>
</html>
"""

    # Generate categories HTML
    categories_html = ""
    for category, data in training_db['categories'].items():
        subcats = ', '.join(data['subcategories'].values()) if data['subcategories'] else "Général"
        dtu_refs = ', '.join(data['dtu_references'])

        categories_html += f"""
        <div class="category-section" data-category="{category}">
            <div class="category-header">
                <h2>{data['name']}</h2>
                <div class="category-meta">
                    <span class="meta-tag">📋 {len(data['images'])} exemples</span>
                    <span class="meta-tag">📚 {dtu_refs}</span>
                    <span class="meta-tag">⚠️ Sévérité: {' / '.join(data['severity_range'])}</span>
                </div>
            </div>

            <div class="learning-objectives">
                <h3>🎯 Objectifs Pédagogiques</h3>
                <ul>
                    {''.join(f'<li>{obj}</li>' for obj in data['learning_objectives'])}
                </ul>
            </div>

            <div class="image-gallery">
        """

        for img in data['images']:
            categories_html += f"""
                <div class="image-card" onclick="openImage('{img['url']}')">
                    <img src="{img['url_preview']}" alt="{img['filename']}" loading="lazy">
                    <div class="image-info">
                        <h4>{img['zone'].replace('-', ' ').title()}</h4>
                        <span class="view-badge">{img['view_type']}</span>
                        <p><strong>ID:</strong> {img['id']} | <strong>Phase:</strong> {img['phase']}</p>
                        <p style="margin-top: 0.5rem; font-style: italic;">{img['view_type_description']}</p>
                    </div>
                </div>
            """

        categories_html += """
            </div>
        </div>
        """

    # Fill template
    html = html.format(
        version=training_db['meta']['version'],
        total_images=training_db['meta']['total_images'],
        selected_examples=training_db['meta']['selected_examples'],
        defect_categories=training_db['meta']['defect_categories'],
        categories_html=categories_html,
        date="2025-11-11"
    )

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"[OK] HTML catalog generated: {output_path}")

def generate_best_practices_guide(output_path: str):
    """Generate comprehensive best practices guide."""

    guide = """# 📘 Guide des Bonnes Pratiques - Rénovation Salle de Bain

## Table des Matières

1. [Introduction](#introduction)
2. [Préparation du Support](#preparation)
3. [Étanchéité](#etancheite)
4. [Carrelage](#carrelage)
5. [Plomberie](#plomberie)
6. [Électricité](#electricite)
7. [Finitions](#finitions)
8. [Contrôle Qualité](#controle)
9. [Checklist Finale](#checklist)

---

## 1. Introduction {#introduction}

Ce guide compile les meilleures pratiques pour la rénovation de salles de bain selon les normes DTU françaises. Il s'appuie sur l'analyse de 94 images de chantier documentant 204 défauts réels.

### Principes Fondamentaux

✅ **Toujours respecter les DTU applicables**
✅ **Préparer correctement les supports avant pose**
✅ **Assurer l'étanchéité en priorité**
✅ **Documenter chaque étape avec photos**
✅ **Faire valider par un tiers si doute**

---

## 2. Préparation du Support {#preparation}

### Règles DTU 25.41 & 52.2

Le support doit être :
- **Propre** : Exempt de poussière, graisse, peinture écaillée
- **Sain** : Pas d'humidité résiduelle, moisissures éliminées
- **Stable** : Aucune partie friable ou mobile
- **Plan** : Écart max 5mm sous règle de 2m

### Procédure Recommandée

1. **Diagnostic Initial**
   - Mesurer l'humidité (< 3% pour pose carrelage)
   - Tester la cohésion (grattage, tape test)
   - Vérifier la planéité

2. **Nettoyage**
   - Aspiration poussière
   - Dégraissage si nécessaire
   - Décapage zones dégradées

3. **Réparation**
   - Reboucher fissures et trous
   - Ragréage si planéité insuffisante
   - Temps de séchage: minimum 7 jours

4. **Primaire d'Accrochage**
   - Appliquer primaire adapté au support
   - Respecter temps de séchage (généralement 24h)

### ⚠️ Erreurs Fréquentes Observées

| Défaut | Conséquence | Photo Ref |
|--------|-------------|-----------|
| Support humide non séché | Décollement carrelage | 0001, 0009 |
| Peinture non décapée | Perte d'adhérence | 0001, 0002 |
| Planéité non corrigée | Carrelage désaligné | 2401-2405 |

---

## 3. Étanchéité {#etancheite}

### DTU 52.2 - Article 4 : Étanchéité des Locaux Humides

#### Zones à Traiter OBLIGATOIREMENT

**Volume 0** (dans douche/baignoire) :
- Membrane continue sur 2m de hauteur minimum
- Remontée en plinthe de 10cm minimum

**Volume 1** (proche douche) :
- Membrane jusqu'à 1,20m de hauteur
- Protection des angles par bandes d'étanchéité

**Zones à risque** :
- Passage de canalisations
- Angles mur/sol et mur/mur
- Seuils de porte

#### Systèmes Recommandés

**Option A - Membrane Liquide** (ex: SPEC, Schlüter)
- Avantages: Application facile, continuité garantie
- Inconvénients: Sensible à l'application, nécessite 2-3 couches
- Séchage: 24h entre couches, 48h avant pose carrelage

**Option B - Membrane en Rouleau** (ex: Schlüter-KERDI)
- Avantages: Robuste, mise en œuvre rapide
- Inconvénients: Recouvrement précis nécessaire, découpes complexes
- Pose: Colle spéciale, recouvrements 5cm minimum

#### Mise en Œuvre Étape par Étape

1. **Préparation**
   - Support propre et primé
   - Bandes d'angle pré-posées

2. **Application Membrane**
   - Commencer par le bas
   - Respecter épaisseur prescrite (1-2mm pour liquide)
   - Recouvrement min 5cm pour rouleaux

3. **Renforcement Angles**
   - Bande périphérique 12cm
   - Enrobage complet dans la membrane

4. **Contrôle**
   - Test d'étanchéité (remplissage si receveur)
   - Vérification visuelle (continuité, bulles)

### ⚠️ Défauts Critiques Identifiés

| Image | Défaut | Gravité | Action |
|-------|--------|---------|--------|
| 2101 | Membrane déchirée | 🔴 CRITIQUE | Refaire totalement |
| 2004, 2005 | Infiltration sous-meuble | 🟠 MAJEUR | Identifier source + refaire |

---

## 4. Carrelage {#carrelage}

### DTU 52.2 - Pose en Locaux Humides

#### Choix du Carrelage

**Critères Obligatoires** :
- Classement PEI minimum III (sol) / II (mur)
- Porosité adaptée (E < 3% pour sol)
- Format compatible avec la surface

**Formats Recommandés SDB** :
- Sol: 30x30 à 60x60 cm
- Mur: 20x20 à 30x60 cm
- Éviter grands formats (>60cm) si support ancien

#### Colle et Joints

**Colle à Carrelage** (DTU 52.2 - Partie 1-1, §5.4) :
- Type C2 minimum (améliorée)
- Flexibilité S1 ou S2 si plancher chauffant ou structure bois
- Étiquette: "Colle C2S1" ou "C2S2"

**Mortier de Jointement** :
- Joints ciment: CG2 (amélioré) pour sol
- Joints époxy: RG (zones très exposées à l'eau)
- Largeur joints: 2-10mm selon format

#### Technique de Pose

1. **Traçage**
   - Partir du centre ou d'un mur de référence
   - Prévoir coupes égales sur côtés opposés
   - Éviter coupes < 5cm

2. **Encollage**
   - Double encollage obligatoire (support + carrelage)
   - Peigne adapté au format (8-10mm standard)
   - Respecter temps ouvert colle (15-30min)

3. **Pose**
   - Battre le carreau (maillet caoutchouc)
   - Vérifier planéité au fur et à mesure
   - Croisillons pour régularité joints

4. **Jointoiement**
   - Attendre 24-48h minimum
   - Nettoyer joints avant application
   - Lisser à l'éponge humide

### ⚠️ Défauts de Pose Recensés

| Type Défaut | Images | Cause Probable | Correction |
|-------------|--------|----------------|------------|
| Désalignement | 2401-2405 | Croisillons absents, colle irrégulière | Dépose + repose |
| Joints irréguliers | 2301-2312 | Application bâclée | Grattage + refection |
| Planéité | 2401 | Support non ragréé | Refaire ragréage + pose |

---

## 5. Plomberie {#plomberie}

### DTU 60.1 - Plomberie Sanitaire

#### Matériaux et Raccordements

**Tuyauterie** :
- Cuivre: Brasure forte ou raccords à compression
- PER: Raccords à glissement ou sertissage
- PVC évacuation: Diamètre ≥ 40mm

**Interdictions** :
- ❌ Raccords push-fit en zone encastrée
- ❌ Mélange cuivre/acier galvanisé (corrosion)
- ❌ PVC rigide sans dilatation

#### Mise en Œuvre

1. **Alimentation Eau**
   - Pente ascendante 5mm/m (purge d'air)
   - Robinets d'arrêt accessibles
   - Colliers fixes tous les 0,80m

2. **Évacuation**
   - Pente descendante 1-3cm/m
   - Siphons avec garde d'eau 50mm mini
   - Évent si longueur > 5m

3. **Essais**
   - Pression 1,5x pression service (généralement 6 bar)
   - Maintien 1h minimum
   - Aucune chute = OK

### ⚠️ Défauts Plomberie Observés

| Image | Défaut | Risque | Solution |
|-------|--------|--------|----------|
| 2101-2109 | Corrosion raccords | 🔴 Fuite imminente | Remplacement complet |
| 2102, 2108 | Évacuation mal fixée | 🟠 Déformation + fuite | Ajout colliers |
| 2103-2107 | Siphon sans garde d'eau | 🟡 Odeurs | Vérification + remplacement |

---

## 6. Électricité {#electricite}

### NF C 15-100 - Volumes Salle de Bain

#### Définition des Volumes

**Volume 0** : Intérieur baignoire/receveur
- Appareils: Aucun autorisé (sauf TBTS 12V)
- Protection: IPX7

**Volume 1** : Au-dessus volume 0 jusqu'à 2,25m
- Appareils: Chauffe-eau instantané IPX5
- Éclairage: IPX5 (classe II ou TBTS)

**Volume 2** : 60cm autour volume 1
- Appareils: Luminaires, extracteur IPX4
- Prises: Interdites (sauf rasoir TBTS)

**Hors volumes** : > 60cm du volume 2
- Appareils: Standards IP21
- Prises: 16A avec protection 30mA

#### Installation Conforme

1. **Protections**
   - Interrupteur différentiel 30mA (obligatoire)
   - Disjoncteur divisionnaire par circuit
   - Liaisons équipotentielles (baignoire métal, tuyaux)

2. **Câblage**
   - Section mini: 1,5mm² (éclairage), 2,5mm² (prises)
   - Gaines ICTA ou passage en encastré
   - Boîtes de dérivation hors volumes ou étanches

3. **Mise à la Terre**
   - Obligatoire sur tous les circuits
   - Résistance < 100Ω
   - Borne visible dans tableau

### ⚠️ Violations Électriques Détectées

| Image | Défaut | Gravité | Conformité |
|-------|--------|---------|------------|
| 2304 | Interrupteur/prise en volume | 🔴 CRITIQUE | ❌ NF C 15-100 |
| 2505, 2506 | Spot sans IP adapté | 🟠 MAJEUR | ⚠️ Vérifier IP |

---

## 7. Finitions {#finitions}

### Joints Silicone

**Zones d'Application** :
- Jonction carrelage/baignoire
- Jonction carrelage/vasque
- Angles douche/receveur

**Technique** :
1. Support propre et sec
2. Ruban de masquage
3. Application en un seul passage
4. Lissage immédiat (doigt savonneux)
5. Retrait masquage avant séchage

**Entretien** :
- Renouveler tous les 2-3 ans
- Gratter ancien joint complètement
- Désinfecter avant nouvelle pose

### Baguettes et Finitions

- Utiliser profils PVC ou aluminium anodisé
- Coller/visser selon DTU 59.1
- Joints néoprène aux jonctions

---

## 8. Contrôle Qualité {#controle}

### Points de Contrôle par Phase

**Après Préparation Support** :
- [ ] Planéité vérifiée (règle 2m, écart < 5mm)
- [ ] Humidité mesurée (< 3%)
- [ ] Surface propre et primée

**Après Étanchéité** :
- [ ] Test d'eau 24h (si receveur)
- [ ] Vérification visuelle continuité
- [ ] Bandes d'angle bien enrobées

**Après Pose Carrelage** :
- [ ] Alignement vérifié (fils tendus)
- [ ] Aucun carreau sonne creux
- [ ] Joints réguliers

**Après Plomberie** :
- [ ] Essai pression 6 bar pendant 1h
- [ ] Aucune fuite visible
- [ ] Évacuations testées (eau)

**Avant Réception** :
- [ ] Électricité testée (multimètre)
- [ ] Ventilation fonctionnelle
- [ ] Joints silicone propres

---

## 9. Checklist Finale {#checklist}

### Liste de Vérification Complète

#### Structure et Supports
- [ ] Murs sains et stables
- [ ] Plancher niveau et rigide
- [ ] Ventilation efficace (naturelle ou VMC)
- [ ] Éclairage naturel ou artificiel suffisant

#### Étanchéité
- [ ] Membrane continue sans déchirure
- [ ] Angles renforcés
- [ ] Remontées en plinthe conformes
- [ ] Test d'étanchéité réussi

#### Carrelage
- [ ] Carreaux adhérents (aucun son creux)
- [ ] Alignement et planéité corrects
- [ ] Joints remplis uniformément
- [ ] Coupes propres et régulières

#### Plomberie
- [ ] Aucune fuite détectée
- [ ] Pressions correctes (chaud/froid)
- [ ] Évacuations fluides sans stagnation
- [ ] Siphons en place avec garde d'eau

#### Électricité
- [ ] Tous circuits protégés 30mA
- [ ] Volumes respectés
- [ ] Appareils IP conforme
- [ ] Éclairage fonctionnel

#### Finitions
- [ ] Joints silicone lisses et continus
- [ ] Baguettes bien fixées
- [ ] Peinture/enduit sans défaut
- [ ] Nettoyage final effectué

---

## Annexes

### Références DTU Essentielles

- **DTU 25.41** : Ouvrages en plaques de plâtre - Plafonds suspendus
- **DTU 52.2** : Pose collée des revêtements céramiques et assimilés
- **DTU 60.1** : Plomberie sanitaire pour bâtiments à usage d'habitation
- **DTU 60.33** : Mise en œuvre des éléments d'installations électriques dans les locaux d'habitation
- **NF C 15-100** : Installations électriques basse tension

### Contact et Support

Pour toute question sur ce guide :
- Documentation complète : `VISION_BOOST_PRO_ANALYSIS_REPORT.md`
- Catalogue images : `training_catalog.html`
- Base de données : `training_catalog_database.json`

---

**Document généré par ArBot Vision Boost Pro Plus**
*Version 1.0.0 - Novembre 2025*
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(guide)

    print(f"[OK] Best practices guide generated: {output_path}")

def main():
    """Main execution."""
    print("=== Professional Training Catalog Builder ===\n")

    # Load data
    print("[1/6] Loading databases...")
    with open('json/images_db.json', 'r', encoding='utf-8') as f:
        images_db = json.load(f)

    with open('pipeline_output/def_all.json', 'r', encoding='utf-8') as f:
        defects_db = json.load(f)

    print(f"  ✓ Loaded {images_db['count']} images")
    print(f"  ✓ Loaded {len(defects_db.get('DEF_ALL', defects_db.get('defects', [])))} defects")

    # Generate training database
    print("\n[2/6] Analyzing and categorizing images...")
    training_db = generate_training_database(images_db, defects_db)
    print(f"  ✓ {training_db['meta']['selected_examples']} images selected for training")
    print(f"  ✓ {len(training_db['categories'])} categories populated")

    # Create output directory
    output_dir = Path("training_catalog")
    output_dir.mkdir(exist_ok=True)

    # Save training database
    print("\n[3/6] Saving training database...")
    db_path = output_dir / "training_catalog_database.json"
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(training_db, f, ensure_ascii=False, indent=2)
    print(f"  ✓ Database saved: {db_path}")

    # Generate HTML catalog
    print("\n[4/6] Generating interactive HTML catalog...")
    html_path = output_dir / "training_catalog.html"
    generate_html_catalog(training_db, str(html_path))
    print(f"  ✓ Catalog saved: {html_path}")

    # Generate best practices guide
    print("\n[5/6] Creating best practices guide...")
    guide_path = output_dir / "BEST_PRACTICES_GUIDE.md"
    generate_best_practices_guide(str(guide_path))
    print(f"  ✓ Guide saved: {guide_path}")

    # Print summary
    print("\n[6/6] Generation complete! 📚\n")
    print("=" * 60)
    print("CATALOG SUMMARY")
    print("=" * 60)
    print(f"Total images analyzed:     {training_db['meta']['total_images']}")
    print(f"Training examples selected: {training_db['meta']['selected_examples']}")
    print(f"Defect categories:         {training_db['meta']['defect_categories']}")
    print(f"\nOutput directory: {output_dir.absolute()}/")
    print("\nGenerated files:")
    print(f"  1. training_catalog_database.json  - Structured data")
    print(f"  2. training_catalog.html           - Interactive catalog")
    print(f"  3. BEST_PRACTICES_GUIDE.md         - Complete guide")
    print("\n" + "=" * 60)

    # Statistics breakdown
    print("\nIMAGES BY CATEGORY:")
    for cat, count in training_db['statistics']['selected_by_category'].items():
        if cat not in ['OVERVIEW', 'AUTRES']:
            print(f"  {cat:20s}: {count:2d} images")

    print("\nIMAGES BY VIEW TYPE:")
    for view, count in sorted(training_db['statistics']['images_by_view_type'].items(),
                              key=lambda x: x[1], reverse=True):
        print(f"  {view:5s}: {count:2d} images")

    print(f"\nPhase distribution:")
    for phase, count in training_db['statistics']['images_by_phase'].items():
        print(f"  {phase:10s}: {count:2d} images")

    print("\n✅ Catalog ready for professional training use!")

if __name__ == "__main__":
    main()
