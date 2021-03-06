import json
import logging

import fire
import pandas as pd
from sklearn.impute import KNNImputer


def knn_impute(df: pd.DataFrame, keep_na_indicator: bool = True) -> pd.DataFrame:
    """Iterative KNN imputation of missing values

    Args:
        df (pd.DataFrame): dataframe with missing values

    Returns:
        pd.DataFrame: imputed datafram
    """
    na_columns = df.columns[df.isna().any().sort_values()].tolist()

    for column in na_columns:
        columns_used_to_impute = [col for col in df.columns if (col not in na_columns or col == column)]
        if keep_na_indicator is True:
            df[f"{column}_na"] = df[column].apply(lambda x: 0 if x == x else 1)
        knni = KNNImputer()
        df[columns_used_to_impute] = knni.fit_transform(df[columns_used_to_impute])
    return df


def run(input_path: str, output_path: str, keep_na_indicator: bool = True):
    logging.info(f"Reading data from {input_path}")
    df = pd.read_csv(input_path)
    imputed = knn_impute(df, keep_na_indicator)
    imputed.to_csv(output_path, index=False)
    xcom_return = {"imputed_path": output_path}
    logging.info(f"Sending xcom : {xcom_return}")

    with open("/airflow/xcom/return.json", "w") as file:
        json.dump(xcom_return, file)


if __name__ == "__main__":
    fire.Fire(run)
