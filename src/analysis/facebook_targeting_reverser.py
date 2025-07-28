"""
Facebook Targeting Reverse Engineer - Maps Facebook's psychological categorization
Decodes how Facebook classified user psychology from advertising data
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from ..models.behavioral_vectors import OceanTraits, FacebookPsychProfile


class FacebookTargetingReverseEngineer:
    """Reverse engineer Facebook's psychological targeting system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Facebook's psychology mapping based on their targeting categories
        self.FACEBOOK_PSYCHOLOGY_MAP = {
            'interests': {
                'technology': {'openness': 0.8, 'conscientiousness': 0.6},
                'fitness': {'conscientiousness': 0.9, 'neuroticism': -0.3},
                'luxury_brands': {'openness': 0.7, 'neuroticism': 0.4},
                'art': {'openness': 0.9, 'agreeableness': 0.6},
                'travel': {'openness': 0.9, 'extraversion': 0.7},
                'music': {'openness': 0.8, 'extraversion': 0.5},
                'food': {'agreeableness': 0.6, 'openness': 0.5},
                'sports': {'extraversion': 0.7, 'conscientiousness': 0.6},
                'politics': {'openness': 0.6, 'neuroticism': 0.5},
                'fashion': {'openness': 0.7, 'extraversion': 0.6}
            },
            'behaviors': {
                'frequent_travelers': {'openness': 0.9, 'extraversion': 0.7},
                'mobile_device_users': {'openness': 0.6, 'conscientiousness': 0.5},
                'online_shoppers': {'conscientiousness': -0.3, 'neuroticism': 0.4},
                'social_media_users': {'extraversion': 0.8, 'neuroticism': 0.3},
                'gamers': {'openness': 0.6, 'conscientiousness': -0.2},
                'early_adopters': {'openness': 0.9, 'conscientiousness': 0.5}
            },
            'demographics': {
                'relationship_status_single': {'neuroticism': 0.3, 'extraversion': -0.2},
                'relationship_status_married': {'agreeableness': 0.6, 'conscientiousness': 0.7},
                'education_college': {'openness': 0.7, 'conscientiousness': 0.6},
                'education_high_school': {'openness': -0.3, 'conscientiousness': -0.2},
                'parent': {'agreeableness': 0.8, 'conscientiousness': 0.7},
                'new_job': {'conscientiousness': 0.6, 'neuroticism': 0.4}
            },
            'vulnerabilities': {
                'anxiety_health': {'neuroticism': 0.9, 'vulnerability': 'health_anxiety'},
                'financial_stress': {'neuroticism': 0.8, 'vulnerability': 'financial_vulnerability'},
                'relationship_issues': {'neuroticism': 0.7, 'vulnerability': 'emotional_vulnerability'},
                'career_uncertainty': {'neuroticism': 0.6, 'vulnerability': 'professional_insecurity'},
                'social_isolation': {'extraversion': -0.8, 'vulnerability': 'social_vulnerability'}
            }
        }
        
    def reverse_engineer_facebook_psychology(self, fb_profile: FacebookPsychProfile) -> OceanTraits:
        """
        Reverse engineer Facebook's psychological assessment from targeting data
        Returns Facebook's inferred OCEAN personality traits
        """
        traits = OceanTraits()
        trait_contributions = {
            'openness': [],
            'conscientiousness': [],
            'extraversion': [],
            'agreeableness': [],
            'neuroticism': []
        }
        
        # Analyze interests
        for interest, confidence in fb_profile.inferred_interests.items():
            psychology = self._map_interest_to_psychology(interest)
            for trait, score in psychology.items():
                if trait in trait_contributions:
                    trait_contributions[trait].append(score * confidence)
                    
        # Analyze behavioral segments
        for segment in fb_profile.behavioral_segments:
            psychology = self._map_segment_to_psychology(segment)
            for trait, score in psychology.items():
                if trait in trait_contributions:
                    trait_contributions[trait].append(score)
                    
        # Analyze targeting categories
        for category in fb_profile.targeting_categories:
            psychology = self._map_category_to_psychology(category)
            for trait, score in psychology.items():
                if trait in trait_contributions:
                    trait_contributions[trait].append(score)
                    
        # Calculate average trait scores
        for trait, scores in trait_contributions.items():
            if scores:
                avg_score = sum(scores) / len(scores)
                # Normalize to 0-1 range and handle negative scores
                normalized_score = max(0.0, min(1.0, (avg_score + 1.0) / 2.0))
                setattr(traits, trait, normalized_score)
                
        # Set confidence scores
        traits.confidence = {
            trait: min(1.0, len(scores) * 0.1) for trait, scores in trait_contributions.items()
        }
        
        return traits
    
    def _map_interest_to_psychology(self, interest: str) -> Dict[str, float]:
        """Map Facebook interest to psychological traits"""
        interest_lower = interest.lower()
        psychology = {}
        
        for category, traits in self.FACEBOOK_PSYCHOLOGY_MAP['interests'].items():
            if category in interest_lower or any(keyword in interest_lower for keyword in category.split('_')):
                psychology.update(traits)
                break
                
        return psychology
    
    def _map_segment_to_psychology(self, segment: str) -> Dict[str, float]:
        """Map Facebook behavioral segment to psychological traits"""
        segment_lower = segment.lower()
        psychology = {}
        
        # Parse segment format: "trait_score_advertiser"
        if '_' in segment:
            parts = segment.split('_')
            if len(parts) >= 2:
                trait = parts[0]
                try:
                    score = float(parts[1])
                    if trait in ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
                        psychology[trait] = score
                except ValueError:
                    pass
                    
        # Also check behavior patterns
        for category, traits in self.FACEBOOK_PSYCHOLOGY_MAP['behaviors'].items():
            if category in segment_lower:
                psychology.update(traits)
                break
                
        return psychology
    
    def _map_category_to_psychology(self, category: str) -> Dict[str, float]:
        """Map Facebook targeting category to psychological traits"""
        category_lower = category.lower()
        psychology = {}
        
        # Check all category types
        for category_type, category_mappings in self.FACEBOOK_PSYCHOLOGY_MAP.items():
            if category_type in ['interests', 'behaviors', 'demographics']:
                for cat_name, traits in category_mappings.items():
                    if cat_name in category_lower or any(keyword in category_lower for keyword in cat_name.split('_')):
                        psychology.update(traits)
                        
        return psychology
    
    def identify_facebook_manipulation_tactics(self, fb_profile: FacebookPsychProfile) -> Dict[str, List[str]]:
        """
        Identify specific manipulation tactics Facebook used based on targeting
        """
        tactics = {
            'emotional_manipulation': [],
            'social_pressure': [],
            'scarcity_tactics': [],
            'authority_appeals': [],
            'vulnerability_exploitation': []
        }
        
        # Analyze vulnerability windows for manipulation timing
        for timestamp, vulnerability_description in fb_profile.vulnerability_windows:
            if 'emotional' in vulnerability_description:
                tactics['emotional_manipulation'].append(
                    f"Targeted during emotional vulnerability: {vulnerability_description}"
                )
            elif 'financial' in vulnerability_description:
                tactics['vulnerability_exploitation'].append(
                    f"Exploited financial stress: {vulnerability_description}"
                )
                
        # Analyze ad engagement patterns for manipulation effectiveness
        for interaction, count in fb_profile.ad_engagement_patterns.items():
            if count > 5:  # High engagement indicates effective manipulation
                if 'anxiety' in interaction.lower() or 'stress' in interaction.lower():
                    tactics['emotional_manipulation'].append(
                        f"High engagement with anxiety-inducing content: {interaction}"
                    )
                elif 'social' in interaction.lower():
                    tactics['social_pressure'].append(
                        f"Responded to social pressure tactics: {interaction}"
                    )
                    
        # Analyze targeting categories for manipulation methods
        for category in fb_profile.targeting_categories:
            category_lower = category.lower()
            
            if any(word in category_lower for word in ['urgent', 'limited', 'exclusive', 'now']):
                tactics['scarcity_tactics'].append(f"Scarcity-based targeting: {category}")
            elif any(word in category_lower for word in ['expert', 'doctor', 'certified', 'professional']):
                tactics['authority_appeals'].append(f"Authority-based targeting: {category}")
            elif any(word in category_lower for word in ['lonely', 'single', 'isolated', 'struggling']):
                tactics['vulnerability_exploitation'].append(f"Loneliness exploitation: {category}")
                
        return tactics
    
    def calculate_manipulation_susceptibility(self, fb_profile: FacebookPsychProfile, 
                                           actual_traits: OceanTraits) -> Dict[str, float]:
        """
        Calculate susceptibility to different manipulation types
        Based on personality traits and Facebook's targeting success
        """
        susceptibility = {
            'emotional_manipulation': 0.0,
            'social_proof': 0.0,
            'authority_appeals': 0.0,
            'scarcity_tactics': 0.0,
            'personalization_bias': 0.0
        }
        
        # Base susceptibility on personality traits
        if actual_traits.neuroticism > 0.6:
            susceptibility['emotional_manipulation'] += 0.4
            
        if actual_traits.extraversion > 0.7:
            susceptibility['social_proof'] += 0.4
            
        if actual_traits.conscientiousness < 0.4:
            susceptibility['scarcity_tactics'] += 0.3
            
        if actual_traits.openness > 0.7:
            susceptibility['personalization_bias'] += 0.3
            
        if actual_traits.agreeableness > 0.7:
            susceptibility['authority_appeals'] += 0.3
            
        # Increase susceptibility based on Facebook's targeting success
        for interaction, count in fb_profile.ad_engagement_patterns.items():
            normalized_engagement = min(1.0, count / 10.0)  # Normalize engagement
            
            if 'emotional' in interaction.lower():
                susceptibility['emotional_manipulation'] += normalized_engagement * 0.2
            elif 'social' in interaction.lower():
                susceptibility['social_proof'] += normalized_engagement * 0.2
                
        # Cap all susceptibility scores at 1.0
        for key in susceptibility:
            susceptibility[key] = min(1.0, susceptibility[key])
            
        return susceptibility
    
    def generate_targeting_resistance_strategies(self, 
                                               manipulation_tactics: Dict[str, List[str]],
                                               susceptibility: Dict[str, float]) -> List[str]:
        """
        Generate personalized strategies to resist manipulation based on identified tactics
        """
        strategies = []
        
        # Strategies for high emotional manipulation susceptibility
        if susceptibility.get('emotional_manipulation', 0) > 0.6:
            strategies.append("Implement emotional decision-making delays: Wait 24 hours before acting on emotionally charged content")
            strategies.append("Create emotional state awareness check: Ask 'How am I feeling right now?' before engaging with ads")
            
        # Strategies for high social proof susceptibility  
        if susceptibility.get('social_proof', 0) > 0.6:
            strategies.append("Question social validation: Ask 'Do I actually want this, or do I want to fit in?'")
            strategies.append("Seek diverse perspectives: Actively look for counter-opinions before making decisions")
            
        # Strategies for authority appeal susceptibility
        if susceptibility.get('authority_appeals', 0) > 0.6:
            strategies.append("Verify credentials: Check the actual qualifications of 'experts' in ads")
            strategies.append("Seek second opinions: Consult multiple sources before trusting authority figures")
            
        # Strategies for scarcity tactic susceptibility
        if susceptibility.get('scarcity_tactics', 0) > 0.6:
            strategies.append("Implement scarcity immunity: Ask 'Will I still want this in a week?'")
            strategies.append("Research alternatives: Always look for similar options when feeling time pressure")
            
        # Strategies for personalization bias
        if susceptibility.get('personalization_bias', 0) > 0.6:
            strategies.append("Recognize filter bubbles: Actively seek content outside your usual interests")
            strategies.append("Question 'perfect' matches: Be suspicious when something seems too perfectly targeted")
            
        # Add tactics-specific strategies
        if manipulation_tactics.get('vulnerability_exploitation'):
            strategies.append("Vulnerability protection: Avoid decision-making during stressful periods")
            strategies.append("Create support networks: Have trusted people to consult during vulnerable times")
            
        return strategies
