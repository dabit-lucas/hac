import pandas as pd
import numpy as np
from .key_points import X_COLS, Y_COLS, \
                        ALL_XY_COLS, HAND_XY_COLS, \
                        LEFT_HAND_X_COLS, LEFT_HAND_Y_COLS, \
                        RIGHT_HAND_X_COLS, RIGHT_HAND_Y_COLS, \
                        LABEL_COLS

def get_columns_end_x(cols):
    return [col for col in cols if "_x" in col]

def get_columns_end_xy(cols):
    return [col for col in cols if "_x" in col] + [col for col in cols if "_y" in col] + [col for col in cols if "_v" in col]

def df_copy_structure(df):
    df_aug = pd.DataFrame(columns=df.columns)
    df_aug = df_aug.astype(df.dtypes)

    return df_aug

def pertubation(df):

    df_aug = df_copy_structure(df)
    xy_cols = get_columns_end_xy(df.columns)
    
    sigma = 1e-3
    df_aug[xy_cols] = df[xy_cols] + np.random.normal(0.0, sigma, df[xy_cols].shape)
    df_aug[LABEL_COLS] = df[LABEL_COLS]

    return df_aug

def rotation_2D(df):
    df_aug = df_copy_structure(df)

    return df_aug

def rotation_3D(df):
    df_aug = df_copy_structure(df)

    return df_aug

def scale(df):

    xy_cols = get_columns_end_xy(df.columns)
    x_cols = get_columns_end_x(df.columns)

    scale_factors = [0.95, 1.05]
    
    dfs = []

    for scale_factor in scale_factors:
        df_aug = df_copy_structure(df)
        df_aug[xy_cols] = df[xy_cols]
        df_aug[LABEL_COLS] = df[LABEL_COLS]
        df_aug[x_cols] = df_aug[x_cols] * scale_factor
        dfs.append(df_aug)

    df_aug = pd.concat(dfs)
    df_aug = df_aug.reset_index(drop=True)    

    return df_aug

def data_augmentation(df):

    df_scale = scale(df)
    df_pertubation = pertubation(df)
    df_rotation_2D = rotation_2D(df)
    df_rotation_3D = rotation_3D(df)

    df_augmentation = pd.concat([df, df_scale, df_pertubation, df_rotation_2D, df_rotation_3D])
    df_augmentation = df_augmentation.reset_index(drop=True)

    print(df_augmentation.shape)

    return df_augmentation
