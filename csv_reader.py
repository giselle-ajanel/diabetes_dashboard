"""
Custom CSV Reader Implementation
Optimized for NHANES DEMO_L Dataset (11,935 rows, 27 columns)
Handles quotes, escapes, missing values without using pandas or csv library
"""

from mini_dataframe import MiniDataFrame


def read_csv(filepath, separator=',', has_header=True):
    """
    Read CSV file and return MiniDataFrame.
    
    Args:
        filepath: path to CSV file
        separator: field separator (default: ',')
        has_header: whether first row is header
        
    Returns:
        MiniDataFrame object
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if not lines:
        raise ValueError("Empty file")
    
    # Parse header
    header_line = lines[0].strip()
    headers = _parse_csv_line(header_line, separator)
    num_cols = len(headers)
    
    print(f"Reading CSV: {len(lines)-1} data rows, {num_cols} columns")
    
    if not has_header:
        headers = [f"col_{i}" for i in range(num_cols)]
        data_lines = lines
    else:
        data_lines = lines[1:]
    
    # Initialize data structure
    data = {col: [] for col in headers}
    
    # Parse data rows with progress indicator
    errors = []
    success_count = 0
    
    for line_num, line in enumerate(data_lines, start=2 if has_header else 1):
        line = line.strip()
        if not line:  # Skip empty lines
            continue
        
        try:
            fields = _parse_csv_line(line, separator)
            
            # Validate column count
            if len(fields) != num_cols:
                error_msg = f"Line {line_num}: Expected {num_cols} columns, got {len(fields)}"
                errors.append(error_msg)
                if len(errors) <= 5:  # Only show first 5 errors
                    print(f"Warning: {error_msg}")
                continue
            
            # Add to data
            for col, value in zip(headers, fields):
                # Convert empty strings to None
                processed_value = _convert_value(value)
                data[col].append(processed_value)
            
            success_count += 1
            
            # Progress indicator for large files
            if success_count % 1000 == 0:
                print(f"  Processed {success_count} rows...")
                
        except Exception as e:
            error_msg = f"Error parsing line {line_num}: {str(e)}"
            errors.append(error_msg)
            if len(errors) <= 5:
                print(f"Warning: {error_msg}")
    
    print(f"Successfully loaded {success_count} rows")
    if len(errors) > 5:
        print(f"Total errors: {len(errors)} (showing first 5)")
    
    return MiniDataFrame(data, headers)


def read_csv_iter(filepath, chunk_size=2000, separator=',', has_header=True):
    """
    Read CSV file in chunks (iterator version).
    Optimized for NHANES DEMO_L dataset.
    
    Args:
        filepath: path to CSV file
        chunk_size: number of rows per chunk (default: 2000)
        separator: field separator
        has_header: whether first row is header
        
    Yields:
        MiniDataFrame chunks
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        # Read header
        header_line = f.readline().strip()
        headers = _parse_csv_line(header_line, separator)
        num_cols = len(headers)
        
        if not has_header:
            headers = [f"col_{i}" for i in range(num_cols)]
            f.seek(0)
        
        chunk_data = {col: [] for col in headers}
        rows_in_chunk = 0
        line_num = 2 if has_header else 1
        total_rows = 0
        
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            try:
                fields = _parse_csv_line(line, separator)
                
                if len(fields) != num_cols:
                    # Skip malformed rows
                    line_num += 1
                    continue
                
                for col, value in zip(headers, fields):
                    processed_value = _convert_value(value)
                    chunk_data[col].append(processed_value)
                
                rows_in_chunk += 1
                total_rows += 1
                
                # Yield chunk when full
                if rows_in_chunk >= chunk_size:
                    print(f"  Yielding chunk: {total_rows} rows processed")
                    yield MiniDataFrame(chunk_data, headers)
                    chunk_data = {col: [] for col in headers}
                    rows_in_chunk = 0
                
            except Exception:
                # Skip problematic rows silently
                pass
            
            line_num += 1
        
        # Yield remaining data
        if rows_in_chunk > 0:
            print(f"  Yielding final chunk: {total_rows} total rows processed")
            yield MiniDataFrame(chunk_data, headers)


