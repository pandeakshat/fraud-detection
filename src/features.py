import numpy as np
import pandas as pd

def calculate_haversine(lat1, lon1, lat2, lon2):
    """Calculates distance in KM between two lat/long points."""
    R = 6371
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R * c

def calculate_ratios(df):
    """Safe division for financial ratios."""
    # Avoid div by zero
    if 'goods_price' in df.columns and 'credit' in df.columns:
        df['credit_goods_ratio'] = df['credit'] / (df['goods_price'] + 1.0)
    
    if 'annuity' in df.columns and 'credit' in df.columns:
        df['payment_rate'] = df['annuity'] / (df['credit'] + 1.0)
    
    return df