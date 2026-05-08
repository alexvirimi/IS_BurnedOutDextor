from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder


def prepare_dataset(
    folder_path: Path | str | None = None,
    output_path: Path | str | None = None,
    reference_date: str = "2026-05-02",
) -> tuple[pd.DataFrame, dict]:
    """
    Load, merge, and preprocess training data from CSV files.

    Args:
        folder_path : Path | str | None
            Directory that contains workers.csv, company.csv, and answers_survey.csv.
            Defaults to <project_root>/data/training_data.
        output_path : Path | str | None
            Directory where the preprocessed dataset will be saved.
            Defaults to <folder_path>/data/training_dataset.csv.
        reference_date : str
            ISO date used to compute seniority (default: "2026-05-02").

    Returns:
        df : pd.DataFrame
            Preprocessed dataset ready for modelling.
        label_mappings : dict
            Dictionary with the category → encoded-value mappings for each
            label-encoded column.
    """

    # paths
    if folder_path is None:
        ROOT = Path(__file__).resolve().parents[0]
        folder_path = ROOT / "data" / "training_data"
    folder_path = Path(folder_path)
    print(f"Loading data from: {folder_path}")

    # load datasets
    workers = pd.read_csv(folder_path / "workers.csv")
    company = pd.read_csv(folder_path / "company.csv", parse_dates=["start_date"])
    survey  = pd.read_csv(folder_path / "answers_survey.csv")

    # merge datasets
    df = (
        workers
        .merge(company, left_on="id", right_on="id_worker")
        .merge(survey, on="id_worker")
        .drop(columns=["id_worker"])   # remove redundant key from survey
    )

    # features
    # seniority in years since the date of entry
    today = pd.Timestamp(reference_date)
    df["seniority_years"] = ((today - df["start_date"]).dt.days / 365).round(1)

    # task completion rate (handle division by zero by replacing 0 with NaN)
    df["completion_rate"] = (
        df["completed_tasks"] / df["assigned_tasks"].replace(0, np.nan)
    ).round(3)

    # label encoding
    label_mappings: dict = {}
    categorical_cols = ["gender", "work_mode", "location"]

    le = LabelEncoder()
    for col in categorical_cols:
        enc_col = f"{col}_enc"
        df[enc_col] = le.fit_transform(df[col])
        label_mappings[col] = dict(zip(df[col], df[enc_col]))
    
    # save dataset
    if output_path is None:
        output_path = folder_path / "training_dataset.csv"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    return df, label_mappings


if __name__ == "__main__":
    df, mappings = prepare_dataset()
