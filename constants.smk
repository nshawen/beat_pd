from os.path import join

TEST = "test"
TRAIN = "train"
SPLITS = [TEST, TRAIN]

# Directory / file constants
SRC_DIR = "src"
DATA_DIR = join(config['base'], "data") if 'base' in config.keys() else "data"
RAW_DIR = join(DATA_DIR, "raw")
RAW_TRAIN_DIR = join(RAW_DIR, TRAIN)
RAW_TEST_DIR = join(RAW_DIR, TEST)
PROCESSED_DIR = join(DATA_DIR, "processed")

FEATURES_DIR = join(PROCESSED_DIR, "features")
MODELS_DIR = join(PROCESSED_DIR, "models")
PREDICTIONS_DIR = join(PROCESSED_DIR, "predictions")
LABELS_DIR = join(PROCESSED_DIR, "labels")

assert('team' in config.keys())
TEAM_NAME = config['team']