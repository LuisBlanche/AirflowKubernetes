# -*- coding: utf-8 -*-
import logging
from pathlib import Path
import pandas as pd 


def main(data_path):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info(f'Spliting unseen and training data in {data_path}')

    df = pd.read_csv(data_path / "raw" / "archive.zip")
    unseen = df.copy().sample(frac=0.05, random_state=42)
    train = df.drop(unseen.index)
    unseen.reset_index(drop=True, inplace=True)
    train.reset_index(drop=True, inplace=True)
    train.to_csv(data_path / "interim" / "train.csv")
    unseen.to_csv(data_path / "interim" / "unseen.csv")



if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    main(project_dir / "data")
