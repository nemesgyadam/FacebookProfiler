"""
Ads Data Parser - Critical for reverse-engineering Facebook's psychological profile
Extracts Facebook's own psychological categorization from advertising data
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .json_parser import FacebookDataParser
from ..models.behavioral_vectors import FacebookPsychProfile, PsychologicalVulnerability


class AdsDataParser(FacebookDataParser):
    """Parser for ads_information directory - Facebook's psychological assessment"""
    
    def __init__(self, data_root: Path):
        super().__init__(data_root)
        self.ads_dir = self.data_root / 'ads_information'
        self.logger = logging.getLogger(__name__)
        
    def parse_ad_preferences(self) -> Dict[str, Any]:
        """
        Parse ad_preferences.json - User's advertising preferences
        Shows what Facebook thinks you're interested in
        """
        file_path = self.ads_dir / 'ad_preferences.json'
        data = self.safe_load_json(file_path)
        
        if not data:
            return {}
            
        preferences = {
            'interests': [],
            'advertisers': [],
            'categories': []
        }
        
        # Extract interests that Facebook identified
        for item in data.get('topics_v2', []):
            if 'name' in item:
                preferences['interests'].append(item['name'])
                
        # Extract advertiser preferences
        for item in data.get('advertisers_v2', []):
            if 'name' in item:
                preferences['advertisers'].append(item['name'])
                
        return preferences
        
    def parse_advertisers_using_data(self) -> Dict[str, Any]:
        """
        Parse advertisers_using_your_activity_or_information.json
        CRITICAL FILE: Shows Facebook's psychological categorization
        """
        file_path = self.ads_dir / 'advertisers_using_your_activity_or_information.json'
        data = self.safe_load_json(file_path)
        
        if not data:
            return {}
            
        psychological_categories = {
            'custom_audiences': [],
            'behavioral_targeting': [],
            'demographic_targeting': [],
            'interest_targeting': [],
            'vulnerability_indicators': []
        }
        
        # Extract custom audience data - most revealing for psychology
        for audience in data.get('custom_audiences_v2', []):
            advertiser_name = audience.get('advertiser_name', 'Unknown')
            has_data_file = audience.get('has_data_file_custom_audience', False)
            
            psychological_categories['custom_audiences'].append({
                'advertiser': advertiser_name,
                'has_personal_data': has_data_file,
                'targeting_method': self._infer_targeting_psychology(advertiser_name)
            })
            
        return psychological_categories
        
    def _infer_targeting_psychology(self, advertiser_name: str) -> Dict[str, float]:
        """
        Infer psychological targeting from advertiser name/category
        Maps to OCEAN personality traits and vulnerabilities
        """
        name_lower = advertiser_name.lower()
        
        psychology_mapping = {
            'openness': 0.0,
            'conscientiousness': 0.0, 
            'extraversion': 0.0,
            'agreeableness': 0.0,
            'neuroticism': 0.0,
            'vulnerability_type': None
        }
        
        # Openness indicators
        if any(word in name_lower for word in ['art', 'travel', 'culture', 'music', 'creative', 'design']):
            psychology_mapping['openness'] = 0.8
            
        # Conscientiousness indicators  
        if any(word in name_lower for word in ['productivity', 'organization', 'planning', 'finance', 'investment']):
            psychology_mapping['conscientiousness'] = 0.8
            
        # Extraversion indicators
        if any(word in name_lower for word in ['social', 'party', 'event', 'networking', 'dating']):
            psychology_mapping['extraversion'] = 0.8
            
        # Agreeableness indicators
        if any(word in name_lower for word in ['charity', 'family', 'community', 'volunteer', 'caring']):
            psychology_mapping['agreeableness'] = 0.8
            
        # Neuroticism/vulnerability indicators
        if any(word in name_lower for word in ['anxiety', 'stress', 'health', 'insurance', 'security', 'therapy']):
            psychology_mapping['neuroticism'] = 0.8
            psychology_mapping['vulnerability_type'] = 'emotional_vulnerability'
            
        # Financial vulnerability
        if any(word in name_lower for word in ['loan', 'debt', 'credit', 'payday', 'financial_help']):
            psychology_mapping['vulnerability_type'] = 'financial_vulnerability'
            
        return psychology_mapping
        
    def parse_advertisers_interacted_with(self) -> List[Dict[str, Any]]:
        """
        Parse advertisers_you've_interacted_with.json
        Shows actual engagement with psychological targeting
        """
        file_path = self.ads_dir / 'advertisers_you've_interacted_with.json'
        data = self.safe_load_json(file_path)
        
        if not data:
            return []
            
        interactions = []
        for item in data.get('history_v2', []):
            interaction = {
                'advertiser': item.get('advertiser_name', 'Unknown'),
                'action': item.get('action', 'Unknown'),
                'timestamp': self.parse_facebook_timestamp(item.get('timestamp'))
            }
            interactions.append(interaction)
            
        return interactions
        
    def parse_other_targeting_categories(self) -> Dict[str, List[str]]:
        """
        Parse other_categories_used_to_reach_you.json
        Additional psychological categorization by Facebook
        """
        file_path = self.ads_dir / 'other_categories_used_to_reach_you.json'
        data = self.safe_load_json(file_path)
        
        if not data:
            return {}
            
        categories = {
            'interests': [],
            'behaviors': [],
            'demographics': []
        }
        
        for category in data.get('other_categories_v2', []):
            category_name = category.get('category', '')
            if 'interest' in category_name.lower():
                categories['interests'].append(category_name)
            elif 'behavior' in category_name.lower():
                categories['behaviors'].append(category_name)
            else:
                categories['demographics'].append(category_name)
                
        return categories
        
    def extract_facebook_psychological_profile(self) -> FacebookPsychProfile:
        """
        Main method: Extract Facebook's complete psychological assessment
        This is the reverse-engineering of their targeting system
        """
        profile = FacebookPsychProfile()
        
        # Get ad preferences (what Facebook thinks you like)
        preferences = self.parse_ad_preferences()
        profile.inferred_interests = {
            interest: 1.0 for interest in preferences.get('interests', [])
        }
        
        # Get advertisers using your data (psychological categories)
        advertiser_data = self.parse_advertisers_using_data()
        profile.behavioral_segments = []
        
        for audience in advertiser_data.get('custom_audiences', []):
            psychology = audience.get('targeting_method', {})
            advertiser = audience.get('advertiser', '')
            
            # Identify high-confidence psychological categorizations
            for trait, score in psychology.items():
                if isinstance(score, float) and score > 0.6:
                    profile.behavioral_segments.append(f"{trait}_{score:.1f}_{advertiser}")
                    
            # Identify vulnerability exploitation
            if psychology.get('vulnerability_type'):
                vuln_type = psychology['vulnerability_type']
                profile.vulnerability_windows.append((
                    datetime.now(),  # We don't have exact timing
                    f"{vuln_type}_targeting_by_{advertiser}"
                ))
                
        # Get interaction patterns (engagement with psychological targeting)
        interactions = self.parse_advertisers_interacted_with()
        engagement_patterns = {}
        
        for interaction in interactions:
            advertiser = interaction['advertiser']
            action = interaction['action']
            
            key = f"{advertiser}_{action}"
            engagement_patterns[key] = engagement_patterns.get(key, 0) + 1
            
        profile.ad_engagement_patterns = engagement_patterns
        
        # Get additional targeting categories
        other_categories = self.parse_other_targeting_categories()
        for category_type, categories in other_categories.items():
            profile.targeting_categories.extend([
                f"{category_type}:{cat}" for cat in categories
            ])
            
        return profile
        
    def identify_manipulation_vulnerabilities(self) -> List[PsychologicalVulnerability]:
        """
        Identify psychological vulnerabilities Facebook exploited
        Based on targeting patterns and advertiser types
        """
        vulnerabilities = []
        
        # Parse advertiser data to find vulnerability exploitation
        advertiser_data = self.parse_advertisers_using_data()
        
        vulnerability_patterns = {
            'emotional_vulnerability': [
                'anxiety', 'depression', 'stress', 'therapy', 'counseling', 'mental health'
            ],
            'financial_vulnerability': [
                'loan', 'debt', 'credit repair', 'payday', 'financial assistance'
            ],
            'social_vulnerability': [
                'dating', 'loneliness', 'social skills', 'relationship advice'
            ],
            'health_anxiety': [
                'medical', 'symptoms', 'disease', 'treatment', 'healthcare'
            ]
        }
        
        for audience in advertiser_data.get('custom_audiences', []):
            advertiser = audience.get('advertiser', '').lower()
            
            for vuln_type, keywords in vulnerability_patterns.items():
                if any(keyword in advertiser for keyword in keywords):
                    vulnerability = PsychologicalVulnerability(
                        vulnerability_type=vuln_type,
                        severity=0.8,  # High if Facebook targeted you for this
                        triggers=[advertiser],
                        exploitation_evidence=[f"Targeted by {audience.get('advertiser', '')}"],
                        timing_patterns=[]  # Would need more data for timing
                    )
                    vulnerabilities.append(vulnerability)
                    
        return vulnerabilities
