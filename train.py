import json
import os
import argparse
import scipy.stats as stats 
import numpy as np
import pandas as pd
import torch
import random
import sys
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import time
import torch.utils.data as data

from sklearn.model_selection import StratifiedKFold
from collections import Counter
from tqdm import tqdm
from pathlib import Path
from pyhac.model import HACModel

from pyhac.utils.key_points import W_LIST_POSE, W2I_POSE, \
                                   W_LIST_LEFT_HAND, W2I_LEFT_HAND, \
                                   W_LIST_RIGHT_HAND, W2I_RIGHT_HAND, \
                                   X_COLS, Y_COLS, \
                                   ALL_XY_COLS, HAND_XY_COLS, \
                                   LEFT_HAND_X_COLS, LEFT_HAND_Y_COLS, \
                                   RIGHT_HAND_X_COLS, RIGHT_HAND_Y_COLS
from pyhac.utils.normalizer import normalize_data, normalize_hand_data
from pyhac.utils.data_augmentation import data_augmentation

class Dataset(torch.utils.data.Dataset):
    
    def __init__(self, X, y):
        self.X = X
        self.y = y
        
        assert self.X.shape[0] == self.y.shape[0]

    def __len__(self):
        
        return self.y.shape[0]
    
    def __getitem__(self, idx):

        return self.X[idx,:], self.y[idx]

def train(model, train_loader, val_loader, optimizer, 
          loss_fn, device, num_epochs, model_dir, actions, 
          target_columns_x):

    model.train()
    
    accs = []
    losses = []
    val_accs = []
    val_losses = []
    best_val_acc = 0.0

    for epoch in tqdm(range(0, num_epochs)):
        epoch_loss = 0.0
        epoch_acc = 0.0
        count = 0
        for x, y in train_loader:
            x = x.view(-1, model.in_channels, x.shape[1]//model.in_channels, 1).to(device).float()
            y = y.to(device)

            optimizer.zero_grad()
            pred = model(x).reshape((y.shape[0], -1))
            loss = loss_fn(pred, y)      
            
            epoch_loss += loss.item()
            loss.backward()

            epoch_acc += (pred.argmax(axis=1, keepdim=True).squeeze() == y).sum().item()
            optimizer.step()
            count += x.size()[0]

        epoch_loss /= len(train_loader)
        epoch_acc /= count
        losses.append(epoch_loss)
        accs.append(epoch_acc)
        print("epoch loss:", epoch_loss)
        print("acc:", epoch_acc)
        
        if val_loader:
            val_loss, val_acc = evaluate(model, val_loader, loss_fn, device)
            val_losses.append(val_loss)
            val_accs.append(val_acc)
            
        if val_loader and (val_acc > best_val_acc):
            best_val_acc = val_acc
            filename = "best_model.pth"
            Path(model_dir).mkdir(parents=True, exist_ok=True)
            model_path = os.path.join(model_dir, filename)
            print("save model to", model_path)
            model_data = {
                "model": model,
                'epoch': epoch,
                'optimizer': optimizer.state_dict(),
                'actions': actions,
                'target_columns': target_columns_x
            }
            torch.save(model_data, model_path)
            
    return losses, accs, val_losses, val_accs

def evaluate(model, val_loader, loss_fn, device):

    model.eval()
    
    val_loss = 0.0
    val_acc = 0.0
    count = 0
    for x, y in val_loader:
        x = x.view(-1, model.in_channels, x.shape[1]//model.in_channels, 1).to(device).float()
        y = y.to(device)

        pred = model(x).reshape((y.shape[0], -1))
        loss = loss_fn(pred, y)
        val_loss += loss.item()

        val_acc += (pred.argmax(axis=1, keepdim=True).squeeze() == y).sum().item()
        count += x.size()[0]
        
    val_loss /= len(val_loader)
    val_acc /= count
    print("val loss:", val_loss)
    print("val acc:", val_acc)
        
    return val_loss, val_acc

if __name__ == "__main__":
 
    torch.random.manual_seed(5566)
    np.random.seed(5566)
    random.seed(5566)
 
    parser = argparse.ArgumentParser()
    parser.add_argument("--conf", help="a config file path in conf/action_sets")
    parser.add_argument("--model_name", help="model name (e.g., mouse_control)")
    parser.add_argument("--in_channels", type=int, default=3)

    args = parser.parse_args()
    with open(args.conf) as f:
        conf_json = json.load(f)

    data_path = os.path.join("data", "actions")
    model_target = conf_json["type"]

    if model_target == "actions":
        mode = "pose_hand"
        actions = ["walk", "jump", "hands_on_hips", "point_left", "point_right", "arms_lift", "punch", "trample", "lateral_raise", "stand"]
        target_columns_x = ALL_XY_COLS.copy()
        ALL_XY_COLS += ["image_name", "label"] # keep label
    elif model_target == "gesture_only":
        mode = "hand"
        actions = conf_json["actions"]
        target_columns_x = HAND_XY_COLS.copy()
        HAND_XY_COLS += ["image_name", "label"] # keep label
    else:
        RunTimeError("???")

    dfs = []
    for idx, action in enumerate(actions):
        file_path = os.path.join(data_path, action, "data.csv")
        print(file_path)
        df = pd.read_csv(file_path)

        df.label = idx
        dfs.append(df)

    df_data = pd.concat(dfs)
    df_data = df_data.reset_index(drop=True)

    if model_target == "actions":
        df_data = normalize_data(df_data)
    if model_target == "gesture_only":
        df_data = normalize_hand_data(df_data)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    in_channels = args.in_channels
    hop = 2
    batch_size = 8
    num_epochs = 100
    num_class = len(actions)
    skf = StratifiedKFold(n_splits=5)
    model_dir = "pyhac\\trained_model\\gcn\\" + args.model_name

    k_fold_losses = []
    k_fold_accs = []
    k_fold_val_losses = []
    k_fold_val_accs = []
    count = 0
    for train_index, test_index in skf.split(df_data[target_columns_x].values, df_data.label.values):

        if count <= 1:
            count += 1
            continue
        
        df_train = data_augmentation(df_data.iloc[train_index])
        
        X = df_train[target_columns_x].values
        y = df_train["label"].values
        val_X = df_data[target_columns_x].values[test_index]
        val_y = df_data["label"].values[test_index]
        
        dataset = Dataset(X, y)
        val_dataset = Dataset(val_X, val_y)
        
        train_loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)
        val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        
        model = HACModel(in_channels, num_class, hop, mode).to('cuda')
        loss_fn = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        
        losses, accs, val_losses, val_accs = train(model, train_loader, val_loader, optimizer, 
                                                loss_fn, device, num_epochs, model_dir, actions,
                                                target_columns_x)
        k_fold_losses.append(losses)
        k_fold_accs.append(accs)
        
        k_fold_val_losses.append(val_losses)
        k_fold_val_accs.append(val_accs)
        
        break