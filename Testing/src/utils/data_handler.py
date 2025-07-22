import logging
import os
import pandas as pd

from config import Config

class DataHandler:
    """
    Handles data loading, preprocessing, and consolidation.
    """
    def __init__(self, config: Config):
        self.config = config

    def _to_list(self, text):
        """Helper to convert comma-separated string to a list of terms."""
        try:
            if pd.notna(text) and text != "N/A":
                items = [item.strip().replace(" ", "+").replace("“", "+") for item in text.split(',')]
                return [item for item in items if item]
            return "N/A"
        except Exception:
            return "N/A"

    def load_and_process_metadata_input(self) -> pd.DataFrame:
        """
        Loads the input Excel file for metadata extraction, processes keyword columns, 
        and filters for selected themes.
        """
        try:
            df = pd.read_excel(self.config.INPUT_FILE_METADATA)
        except FileNotFoundError:
            logging.error(f"Error: Input file not found at {self.config.INPUT_FILE_METADATA}")
            return pd.DataFrame()

        df['keywords_full_list'] = df['OSMOSE key words full'].apply(
            lambda x: [item.strip().replace(" “", "+") for item in x.split(' ')] if pd.notna(x) else []
        )
        df['keywords_full_list'] = df['keywords_full_list'].apply(
            lambda x: [item for item in x if item]
        )
        
        df['keywords_in_title_list'] = df['OSMOSE key words in title'].apply(self._to_list)
        df['sender_criteria_list'] = df['OSMOSE Sender criteria'].apply(self._to_list)
        df['recipient_criteria_list'] = df['OSMOSE Recipient criteria'].apply(self._to_list)

        selected_themes = df[df['Selected'] == "Y"].copy()
        
        if selected_themes.empty:
            logging.warning("No themes marked as 'Y' in the 'Selected' column. Nothing to process.")
        
        return selected_themes

    def load_and_process_content_input(self) -> pd.DataFrame:
        """Loads data from CSV for content extraction, preprocesses it, and generates URLs."""
        try:
            df = pd.read_csv(self.config.INPUT_FILE_CONTENT)
        except FileNotFoundError:
            logging.error(f"Error: Input CSV file not found at {self.config.INPUT_FILE_CONTENT}")
            return pd.DataFrame()
        except Exception as e:
            logging.error(f"Error reading CSV file: {e}")
            return pd.DataFrame()

        df['Converted Date'] = pd.to_datetime(df['epoch'], unit='s')
        df = df[df['isAttachment'] != True].copy()

        email_mask = df['entityType'] == 'Email'
        emails_df = df[email_mask].sort_values('epoch', ascending=False).drop_duplicates('Title')
        non_emails_df = df[~email_mask]
        
        processed_df = pd.concat([non_emails_df, emails_df], ignore_index=True)
        processed_df['URL'] = processed_df.apply(
            lambda row: self._generate_url(row, self.config.OSMOSE_BASE_URL, self.config.MISSION_ID),
            axis=1
        )
        return processed_df

    def _generate_url(self, row: pd.Series, base_url: str, mission_id: str) -> str:
        """Generate the appropriate URL for a given dataset row."""
        if row.get("isAttachment"):
            return f'{base_url}{"api"}/{row["u"]}'
        
        entity_type = row.get("entityType")
        msg_id = row.get("msgId")
        lot = row.get("lot")

        if entity_type == "Email":
            return f"{base_url}api/{mission_id}/eml-embed/{lot}/{msg_id}/Email.txt?highlight=queue="
        elif entity_type == "Voice":
            return f"{base_url}api/{mission_id}/vox/{msg_id}/"
        elif entity_type == "Chat":
            return f"{base_url}api/{mission_id}/bbg/{msg_id}/Chat.txt?"
        else:
            return ""

    def consolidate_results(self):
        """
        Consolidates all generated CSV files from Process_ID subfolders into a single file.
        """
        logging.info("Starting consolidation of result files...")
        consolidated_list = []
        autosearch_dir = self.config.OUTPUT_PATH_METADATA

        for process_folder in os.listdir(autosearch_dir):
            process_path = os.path.join(autosearch_dir, process_folder)
            if os.path.isdir(process_path):
                for file in os.listdir(process_path):
                    if file.endswith(".csv.tar.gz"):
                        file_path = os.path.join(process_path, file)
                        try:
                            df = pd.read_csv(file_path, encoding="utf-8-sig")
                            df['Process_ID'] = process_folder
                            consolidated_list.append(df)
                            logging.info(f"Added file {file_path} for Process_ID {process_folder}")
                        except Exception as e:
                            logging.error(f"Error reading {file_path}: {e}")
        
        if consolidated_list:
            consolidated_df = pd.concat(consolidated_list, ignore_index=True)
            if 'Process_ID' in consolidated_df.columns:
                columns = ['Process_ID'] + [col for col in consolidated_df.columns if col != 'Process_ID']
                consolidated_df = consolidated_df[columns]

            consolidated_output_path = os.path.join(autosearch_dir, "consolidated_Auto_Search.csv.tar.gz")
            consolidated_df.to_csv(consolidated_output_path, index=False, encoding="utf-8-sig", escapechar='\\')
            logging.info(f"Consolidated file saved at: {consolidated_output_path}")
        else:
            logging.warning("No CSV files found for consolidation.") 