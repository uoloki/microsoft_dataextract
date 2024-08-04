import pandas as pd
from src.common.logger import get_logger

logger = get_logger(__name__)

class PurviewDataProcessor:
    @staticmethod
    def add_y_columns(dataframe):
        for col in dataframe.columns:
            dataframe[f"{col}_Y"] = dataframe[col].apply(lambda x: 'Y' if pd.notna(x) else '')
        return dataframe

    @staticmethod
    def filter_columns_with_Y(df):
        columns_to_keep = []
        for col in df.columns:
            if col.endswith('_Y') and 'Y' in df[col].values:
                original_col = col[:-2]
                columns_to_keep.append(original_col)
        filtered_df = df[columns_to_keep]
        return filtered_df