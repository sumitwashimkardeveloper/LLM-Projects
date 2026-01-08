import os
import json
import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class DatasetProcessor:
    ALLOWED_FORMATS = {'csv', 'json', 'jsonl', 'parquet'}

    @staticmethod
    def validate_file(file_path, file_format):
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")

        if file_format.lower() not in DatasetProcessor.ALLOWED_FORMATS:
            raise ValueError(f"Unsupported format: {file_format}")

        return True

    @staticmethod
    def load_dataset(file_path, file_format):
        try:
            if file_format.lower() == 'csv':
                return pd.read_csv(file_path)
            elif file_format.lower() == 'json':
                return pd.read_json(file_path)
            elif file_format.lower() == 'jsonl':
                return pd.read_json(file_path, lines=True)
            elif file_format.lower() == 'parquet':
                return pd.read_parquet(file_path)
        except Exception as e:
            logger.error(f"Error loading dataset: {str(e)}")
            raise

    @staticmethod
    def get_dataset_stats(df):
        return {
            'total_rows': len(df),
            'columns': list(df.columns),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'null_counts': df.isnull().sum().to_dict(),
            'memory_usage': int(df.memory_usage(deep=True).sum())
        }

    @staticmethod
    def split_dataset(df, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1, random_state=42):
        if not abs(train_ratio + val_ratio + test_ratio - 1.0) < 0.01:
            raise ValueError("Ratios must sum to approximately 1.0")

        n = len(df)
        train_idx = int(n * train_ratio)
        val_idx = train_idx + int(n * val_ratio)

        shuffled_df = df.sample(frac=1, random_state=random_state).reset_index(drop=True)

        train_df = shuffled_df[:train_idx]
        val_df = shuffled_df[train_idx:val_idx]
        test_df = shuffled_df[val_idx:]

        return {
            'train': train_df,
            'val': val_df,
            'test': test_df
        }

    @staticmethod
    def save_splits(splits, output_dir):
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        for split_name, df in splits.items():
            output_path = os.path.join(output_dir, f'{split_name}.jsonl')
            df.to_json(output_path, orient='records', lines=True)

        return output_dir

class DatasetFormatter:
    @staticmethod
    def format_for_training(data, text_column='text', label_column=None):
        formatted = []

        if isinstance(data, pd.DataFrame):
            for idx, row in data.iterrows():
                item = {'text': str(row[text_column])}
                if label_column and label_column in row:
                    item['label'] = row[label_column]
                formatted.append(item)

        return formatted

    @staticmethod
    def validate_training_format(data):
        if not data or len(data) == 0:
            return False

        required_fields = {'text'}
        first_item = data[0] if isinstance(data, list) else next(iter(data))

        return all(field in first_item for field in required_fields)
