"""
Unit Tests for DSCI 551 Project
Tests CSV reader, DataFrame operations, and all SQL-style functions
"""

import unittest
import os
import tempfile
from mini_dataframe import MiniDataFrame, GroupBy
from csv_reader import read_csv, read_csv_iter, _parse_csv_line


class TestCSVParser(unittest.TestCase):
    """Test CSV parsing functions"""
    
    def test_simple_parsing(self):
        """Test parsing simple CSV line"""
        line = "John,25,New York"
        result = _parse_csv_line(line, ',')
        self.assertEqual(result, ["John", "25", "New York"])
    
    def test_quoted_fields(self):
        """Test parsing fields with quotes"""
        line = '"John Doe","25","New York, NY"'
        result = _parse_csv_line(line, ',')
        self.assertEqual(result, ["John Doe", "25", "New York, NY"])
    
    def test_escaped_quotes(self):
        """Test parsing escaped quotes inside fields"""
        line = '"He said ""Hello""",25'
        result = _parse_csv_line(line, ',')
        self.assertEqual(result, ['He said "Hello"', "25"])
    
    def test_empty_fields(self):
        """Test parsing empty fields"""
        line = "John,,New York"
        result = _parse_csv_line(line, ',')
        self.assertEqual(result, ["John", "", "New York"])


class TestMiniDataFrame(unittest.TestCase):
    """Test DataFrame operations"""
    
    def setUp(self):
        """Set up test data"""
        self.data = {
            'Name': ['Alice', 'Bob', 'Charlie', 'David'],
            'Age': [25, 30, 35, 40],
            'Salary': [50000, 60000, 70000, 80000],
            'Department': ['HR', 'IT', 'IT', 'Finance']
        }
        self.df = MiniDataFrame(self.data, ['Name', 'Age', 'Salary', 'Department'])
    
    def test_initialization(self):
        """Test DataFrame initialization"""
        self.assertEqual(len(self.df), 4)
        self.assertEqual(self.df.columns, ['Name', 'Age', 'Salary', 'Department'])
    
    def test_filter(self):
        """Test filter operation"""
        result = self.df.filter(lambda row: row['Age'] > 30)
        self.assertEqual(len(result), 2)
        self.assertEqual(result.data['Name'], ['Charlie', 'David'])
    
    def test_project(self):
        """Test projection operation"""
        result = self.df.project(['Name', 'Age'])
        self.assertEqual(result.columns, ['Name', 'Age'])
        self.assertEqual(len(result), 4)
        self.assertNotIn('Salary', result.columns)
    
    def test_head(self):
        """Test head operation"""
        result = self.df.head(2)
        self.assertEqual(len(result), 2)
        self.assertEqual(result.data['Name'], ['Alice', 'Bob'])
    
    def test_tail(self):
        """Test tail operation"""
        result = self.df.tail(2)
        self.assertEqual(len(result), 2)
        self.assertEqual(result.data['Name'], ['Charlie', 'David'])


class TestGroupBy(unittest.TestCase):
    """Test GroupBy and Aggregation operations"""
    
    def setUp(self):
        """Set up test data"""
        self.data = {
            'Department': ['IT', 'IT', 'HR', 'HR', 'Finance'],
            'Salary': [60000, 70000, 50000, 55000, 80000],
            'Age': [30, 35, 25, 28, 40]
        }
        self.df = MiniDataFrame(self.data, ['Department', 'Salary', 'Age'])
    
    def test_groupby_count(self):
        """Test count aggregation"""
        result = self.df.groupby('Department').agg({'Department': 'count'})
        self.assertEqual(len(result), 3)
        dept_counts = dict(zip(result.data['Department'], result.data['Department']))
        self.assertEqual(dept_counts[('IT',)], 2)
    
    def test_groupby_avg(self):
        """Test average aggregation"""
        result = self.df.groupby('Department').agg({'Salary': 'avg'})
        self.assertEqual(len(result), 3)
        
        # Check IT department average
        for i, dept in enumerate(result.data['Department']):
            if dept == ('IT',):
                self.assertAlmostEqual(result.data['Salary'][i], 65000.0)
    
    def test_groupby_multiple_agg(self):
        """Test multiple aggregations"""
        result = self.df.groupby('Department').agg({
            'Salary': 'avg',
            'Age': 'max',
            'Department': 'count'
        })
        self.assertEqual(len(result.columns), 4)  # Department + 3 agg columns
    
    def test_groupby_with_nulls(self):
        """Test groupby with null values"""
        data = {
            'Category': ['A', 'A', 'B', 'B'],
            'Value': [10, None, 20, 30]
        }
        df = MiniDataFrame(data, ['Category', 'Value'])
        result = df.groupby('Category').agg({'Value': 'avg'})
        
        # Category A should average only non-null value
        for i, cat in enumerate(result.data['Category']):
            if cat == ('A',):
                self.assertAlmostEqual(result.data['Value'][i], 10.0)