def _parse_csv_line(line, separator=','):
    """
    Parse a single CSV line handling quotes and escapes.
    
    Args:
        line: CSV line string
        separator: field separator
        
    Returns:
        List of field values
    """
    fields = []
    current_field = []
    in_quotes = False
    i = 0
    
    while i < len(line):
        char = line[i]
        
        if char == '"':
            if in_quotes:
                # Check for escaped quote ("")
                if i + 1 < len(line) and line[i + 1] == '"':
                    current_field.append('"')
                    i += 2
                    continue
                else:
                    # End of quoted field
                    in_quotes = False
                    i += 1
                    continue
            else:
                # Start of quoted field
                in_quotes = True
                i += 1
                continue
        
        elif char == separator and not in_quotes:
            # End of field
            fields.append(''.join(current_field))
            current_field = []
            i += 1
            continue
        
        else:
            current_field.append(char)
            i += 1
    
    # Add last field
    fields.append(''.join(current_field))
    
    return fields


def _convert_value(value):
    """
    Convert string value to appropriate type.
    Handles NHANES specific values like scientific notation.
    
    Args:
        value: String value
        
    Returns:
        Converted value (float, int, or None)
    """
    value = value.strip()
    
    # Empty string -> None
    if value == '' or value == '.':
        return None
    
    # Try to convert to number
    try:
        # Handle scientific notation (e.g., 5.397605346934028e-79)
        if 'e' in value.lower():
            float_val = float(value)
            # Very small values close to 0 -> None
            if abs(float_val) < 1e-10:
                return None
            return float_val
        
        # Try integer first
        if '.' not in value:
            return int(float(value))
        else:
            return float(value)
    except (ValueError, OverflowError):
        # Keep as string
        return value


def merge_aggregated_chunks(chunks, group_by_cols, agg_dict):
    """
    Merge aggregated results from multiple chunks.
    Used for processing large files in chunks.
    
    Args:
        chunks: list of aggregated MiniDataFrames
        group_by_cols: columns used for grouping
        agg_dict: aggregation dictionary
        
    Returns:
        Final aggregated MiniDataFrame
    """
    if not chunks:
        return MiniDataFrame()
    
    # Combine all chunks
    combined_data = {col: [] for col in chunks[0].columns}
    for chunk in chunks:
        for col in chunk.columns:
            combined_data[col].extend(chunk.data[col])
    
    combined_df = MiniDataFrame(combined_data, chunks[0].columns)
    
    # Re-aggregate
    return combined_df.groupby(group_by_cols).agg(agg_dict)


def get_column_info(df):
    """
    Get information about columns in the DataFrame.
    Useful for understanding NHANES data structure.
    
    Args:
        df: MiniDataFrame
        
    Returns:
        Dictionary with column information
    """
    info = {}
    for col in df.columns:
        values = df.data[col]
        non_null = [v for v in values if v is not None]
        
        info[col] = {
            'total': len(values),
            'non_null': len(non_null),
            'null': len(values) - len(non_null),
            'null_pct': round((len(values) - len(non_null)) / len(values) * 100, 2)
        }
        
        # Try to determine type
        if non_null:
            sample = non_null[0]
            if isinstance(sample, (int, float)):
                info[col]['type'] = 'numeric'
                try:
                    numeric_vals = [float(v) for v in non_null if isinstance(v, (int, float))]
                    if numeric_vals:
                        info[col]['min'] = min(numeric_vals)
                        info[col]['max'] = max(numeric_vals)
                        info[col]['mean'] = sum(numeric_vals) / len(numeric_vals)
                except:
                    pass
            else:
                info[col]['type'] = 'categorical'
                info[col]['unique'] = len(set(str(v) for v in non_null))
    
    return info