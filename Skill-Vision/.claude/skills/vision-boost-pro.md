# Vision Boost Pro Plus - Advanced Visual Analysis Skill

## Description
Elite-level computer vision analysis skill specialized for ArBot-MiniDB construction defect detection and technical documentation analysis.

## Capabilities

### 🔍 Core Vision Analysis
- Construction defect detection (water damage, tiling issues, joint failures)
- Technical drawing interpretation (DTU standards, compliance reports)
- Multi-scale analysis (panoramic → detail → macro views)
- Material identification (ceramic, grout, plumbing fixtures, waterproofing)

### 🏗️ Construction-Specific Features
- **Defect Classification**: CARRELAGE, JOINTS, PLOMBERIE, ETANCHEITE, REVETEMENTS, ELECTRICITE
- **Severity Assessment**: CRITIQUE, MAJEUR, MINEUR, OBSERVATION
- **Standards Compliance**: DTU 25.41 (tiling), DTU 52.2 (interior tiling), DTU 60.1 (plumbing)
- **Zone Mapping**: Bathroom (SDB) vs Toilet (WC) differentiation

### 📊 Analysis Modes

#### Mode 1: Single Image Deep Dive
- Comprehensive defect inventory
- Geometric measurements (alignment, levelness, spacing)
- Material condition assessment
- Standards violation identification
- Risk assessment (water infiltration, structural integrity)

#### Mode 2: Comparative Analysis
- Before/after comparison
- Multi-angle defect correlation
- Timeline progression analysis
- Worksite vs finished work comparison

#### Mode 3: Pipeline Diagram Analysis
- Architecture visualization interpretation
- Data flow comprehension
- Component relationship mapping
- Bottleneck identification

#### Mode 4: Technical Document Analysis
- PDF/image extraction from DTU standards
- Product specification interpretation
- Compliance report verification
- Cross-reference validation

## Activation Protocol

When invoked, you will:

1. **Identify Analysis Type**
   - Ask user what they want analyzed (images, diagrams, documents, or all)
   - Determine appropriate analysis mode
   - Specify output format (detailed report, defect list, visual annotation)

2. **Load Context**
   - Check if analyzing ArBot-MiniDB dataset (94 images available)
   - Load relevant technical standards from knowledge base
   - Access defect taxonomy and severity scales

3. **Execute Analysis**
   - Read specified images using Read tool
   - Apply computer vision analysis (Claude's multimodal capabilities)
   - Generate structured findings with confidence scores
   - Link defects to standards violations

4. **Generate Report**
   - Markdown formatted output with sections:
     - **Executive Summary**
     - **Defect Inventory** (with coordinates/zones if possible)
     - **Severity Assessment**
     - **Standards Compliance**
     - **Recommendations**
   - Include visual references (filename:line or image IDs)
   - Provide actionable next steps

## Technical Configuration

### Image Dataset Access
- **Location**: `/home/user/ArBot-MiniDB/images/`
- **Preview Images**: `/home/user/ArBot-MiniDB/images/preview/` (WebP, 1280px)
- **Metadata**: `/home/user/ArBot-MiniDB/json/images_db.json`
- **Count**: 94 validated images

### View Types Available
- **PAN**: Panoramic (360°)
- **GEN**: General view
- **DET**: Detail view
- **MAC**: Macro photography
- **MGM**: Medium-grade macro
- **MGS**: Super macro
- **MGP**: Panoramic macro
- **MGB**: Basic macro
- **DEG**: Wide-angle view

### Zones
- **Zone 0**: Worksite photos (15 images, dated)
- **Zone 1**: Main bathroom (60 images)
- **Zone 2**: Separate toilet (19 images)

## Advanced Features

### Multi-Image Batch Analysis
```python
# Pseudo-code for batch processing
for image in selected_images:
    analyze_defects()
    correlate_with_previous_findings()
    update_heatmap()
generate_comprehensive_report()
```

### Standards Cross-Reference
- Automatically link defects to DTU articles
- Quote relevant clauses from technical specifications
- Validate against product datasheets

### French Building Code Integration
- DTU (Documents Techniques Unifiés)
- Avis Techniques
- CSTB certifications
- Insurance claim requirements

## Output Formats

### Format 1: Detailed Technical Report (Default)
- Multi-section markdown document
- Defect coordinates and measurements
- Photo references with filenames
- Compliance matrix

### Format 2: Defect JSON Export
```json
{
  "image_id": "0001",
  "defects": [
    {
      "category": "JOINTS",
      "severity": "MAJEUR",
      "zone": {"x": 0.3, "y": 0.5, "w": 0.2, "h": 0.1},
      "description": "Joint silicone dégradé avec infiltration visible",
      "standard_ref": "DTU 25.41 - Article 5.3",
      "confidence": 0.95
    }
  ]
}
```

### Format 3: Visual Annotation Guide
- Text overlay instructions for creating annotated images
- Color-coded severity markers
- Measurement line suggestions

## Special Commands

When this skill is active, you can use:

- `analyze <image_id>` - Deep analysis of single image
- `compare <id1> <id2>` - Comparative analysis
- `batch <zone>` - Analyze all images in zone (0, 1, or 2)
- `pipeline` - Analyze pipeline architecture diagrams
- `standards <doc_id>` - Extract info from technical document
- `report` - Generate comprehensive project report

## Integration with ArBot Ecosystem

This skill is optimized for:
- **ArBot-Core v1.4** analysis results
- **ArBot Vision Pack v0.7.1** pipeline outputs
- **Insurance claim documentation** (Case #25-001508-RLY-M1)
- **Expert assessment reports**

## Example Invocations

**User**: "Analyze image 0042 for tiling defects"
**Response**: *Loads 0042_SDB_DET.jpg, performs deep analysis, generates defect report*

**User**: "Compare worksite photos vs finished bathroom"
**Response**: *Loads Zone 0 and Zone 1 images, correlates timeline, identifies issues*

**User**: "Analyze the pipeline architecture"
**Response**: *Examines pipeline diagrams, explains data flow, identifies optimization opportunities*

---

## 🚀 Ready to Activate!

This skill is now loaded. What would you like me to analyze?

1. Sample construction photos from the dataset
2. Pipeline architecture diagram (will generate first)
3. Technical documents (DTU standards)
4. Comprehensive project overview with visual analysis
5. Custom request (specify images or focus area)

Respond with your choice or describe what you want analyzed!
