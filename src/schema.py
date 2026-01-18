# src/schema.py

DOMAIN_CONFIG = {
    "Credit Card": {
        "target": "is_fraud",
        "drop_cols": ["trans_date_trans_time", "cc_num", "unix_time", "trans_num"],
        "features": {
            # Define Min/Max for sliders here
            "numerical": {
                "amt": {"min": 0.0, "max": 5000.0, "step": 10.0},
                "lat": {"min": 20.0, "max": 50.0, "step": 0.1},
                "long": {"min": -125.0, "max": -65.0, "step": 0.1},
                "city_pop": {"min": 1000.0, "max": 1000000.0, "step": 1000.0},
                "merch_lat": {"min": 20.0, "max": 50.0, "step": 0.1},
                "merch_long": {"min": -125.0, "max": -65.0, "step": 0.1}
            },
            "categorical": ["category", "gender", "job"], 
            "flags": [] 
        }
    },
    "Loan Application": {
        "target": "NAME_CONTRACT_STATUS",
        "drop_cols": ["SK_ID_CURR", "SK_ID_PREV"], # ID columns confuse models
        "features": {
            "numerical": {
                "AMT_CREDIT": {"min": 10000.0, "max": 2000000.0, "step": 5000.0},
                "AMT_ANNUITY": {"min": 1000.0, "max": 100000.0, "step": 500.0},
                "AMT_GOODS_PRICE": {"min": 10000.0, "max": 2000000.0, "step": 5000.0},
                "DAYS_DECISION": {"min": -3000.0, "max": 0.0, "step": 1.0}, # Negative days
                "CNT_PAYMENT": {"min": 6.0, "max": 60.0, "step": 6.0}
            },
            "categorical": ["NAME_CONTRACT_TYPE", "NAME_CLIENT_TYPE"],
            "flags": ["NFLAG_INSURED_ON_APPROVAL"]
        }
    },
    "Mobile Transaction": {
        "target": "isFraud",
        # STRICTLY DROP 'isFlaggedFraud' -> It is a target leak!
        "drop_cols": ["nameOrig", "nameDest", "isFlaggedFraud"], 
        "features": {
            "numerical": {
                "amount": {"min": 0.0, "max": 1000000.0, "step": 1000.0},
                "oldbalanceOrg": {"min": 0.0, "max": 1000000.0, "step": 1000.0},
                "newbalanceOrig": {"min": 0.0, "max": 1000000.0, "step": 1000.0},
                "oldbalanceDest": {"min": 0.0, "max": 1000000.0, "step": 1000.0},
                "newbalanceDest": {"min": 0.0, "max": 1000000.0, "step": 1000.0},
                "step": {"min": 1.0, "max": 744.0, "step": 1.0} # Time steps
            },
            "categorical": ["type"],
            "flags": []
        }
    }
}