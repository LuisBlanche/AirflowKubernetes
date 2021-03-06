# -*- coding: utf-8 -*-
import json
import logging
import os
from pathlib import Path

import fire
import pandas as pd


def run(data_path_str: str, target_name: str = "Potability"):
    """This will take in a zipped csv located at datapath and split it to build
    the different parts of data needed for the ML pipeline (traininng features and target, and unseen data features and
    target)

    Args:
        data_path_str (str): data folder pat
        target_name (str, optional): Column name for the target. Defaults to "Potability".
    """
    print("Start")
    logger = logging.getLogger(__name__)
    logger.info(f"Spliting unseen and training data in {data_path_str} / interim")
    data_path = Path(data_path_str)

    df = pd.read_csv(data_path / "raw" / "archive.zip")
    unseen = df.copy().sample(frac=0.05, random_state=42)
    train = df.drop(unseen.index)
    unseen.reset_index(drop=True, inplace=True)
    train.reset_index(drop=True, inplace=True)
    train_features, train_target = split_features_target(train, target_name)
    unseen_features, unseen_real_target = split_features_target(unseen, target_name)
    train_features_path = data_path / "interim" / "train_features.csv"
    train_features.to_csv(train_features_path, index=False)
    train_target_path = data_path / "interim" / "train_target.csv"
    train_target.to_csv(train_target_path, index=False)
    unseen_features_path = data_path / "interim" / "unseen_features.csv"
    unseen_features.to_csv(unseen_features_path, index=False)
    unseen_real_target_path = data_path / "interim" / "unseen_real_target.csv"
    unseen_real_target.to_csv(unseen_real_target_path, index=False)
    xcom_return = {
        "train_features_path": str(train_features_path),
        "train_target_path": str(train_target_path),
        "unseen_features_path": str(unseen_features_path),
        "unseen_real_target": str(unseen_real_target_path),
    }
    with open("/airflow/xcom/return.json", "w") as file:
        logging.info(f"Sending xcom : {xcom_return}")
        json.dump(xcom_return, file)
    print(os.listdir("/airflow/xcom"))


def split_features_target(df: pd.DataFrame, target_name: str):
    """Splits a dataframe between its features and target

    Args:
        df (pd.DataFrame): machine learning dataframe
        target_name (str): Column name for the target

    Returns:
        pd.DataFrame, pd.Series: splitted features and target
    """
    target = df[target_name]
    features = df.drop(columns=[target_name])
    return features, target


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    fire.Fire(run)
