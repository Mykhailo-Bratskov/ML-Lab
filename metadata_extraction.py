import zipfile
from pathlib import Path
import pandas as pd 
import edfio 
# python layer to extract information and data from zipfolders

# Exctracting name of the files from the zip file
def get_files_zip(zip_folder: str):
    # Convert to Path object for better handling

    lst_files = []
    with zipfile.ZipFile(zip_folder) as zip_ref:
        zip_ref.extractall()
        for file in zip_ref.namelist():
            lst_files.append(file)
        return lst_files
    

def extract_metadata_file(lst_of_files: list):
    """
    Extract metadata from various file types.
    Supports: CSV, JSON, XML, Excel (xlsx/xls), Text, Parquet, EDF, TSV
    """
    metadata_results = {}
    
    for file in lst_of_files:
        filepath = Path(file)
        filetype = filepath.suffix.lower()
        
        try:
            # Skip directories
            if filepath.is_dir():
                continue
            
            # CSV files
            if filetype == '.csv':
                df = pd.read_csv(filepath)
                metadata_results[str(filepath)] = {
                    'type': 'CSV',
                    'shape': df.shape,
                    'columns': list(df.columns),
                    'dtypes': df.dtypes.to_dict(),
                    'null_count': df.isnull().sum().to_dict(),
                    'size_bytes': filepath.stat().st_size
                }
            
            # TSV files
            elif filetype == '.tsv':
                df = pd.read_csv(filepath, sep='\t')
                metadata_results[str(filepath)] = {
                    'type': 'TSV',
                    'shape': df.shape,
                    'columns': list(df.columns),
                    'dtypes': df.dtypes.to_dict(),
                    'null_count': df.isnull().sum().to_dict(),
                    'size_bytes': filepath.stat().st_size
                }
            
            # JSON files
            elif filetype == '.json':
                with open(filepath, 'r', encoding='utf-8') as f:
                    import json
                    data = json.load(f)
                    if isinstance(data, list):
                        metadata_results[str(filepath)] = {
                            'type': 'JSON',
                            'structure': 'list',
                            'length': len(data),
                            'keys': list(data[0].keys()) if data else [],
                            'size_bytes': filepath.stat().st_size
                        }
                    elif isinstance(data, dict):
                        metadata_results[str(filepath)] = {
                            'type': 'JSON',
                            'structure': 'dict',
                            'keys': list(data.keys()),
                            'size_bytes': filepath.stat().st_size
                        }
            
            # Excel files (xlsx, xls)
            elif filetype in ['.xlsx', '.xls']:
                excel_file = pd.ExcelFile(filepath)
                sheet_info = {}
                for sheet in excel_file.sheet_names:
                    df = pd.read_excel(filepath, sheet_name=sheet)
                    sheet_info[sheet] = {
                        'shape': df.shape,
                        'columns': list(df.columns)
                    }
                metadata_results[str(filepath)] = {
                    'type': 'Excel',
                    'sheets': sheet_info,
                    'size_bytes': filepath.stat().st_size
                }
            
            # Parquet files
            elif filetype == '.parquet' or filetype == '.pq':
                df = pd.read_parquet(filepath)
                metadata_results[str(filepath)] = {
                    'type': 'Parquet',
                    'shape': df.shape,
                    'columns': list(df.columns),
                    'dtypes': df.dtypes.to_dict(),
                    'size_bytes': filepath.stat().st_size
                }
            
            # EDF files (EEG/Medical data)
            elif filetype == '.edf':
                try:
                    edf = edfio.read_edf(filepath)
                    metadata_results[str(filepath)] = {
                        'type': 'EDF',
                        'signals': len(edf.signals),
                        'signal_labels': [sig.label for sig in edf.signals],
                        'sample_rate': edf.signals[0].sample_rate if edf.signals else None,
                        'duration_seconds': edf.signals[0].n_samples / edf.signals[0].sample_rate if edf.signals else None,
                        'size_bytes': filepath.stat().st_size
                    }
                except Exception as e:
                    metadata_results[str(filepath)] = {
                        'type': 'EDF',
                        'error': f"Failed to read EDF: {str(e)}",
                        'size_bytes': filepath.stat().st_size
                    }
            
            # XML files
            elif filetype == '.xml':
                try:
                    import xml.etree.ElementTree as ET
                    tree = ET.parse(filepath)
                    root = tree.getroot()
                    metadata_results[str(filepath)] = {
                        'type': 'XML',
                        'root_tag': root.tag,
                        'root_attributes': dict(root.attrib),
                        'child_count': len(list(root)),
                        'size_bytes': filepath.stat().st_size
                    }
                except Exception as e:
                    metadata_results[str(filepath)] = {
                        'type': 'XML',
                        'error': f"Failed to parse XML: {str(e)}",
                        'size_bytes': filepath.stat().st_size
                    }
            
            # Text files
            elif filetype in ['.txt', '.log', '.md', '.py', '.java', '.cpp', '.js', '.html', '.css']:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                    metadata_results[str(filepath)] = {
                        'type': 'Text',
                        'extension': filetype,
                        'lines': len(lines),
                        'characters': len(content),
                        'words': len(content.split()),
                        'size_bytes': filepath.stat().st_size
                    }
            
            # Unknown file type
            else:
                metadata_results[str(filepath)] = {
                    'type': 'Unknown',
                    'extension': filetype,
                    'size_bytes': filepath.stat().st_size
                }
        
        except Exception as e:
            metadata_results[str(filepath)] = {
                'error': f"Failed to extract metadata: {str(e)}",
                'extension': filetype,
                'size_bytes': filepath.stat().st_size if filepath.exists() else 'N/A'
            }
    
    return metadata_results


