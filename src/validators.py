import re
import pandas as pd
from abc import ABC, abstractmethod

class BaseValidator(ABC):
    @property
    @abstractmethod
    def domain_name(self): pass

    @property
    @abstractmethod
    def column_patterns(self): pass

    def normalize(self, df: pd.DataFrame):
        """Finds columns via Regex and renames them to internal standard."""
        df_cols = df.columns.tolist()
        rename_map = {}
        found_internal_cols = []

        for internal, pattern in self.column_patterns.items():
            for col in df_cols:
                if re.search(pattern, col, re.IGNORECASE):
                    rename_map[col] = internal
                    found_internal_cols.append(internal)
                    break
        
        # Rename and keep only relevant columns
        clean_df = df.rename(columns=rename_map)
        # Filter to keep only mapped columns to avoid noise
        final_df = clean_df[list(rename_map.values())]
        
        return final_df, found_internal_cols

    def check_capabilities(self, found_cols: list) -> list:
        """Returns a list of fraud detection types possible with these columns."""
        caps = ["Basic Anomaly Detection"] # Default
        return caps

# --- Domain Specifics ---

class CreditCardValidator(BaseValidator):
    domain_name = "Credit Card"
    column_patterns = {
        "amt": r"amt|amount|val",
        "lat": r"^lat|cust_lat",
        "long": r"^long|cust_long",
        "merch_lat": r"merch.*lat",
        "merch_long": r"merch.*long",
        "time": r"time|date|trans_ts",
        "category": r"cat|merchant_type"
    }

    def check_capabilities(self, found_cols):
        caps = ["Amount Outlier Detection"]
        if "lat" in found_cols and "merch_lat" in found_cols:
            caps.append("Geospatial Analysis (Haversine)")
        if "time" in found_cols:
            caps.append("Velocity/Time Analysis")
        return caps

class MobileValidator(BaseValidator):
    domain_name = "Mobile Transaction"
    column_patterns = {
        "amount": r"amount|amt",
        "oldbalanceOrg": r"old.*orig",
        "newbalanceOrig": r"new.*orig",
        "oldbalanceDest": r"old.*dest",
        "newbalanceDest": r"new.*dest",
        "type": r"type|txn_type"
    }

    def check_capabilities(self, found_cols):
        caps = ["Large Transfer Detection"]
        if "oldbalanceOrg" in found_cols and "newbalanceOrig" in found_cols:
            caps.append("Origin Account Takeover Logic")
        if "oldbalanceDest" in found_cols:
            caps.append("Mule Account Detection")
        return caps

class LoanValidator(BaseValidator):
    domain_name = "Loan Application"
    column_patterns = {
        "credit": r"amt_credit|loan_amt",
        "annuity": r"amt_annuity|payment",
        "goods_price": r"goods_price",
        "days": r"days_decision"
    }

    def check_capabilities(self, found_cols):
        caps = ["Credit Limit Analysis"]
        if "credit" in found_cols and "annuity" in found_cols:
            caps.append("Affordability Ratio Analysis")
        if "goods_price" in found_cols:
            caps.append("Over-financing Detection")
        return caps