import pandas as pd
import markdown
import os

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
    
    html_content = markdown.markdown(md_content)

    # 2. Read Data
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found.")
        return

    df = pd.read_excel(EXCEL_FILE)
    
    # Rename columns for better display if needed (Optional)
    # The columns are likely: 'Nome...', 'Telefone...', 'Localização', 'Endereço_Google', 'Logradouro', ...
    # Let's select only relevant columns to show to avoid horizontal scroll hell
    # We want: Nome (N), Telefone (O), Endereço Completo (Treatado)
    
    # Let's inspect columns briefly or just take the treated ones + Nome
    # Columns from previous script: cols_n_o_p + 'Endereço_Google' + parsed_cols
    # N is usually Name. O is Phone.
    
    # Let's try to identify 'Nome' column (index 0 of the n_o_p slice, or by name)
    # In the previous script we saw column 13 is Name.
    # But in the Excel file, they have names.
    # Let's clean up the dataframe for display
    
    # Create a nice subset
    display_df = df.copy()
    
    # Convert to HTML Table
    # valid classes for Bootstrap + DataTables
    table_html = display_df.to_html(classes="table table-striped table-hover", index=False, border=0, table_id="dataTable")

    # 3. Build Full HTML
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
    
    <style>
        body {{
            background-color: #f8f9fa;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        .report-container {{
            max_width: 1000px;
            margin: 40px auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        h1, h2, h3 {{
            color: #2c3e50;
            margin-top: 1.5em;
        }}
        h1 {{
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}
        .table-responsive {{
            margin-top: 30px;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        footer {{
            text-align: center;
            margin-top: 50px;
            color: #6c757d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>

    <div class="container report-container">
        <!-- Markdown Content Injection -->
        {html_content}
    </div>

    <div class="container-fluid">
        <div class="row justify-content-center">
            <div class="col-11">
                <div class="table-responsive">
                    <h3 class="mb-4">Dados Processados ({len(df)} Registros)</h3>
                    <p class="text-muted">Abaixo estão listados os estabelecimentos com endereços tratados.</p>
                    {table_html}
                </div>
            </div>
        </div>
    </div>

    <footer>
        <p>Gerado automaticamente via Python - Projeto Açaí no Ponto</p>
    </footer>

    <!-- Scripts -->
    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.4/js/dataTables.bootstrap5.min.js"></script>
    <script>
        $(document).ready(function () {{
            $('#dataTable').DataTable({{
                "language": {{
                    "url": "//cdn.datatables.net/plug-ins/1.13.4/i18n/pt-BR.json"
                }},
                "pageLength": 10,
                "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
                "scrollX": true
            }});
        }});
    </script>
</body>
</html>
    """

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"Successfully generated {OUTPUT_HTML}")

if __name__ == "__main__":
    generate_html()
