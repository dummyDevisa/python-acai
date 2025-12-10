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

    df = pd.read_excel(EXCEL_FILE)
    
    # --- Analytics ---
    total_records = len(df)
    unique_bairros = df['Bairro'].nunique() if 'Bairro' in df.columns else 0
    unique_ceps = df['CEP'].nunique() if 'CEP' in df.columns else 0

    # Chart Data
    if 'Bairro' in df.columns:
        bairros_counts = df['Bairro'].value_counts().head(15)
        # Drop None/NaN if present in index
        bairros_counts = bairros_counts[bairros_counts.index.notnull()]
        chart_bairros_labels = bairros_counts.index.tolist()
        chart_bairros_data = bairros_counts.values.tolist()
    else:
        chart_bairros_labels = []
        chart_bairros_data = []

    quality_labels = ['Com Logradouro', 'Com Bairro', 'Com Número', 'Com CEP']
    quality_data = []
    for col in ['Logradouro', 'Bairro', 'Número', 'CEP']:
        if col in df.columns:
            count = df[col].notnull().sum()
            quality_data.append(int(count))
        else:
            quality_data.append(0)

    # Convert to HTML Table
    table_html = df.to_html(classes="table table-striped table-hover", index=False, border=0, table_id="dataTable")

    # 3. Build Full HTML
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
        }}
        #map {{
            height: 600px; /* Good height for desktop */
            width: 100%;
        }}
        @media (max-width: 768px) {{
             #map {{ height: 450px; }}
        }}
        
        /* Custom Map Popup */
        .custom-popup .leaflet-popup-content-wrapper {{
            border-radius: 8px;
            padding: 5px;
        }}
        .custom-popup .leaflet-popup-content {{
            margin: 10px;
            line-height: 1.5;
        }}
        .popup-title {{
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 5px;
            color: #333;
        }}
        .popup-info {{
            margin-bottom: 3px;
        }}

        /* Dashboard Cards */
        .kpi-card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            height: 100%;
            border-left: 5px solid #6f42c1;
            transition: transform 0.2s;
        }}
        .kpi-card:hover {{
            transform: translateY(-5px);
        }}
        .kpi-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #6f42c1;
        }}
        .kpi-label {{
            color: #6c757d;
            font-weight: 500;
            text-transform: uppercase;
            font-size: 0.85em;
        }}
        
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }}

        /* Table Styling */
        .table-responsive {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        #dataTable th {{
            background-color: #6f42c1;
            color: white;
            border-bottom: none;
        }}
        #dataTable th, #dataTable td {{
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 180px; 
            vertical-align: middle;
        }}

        footer {{
            text-align: center;
            margin-top: 50px;
            padding-bottom: 20px;
            color: #6c757d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>

    <!-- Header / Report Section -->
    <div class="report-header">
        <div class="report-container">
             <div class="markdown-body">
                {html_content}
             </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="report-container">
        
        <!-- KPIs -->
        <div class="row mb-4 g-3">
            <div class="col-md-4">
                <div class="kpi-card">
                    <div class="kpi-value">{total_records}</div>
                    <div class="kpi-label">Pontos Mapeados</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="kpi-card">
                    <div class="kpi-value">{unique_bairros}</div>
                    <div class="kpi-label">Bairros Atendidos</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="kpi-card">
                    <div class="kpi-value">{int((unique_bairros/71)*100)}%</div> <!-- Belém has approx 71 neighborhoods -->
                    <div class="kpi-label">Cobertura Estimada (Bairros)</div>
                </div>
            </div>
        </div>

        <!-- Geographic Map Section -->
        <div id="map-container">
            <h4 class="p-3 bg-white m-0 border-bottom">Mapa de Dispersão Espacial</h4>
            <div id="map"></div>
        </div>

        <!-- Charts Row -->
        <div class="row mb-2">
            <!-- Chart 1: Top Bairros -->
            <div class="col-lg-8">
                <div class="chart-container">
                    <h5 class="text-center mb-3">Top 15 Bairros com Mais Pontos</h5>
                    <canvas id="chartBairros" height="300"></canvas>
                </div>
            </div>
             <!-- Chart 2: Data Quality -->
            <div class="col-lg-4">
                <div class="chart-container">
                    <h5 class="text-center mb-3">Qualidade dos Endereços</h5>
                    <div style="position: relative; height: 300px;">
                        <canvas id="chartQuality"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- Data Table -->
        <div class="table-responsive">
            <h3 class="mb-4">Base de Dados Detalhada</h3>
            {table_html}
        </div>
    </div>

    <footer>
        <p>Gerado via Python - Projeto Açaí no Ponto &copy; 2025</p>
    </footer>

    <!-- Scripts -->
    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <!-- Leaflet JS -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
    
    <!-- DataTables -->
    <script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.4/js/dataTables.bootstrap5.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.3.6/js/dataTables.buttons.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.3.6/js/buttons.bootstrap5.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.3.6/js/buttons.html5.min.js"></script>
    
    <!-- Load Map Data -->
    <script src="data.js"></script>

    <script>
        // --- CHARTS LOGIC ---
        const bairrosLabels = {json.dumps(chart_bairros_labels)};
        const bairrosData = {json.dumps(chart_bairros_data)};
        const qualityLabels = {json.dumps(quality_labels)};
        const qualityData = {json.dumps(quality_data)};

        // Bairros
        const ctxBairros = document.getElementById('chartBairros').getContext('2d');
        new Chart(ctxBairros, {{
            type: 'bar',
            data: {{
                labels: bairrosLabels,
                datasets: [{{
                    label: 'Pontos de Venda',
                    data: bairrosData,
                    backgroundColor: 'rgba(111, 66, 193, 0.7)',
                    borderColor: 'rgba(111, 66, 193, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                scales: {{ x: {{ beginAtZero: true }} }},
                plugins: {{ legend: {{ display: false }} }}
            }}
        }});

        // Quality
        const ctxQuality = document.getElementById('chartQuality').getContext('2d');
        new Chart(ctxQuality, {{
            type: 'polarArea',
            data: {{
                labels: qualityLabels,
                datasets: [{{
                    data: qualityData,
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(255, 205, 86, 0.6)',
                        'rgba(255, 99, 132, 0.6)'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'bottom' }}
                }}
            }}
        }});
        
        // --- DATA TABLE LOGIC ---
        $(document).ready(function () {{
            $('#dataTable').DataTable({{
                "language": {{ "url": "//cdn.datatables.net/plug-ins/1.13.4/i18n/pt-BR.json" }},
                "pageLength": 10,
                "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
                "scrollX": true,
                "dom": 'Bfrtip',
                "buttons": [
                    {{
                        extend: 'excelHtml5',
                        text: '📥 Exportar Excel',
                        className: 'btn btn-success btn-sm',
                        title: 'Relatorio_Acai_Enderecos'
                    }}
                ]
            }});
        }});

        // --- MAP LOGIC (Copied from User's Implementation) ---
        // Initialize Map
        const map = L.map('map').setView([-1.455, -48.49], 12);
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 19,
            attribution: '© OpenStreetMap contributors'
        }}).addTo(map);

        function getColor(d) {{
            return d === 'DAENT' ? '#1f77b4' : 
                   d === 'DAGUA' ? '#17becf' : 
                   d === 'DASAC' ? '#ff7f0e' :
                   d === 'DAICO' ? '#2ca02c' : 
                   d === 'DABEL' ? '#d62728' : 
                   d === 'DABEN' ? '#9467bd' :
                   d === 'DAOUT' ? '#bcbd22' : 
                   d === 'DAMOS' ? '#e377c2' : '#7f7f7f';
        }}

        function createPopupContent(properties) {{
            const district = properties["Qual o distrito de saúde?"] || "Não informado";
            const color = getColor(district);
            let content = `<div class="popup-title" style="color: ${{color}}">${{properties["Nome do ponto de venda ou do proprietário"] || "Ponto de Açaí"}}</div>`;
            if (properties["Nome do profissional de saúde"]) content += `<div class="popup-info"><strong>Profissional:</strong> ${{properties["Nome do profissional de saúde"]}}</div>`;
            if (properties["Telefone de contato"]) content += `<div class="popup-info"><strong>Telefone:</strong> ${{properties["Telefone de contato"]}}</div>`;
            content += `<div class="popup-info"><strong>Distrito:</strong> ${{district}}</div>`;
            if (properties["_submission_time"]) {{
                const date = new Date(properties["_submission_time"]).toLocaleDateString('pt-BR');
                content += `<div class="popup-info"><strong>Data:</strong> ${{date}}</div>`;
            }}
            return content;
        }}

        // Render GeoJSON
        if (window.mapData && Array.isArray(window.mapData)) {{
            const districts = ['DAENT', 'DAGUA', 'DASAC', 'DAICO', 'DABEL', 'DABEN', 'DAOUT', 'DAMOS'];
            const layers = {{}};

            districts.forEach(d => {{ layers[d] = L.featureGroup().addTo(map); }});
            layers['Outros'] = L.featureGroup().addTo(map);

            window.mapData.forEach(featureCollection => {{
                if (!featureCollection.features) return;
                featureCollection.features.forEach(feature => {{
                    if (!feature.geometry || !feature.geometry.coordinates) return;
                    
                    const district = feature.properties["Qual o distrito de saúde?"];
                    const targetLayer = (districts.includes(district)) ? layers[district] : layers['Outros'];
                    
                    // Coordinates in GeoJSON are often [long, lat], but circleMarker expects [lat, long]??
                    // Wait, Leaflet L.geoJSON handles projection. But L.circleMarker takes [lat, lng].
                    // Logic from maps.html: const latlng = [feature.geometry.coordinates[1], feature.geometry.coordinates[0]];
                    // Correct!
                    const latlng = [feature.geometry.coordinates[1], feature.geometry.coordinates[0]];
                    
                    const marker = L.circleMarker(latlng, {{
                        radius: 6, // Slightly smaller for report density
                        fillColor: getColor(district), 
                        color: "#fff",
                        weight: 1, 
                        opacity: 1, 
                        fillOpacity: 0.8
                    }});
                    
                    if (feature.properties) {{
                        marker.bindPopup(createPopupContent(feature.properties), {{ className: 'custom-popup' }});
                    }}
                    marker.addTo(targetLayer);
                }});
            }});

            // Legend / Layer Control
            const overlays = {{}};
            districts.forEach(d => {{
                const color = getColor(d);
                const label = `<i style="background: ${{color}}; width: 12px; height: 12px; display: inline-block; border-radius: 50%; margin-right: 5px; vertical-align: middle;"></i> ${{d}}`;
                overlays[label] = layers[d];
            }});
            const colorOutros = getColor('Outros');
            const labelOutros = `<i style="background: ${{colorOutros}}; width: 12px; height: 12px; display: inline-block; border-radius: 50%; margin-right: 5px; vertical-align: middle;"></i> Outros`;
            overlays[labelOutros] = layers['Outros'];

            L.control.layers(null, overlays, {{ collapsed: false, position: 'bottomright' }}).addTo(map);

            // Fit Bounds
            const allLayers = L.featureGroup(Object.values(layers));
            if (allLayers.getLayers().length > 0) {{
                // pad to avoid cutting off markers
                map.fitBounds(allLayers.getBounds(), {{padding: [50, 50]}}); 
            }}
        }} else {{
            console.error("Dados do mapa não encontrados em window.mapData");
        }}
    </script>
</body>
</html>
    """

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"Successfully generated {OUTPUT_HTML} with Map + Analytics.")

if __name__ == "__main__":
    generate_html()
