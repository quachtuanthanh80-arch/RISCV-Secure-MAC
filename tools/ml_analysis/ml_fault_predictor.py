#!/usr/bin/env python3
"""
Machine Learning Models for Hardware Fault Prediction & Statistical Theorem Validation
1. Random Forest Classifier: Fault Detection Classification & Feature Importance.
2. Gradient Boosting Regressor: Continuous FDR Prediction across Double-Bit Space.
3. Logistic Regression: Interpretable Statistical Model validating the Bit-Distance Parity Theorem.
"""

import os
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, KFold, cross_validate
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    mean_squared_error, mean_absolute_error, r2_score
)
from sklearn.preprocessing import StandardScaler


def train_and_evaluate_models(data_path=None, output_dir=None):
    if data_path is None:
        data_path = Path(__file__).resolve().parent / "data" / "double_bit_features.csv"
    else:
        data_path = Path(data_path)

    if output_dir is None:
        output_dir = Path(__file__).resolve().parent / "data"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[*] Loading double-bit dataset from: {data_path}")
    df = pd.read_csv(data_path)

    # Filter target = pipe_c (primary 32-bit datapath accumulator)
    df_32 = df[df["target_signal"] == "pipe_c"].copy().reset_index(drop=True)
    print(f"[+] Loaded {len(df_32)} double-bit pairs for 32-bit datapath (pipe_c)")

    feature_cols = [
        "bit_i", "bit_j", "bit_distance", "distance_parity",
        "bit_i_parity", "bit_j_parity"
    ]
    X = df_32[feature_cols].values
    y_class = df_32["is_detected"].values
    y_reg = df_32["fdr"].values

    results = {}

    # =========================================================================
    # Model 1: Random Forest Classifier
    # =========================================================================
    print("\n--- Training Model 1: Random Forest Classifier (5-Fold Stratified CV) ---")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    rf = RandomForestClassifier(n_estimators=150, max_depth=8, random_state=42)

    acc_list, prec_list, rec_list, f1_list, auc_list = [], [], [], [], []
    importances_list = []

    for train_idx, test_idx in skf.split(X, y_class):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y_class[train_idx], y_class[test_idx]

        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_test)
        y_prob = rf.predict_proba(X_test)[:, 1]

        acc_list.append(accuracy_score(y_test, y_pred))
        prec_list.append(precision_score(y_test, y_pred, zero_division=0))
        rec_list.append(recall_score(y_test, y_pred, zero_division=0))
        f1_list.append(f1_score(y_test, y_pred, zero_division=0))
        auc_list.append(roc_auc_score(y_test, y_prob))
        importances_list.append(rf.feature_importances_)

    mean_importances = np.mean(importances_list, axis=0)
    rf_feat_imp = {feat: float(imp) for feat, imp in zip(feature_cols, mean_importances)}
    # Sort feature importance
    rf_feat_imp_sorted = dict(sorted(rf_feat_imp.items(), key=lambda x: x[1], reverse=True))

    results["Random_Forest"] = {
        "Accuracy_mean": float(np.mean(acc_list)),
        "Accuracy_std": float(np.std(acc_list)),
        "Precision_mean": float(np.mean(prec_list)),
        "Recall_mean": float(np.mean(rec_list)),
        "F1_Score_mean": float(np.mean(f1_list)),
        "ROC_AUC_mean": float(np.mean(auc_list)),
        "Feature_Importance": rf_feat_imp_sorted
    }

    print(f"RF Accuracy:  {np.mean(acc_list)*100:.2f}% ± {np.std(acc_list)*100:.2f}%")
    print(f"RF F1-Score:  {np.mean(f1_list)*100:.2f}%")
    print(f"RF ROC-AUC:   {np.mean(auc_list)*100:.2f}%")
    print("Top Features:", list(rf_feat_imp_sorted.items())[:4])

    # =========================================================================
    # Model 2: Gradient Boosting Regressor (Continuous FDR prediction)
    # =========================================================================
    print("\n--- Training Model 2: Gradient Boosting Regressor (5-Fold CV) ---")
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    gbr = HistGradientBoostingRegressor(max_iter=150, max_depth=6, random_state=42)

    rmse_list, mae_list, r2_list = [], [], []
    gbr_preds = np.zeros(len(df_32))

    for train_idx, test_idx in kf.split(X, y_reg):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y_reg[train_idx], y_reg[test_idx]

        gbr.fit(X_train, y_train)
        preds = gbr.predict(X_test)
        gbr_preds[test_idx] = preds

        rmse_list.append(np.sqrt(mean_squared_error(y_test, preds)))
        mae_list.append(mean_absolute_error(y_test, preds))
        r2_list.append(r2_score(y_test, preds))

    df_32["gbr_predicted_fdr"] = gbr_preds

    results["Gradient_Boosting"] = {
        "RMSE_mean": float(np.mean(rmse_list)),
        "RMSE_std": float(np.std(rmse_list)),
        "MAE_mean": float(np.mean(mae_list)),
        "R2_mean": float(np.mean(r2_list))
    }
    print(f"GBR RMSE: {np.mean(rmse_list):.2f}%")
    print(f"GBR MAE:  {np.mean(mae_list):.2f}%")
    print(f"GBR R^2:  {np.mean(r2_list):.4f}")

    # =========================================================================
    # Model 3: Logistic Regression (Interpretable Statistical Validation)
    # =========================================================================
    print("\n--- Training Model 3: Logistic Regression (Statistical Proof of Theorem 2) ---")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    lr = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
    lr.fit(X_scaled, y_class)

    # Standard error and Wald statistic calculation
    probs = lr.predict_proba(X_scaled)[:, 1]
    V = np.diagflat(probs * (1.0 - probs))
    X_design = np.hstack([np.ones((X_scaled.shape[0], 1)), X_scaled])
    # Covariance matrix: (X^T * V * X)^(-1)
    XT_V_X = np.dot(np.dot(X_design.T, V), X_design) + np.eye(X_design.shape[1]) * 1e-4
    cov_matrix = np.linalg.pinv(XT_V_X)
    std_err = np.sqrt(np.diag(cov_matrix))

    coefficients = np.hstack([lr.intercept_, lr.coef_[0]])
    wald_z = coefficients / std_err
    p_values = 2 * (1 - stats.norm.cdf(np.abs(wald_z)))

    stat_report = {}
    col_names_with_intercept = ["Intercept"] + feature_cols
    for name, coef, se, z, p in zip(col_names_with_intercept, coefficients, std_err, wald_z, p_values):
        stat_report[name] = {
            "Coefficient": float(coef),
            "Std_Error": float(se),
            "Wald_z": float(z),
            "p_value": float(p),
            "Significant_p_lt_001": bool(p < 0.001)
        }

    # Cross-validation accuracy for Logistic Regression
    lr_cv = cross_validate(lr, X_scaled, y_class, cv=skf, scoring=['accuracy', 'roc_auc', 'f1'])
    results["Logistic_Regression"] = {
        "Accuracy_mean": float(np.mean(lr_cv['test_accuracy'])),
        "ROC_AUC_mean": float(np.mean(lr_cv['test_roc_auc'])),
        "F1_Score_mean": float(np.mean(lr_cv['test_f1'])),
        "Statistical_Inference": stat_report
    }

    print(f"LR Accuracy: {np.mean(lr_cv['test_accuracy'])*100:.2f}%")
    print(f"LR ROC-AUC:  {np.mean(lr_cv['test_roc_auc'])*100:.2f}%")
    print("\nKey Coefficient Significance:")
    for feat in ["same_bit_parity", "distance_parity", "bit_distance"]:
        if feat in stat_report:
            item = stat_report[feat]
            print(f"  Feature '{feat}': Beta = {item['Coefficient']:+.4f}, z = {item['Wald_z']:+.2f}, p-value = {item['p_value']:.4e} (p < 0.001: {item['Significant_p_lt_001']})")

    # Save output metrics & predictions
    metrics_path = output_dir / "ml_evaluation_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[+] Saved ML evaluation metrics to: {metrics_path}")

    # Save updated dataset with predictions
    df_32.to_csv(output_dir / "double_bit_predictions.csv", index=False)
    print(f"[+] Saved double-bit predictions to: {output_dir / 'double_bit_predictions.csv'}")

    return results


if __name__ == "__main__":
    train_and_evaluate_models()
