import os
import pandas as pd
from pandas import DataFrame
import extraction_functions
import numpy as np

# Sampling Rate
SAMPLING = 30
# Sliding Window Overlap in %
SLIDING = 0.5

# Data Directory
CURRENT_DIR = os.getcwd()
PARENT_DIR = os.path.dirname(CURRENT_DIR)
DATA_DIR = os.path.join(CURRENT_DIR, "data")
TEST_DATA_DIR = os.path.join(CURRENT_DIR, "test_data.csv")


# Get the gradient for the raw data
def gradient_of(data):
    return pd.DataFrame(np.gradient(data, axis=1))


def extract_segment(segment, functions):
    row = np.empty(0)
    acc = segment.iloc[:, 0:3]
    gyro = segment.iloc[:, 3:6]

    # Getting all the data and extracting row by row
    for data in [acc,
                 gyro,
                 gradient_of(acc),
                 gradient_of(gyro),
                 ]:
        for fn in functions:
            # calling each function from the pointer
            f = getattr(extraction_functions, fn)

            # extract features by row
            row = np.append(row, np.asarray(f(data)))

    extracted_segment = row

    print(extracted_segment.shape)
    return extracted_segment


def extract_features(segments):
    df = np.empty(0)
    functions = [f for f in extraction_functions.__dict__ if
                 callable(getattr(extraction_functions, f)) and f.startswith("get_")]

    row = np.empty(0)
    for segment in segments:
        # each row is an extracted feature for one segement
        row = extract_segment(segment, functions)
        df = np.append(df, row)

    df = df.reshape(-1, len(row))
    extracted = pd.DataFrame(df)

    return extracted


def segment_data(df):
    def check_sampling_size(x):
        if len(x) == SAMPLING:
            return True
        else:
            return False

    step = int((1 - SLIDING) * SAMPLING)
    segments = list(
        filter(check_sampling_size,
               list(df.rolling(SAMPLING))[SAMPLING - 1::step]))

    return segments


def process_data():
    processed_data = pd.DataFrame()
    col_names = ["accX", "accY", "accZ", "gyroX", "gyroY", "gyroZ"]

    for moves_folder in os.listdir(DATA_DIR):

        # moves_folder => folder containing csv_files e.g. dab, listen
        if moves_folder != '.DS_Store':
            moves_folder = os.path.join(DATA_DIR, moves_folder)

            for data_file in os.listdir(moves_folder):
                if data_file != '.DS_Store':
                    # data_file => csv file with all the data for a move e.g. dab-1, dab-2
                    data_file = os.path.join(moves_folder, data_file)
                    df = pd.read_csv(data_file, names=col_names, header=None)

                    # sliding window
                    segments = segment_data(df)

                    # extract
                    features = extract_features(segments)

                    # label data for training
                    label = os.path.basename(moves_folder)
                    features["LABEL"] = label


                    # combine csv files within the same folder
                    processed_data = processed_data.append(features, ignore_index=True)

    return processed_data


def process_data_stream(data_stream):
    extracted_feature = pd.DataFrame()
    col_names = ["accX", "accY", "accZ", "gyroX", "gyroY", "gyroZ"]

    df = data_stream

    # get extraction functions
    functions = [f for f in extraction_functions.__dict__ if
                 callable(getattr(extraction_functions, f)) and f.startswith("get_")]
    # extract
    extracted_feature = extract_segment(df, functions)

    return extracted_feature


def process_data_test():
    extracted_features = pd.DataFrame()
    col_names = ["accX", "accY", "accZ", "gyroX", "gyroY", "gyroZ"]

    df = pd.read_csv(TEST_DATA_DIR, names=col_names, header=None)
    segments = segment_data(df)

    # extract
    extracted_features = extract_features(segments)

    return extracted_features
