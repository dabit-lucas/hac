import pandas
from .key_points import X_COLS, Y_COLS, \
                        ALL_XY_COLS, HAND_XY_COLS, \
                        LEFT_HAND_X_COLS, LEFT_HAND_Y_COLS, \
                        RIGHT_HAND_X_COLS, RIGHT_HAND_Y_COLS

def normalize_data(df):
    
    df_data = df.copy()
    df_data = df_data.fillna(0)
    
    center_x_cols = ['lh_x', 'rh_x']
    center_y_cols = ['lh_y', 'rh_y']
    
    x_center = df[center_x_cols].mean(axis=1)
    y_center = df[center_y_cols].mean(axis=1)
    
    df_data[X_COLS] = df[X_COLS].sub(x_center, axis=0)
    df_data[Y_COLS] = df[Y_COLS].sub(y_center, axis=0)
    
    return df_data
    
def normalize_hand_data(df):
    
    df_hand_data = df[HAND_XY_COLS].copy()
    df_hand_data = df_hand_data.fillna(0)
    
    left_hand_center_x_cols = ['l_w_x']
    left_hand_center_y_cols = ['l_w_y']
    right_hand_center_x_cols = ['r_w_x']
    right_hand_center_y_cols = ['r_w_y']
    
    x_left_hand_root = df[left_hand_center_x_cols].mean(axis=1)
    y_left_hand_root = df[left_hand_center_y_cols].mean(axis=1)
    x_right_hand_root = df[right_hand_center_x_cols].mean(axis=1)
    y_right_hand_root = df[right_hand_center_y_cols].mean(axis=1)
    
    df_hand_data[LEFT_HAND_X_COLS] = df[LEFT_HAND_X_COLS].sub(x_left_hand_root, axis=0)
    df_hand_data[LEFT_HAND_Y_COLS] = df[LEFT_HAND_Y_COLS].sub(y_left_hand_root, axis=0)
    df_hand_data[RIGHT_HAND_X_COLS] = df[RIGHT_HAND_X_COLS].sub(x_right_hand_root, axis=0)
    df_hand_data[RIGHT_HAND_Y_COLS] = df[RIGHT_HAND_Y_COLS].sub(y_right_hand_root, axis=0)
    
    return df_hand_data