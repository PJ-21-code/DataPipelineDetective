import os
import json
import numpy as np
import pandas as pd

np.random.seed(42)

BENCHMARK_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BENCHMARK_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

def generate_anomaly_dataset(n_samples=1000, anomaly_rate=0.05, n_features=4, scenario_name="5pct"):
    """
    Generate synthetic dataset with known ground truth anomalies for Isolation Forest evaluation.
    Normal data: Gaussian distribution ~ N(50, 10)
    Anomalies: Uniformly distributed across extreme ranges [150, 300] or [-100, -20]
    """
    n_anomalies = int(n_samples * anomaly_rate)
    n_inliers = n_samples - n_anomalies
    
    # Inliers
    X_inliers = np.random.normal(loc=50.0, scale=10.0, size=(n_inliers, n_features))
    y_inliers = np.zeros(n_inliers, dtype=int)
    
    # Outliers
    if n_anomalies > 0:
        # Mix of high and low extreme values
        high_outliers = np.random.uniform(low=120.0, high=250.0, size=(n_anomalies // 2, n_features))
        low_outliers = np.random.uniform(low=-100.0, high=-10.0, size=(n_anomalies - (n_anomalies // 2), n_features))
        X_outliers = np.vstack([high_outliers, low_outliers])
        y_outliers = np.ones(n_anomalies, dtype=int)
        
        X = np.vstack([X_inliers, X_outliers])
        y = np.concatenate([y_inliers, y_outliers])
    else:
        X = X_inliers
        y = y_inliers
        
    # Shuffle
    indices = np.arange(n_samples)
    np.random.shuffle(indices)
    X = X[indices]
    y = y[indices]
    
    col_names = [f"feature_{i+1}" for i in range(n_features)]
    df = pd.DataFrame(X, columns=col_names)
    
    # Save CSV without label column (matching production input)
    csv_path = os.path.join(DATA_DIR, f"anomaly_synth_{scenario_name}.csv")
    df.to_csv(csv_path, index=False)
    
    # Save ground truth labels separately
    meta_path = os.path.join(DATA_DIR, f"anomaly_synth_{scenario_name}_labels.json")
    with open(meta_path, "w") as f:
        json.dump({
            "n_samples": n_samples,
            "anomaly_rate": anomaly_rate,
            "n_anomalies": n_anomalies,
            "n_inliers": n_inliers,
            "ground_truth": y.tolist()
        }, f, indent=2)
        
    print(f"Generated {csv_path}: {n_samples} rows, {n_anomalies} anomalies ({anomaly_rate*100:.1f}%)")
    return csv_path, y

def generate_performance_datasets():
    """Generate datasets of sizes 100, 1,000, and 10,000 for scalability benchmarking."""
    sizes = [100, 1000, 10000]
    paths = {}
    
    for n in sizes:
        user_ids = np.arange(1, n + 1)
        names = [f"user_{i}" for i in user_ids]
        scores = np.random.normal(75.0, 12.0, size=n).round(2)
        amounts = np.random.exponential(scale=100.0, size=n).round(2)
        latencies = np.random.gamma(shape=2.0, scale=15.0, size=n).round(2)
        
        # Inject standard 2% duplicates and 1% nulls to simulate realistic pipeline load
        df = pd.DataFrame({
            "user_id": user_ids,
            "name": names,
            "score": scores,
            "amount": amounts,
            "latency_ms": latencies
        })
        
        # Inject 2% duplicates
        n_dupes = max(1, int(n * 0.02))
        dupe_rows = df.sample(n=n_dupes, random_state=42)
        df = pd.concat([df, dupe_rows], ignore_index=True)
        
        # Inject nulls
        n_nulls = max(1, int(n * 0.01))
        null_indices = np.random.choice(len(df), size=n_nulls, replace=False)
        df.loc[null_indices, "score"] = np.nan
        
        csv_path = os.path.join(DATA_DIR, f"perf_{n}.csv")
        df.to_csv(csv_path, index=False)
        paths[n] = csv_path
        print(f"Generated {csv_path}: {len(df)} total rows (base {n} + {n_dupes} dupes, {n_nulls} nulls)")
        
    return paths

def generate_routing_datasets():
    """Generate strictly clean and deliberately corrupted datasets for routing verification."""
    # 1. Clean dataset: pristine, no nulls, no duplicates, normal values within 2 sigma
    n = 500
    clean_df = pd.DataFrame({
        "transaction_id": [f"TXN-{10000+i}" for i in range(n)],
        "account_id": [f"ACC-{5000+i}" for i in range(n)],
        "amount": np.random.uniform(10.0, 500.0, size=n).round(2),
        "fee": np.random.uniform(1.0, 15.0, size=n).round(2)
    })
    clean_path = os.path.join(DATA_DIR, "routing_clean.csv")
    clean_df.to_csv(clean_path, index=False)
    
    # 2. Corrupted dataset: has duplicates, nulls, and extreme outliers
    corrupt_df = clean_df.copy()
    # 10 duplicates
    corrupt_df = pd.concat([corrupt_df, corrupt_df.iloc[:10]], ignore_index=True)
    # 15 nulls in amount
    corrupt_df.loc[20:34, "amount"] = np.nan
    # 5 extreme outliers
    corrupt_df.loc[50:54, "amount"] = 9999999.99
    
    corrupt_path = os.path.join(DATA_DIR, "routing_corrupted.csv")
    corrupt_df.to_csv(corrupt_path, index=False)
    
    print(f"Generated {clean_path} (clean) and {corrupt_path} (corrupted)")
    return clean_path, corrupt_path

def generate_sql_remediation_datasets():
    """Generate specific test matrices for SQL fix and validation verification."""
    # Test A: Pure Duplicates
    df_dupes = pd.DataFrame({
        "record_id": [1, 2, 2, 3, 4, 4, 4, 5, 6, 7],
        "category": ["A", "B", "B", "C", "D", "D", "D", "E", "F", "G"],
        "metric": [10.5, 20.0, 20.0, 30.1, 40.0, 40.0, 40.0, 50.2, 60.0, 70.0]
    })
    p_dupes = os.path.join(DATA_DIR, "remediation_duplicates.csv")
    df_dupes.to_csv(p_dupes, index=False)
    
    # Test B: Pure Nulls
    df_nulls = pd.DataFrame({
        "id": list(range(1, 11)),
        "col_int": [1, 2, np.nan, 4, 5, np.nan, 7, 8, 9, 10],
        "col_str": ["alpha", "beta", "gamma", None, "epsilon", "zeta", "eta", None, "iota", "kappa"],
        "col_float": [1.1, np.nan, 3.3, 4.4, 5.5, 6.6, np.nan, 8.8, 9.9, 10.0]
    })
    p_nulls = os.path.join(DATA_DIR, "remediation_nulls.csv")
    df_nulls.to_csv(p_nulls, index=False)
    
    # Test C: Mixed severe corruption (50 rows)
    n = 50
    ids = list(range(1, n + 1))
    vals = [float(i * 10) for i in ids]
    statuses = ["ACTIVE" if i % 2 == 0 else "PENDING" for i in ids]
    df_mixed = pd.DataFrame({"id": ids, "val": vals, "status": statuses})
    # Add 10 duplicates
    df_mixed = pd.concat([df_mixed, df_mixed.iloc[:10]], ignore_index=True)
    # Add nulls
    df_mixed.loc[15:20, "val"] = np.nan
    df_mixed.loc[25:28, "status"] = None
    p_mixed = os.path.join(DATA_DIR, "remediation_mixed.csv")
    df_mixed.to_csv(p_mixed, index=False)
    
    print(f"Generated SQL remediation test datasets in {DATA_DIR}")

def main():
    print("--- Generating Benchmark Datasets ---")
    generate_anomaly_dataset(1000, anomaly_rate=0.05, scenario_name="5pct")
    generate_anomaly_dataset(1000, anomaly_rate=0.02, scenario_name="2pct")
    generate_anomaly_dataset(1000, anomaly_rate=0.10, scenario_name="10pct")
    generate_anomaly_dataset(1000, anomaly_rate=0.15, scenario_name="15pct")
    generate_anomaly_dataset(1000, anomaly_rate=0.00, scenario_name="0pct_clean")
    generate_performance_datasets()
    generate_routing_datasets()
    generate_sql_remediation_datasets()
    print("All datasets successfully generated.\n")

if __name__ == "__main__":
    main()
