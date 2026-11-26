"""
Mini DataFrame Implementation for DSCI 551 Project
Optimized for NHANES DEMO_L Dataset
Authors: Chloe Chen, Giselle Ajanel
"""

class MiniDataFrame:
    """
    A lightweight DataFrame implementation that stores data as a dictionary of lists.
    Supports filtering, projection, groupby, aggregation, and joins.
    Optimized for NHANES demographic data with proper null handling.
    """
    
    def __init__(self, data=None, columns=None):
        """
        Initialize DataFrame with data dictionary or empty.
        
        Args:
            data: dict of column_name -> list of values
            columns: list of column names (optional, inferred from data)
        """
        if data is None:
            self.data = {}
            self.columns = []
        else:
            self.data = data
            self.columns = columns if columns else list(data.keys())
        
        # Validate all columns have same length
        if self.data:
            lengths = [len(v) for v in self.data.values()]
            if len(set(lengths)) > 1:
                raise ValueError(f"All columns must have same length. Got: {lengths}")
            self._num_rows = lengths[0] if lengths else 0
        else:
            self._num_rows = 0
    
    def __len__(self):
        """Return number of rows"""
        return self._num_rows
    
    def __repr__(self):
        """String representation of DataFrame"""
        if self._num_rows == 0:
            return f"MiniDataFrame(columns={self.columns}, rows=0)"
        
        # Show first 5 and last 5 rows if more than 10
        display_rows = min(10, self._num_rows)
        lines = [" | ".join(str(c)[:15] for c in self.columns)]
        lines.append("-" * min(80, len(lines[0])))
        
        for i in range(min(5, self._num_rows)):
            row = [str(self.data[col][i])[:15] if self.data[col][i] is not None else 'NULL' 
                   for col in self.columns]
            lines.append(" | ".join(row))
        
        if self._num_rows > 10:
            lines.append("...")
            for i in range(max(5, self._num_rows - 5), self._num_rows):
                row = [str(self.data[col][i])[:15] if self.data[col][i] is not None else 'NULL' 
                       for col in self.columns]
                lines.append(" | ".join(row))
        elif self._num_rows > 5:
            for i in range(5, self._num_rows):
                row = [str(self.data[col][i])[:15] if self.data[col][i] is not None else 'NULL' 
                       for col in self.columns]
                lines.append(" | ".join(row))
        
        lines.append(f"\n[{self._num_rows} rows x {len(self.columns)} columns]")
        return "\n".join(lines)
    
    def filter(self, predicate):
        """
        Filter rows based on predicate function.
        Handles None values gracefully.
        
        Args:
            predicate: function that takes a row dict and returns bool
            
        Returns:
            New MiniDataFrame with filtered rows
        """
        filtered_data = {col: [] for col in self.columns}
        
        for i in range(self._num_rows):
            row = {col: self.data[col][i] for col in self.columns}
            try:
                if predicate(row):
                    for col in self.columns:
                        filtered_data[col].append(self.data[col][i])
            except (ValueError, TypeError):
                # Skip rows where predicate fails (e.g., None values)
                continue
        
        return MiniDataFrame(filtered_data, self.columns)
    
    def project(self, columns):
        """
        Select specific columns.
        
        Args:
            columns: list of column names to keep
            
        Returns:
            New MiniDataFrame with selected columns
        """
        if not all(col in self.columns for col in columns):
            missing = [col for col in columns if col not in self.columns]
            raise ValueError(f"Columns not found: {missing}")
        
        projected_data = {col: self.data[col][:] for col in columns}
        return MiniDataFrame(projected_data, columns)
    
    def groupby(self, by_columns):
        """
        Group data by one or more columns.
        
        Args:
            by_columns: list of column names to group by
            
        Returns:
            GroupBy object for aggregation
        """
        if isinstance(by_columns, str):
            by_columns = [by_columns]
        
        if not all(col in self.columns for col in by_columns):
            missing = [col for col in by_columns if col not in self.columns]
            raise ValueError(f"Grouping columns not found: {missing}")
        
        return GroupBy(self, by_columns)
    
    def join(self, other, on, how='inner'):
        """
        Join with another DataFrame.
        
        Args:
            other: Another MiniDataFrame
            on: Column name to join on
            how: 'inner' or 'left'
            
        Returns:
            New MiniDataFrame with joined data
        """
        if on not in self.columns:
            raise ValueError(f"Join column '{on}' not found in left DataFrame")
        if on not in other.columns:
            raise ValueError(f"Join column '{on}' not found in right DataFrame")
        
        # Build hash table from right DataFrame
        right_hash = {}
        for i in range(len(other)):
            key = other.data[on][i]
            if key is not None:  # Skip None keys
                if key not in right_hash:
                    right_hash[key] = []
                right_hash[key].append(i)
        
        # Prepare result columns (avoid duplicates)
        result_columns = self.columns[:]
        right_cols_to_add = [col for col in other.columns if col != on]
        
        # Handle duplicate column names
        for col in right_cols_to_add:
            if col in result_columns:
                result_columns.append(f"{col}_right")
            else:
                result_columns.append(col)
        
        result_data = {col: [] for col in result_columns}
        
        # Perform join
        for i in range(len(self)):
            left_key = self.data[on][i]
            
            if left_key is not None and left_key in right_hash:
                # Match found - add all matching rows
                for right_idx in right_hash[left_key]:
                    # Add left columns
                    for col in self.columns:
                        result_data[col].append(self.data[col][i])
                    
                    # Add right columns (excluding join key)
                    for col in right_cols_to_add:
                        target_col = f"{col}_right" if col in self.columns else col
                        result_data[target_col].append(other.data[col][right_idx])
            
            elif how == 'left':
                # Left join - keep row with nulls for right columns
                for col in self.columns:
                    result_data[col].append(self.data[col][i])
                
                for col in right_cols_to_add:
                    target_col = f"{col}_right" if col in self.columns else col
                    result_data[target_col].append(None)
        
        return MiniDataFrame(result_data, result_columns)
    
    def to_dict(self):
        """Convert to dictionary format"""
        return {col: self.data[col][:] for col in self.columns}
    
    def head(self, n=5):
        """Return first n rows"""
        head_data = {col: self.data[col][:n] for col in self.columns}
        return MiniDataFrame(head_data, self.columns)
    
    def tail(self, n=5):
        """Return last n rows"""
        tail_data = {col: self.data[col][-n:] for col in self.columns}
        return MiniDataFrame(tail_data, self.columns)
    
    def describe(self):
        """Get summary statistics for numeric columns"""
        stats = {}
        for col in self.columns:
            values = [v for v in self.data[col] if v is not None]
            if values:
                try:
                    numeric_values = [float(v) for v in values]
                    stats[col] = {
                        'count': len(numeric_values),
                        'mean': sum(numeric_values) / len(numeric_values),
                        'min': min(numeric_values),
                        'max': max(numeric_values),
                        'null_count': self._num_rows - len(numeric_values)
                    }
                except (ValueError, TypeError):
                    # Non-numeric column
                    stats[col] = {
                        'count': len(values),
                        'unique': len(set(str(v) for v in values)),
                        'null_count': self._num_rows - len(values)
                    }
        return stats


