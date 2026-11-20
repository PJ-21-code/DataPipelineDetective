import os
import sys
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

# Ensure project root is in python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from Agents.anomaly import anomaly_node

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def evaluate_scenario(scenario_name):
    csv_file = os.path.join(DATA_DIR, f"anomaly_synth_{scenario_name}.csv")
    meta_file = os.path.join(DATA_DIR, f"anomaly_synth_{scenario_name}_labels.json")
    
    with open(meta_file, "r") as f:
        meta = json.load(f)
        
    y_true = np.array(meta["ground_truth"])  # 1 = anomaly, 0 = normal
    
    # 1. Test project's anomaly_node function directly
    state = {"file_path": csv_file}
    node_output = anomaly_node(state)
    reported_count = node_output.get("anomaly", {}).get("anomaly_count", 0)
    reported_pct = node_output.get("anomaly", {}).get("percentage", 0.0)
    
    # 2. Extract numeric features and replicate exact model inference for point-by-point ground truth scoring
    df = pd.read_csv(csv_file)
    df_numeric = df.select_dtypes(include=['number']).dropna()
    
    iso = IsolationForest(contamination=0.05, random_state=42)
    preds = iso.fit_predict(df_numeric)
    # preds is 1 for inlier, -1 for outlier. Convert to 0 for inlier, 1 for outlier
    y_pred = np.where(preds == -1, 1, 0)
    
    # Verify exact match between node logic and reproduction
    assert reported_count == int((y_pred == 1).sum()), "Reproduction mismatch with anomaly_node!"
    
    # Metrics
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    accuracy = (tp + tn) / len(y_true) if len(y_true) > 0 else 0.0
    
    results = {
        "scenario": scenario_name,
        "n_samples": len(y_true),
        "true_anomalies": int(y_true.sum()),
        "true_anomaly_rate": float(y_true.sum() / len(y_true)),
        "predicted_anomalies": reported_count,
        "reported_percentage": reported_pct,
        "confusion_matrix": {
            "TP": tp,
            "FP": fp,
            "TN": tn,
            "FN": fn
        },
        "metrics": {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "false_positive_rate": round(fpr, 4),
            "accuracy": round(accuracy, 4)
        }
    }
    return results

def run_anomaly_benchmarks():
    print("=" * 70)
    print("🔬 ANOMALY DETECTION BENCHMARK SUITE (Isolation Forest)")
    print("=" * 70)
    
    scenarios = ["0pct_clean", "2pct", "5pct", "10pct", "15pct"]
    all_results = {}
    
    for sc in scenarios:
        res = evaluate_scenario(sc)
        all_results[sc] = res
        m = res["metrics"]
        cm = res["confusion_matrix"]
        print(f"\nScenario: {sc.upper()}")
        print(f"  Samples: {res['n_samples']} | True Anomalies: {res['true_anomalies']} ({res['true_anomaly_rate']*100:.1f}%) | Flagged: {res['predicted_anomalies']}")
        print(f"  Confusion Matrix: TP={cm['TP']}, FP={cm['FP']}, TN={cm['TN']}, FN={cm['FN']}")
        print(f"  Precision: {m['precision']:.4f} | Recall: {m['recall']:.4f} | F1: {m['f1_score']:.4f} | FPR: {m['false_positive_rate']:.4f}")
        
    return all_results

if __name__ == "__main__":
    results = run_anomaly_benchmarks()
    out_file = os.path.join(os.path.dirname(__file__), "anomaly_benchmark_results.json")
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_file}")
