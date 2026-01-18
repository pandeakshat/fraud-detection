import numpy as np
import pandas as pd
from src.features import calculate_haversine

class AdvancedFraudEngine:
    """
    Multi-Factor Decision Engine.
    Each domain has a unique 'Pathway' of checks.
    """

    def analyze_transaction(self, inputs: dict, domain: str):
        # Initialize the scorecard
        score = 0
        factors = {}
        decision_type = "Fraud Risk" # Default label
        
        # --- PATHWAY 1: LOAN APPLICATION (Creditworthiness & Consistency) ---
        if domain == "Loan Application":
            decision_type = "Rejection Probability"
            
            # 1. Financial Stress Test (Weight: 40)
            # Logic: Is the annuity (yearly payment) too high for the credit?
            amt_credit = inputs.get('AMT_CREDIT', 1)
            amt_annuity = inputs.get('AMT_ANNUITY', 0)
            payment_ratio = amt_annuity / amt_credit if amt_credit > 0 else 0
            
            if payment_ratio > 0.15: # High interest/payment burden
                score += 30
                factors['High Payment Burden'] = f"Payment is {payment_ratio:.1%} of loan"
            
            # 2. Over-Financing Check (Weight: 30)
            # Logic: Are they asking for more money than the goods cost?
            goods_price = inputs.get('AMT_GOODS_PRICE', 1)
            if amt_credit > (goods_price * 1.2):
                score += 30
                factors['Over-Financing'] = "Loan > 120% of Goods Value"

            # 3. Behavioral/History (Weight: 30)
            days_decision = inputs.get('DAYS_DECISION', 0)
            # If they applied very recently (near 0) and were rejected before
            if -5 < days_decision < 0:
                score += 25
                factors['Rapid Re-application'] = "Applied within last 5 days"

        # --- PATHWAY 2: CREDIT CARD (Spatial & Contextual) ---
        elif domain == "Credit Card":
            decision_type = "Fraud Probability"
            
            # 1. Geospatial check (Weight: 50) - The biggest indicator
            lat, long = inputs.get('lat', 0), inputs.get('long', 0)
            m_lat, m_long = inputs.get('merch_lat', 0), inputs.get('merch_long', 0)
            
            dist = calculate_haversine(lat, long, m_lat, m_long)
            if dist > 800:
                score += 50
                factors['Impossible Travel'] = f"Merchant is {int(dist)}km away"
            elif dist > 100:
                score += 20
                factors['Unusual Distance'] = f"Merchant is {int(dist)}km away"

            # 2. Amount Context (Weight: 30)
            amt = inputs.get('amt', 0)
            category = inputs.get('category', 'unknown')
            
            # Thresholds based on category (Simulation of historical averages)
            thresholds = {'grocery': 200, 'travel': 3000, 'tech': 1500}
            limit = thresholds.get(category, 500)
            
            if amt > limit:
                score += 30
                factors['Amount Spikes'] = f"${amt} exceeds {category} avg"

        # --- PATHWAY 3: MOBILE (Account Integrity) ---
        elif domain == "Mobile Transaction":
            decision_type = "Account Compromise Risk"
            
            # 1. The "Drain" Pattern (Weight: 60)
            old_bal = inputs.get('oldbalanceOrg', 0)
            new_bal = inputs.get('newbalanceOrig', 0)
            amount = inputs.get('amount', 0)
            
            if old_bal > 0 and new_bal == 0:
                score += 60
                factors['Wallet Drain'] = "Account completely emptied"
            
            # 2. The "Math Error" (Backend Manipulation) (Weight: 40)
            expected_new = old_bal - amount
            if abs(expected_new - new_bal) > 1.0:
                score += 40
                factors['Balance Mismatch'] = "Server-side math error detected"

        # Final Cap
        score = min(score, 100)
        
        return {
            "score": score,
            "type": decision_type,
            "factors": factors,
            "action": "BLOCK" if score > 75 else ("MANUAL REVIEW" if score > 40 else "APPROVE")
        }