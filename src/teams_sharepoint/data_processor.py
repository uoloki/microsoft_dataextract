import pandas as pd

class DataProcessor:
    @staticmethod
    def add_y_columns(df):
        """Add a 'Y' column for each existing column."""
        for column in df.columns:
            df[f'{column}_Y'] = 'Y'
        return df

    @staticmethod
    def filter_data(df):
        """Filter data based on 'Y' in corresponding _Y columns."""
        filtered_df = pd.DataFrame()
        for column in df.columns:
            if column.endswith('_Y') and df[column].iloc[0] == 'Y':
                original_column = column[:-2]
                filtered_df[original_column] = df[original_column]
        return filtered_df