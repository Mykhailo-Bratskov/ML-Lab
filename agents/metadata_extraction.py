import zipfile
import json
from pathlib import Path
from collections import defaultdict
import pandas as pd 
import edfio 
# python layer to extract information and data from zipfolders

def list_zip_files(zip_folder: str) -> list:
    """
    List all files in a zip archive without extracting.
    """
    lst_files = []
    try:
        with zipfile.ZipFile(zip_folder) as zip_ref:
            lst_files = zip_ref.namelist()
        return lst_files
    except Exception as e:
        print(f"Error listing zip files: {e}")
        return []


def safe_extract_zip(zip_folder: str, extract_dir: str = "extracted_data", max_files: int = None) -> Path:
    """
    Safely extract zip file to a designated directory.
    
    Args:
        zip_folder: Path to zip file
        extract_dir: Directory to extract to
        max_files: Maximum number of files to extract (None = no limit)
    
    Returns:
        Path to extraction directory
    """
    extract_path = Path(extract_dir)
    extract_path.mkdir(exist_ok=True, parents=True)
    
    try:
        with zipfile.ZipFile(zip_folder) as zip_ref:
            file_list = zip_ref.namelist()
            
            if max_files and len(file_list) > max_files:
                print(f"Warning: Archive contains {len(file_list)} files. Extracting only first {max_files}.")
                file_list = file_list[:max_files]
            
            for i, file in enumerate(file_list):
                # Security: check for path traversal
                member_path = Path(file)
                if ".." in member_path.parts or member_path.is_absolute():
                    print(f"Warning: Skipping suspicious path: {file}")
                    continue
                
                # Extract safely
                try:
                    zip_ref.extract(file, extract_path)
                except Exception as e:
                    print(f"Warning: Failed to extract {file}: {e}")
        
        return extract_path
    except Exception as e:
        print(f"Error extracting zip: {e}")
        raise


def inspect_csv(filepath: Path, nrows: int = 1000) -> dict:
    """
    Inspect CSV file with sampling to avoid loading entire large files.
    """
    try:
        df = pd.read_csv(filepath, nrows=nrows)
        return {
            'type': 'CSV',
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'null_count': df.isnull().sum().to_dict(),
            'size_bytes': filepath.stat().st_size,
            'sample_shape': f"First {min(nrows, len(df))} rows loaded for inspection"
        }
    except Exception as e:
        return {'type': 'CSV', 'error': str(e), 'size_bytes': filepath.stat().st_size}


def inspect_tsv(filepath: Path, nrows: int = 1000) -> dict:
    """
    Inspect TSV file with sampling.
    """
    try:
        df = pd.read_csv(filepath, sep='\t', nrows=nrows)
        return {
            'type': 'TSV',
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'null_count': df.isnull().sum().to_dict(),
            'size_bytes': filepath.stat().st_size,
            'sample_shape': f"First {min(nrows, len(df))} rows loaded for inspection"
        }
    except Exception as e:
        return {'type': 'TSV', 'error': str(e), 'size_bytes': filepath.stat().st_size}


