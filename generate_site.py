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

    df = pd.read_excel(EXCEL_FILE).fillna('')
    
    # --- Analytics & Data Prep ---
    total_records = len(df)
    unique_bairros = df['Bairro'].nunique() if 'Bairro' in df.columns else 0
    unique_ceps = df['CEP'].nunique() if 'CEP' in df.columns else 0

    # Chart Data (Graphs are lightweight JSON, keeping them is usually fine, but user asked for Report + Table primarily)
    # I will keep the charts as they add value and are light (JS arrays).
    if 'Bairro' in df.columns:
        bairros_counts = df[df['Bairro'] != '']['Bairro'].value_counts().head(10)
        chart_bairros_labels = bairros_counts.index.tolist()
        chart_bairros_data = bairros_counts.values.tolist()
    else:
        chart_bairros_labels = []
        chart_bairros_data = []

    # --- JSON Table Data (Crucial for performance with large datasets) ---
    # We strip down columns to what is essential to reduce JSON size
    cols_to_keep = []
    
    # Priority columns
    potential_cols = [
        'Nome do ponto de venda ou do proprietário', 
        'Telefone de contato', 
        'Logradouro', 
        'Número', 
        'Bairro', 
        'Município',
        'CEP'
    ]
    
    for c in potential_cols:
        if c in df.columns:
            cols_to_keep.append(c)
    
    # Ensure we have something
    if not cols_to_keep:
        cols_to_keep = df.columns[:5].tolist()

    # Limit rows? The user has ~1700, passing 1700 rows in JSON is usually fine (<1MB).
    # If file size is massive, maybe truncate text?
    
    table_df = df[cols_to_keep].copy()
    
    # Truncate long text to save bytes? Not strictly necessary for 1700 rows, but good practice if description is huge.
    # Here fields are short addresses.
    
    table_data_json = table_df.to_dict(orient='records')
    columns_json = json.dumps([{"data": c, "title": c} for c in cols_to_keep])

    # 3. Build HTML
    full_html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório Açaí no Ponto</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
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
            line-height: 1.6;
        }}
        .markdown-body h1, .markdown-body h2 {{ color: #2c3e50; }}
        
        /* Stats Cards */
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            text-align: center;
            border-top: 3px solid #6f42c1;
        }}
        .stat-val {{ font-size: 2em; font-weight: bold; color: #6f42c1; }}
        .stat-lbl {{ color: #777; font-size: 0.9em; text-transform: uppercase; }}

        /* Chart */
        .chart-box {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }}

        /* Table */
        .table-box {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            margin-bottom: 40px;
        }}
        #dataTable th {{
            background-color: #6f42c1;
            color: white;
        }}
        #dataTable td {{
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 200px;
        }}
        
        footer {{
            text-align: center;
            padding: 30px;
            color: #888;
        }}
    </style>
</head>
<body>

    <!-- Report Text -->
    <div class="report-header">
        <div class="report-container">
             <div class="markdown-body">
                {html_content}
             </div>
        </div>
    </div>

    <!-- Dashboard & Data -->
    <div class="report-container">
        
        <!-- KPIs -->
        <div class="row">
            <div class="col-md-4">
                <div class="stat-card">
                    <div class="stat-val">{total_records}</div>
                    <div class="stat-lbl">Pontos Registrados</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="stat-card">
                    <div class="stat-val">{unique_bairros}</div>
                    <div class="stat-lbl">Bairros</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="stat-card">
                    <div class="stat-val">{unique_ceps}</div>
                    <div class="stat-lbl">CEPs</div>
                </div>
            </div>
        </div>

        <!-- Optional: Small Chart -->
        <div class="row">
            <div class="col-12">
                <div class="chart-box">
                    <h5 class="text-center">Top 10 Bairros</h5>
                    <div style="height: 250px;">
                        <canvas id="bairrosChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- Table -->
        <div class="table-box">
            <h4 class="mb-3">Dados Detalhados</h4>
            <table id="dataTable" class="table table-striped w-100"></table>
        </div>

    </div>

    <footer>
        <small>Gerado automaticamente | Projeto Açaí no Ponto</small>
    </footer>

    <!-- JS Libs -->
    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <!-- DataTables -->
    <script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.4/js/dataTables.bootstrap5.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.3.6/js/dataTables.buttons.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.3.6/js/buttons.bootstrap5.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.3.6/js/buttons.html5.min.js"></script>

    <script>
        // Data passed from Python
        const tableData = {json.dumps(table_data_json)};
        const tableCols = {columns_json};
        const chartLabels = {json.dumps(chart_bairros_labels)};
        const chartValues = {json.dumps(chart_bairros_data)};

        $(document).ready(function() {{
            // Init Table with JSON data (Client-side)
            $('#dataTable').DataTable({{
                data: tableData,
                columns: tableCols,
                language: {{ "url": "//cdn.datatables.net/plug-ins/1.13.4/i18n/pt-BR.json" }},
                pageLength: 25,
                scrollX: true,
                dom: 'Bfrtip',
                buttons: [
                    {{ extend: 'excel', text: 'Exportar Excel', className: 'btn btn-success btn-sm' }}
                ]
            }});

            // Init Chart
            if(document.getElementById('bairrosChart')) {{
                new Chart(document.getElementById('bairrosChart'), {{
                    type: 'bar',
                    data: {{
                        labels: chartLabels,
                        datasets: [{{
                            label: 'Pontos',
                            data: chartValues,
                            backgroundColor: '#6f42c1'
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{ legend: {{ display: false }} }}
                    }}
                }});
            }}
        }});
    </script>
</body>
</html>
    """

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"Successfully generated {OUTPUT_HTML} (Lightweight Version).")

if __name__ == "__main__":
    generate_html()
