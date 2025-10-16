import pandas as pd
import sys

def analyze_excel(file_path):
    print(f"\n{'='*80}")
    print(f"Arquivo: {file_path.split('/')[-1]}")
    print(f"{'='*80}")
    
    xl = pd.ExcelFile(file_path)
    print(f"\nAbas encontradas: {len(xl.sheet_names)}")
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet)
        print(f"\n--- Aba: {sheet} ---")
        print(f"Linhas: {len(df)}")
        print(f"Colunas: {len(df.columns)}")
        
        non_empty_cols = [col for col in df.columns if not str(col).startswith('Unnamed')]
        if non_empty_cols:
            print(f"Colunas nomeadas: {non_empty_cols[:15]}")
        
        if len(df) > 0:
            print(f"\nPrimeira linha de exemplo:")
            print(df.head(1).to_dict('records')[0] if len(df) > 0 else {})

if __name__ == "__main__":
    files = [
        'attached_assets/CRONOGRAMA 2.0 (4)_1760629348318.xlsx',
        'attached_assets/Controle Geral 3.0_151015_1760629348318.xlsx',
        'attached_assets/Controle Geral_Considerações_1760629348318.xlsx'
    ]
    
    for f in files:
        try:
            analyze_excel(f)
        except Exception as e:
            print(f"Erro em {f}: {e}")