def inspect_json(filepath: Path) -> dict:
    """
    Inspect JSON file structure.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return {
                    'type': 'JSON',
                    'structure': 'list',
                    'length': len(data),
                    'keys': list(data[0].keys()) if data else [],
                    'sample_item': data[0] if data else None,
                    'size_bytes': filepath.stat().st_size
                }
            elif isinstance(data, dict):
                return {
                    'type': 'JSON',
                    'structure': 'dict',
                    'keys': list(data.keys()),
                    'size_bytes': filepath.stat().st_size
                }
            else:
                return {
                    'type': 'JSON',
                    'structure': type(data).__name__,
                    'size_bytes': filepath.stat().st_size
                }
    except Exception as e:
        return {'type': 'JSON', 'error': str(e), 'size_bytes': filepath.stat().st_size}


def inspect_excel(filepath: Path) -> dict:
    """
    Inspect Excel file sheets and schema.
    """
    try:
        excel_file = pd.ExcelFile(filepath)
        sheet_info = {}
        for sheet in excel_file.sheet_names:
            df = pd.read_excel(filepath, sheet_name=sheet, nrows=100)
            sheet_info[sheet] = {
                'shape': df.shape,
                'columns': list(df.columns),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
            }
        return {
            'type': 'Excel',
            'sheets': sheet_info,
            'size_bytes': filepath.stat().st_size
        }
    except Exception as e:
        return {'type': 'Excel', 'error': str(e), 'size_bytes': filepath.stat().st_size}


def inspect_parquet(filepath: Path) -> dict:
    """
    Inspect Parquet file schema without loading full data.
    """
    try:
        df = pd.read_parquet(filepath, engine='pyarrow', columns=None)
        # Get schema info
        return {
            'type': 'Parquet',
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'size_bytes': filepath.stat().st_size
        }
    except Exception as e:
        return {'type': 'Parquet', 'error': str(e), 'size_bytes': filepath.stat().st_size}


def inspect_edf(filepath: Path) -> dict:
    """
    Inspect EDF file with per-channel metadata using lazy loading.
    """
    try:
        # Lazy load to avoid loading full data
        edf = edfio.read_edf(filepath)
        
        # Rich per-channel metadata
        signals_metadata = [
            {
                'label': sig.label,
                'sample_rate': sig.sample_rate,
                'n_samples': sig.n_samples,
                'physical_dimension': sig.physical_dimension,
                'physical_min': sig.physical_min,
                'physical_max': sig.physical_max
            }
            for sig in edf.signals
        ]
        
        return {
            'type': 'EDF',
            'num_signals': len(edf.signals),
            'signals': signals_metadata,
            'start_time': str(edf.file_meta.record_start_time) if edf.file_meta else None,
            'size_bytes': filepath.stat().st_size
        }
    except Exception as e:
        return {'type': 'EDF', 'error': str(e), 'size_bytes': filepath.stat().st_size}


def inspect_xml(filepath: Path) -> dict:
    """
    Inspect XML file structure.
    """
    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(filepath)
        root = tree.getroot()
        return {
            'type': 'XML',
            'root_tag': root.tag,
            'root_attributes': dict(root.attrib),
            'child_count': len(list(root)),
            'size_bytes': filepath.stat().st_size
        }
    except Exception as e:
        return {'type': 'XML', 'error': str(e), 'size_bytes': filepath.stat().st_size}


def inspect_text(filepath: Path) -> dict:
    """
    Inspect text file (including source code, markdown, logs).
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
            return {
                'type': 'Text',
                'extension': filepath.suffix.lower(),
                'lines': len(lines),
                'characters': len(content),
                'words': len(content.split()),
                'size_bytes': filepath.stat().st_size
            }
    except Exception as e:
        return {'type': 'Text', 'error': str(e), 'extension': filepath.suffix.lower(), 'size_bytes': filepath.stat().st_size}


def inspect_file(filepath: Path) -> dict:
    """
    Dispatch to appropriate inspection function based on file type.
    """
    filetype = filepath.suffix.lower()
    
    if filetype == '.csv':
        return inspect_csv(filepath)
    elif filetype == '.tsv':
        return inspect_tsv(filepath)
    elif filetype == '.json':
        return inspect_json(filepath)
    elif filetype in ['.xlsx', '.xls']:
        return inspect_excel(filepath)
    elif filetype in ['.parquet', '.pq']:
        return inspect_parquet(filepath)
    elif filetype == '.edf':
        return inspect_edf(filepath)
    elif filetype == '.xml':
        return inspect_xml(filepath)
    elif filetype in ['.txt', '.log', '.md', '.py', '.java', '.cpp', '.js', '.html', '.css']:
        return inspect_text(filepath)
    else:
        return {
            'type': 'Unknown',
            'extension': filetype,
            'size_bytes': filepath.stat().st_size
        }


def extract_metadata_file(lst_of_files: list, extract_dir: str = "extracted_data") -> dict:
    """
    Extract metadata from all files in list using appropriate inspection functions.
    
    Args:
        lst_of_files: List of file paths to inspect
        extract_dir: Base directory where files were extracted
    
    Returns:
        Dictionary with file-level metadata and summary statistics
    """
    metadata_results = {}
    file_type_counts = defaultdict(int)
    
    for file in lst_of_files:
        filepath = Path(extract_dir) / file
        
        # Skip directories
        if filepath.is_dir():
            continue
        
        # Skip if file doesn't exist
        if not filepath.exists():
            continue
        
        try:
            metadata = inspect_file(filepath)
            metadata_results[str(file)] = metadata
            file_type_counts[metadata.get('type', 'Unknown')] += 1
        except Exception as e:
            metadata_results[str(file)] = {
                'error': f"Failed to extract metadata: {str(e)}",
                'size_bytes': filepath.stat().st_size if filepath.exists() else 'N/A'
            }
    
    return {
        'files': metadata_results,
        'summary': {
            'total_files': len(metadata_results),
            'file_types': dict(file_type_counts),
            'total_size_bytes': sum(
                m.get('size_bytes', 0) for m in metadata_results.values() 
                if isinstance(m.get('size_bytes'), int)
            )
        }
    }


def get_files_zip(zip_folder: str) -> list:
    """
    Deprecated: Use list_zip_files() instead.
    Kept for backward compatibility.
    """
    return list_zip_files(zip_folder)



