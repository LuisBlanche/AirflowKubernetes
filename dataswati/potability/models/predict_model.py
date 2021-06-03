import logging
import os

import fire
import joblib
import pandas as pd


def load_model(model_path: str):
    model = joblib.load(model_path)
    return model


def run(
    unseen_features_input_path: str,
    unseen_target_input_path: str,
    predictions_output_path: str,
    model_path: str,
):
    logging.info(f"Reading unseen data from {unseen_features_input_path}")
    logging.info(f"Reading real target data from {unseen_target_input_path}")

    unseen_features = pd.read_csv(unseen_features_input_path)
    unseen_target = pd.read_csv(unseen_target_input_path)
    model = load_model(model_path)
    predictions = model.predict(unseen_features)
    pd.Series(predictions, name="Potability").to_csv(predictions_output_path, index=False)
    model.evaluate(unseen_features, unseen_target)


if __name__ == "__main__":
    fire.Fire(run)
