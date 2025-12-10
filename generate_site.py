import pandas as pd
import markdown
import os
import json

# Configuration
MARKDOWN_FILE = 'Relatorio_Projeto_Acai.md'
EXCEL_FILE = 'output_enderecos_tratado.xlsx'
OUTPUT_HTML = 'index.html'

def generate_html():
    # 1. Read and Convert Markdown
    if not os.path.exists(MARKDOWN_FILE):
        print(f"Error: {MARKDOWN_FILE} not found.")
        return
    
    with open(MARKDOWN_FILE, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    html_content = markdown.markdown(md_content, extensions=['tables'])

    # 2. Read Data
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found.")
        return

    # Read Excel and fill NaN to avoid JSON errors
    df = pd.read_excel(EXCEL_FILE).fillna('')
    
    # --- Prepare Data for Charts ---
    total_records = len(df)
    unique_bairros = df['Bairro'].nunique() if 'Bairro' in df.columns else 0
    unique_ceps = df['CEP'].nunique() if 'CEP' in df.columns else 0 # Fixed variable name usage in previous script

    # Chart Data
    if 'Bairro' in df.columns:
        # Filter out empty strings if any
        bairros_counts = df[df['Bairro'] != '']['Bairro'].value_counts().head(15)
        chart_bairros_labels = bairros_counts.index.tolist()
        chart_bairros_data = bairros_counts.values.tolist()
    else:
        chart_bairros_labels = []
        chart_bairros_data = []

    quality_labels = ['Com Logradouro', 'Com Bairro', 'Com Número', 'Com CEP']
    quality_data = []
    for col in ['Logradouro', 'Bairro', 'Número', 'CEP']:
        if col in df.columns:
            # Count non-empty strings
            count = df[df[col] != ''].shape[0]
            quality_data.append(int(count))
        else:
            quality_data.append(0)

    # --- Optimize Table Data Handover ---
    # Instead of generating huge HTML string, we pass JSON to DataTable (Client-side rendering)
    # Select columns to display. Let's keep it informative but not overwhelming.
    # User likely wants: Nome (N), Telefone, Endereço Tratado (Logradouro, Numero, Bairro, Municipio)
    
    # We need to map dataframe columns to list of dicts
    # Let's inspect columns to handle them dynamically or fixed?
    # Fixed is safer for DataTables definition.
    
    # Expected columns based on previous steps:
    # 'Nome do ponto...', 'Telefone...', 'Logradouro', 'Número', 'Bairro', 'Município'
    # Let's try to find them loosely
    
    cols_to_keep = []
    # Find Name
    name_col = next((c for c in df.columns if 'Nome do ponto' in c), None)
    phone_col = next((c for c in df.columns if 'Telefone' in c), None)
    
    if name_col: cols_to_keep.append(name_col)
    if phone_col: cols_to_keep.append(phone_col)
    
    # Address parts
    addr_cols = ['Logradouro', 'Número', 'Bairro', 'Município', 'CEP']
    for c in addr_cols:
        if c in df.columns:
            cols_to_keep.append(c)
            
    # Fallback if specific columns missing, just take first 10
    if not cols_to_keep:
        cols_to_keep = df.columns[:8].tolist()
        
    # Create the lightweight subset for JSON
    table_df = df[cols_to_keep]
    table_data_json = table_df.to_dict(orient='records')
    
    # Prepare Table Headers HTML
    thead_html = "<thead><tr>" + "".join([f"<th>{c}</th>" for c in cols_to_keep]) + "</tr></thead>"
    # JS Column definition
    columns_json = json.dumps([{"data": c, "title": c} for c in cols_to_keep])

    # 3. Build Full HTML
    # We remove {table_html} injection and use empty table with ID
    
    full_html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel Açaí no Ponto - Belém</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="" />
    
    <!-- DataTables CSS -->
    <link href="https://cdn.datatables.net/1.13.4/css/dataTables.bootstrap5.min.css" rel="stylesheet">
    <link href="https://cdn.datatables.net/buttons/2.3.6/css/buttons.bootstrap5.min.css" rel="stylesheet">
    
    <style>
        body {{
            background-color: #f8f9fa;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #333;
        }}
        .report-header {{
            background: white;
            padding: 40px 20px;
            margin-bottom: 30px;
            border-bottom: 4px solid #6f42c1;
        }}
        .report-container {{
            max_width: 1200px;
            margin: 0 auto;
            padding: 0 15px;
        }}
        .markdown-body {{
            max_width: 900px;
            margin: 0 auto;
        }}
        
        /* Map Styles */
        #map-container {{
            margin-bottom: 40px;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            position: relative;
            background: #e9ecef; /* Placeholder color before load */
        }}
        #map {{
            height: 500px; 
            width: 100%;
        }}
        
        .kpi-card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            height: 100%;
            border-left: 5px solid #6f42c1;
        }}
        .kpi-value {{
            font-size: 2.2em;
            font-weight: bold;
            color: #6f42c1;
        }}
        .kpi-label {{
            color: #6c757d;
            font-weight: 500;
            text-transform: uppercase;
            font-size: 0.8em;
        }}
        
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }}

        .table-responsive {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            min-height: 400px;
        }}
        
        footer {{
            text-align: center;
            margin-top: 50px;
            padding-bottom: 20px;
            color: #6c757d;
            font-size: 0.9em;
        }}

        /* Custom Popup */
        .popup-title {{ font-weight: bold; color: #333; }}
        .leaflet-popup-content {{ font-size: 0.9em; }}
    </style>
</head>
<body>

    <div class="report-header">
        <div class="report-container">
             <div class="markdown-body">
                {html_content}
             </div>
        </div>
    </div>

    <div class="report-container">
        
        <!-- KPIs -->
        <div class="row mb-4 g-3">
            <div class="col-6 col-md-4">
                <div class="kpi-card">
                    <div class="kpi-value">{total_records}</div>
                    <div class="kpi-label">Pontos</div>
                </div>
            </div>
            <div class="col-6 col-md-4">
                <div class="kpi-card">
                    <div class="kpi-value">{unique_bairros}</div>
                    <div class="kpi-label">Bairros</div>
                </div>
            </div>
            <div class="col-12 col-md-4">
                <div class="kpi-card">
                    <div class="kpi-value">{unique_ceps}</div>
                    <div class="kpi-label">CEPs</div>
                </div>
            </div>
        </div>

        <!-- Map Section -->
        <div id="map-container">
            <div id="map"></div>
        </div>

        <!-- Charts -->
        <div class="row mb-2">
            <div class="col-lg-8">
                <div class="chart-container">
                    <h5 class="text-center mb-3">Top Bairros</h5>
                    <canvas id="chartBairros" height="250"></canvas>
                </div>
            </div>
            <div class="col-lg-4">
                <div class="chart-container">
                    <h5 class="text-center mb-3">Qualidade</h5>
                    <div style="position: relative; height: 250px;">
                        <canvas id="chartQuality"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- Optimized Data Table -->
        <div class="table-responsive">
            <h3 class="mb-4">Base de Dados</h3>
            <table id="dataTable" class="table table-striped table-hover" style="width:100%">
                {thead_html}
            </table>
        </div>
    </div>

    <footer>
        <p>Projeto Açaí no Ponto - GDOC/VISA</p>
    </footer>

    <!-- Scripts -->
    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
    
    <!-- DataTables -->
    <script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.4/js/dataTables.bootstrap5.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.3.6/js/dataTables.buttons.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.3.6/js/buttons.bootstrap5.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.3.6/js/buttons.html5.min.js"></script>
    
    <!-- Map Data -->
    <script src="data.js"></script>

    <script>
        // --- 1. OPTIMIZED TABLE RENDER ---
        // Pass data as JSON object instead of raw HTML rows
        const tableData = {json.dumps(table_data_json)};
        const tableCols = {columns_json};

        $(document).ready(function () {{
            // Defer rendering slightly to allow UI to paint
            setTimeout(function() {{
                $('#dataTable').DataTable({{
                    data: tableData,
                    columns: tableCols,
                    language: {{ "url": "//cdn.datatables.net/plug-ins/1.13.4/i18n/pt-BR.json" }},
                    pageLength: 10,
                    lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
                    scrollX: true,
                    deferRender: true, // Critical for performance
                    dom: 'Bfrtip',
                    buttons: [
                         {{
                            extend: 'excelHtml5',
                            text: '📥 Excel',
                            className: 'btn btn-success btn-sm',
                            title: 'Acai_Dados'
                        }}
                    ]
                }});
            }}, 50);
        }});

        // --- 2. CHARTS ---
        const bairrosLabels = {json.dumps(chart_bairros_labels)};
        const bairrosData = {json.dumps(chart_bairros_data)};
        const qualityLabels = {json.dumps(quality_labels)};
        const qualityData = {json.dumps(quality_data)};

        if(document.getElementById('chartBairros')) {{
            new Chart(document.getElementById('chartBairros'), {{
                type: 'bar',
                data: {{
                    labels: bairrosLabels,
                    datasets: [{{
                        label: 'Qtd',
                        data: bairrosData,
                        backgroundColor: '#6f42c1',
                        barThickness: 15
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y',
                    plugins: {{ legend: {{ display: false }} }}
                }}
            }});
        }}

        if(document.getElementById('chartQuality')) {{
            new Chart(document.getElementById('chartQuality'), {{
                type: 'doughnut', /* Polar area is too heavy sometimes, Doughnut is cleaner */
                data: {{
                    labels: qualityLabels,
                    datasets: [{{
                        data: qualityData,
                        backgroundColor: ['#28a745', '#17a2b8', '#ffc107', '#dc3545']
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ position: 'right', labels: {{ boxWidth: 10 }} }} }}
                }}
            }});
        }}

        // --- 3. MAP LOGIC ---
        // Load map only if container exists
        if(document.getElementById('map')) {{
            const map = L.map('map', {{ preferCanvas: true }}).setView([-1.455, -48.49], 12);
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                maxZoom: 18,
                attribution: 'OpenStreetMap'
            }}).addTo(map);
            
            // Color Logic
            function getColor(d) {{
                const colors = {{
                    'DAENT': '#1f77b4', 'DAGUA': '#17becf', 'DASAC': '#ff7f0e',
                    'DAICO': '#2ca02c', 'DABEL': '#d62728', 'DABEN': '#9467bd',
                    'DAOUT': '#bcbd22', 'DAMOS': '#e377c2'
                }};
                return colors[d] || '#7f7f7f';
            }}

            // Add Data with Clustering or simple Canvas markers
            // We use simple iteration but ensure we don't block main thread too much if possible
            if (window.mapData && Array.isArray(window.mapData)) {{
                // Use a single FeatureGroup for performance or iterate
                // For 1700 points, L.circleMarker (SVG) is okay, but Canvas is better.
                // We set preferCanvas: true in map init above.
                
                // Let's create layer groups
                 const districts = ['DAENT', 'DAGUA', 'DASAC', 'DAICO', 'DABEL', 'DABEN', 'DAOUT', 'DAMOS'];
                 const layers = {{}};
                 districts.forEach(d => layers[d] = L.layerGroup()); // Use LayerGroup, lighter than FeatureGroup
                 layers['Outros'] = L.layerGroup();
                 
                 window.mapData.forEach(fc => {{
                     if(!fc.features) return;
                     fc.features.forEach(f => {{
                         if(!f.geometry || !f.geometry.coordinates) return;
                         const dist = f.properties["Qual o distrito de saúde?"];
                         const group = (districts.includes(dist)) ? layers[dist] : layers['Outros'];
                         
                         const lat = f.geometry.coordinates[1];
                         const lng = f.geometry.coordinates[0];
                         
                         // Create marker
                         L.circleMarker([lat, lng], {{
                             radius: 5,
                             fillColor: getColor(dist),
                             color: "#fff",
                             weight: 0.5,
                             opacity: 1,
                             fillOpacity: 0.8,
                             renderer: L.canvas() // Force canvas
                         }})
                         .bindPopup(`<b>${{f.properties["Nome do ponto de venda ou do proprietário"] || "Ponto"}}</b><br>${{f.properties["Nome do profissional de sa\u00fade"] || ""}}`)
                         .addTo(group);
                     }});
                 }});
                 
                 // Add to map
                 Object.values(layers).forEach(l => l.addTo(map));
                 
                 // Controls
                 const overlays = {{}};
                 districts.forEach(d => overlays[`<span style='color:${{getColor(d)}}'>■</span> ${{d}}`] = layers[d]);
                 overlays[`<span style='color:${{getColor('Outros')}}'>■</span> Outros`] = layers['Outros'];
                 
                 L.control.layers(null, overlays, {{collapsed: true}}).addTo(map);
            }}
        }}
    </script>
</body>
</html>
    """

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"Successfully generated Optimized {OUTPUT_HTML}")

if __name__ == "__main__":
    generate_html()
