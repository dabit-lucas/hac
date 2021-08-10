W_LIST_POSE = [
        "n", 
        "lei", 
        "le", 
        "leo", 
        "rei",
        "re",
        "reo",
        "lea",
        "rea",
        "ml",
        "mr",
        "ls",
        "rs",
        "lel",
        "rel",
        "lw",
        "rw",
        "lp",
        "rp",
        "li",
        "ri",
        "lt",
        "rt",
        "lh",
        "rh",
        "lk",
        "rk",
        "la",
        "ra",
        "lhe",
        "rhe",
        "lf",
        "rf"
    ]

W2I_POSE = {v: k for k, v in enumerate(W_LIST_POSE)}

W_LIST_LEFT_HAND = [
        "l_w",
        "l_t_c",
        "l_t_m",
        "l_t_i",
        "l_t_t",
        "l_i_m",
        "l_i_p",
        "l_i_d",
        "l_i_t",
        "l_m_m",
        "l_m_p",
        "l_m_d",
        "l_m_t",
        "l_r_m",
        "l_r_p",
        "l_r_d",
        "l_r_t",
        "l_p_m",
        "l_p_p",
        "l_p_d",
        "l_p_t",
    ]

W2I_LEFT_HAND = {v: k for k, v in enumerate(W_LIST_LEFT_HAND)}

W_LIST_RIGHT_HAND = [
    "r_w",
    "r_t_c",
    "r_t_m",
    "r_t_i",
    "r_t_t",
    "r_i_m",
    "r_i_p",
    "r_i_d",
    "r_i_t",
    "r_m_m",
    "r_m_p",
    "r_m_d",
    "r_m_t",
    "r_r_m",
    "r_r_p",
    "r_r_d",
    "r_r_t",
    "r_p_m",
    "r_p_p",
    "r_p_d",
    "r_p_t",
]

W2I_RIGHT_HAND = {v: k for k, v in enumerate(W_LIST_RIGHT_HAND)}

ALL_COLUMNS = W_LIST_POSE + W_LIST_LEFT_HAND + W_LIST_RIGHT_HAND
X_COLS = []
Y_COLS = []
V_COLS = []
for c in ALL_COLUMNS:
    X_COLS.append(c + "_x")
    Y_COLS.append(c + "_y")
    V_COLS.append(c + "_v")
    
LEFT_HAND_X_COLS = []
LEFT_HAND_Y_COLS = []
LEFT_HAND_V_COLS = []
for c in W_LIST_LEFT_HAND:
    LEFT_HAND_X_COLS.append(c + "_x")
    LEFT_HAND_Y_COLS.append(c + "_y")
    LEFT_HAND_V_COLS.append(c + "_v")
    
RIGHT_HAND_X_COLS = []
RIGHT_HAND_Y_COLS = []
RIGHT_HAND_V_COLS = []
for c in W_LIST_RIGHT_HAND:
    RIGHT_HAND_X_COLS.append(c + "_x")
    RIGHT_HAND_Y_COLS.append(c + "_y")
    RIGHT_HAND_V_COLS.append(c + "_v")
    
HAND_XY_COLS = LEFT_HAND_X_COLS + RIGHT_HAND_X_COLS + LEFT_HAND_Y_COLS + RIGHT_HAND_Y_COLS + LEFT_HAND_V_COLS + RIGHT_HAND_V_COLS
ALL_XY_COLS = X_COLS + Y_COLS + V_COLS