# src/ml_logic.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score

class FraudModel:
    def __init__(self, df, config, model_type="Random Forest"):
        self.raw_df = df
        self.config = config
        self.model_type = model_type
        self.encoders = {}
        self.feature_cols = []
        self.debug_info = {}
        
        # --- MODEL SELECTION LOGIC ---
        if self.model_type == "Random Forest":
            self.model = RandomForestClassifier(
                n_estimators=100, 
                max_depth=None, 
                random_state=42, 
                class_weight='balanced_subsample' # Excellent for fraud
            )
        elif self.model_type == "Gradient Boosting":
            # Gradient Boosting is more sensitive but often more precise
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
            # Note: Standard GBM in sklearn doesn't support 'class_weight' natively
            # so we often handle it by undersampling or tuning the threshold.

    def preprocess(self):
        df_clean = self.raw_df.copy().fillna(0)
        
        # 1. DROP FORBIDDEN COLS
        drop_list = self.config.get('drop_cols', [])
        df_clean = df_clean.drop(columns=[c for c in drop_list if c in df_clean.columns], errors='ignore')
        
        # 2. GET TARGET
        target = self.config['target']
        if target not in df_clean.columns:
            raise ValueError(f"Target '{target}' not found!")

        # Robust Target Cleaning
        y_raw = df_clean[target].astype(str).str.strip()
        df_clean[target] = y_raw.apply(lambda x: 1 if x in ['1', '1.0', 'Yes', 'True', 'Refused', 'Fraud', 'TARGET'] else 0)
        
        self.debug_info['class_distribution'] = df_clean[target].value_counts().to_dict()
        
        # 3. FEATURES
        nums = list(self.config['features']['numerical'].keys())
        cats = self.config['features']['categorical']
        flags = self.config['features']['flags']
        
        self.feature_cols = [c for c in nums + cats + flags if c in df_clean.columns]
        
        # Encode
        for col in cats:
            if col in df_clean.columns:
                le = LabelEncoder()
                df_clean[col] = le.fit_transform(df_clean[col].astype(str))
                self.encoders[col] = le
                
        return df_clean[self.feature_cols], df_clean[target]

    def train(self):
        X, y = self.preprocess()
        
        # Safety Check
        if 1 not in y.values:
            return {"error": "NO FRAUD FOUND in data subset."}

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)
        
        self.model.fit(X_train, y_train)
        
        # --- THRESHOLD TUNING ---
        # GBMs often output very low probabilities for everything, so we lower the bar.
        probs = self.model.predict_proba(X_test)[:, 1]
        threshold = 0.25  # Sensitivity tuning
        preds = (probs > threshold).astype(int)
        
        metrics = {
            "precision": precision_score(y_test, preds, zero_division=0),
            "recall": recall_score(y_test, preds, zero_division=0),
            "f1": f1_score(y_test, preds, zero_division=0),
            "importance": dict(zip(self.feature_cols, self.model.feature_importances_)),
            "debug": self.debug_info
        }
        return metrics

    def predict_single(self, input_dict):
        # (Same implementation as previous step...)
        row = pd.DataFrame([input_dict])
        for col, le in self.encoders.items():
            if col in row:
                val = str(row[col][0])
                if val in le.classes_:
                    row[col] = le.transform([val])[0]
                else:
                    row[col] = 0 
        
        for col in self.feature_cols:
            if col not in row:
                row[col] = 0
                
        return self.model.predict_proba(row[self.feature_cols])[0][1]
    
    def generate_advice(self, input_dict, current_risk):
        # (Same implementation as previous step...)
        advice = []
        if current_risk < 0.50: return ["Transaction looks safe."]
        
        for col in self.config['features']['numerical']:
            if col in input_dict:
                original_val = input_dict[col]
                if original_val <= 0: continue
                
                # Try reducing value
                test_inputs = input_dict.copy()
                test_inputs[col] = original_val * 0.7 # Reduce by 30%
                new_risk = self.predict_single(test_inputs)
                
                if new_risk < 0.50:
                    advice.append(f"Reducing **{col}** significantly lowers risk.")
                    break
        return advice if advice else ["Risk pattern is complex (Categorical)."]