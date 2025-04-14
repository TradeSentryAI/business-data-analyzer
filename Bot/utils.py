def load_file(filepath):
    """Automatically loads CSV, Excel, or JSON files based on extension."""
    ext = os.path.splitext(filepath)[1].lower()

    if ext == '.csv':
        return pd.read_csv(filepath)
    elif ext in ['.xls', '.xlsx']:
        return pd.read_excel(filepath)
    elif ext == '.json':
        try:
            data = pd.read_json(filepath)
            # If nested, attempt normalization
            if isinstance(data.iloc[0], dict):
                data = pd.json_normalize(data.to_dict(orient='records'))
            return data
        except Exception as e:
            raise ValueError(f"❌ Error loading JSON: {e}")
    else:
        raise ValueError("❌ Unsupported file type. Use CSV, XLSX, or JSON.")
