import pandas as pd

files = {
    'CRONOGRAMA': 'attached_assets/CRONOGRAMA 2.0 (4)_1760629348318.xlsx',
    'CONTROLE_GERAL': 'attached_assets/Controle Geral 3.0_151015_1760629348318.xlsx',
    'CONSIDERACOES': 'attached_assets/Controle Geral_Considerações_1760629348318.xlsx'
}

for name, path in files.items():
    print(f"\n{'='*60}\n{name}\n{'='*60}")
    xl = pd.ExcelFile(path)
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(path, sheet_name=sheet, nrows=3)
        cols = [c for c in df.columns if not str(c).startswith('Unnamed')]
        print(f"\n{sheet}: {len(pd.read_excel(path, sheet_name=sheet))} linhas")
        if cols:
            print(f"  Colunas: {', '.join(cols[:10])}")
