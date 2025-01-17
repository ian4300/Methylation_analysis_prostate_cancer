import pandas as pd
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, roc_auc_score, auc

fn_bate = "Data/Data-origin/all_beta_normalized.csv"
fn_dmp = "Data/Data-comorbidity/HyperHpo_filtered_comorbidity_both_single_group.csv"
fn_dmp_s = "Data/Data-comorbidity/HyperHpo_filtered_comorbidity_single_sole.csv"
fn_dmp_g = "Data/Data-comorbidity/HyperHpo_filtered_comorbidity_group_sole.csv"
fn_o = "Data/Data-ROC_AUC/comorbidity_both_single_group_auc.csv"
normal_num = 50

data_bate_df = pd.read_csv(fn_bate)

data_dmp_df = pd.read_csv(fn_dmp)
DMP_list = data_dmp_df.iloc[:, 0].tolist()
dmp_bate_df = data_bate_df.loc[data_bate_df[data_bate_df.columns[0]].isin(DMP_list)]

dmp_single_list = pd.read_csv(fn_dmp_s).loc[:, "CpG"].tolist()
dmp_group_list = pd.read_csv(fn_dmp_g).loc[:, "CpG"].tolist()

def cal_cutpoint(row):
    transform_row = row.to_numpy()
    TPRs = []
    FPRs = []

    predict_beta = transform_row[1::2]
    actual_beta = np.ones(278)
    actual_beta[:25] = 0

    fpr, tpr, threshold = roc_curve(actual_beta, predict_beta)

    auc1 = auc(fpr, tpr)

    gdc = "both"
    if transform_row[0] in dmp_single_list:
        gdc = "single"
    elif transform_row[0] in dmp_group_list:
        gdc = "group"

    return pd.Series({"auc": auc1, "GDC": gdc})

data_out = dmp_bate_df.iloc[:, 0].to_frame()

tqdm.pandas(desc="find auc")
data_out[["auc", "GDC"]] = dmp_bate_df.progress_apply(cal_cutpoint, axis = 1)

data_out.columns.values[0] = 'CpG'
data_out = pd.merge(data_dmp_df, data_out, on = ["CpG"], how = "inner")
data_out.loc[data_out["DNAm"] == "hypo", 'auc'] = 1 - data_out.loc[data_out["DNAm"] == "hypo", 'auc']

data_out.to_csv(fn_o, sep=',', encoding='utf-8', index=False)