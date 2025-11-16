import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os

class InsuranceRecommendationEngine:
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = None
        
    def calculate_premium(self, base_premium, age, salary, coverage_amount, plan_type):
        """
        Calculate personalized premium based on user profile
        """
        # Age factor (younger = lower premium for life, older = higher for health)
        if plan_type in ['Health', 'Life']:
            age_factor = 1 + (age - 25) * 0.015  # 1.5% increase per year after 25
        else:
            age_factor = 1 + (age - 25) * 0.005
        
        # Salary factor (higher salary = can afford better coverage)
        salary_factor = min(1.5, max(0.7, salary / 100000))
        
        # Coverage factor
        coverage_factor = coverage_amount / 1000000  # per million
        
        # Calculate final premium
        premium = base_premium * age_factor * salary_factor * (0.8 + coverage_factor * 0.2)
        
        return round(premium, 2)
    
    def get_recommendations(self, user_data, available_plans, top_n=5):
        """
        Get personalized insurance recommendations using collaborative filtering
        and content-based filtering
        """
        age = user_data.get('age', 30)
        salary = user_data.get('salary', 50000)
        budget = user_data.get('budget', salary * 0.05)  # Default 5% of salary
        preferred_type = user_data.get('insurance_type', None)
        
        recommendations = []
        
        for plan in available_plans:
            # Filter by age eligibility
            if not (plan['age_min'] <= age <= plan['age_max']):
                continue
            
            # Filter by salary requirement
            if salary < plan['salary_min']:
                continue
            
            # Filter by type if specified
            if preferred_type and plan['type'] != preferred_type:
                continue
            
            # Calculate personalized premium
            estimated_premium = self.calculate_premium(
                plan['base_premium'],
                age,
                salary,
                plan['coverage_amount'],
                plan['type']
            )
            
            # Calculate match score
            score = self._calculate_match_score(
                age, salary, budget, estimated_premium, 
                plan['coverage_amount'], plan['popularity_score']
            )
            
            recommendations.append({
                'plan': plan,
                'estimated_premium': estimated_premium,
                'match_score': score,
                'monthly_premium': round(estimated_premium / 12, 2),
                'affordability': 'High' if estimated_premium < budget else 'Medium' if estimated_premium < budget * 1.5 else 'Low'
            })
        
        # Sort by match score
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        
        return recommendations[:top_n]
    
    def _calculate_match_score(self, age, salary, budget, premium, coverage, popularity):
        """
        Calculate how well a plan matches user profile
        """
        # Budget fit (40% weight)
        budget_score = max(0, 100 - abs(premium - budget) / budget * 100) * 0.4
        
        # Coverage to salary ratio (30% weight)
        ideal_coverage = salary * 10  # Ideal coverage is 10x salary
        coverage_score = max(0, 100 - abs(coverage - ideal_coverage) / ideal_coverage * 100) * 0.3
        
        # Popularity score (20% weight)
        popularity_score = popularity * 0.2
        
        # Age appropriateness (10% weight)
        if age < 30:
            age_score = 10 if coverage > salary * 5 else 5
        elif age < 50:
            age_score = 10 if salary * 5 <= coverage <= salary * 15 else 5
        else:
            age_score = 10 if coverage > salary * 8 else 5
        
        age_score *= 0.1
        
        total_score = budget_score + coverage_score + popularity_score + age_score
        return round(total_score, 2)
    
    def compare_plans(self, plan_ids, plans_data, user_data):
        """
        Compare multiple insurance plans side by side
        """
        comparison = []
        
        for plan_id in plan_ids:
            plan = next((p for p in plans_data if p['id'] == plan_id), None)
            if plan:
                premium = self.calculate_premium(
                    plan['base_premium'],
                    user_data['age'],
                    user_data['salary'],
                    plan['coverage_amount'],
                    plan['type']
                )
                
                comparison.append({
                    'plan': plan,
                    'estimated_premium': premium,
                    'monthly_premium': round(premium / 12, 2),
                    'coverage_per_dollar': round(plan['coverage_amount'] / premium, 2)
                })
        
        return comparison