class GroupBy:
    """Helper class for groupby operations"""
    
    def __init__(self, dataframe, by_columns):
        self.df = dataframe
        self.by_columns = by_columns
        self._build_groups()
    
    def _build_groups(self):
        """Build internal group structure, handling None values"""
        self.groups = {}
        
        for i in range(len(self.df)):
            # Create group key tuple, skip rows with None in groupby columns
            key_values = [self.df.data[col][i] for col in self.by_columns]
            if any(v is None for v in key_values):
                continue
            
            key = tuple(key_values)
            
            if key not in self.groups:
                self.groups[key] = []
            self.groups[key].append(i)
    
    def agg(self, agg_dict):
        """
        Aggregate grouped data.
        
        Args:
            agg_dict: dict of column_name -> aggregation_function
                     Functions: 'count', 'sum', 'avg', 'min', 'max'
                     
        Returns:
            New MiniDataFrame with aggregated results
        """
        result_columns = self.by_columns + list(agg_dict.keys())
        result_data = {col: [] for col in result_columns}
        
        for group_key, indices in self.groups.items():
            # Add group key values
            for i, col in enumerate(self.by_columns):
                result_data[col].append(group_key[i])
            
            # Compute aggregations
            for col, func in agg_dict.items():
                if col not in self.df.columns:
                    raise ValueError(f"Column '{col}' not found")
                
                values = [self.df.data[col][idx] for idx in indices]
                # Filter out None/null values for aggregation
                values = [v for v in values if v is not None and v != '']
                
                if func == 'count':
                    result_data[col].append(len(values))
                elif func == 'sum':
                    try:
                        result_data[col].append(sum(float(v) for v in values) if values else 0)
                    except (ValueError, TypeError):
                        result_data[col].append(None)
                elif func == 'avg':
                    try:
                        result_data[col].append(
                            sum(float(v) for v in values) / len(values) if values else None
                        )
                    except (ValueError, TypeError):
                        result_data[col].append(None)
                elif func == 'min':
                    try:
                        result_data[col].append(min(float(v) for v in values) if values else None)
                    except (ValueError, TypeError):
                        result_data[col].append(None)
                elif func == 'max':
                    try:
                        result_data[col].append(max(float(v) for v in values) if values else None)
                    except (ValueError, TypeError):
                        result_data[col].append(None)
                else:
                    raise ValueError(f"Unknown aggregation function: {func}")
        
        return MiniDataFrame(result_data, result_columns)