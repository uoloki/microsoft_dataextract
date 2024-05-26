import pandas as pd
import logging

# Configure logging
logging.basicConfig(filename='metadata_capture.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

def load_data(file_path, sheet_name):
    """Load data from an Excel sheet."""
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        logging.info(f"Data loaded from sheet: {sheet_name}")
        return df
    except Exception as e:
        logging.error(f"Error loading data from sheet {sheet_name}: {e}")
        raise

def filter_data(df):
    """Filter data based on 'Y' in the corresponding '_Y' columns."""
    try:
        filtered_df = pd.DataFrame()
        for column in df.columns:
            if column.endswith('_Y') and df[column].iloc[0] == 'Y':
                original_column = column[:-2]
                filtered_df[original_column] = df[original_column]
        logging.info("Data filtered based on 'Y' columns")
        return filtered_df
    except Exception as e:
        logging.error(f"Error filtering data: {e}")
        raise

def save_filtered_data(data_dict):
    """Save filtered data to a new Excel file."""
    file_path = 'filtered_metadata.xlsx'
    try:
        with pd.ExcelWriter(file_path) as writer:
            for sheet_name, df in data_dict.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        logging.info(f"Filtered data saved to {file_path}")
    except Exception as e:
        logging.error(f"Error saving filtered data to Excel: {e}")
        raise

def main():
    """Main function to capture and filter metadata from Excel sheets."""
    file_path = 'all_metadata.xlsx'
    sheet_names = ['Users', 'Groups', 'Teams', 'Channels', 'Messages', 'Sites', 'Files']

    try:
        data_dict = {}
        for sheet_name in sheet_names:
            # Load data from each sheet
            df = load_data(file_path, sheet_name)
            # Filter data based on 'Y' columns
            filtered_df = filter_data(df)
            data_dict[sheet_name] = filtered_df

        # Save filtered data to a new Excel file
        save_filtered_data(data_dict)
    except Exception as e:
        logging.error(f"An error occurred in the main function: {e}")
        raise

if __name__ == "__main__":
    main()