class TestJoin(unittest.TestCase):
    """Test Join operations"""
    
    def setUp(self):
        """Set up test data"""
        self.left_data = {
            'ID': [1, 2, 3, 4],
            'Name': ['Alice', 'Bob', 'Charlie', 'David'],
            'Score': [85, 90, 78, 92]
        }
        self.left_df = MiniDataFrame(self.left_data, ['ID', 'Name', 'Score'])
        
        self.right_data = {
            'ID': [1, 2, 3, 5],
            'Department': ['HR', 'IT', 'Finance', 'Sales'],
            'Manager': ['John', 'Jane', 'Bob', 'Alice']
        }
        self.right_df = MiniDataFrame(self.right_data, ['ID', 'Department', 'Manager'])
    
    def test_inner_join(self):
        """Test inner join"""
        result = self.left_df.join(self.right_df, on='ID', how='inner')
        self.assertEqual(len(result), 3)  # Only IDs 1, 2, 3 match
        self.assertIn('Department', result.columns)
        self.assertIn('Name', result.columns)
    
    def test_left_join(self):
        """Test left join"""
        result = self.left_df.join(self.right_df, on='ID', how='left')
        self.assertEqual(len(result), 4)  # All left rows kept
        
        # Check that ID 4 has null values from right table
        idx_4 = result.data['ID'].index(4)
        self.assertIsNone(result.data['Department'][idx_4])
    
    def test_join_duplicate_columns(self):
        """Test join with duplicate column names"""
        # Add a 'Score' column to right df
        right_data_dup = {
            'ID': [1, 2],
            'Score': [100, 95],
            'Grade': ['A', 'A']
        }
        right_df_dup = MiniDataFrame(right_data_dup, ['ID', 'Score', 'Grade'])
        
        result = self.left_df.join(right_df_dup, on='ID', how='inner')
        
        # Should have Score and Score_right
        self.assertIn('Score', result.columns)
        self.assertIn('Score_right', result.columns)


class TestCSVReading(unittest.TestCase):
    """Test CSV file reading"""
    
    def setUp(self):
        """Create temporary CSV files for testing"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Simple CSV
        self.simple_csv = os.path.join(self.temp_dir, 'simple.csv')
        with open(self.simple_csv, 'w') as f:
            f.write('Name,Age,City\n')
            f.write('Alice,25,New York\n')
            f.write('Bob,30,Los Angeles\n')
        
        # CSV with quotes
        self.quoted_csv = os.path.join(self.temp_dir, 'quoted.csv')
        with open(self.quoted_csv, 'w') as f:
            f.write('Name,Description,Value\n')
            f.write('"John Doe","A person named ""John""",100\n')
            f.write('Jane,Simple description,200\n')
        
        # CSV with missing values
        self.missing_csv = os.path.join(self.temp_dir, 'missing.csv')
        with open(self.missing_csv, 'w') as f:
            f.write('A,B,C\n')
            f.write('1,2,3\n')
            f.write('4,,6\n')
            f.write('7,8,\n')
    
    def test_read_simple_csv(self):
        """Test reading simple CSV"""
        df = read_csv(self.simple_csv)
        self.assertEqual(len(df), 2)
        self.assertEqual(df.columns, ['Name', 'Age', 'City'])
        self.assertEqual(df.data['Name'], ['Alice', 'Bob'])
    
    def test_read_quoted_csv(self):
        """Test reading CSV with quotes"""
        df = read_csv(self.quoted_csv)
        self.assertEqual(len(df), 2)
        self.assertEqual(df.data['Description'][0], 'A person named "John"')
    
    def test_read_missing_values(self):
        """Test reading CSV with missing values"""
        df = read_csv(self.missing_csv)
        self.assertEqual(len(df), 3)
        self.assertIsNone(df.data['B'][1])
        self.assertIsNone(df.data['C'][2])
    
    def test_chunked_reading(self):
        """Test chunked reading"""
        chunks = list(read_csv_iter(self.simple_csv, chunk_size=1))
        self.assertEqual(len(chunks), 2)
        self.assertEqual(len(chunks[0]), 1)
        self.assertEqual(len(chunks[1]), 1)


class TestErrorHandling(unittest.TestCase):
    """Test error handling"""
    
    def test_column_mismatch(self):
        """Test error on column count mismatch"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
        temp_file.write('A,B,C\n')
        temp_file.write('1,2,3\n')
        temp_file.write('4,5\n')  # Wrong number of columns
        temp_file.close()
        
        with self.assertRaises(ValueError):
            read_csv(temp_file.name)
        
        os.unlink(temp_file.name)
    
    def test_invalid_column_project(self):
        """Test error on invalid column in project"""
        data = {'A': [1, 2], 'B': [3, 4]}
        df = MiniDataFrame(data, ['A', 'B'])
        
        with self.assertRaises(ValueError):
            df.project(['A', 'C'])  # C doesn't exist
    
    def test_invalid_groupby_column(self):
        """Test error on invalid groupby column"""
        data = {'A': [1, 2], 'B': [3, 4]}
        df = MiniDataFrame(data, ['A', 'B'])
        
        with self.assertRaises(ValueError):
            df.groupby('C')  # C doesn't exist


def run_all_tests():
    """Run all test suites"""
    print("\n" + "="*70)
    print(" "*20 + "RUNNING UNIT TESTS")
    print("="*70 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCSVParser))
    suite.addTests(loader.loadTestsFromTestCase(TestMiniDataFrame))
    suite.addTests(loader.loadTestsFromTestCase(TestGroupBy))
    suite.addTests(loader.loadTestsFromTestCase(TestJoin))
    suite.addTests(loader.loadTestsFromTestCase(TestCSVReading))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)