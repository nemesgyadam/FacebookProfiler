"""
Digital Psychometrics Engine - Core behavioral vector extraction
Combines all analysis modules to extract comprehensive psychological profile
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..parsers import FacebookDataParser, AdsDataParser, ActivityDataParser
from ..models.behavioral_vectors import (
    BehaviorVector,
    OceanTraits,
    CompletePsychologicalProfile,
    FacebookPsychProfile
)


class DigitalPsychometricsEngine:
    """Main engine for extracting behavioral vectors from Facebook data"""
    
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.logger = logging.getLogger(__name__)
        
        # Initialize parsers
        self.base_parser = FacebookDataParser(self.data_path)
        self.ads_parser = AdsDataParser(self.data_path)
        self.activity_parser = ActivityDataParser(self.data_path)
        
        # Validate data structure
        self.data_validation = self.base_parser.validate_facebook_data_structure()
        
    def extract_behavioral_vectors(self) -> List[BehaviorVector]:
        """
        Extract behavioral vectors from all data sources
        Returns time-series of behavioral snapshots
        """
        vectors = []
        
        # Cognitive vectors from ad preferences and interests
        cognitive_vector = self._extract_cognitive_vectors()
        
        # Affective vectors from message/post content emotional analysis
        affective_vectors = self._extract_affective_vectors()
        
        # Conative vectors from behavioral patterns and actions
        conative_vectors = self._extract_conative_vectors()
        
        # Combine into behavioral vectors with timestamps
        for i, affective in enumerate(affective_vectors):
            vector = BehaviorVector(
                cognitive=cognitive_vector,
                affective=affective['emotions'],
                conative=conative_vectors.get(i, {}),
                timestamp=affective.get('timestamp'),
                confidence=0.7  # Base confidence score
            )
            vectors.append(vector)
            
        return vectors
    
    def _extract_cognitive_vectors(self) -> Dict[str, float]:
        """
        Extract cognitive behavioral vectors (beliefs, interests, values)
        Primarily from ads_information directory
        """
        cognitive = {}
        
        if not self.data_validation.get('ads_information', False):
            self.logger.warning("ads_information directory not found")
            return cognitive
            
        # Extract Facebook's assessment of user interests and beliefs
        fb_profile = self.ads_parser.extract_facebook_psychological_profile()
        
        # Map Facebook's interest categories to cognitive traits
        for interest, confidence in fb_profile.inferred_interests.items():
            # Normalize interest names and map to psychological constructs
            normalized_interest = self._normalize_interest_category(interest)
            cognitive[f"interest_{normalized_interest}"] = confidence
            
        # Extract value systems from targeted content categories
        for category in fb_profile.targeting_categories:
            if ':' in category:
                category_type, category_name = category.split(':', 1)
                values = self._infer_values_from_category(category_name)
                for value, strength in values.items():
                    cognitive[f"value_{value}"] = cognitive.get(f"value_{value}", 0) + strength
                    
        return cognitive
    
    def _extract_affective_vectors(self) -> List[Dict[str, Any]]:
        """
        Extract affective behavioral vectors (emotional states, mood patterns)
        From messages, posts, and activity timeline
        """
        affective_timeline = []
        
        if not self.data_validation.get('your_facebook_activity', False):
            self.logger.warning("your_facebook_activity directory not found")
            return affective_timeline
            
        # Extract emotional timeline from messages
        message_data = self.activity_parser.parse_messages_data()
        
        for conversation in message_data.get('conversations', []):
            emotional_evolution = conversation.get('communication_analysis', {}).get('emotional_evolution', [])
            
            for emotion_point in emotional_evolution:
                emotions = emotion_point.get('emotions', {})
                
                # Convert raw emotional indicators to normalized affective state
                affective_state = {
                    'valence': self._calculate_valence(emotions),
                    'arousal': self._calculate_arousal(emotions),
                    'dominance': self._calculate_dominance(emotions),
                    'anxiety_level': emotions.get('anxiety_markers', 0),
                    'emotional_intensity': self._calculate_emotional_intensity(emotions)
                }
                
                affective_timeline.append({
                    'timestamp': emotion_point.get('timestamp'),
                    'emotions': affective_state,
                    'source': 'messages'
                })
        
        # Extract emotional patterns from posts
        posts_data = self.activity_parser.parse_posts_data()
        
        for post in posts_data.get('posts', []):
            emotional_analysis = post.get('emotional_analysis', {})
            
            affective_state = {
                'valence': self._calculate_valence(emotional_analysis),
                'arousal': self._calculate_arousal(emotional_analysis),
                'dominance': emotional_analysis.get('length', 0) / 100.0,  # Longer posts = more dominance
                'public_expression_level': 1.0,  # Posts are public expression
                'emotional_intensity': self._calculate_emotional_intensity(emotional_analysis)
            }
            
            affective_timeline.append({
                'timestamp': post.get('timestamp'),
                'emotions': affective_state,
                'source': 'posts'
            })
            
        # Sort by timestamp
        affective_timeline.sort(key=lambda x: x.get('timestamp') or datetime.min)
        
        return affective_timeline
    
    def _extract_conative_vectors(self) -> Dict[int, Dict[str, float]]:
        """
        Extract conative behavioral vectors (intent, actions, decision patterns)
        From interaction patterns, response behaviors, and decision indicators
        """
        conative_patterns = {}
        
        # Extract communication action patterns
        message_data = self.activity_parser.parse_messages_data()
        
        communication_actions = {
            'response_speed': 0.0,
            'initiation_tendency': 0.0,
            'conversation_persistence': 0.0,
            'help_seeking_behavior': 0.0
        }
        
        total_conversations = len(message_data.get('conversations', []))
        if total_conversations > 0:
            total_response_time = 0
            total_initiations = 0
            
            for conv in message_data.get('conversations', []):
                analysis = conv.get('communication_analysis', {})
                
                # Response speed (inverse of response time - faster = higher score)
                avg_response = analysis.get('avg_response_time', 3600)  # Default 1 hour
                if avg_response > 0:
                    total_response_time += 1.0 / (avg_response / 3600)  # Normalize to hours
                    
                # Initiation tendency
                user_messages = analysis.get('user_messages', 0)
                total_messages = analysis.get('total_messages', 1)
                if total_messages > 0:
                    total_initiations += user_messages / total_messages
                    
            communication_actions['response_speed'] = total_response_time / total_conversations
            communication_actions['initiation_tendency'] = total_initiations / total_conversations
            
        # Extract help-seeking and AI interaction patterns
        ai_conversations = message_data.get('ai_conversations', {})
        help_seeking = ai_conversations.get('help_seeking_behavior', {})
        communication_actions['help_seeking_behavior'] = help_seeking.get('frequency', 0) / 10.0  # Normalize
        
        # Extract decision patterns from ad interactions
        fb_profile = self.ads_parser.extract_facebook_psychological_profile()
        
        decision_patterns = {
            'impulsivity': 0.0,
            'risk_tolerance': 0.0,
            'social_influence_susceptibility': 0.0
        }
        
        # Analyze ad interaction patterns for decision-making traits
        for interaction_type, count in fb_profile.ad_engagement_patterns.items():
            if 'click' in interaction_type.lower():
                decision_patterns['impulsivity'] += count * 0.1
            elif 'purchase' in interaction_type.lower():
                decision_patterns['risk_tolerance'] += count * 0.2
                
        # Combine all conative patterns
        base_conative = {**communication_actions, **decision_patterns}
        
        # Return indexed conative patterns (could be time-based in future)
        conative_patterns[0] = base_conative
        
        return conative_patterns
    
    def _normalize_interest_category(self, interest: str) -> str:
        """Normalize Facebook interest category to standard format"""
        return interest.lower().replace(' ', '_').replace('-', '_')
    
    def _infer_values_from_category(self, category: str) -> Dict[str, float]:
        """Infer personal values from Facebook targeting category"""
        values = {}
        category_lower = category.lower()
        
        # Map categories to personal values
        value_mappings = {
            'family': {'family_oriented': 0.8, 'traditional': 0.6},
            'career': {'achievement': 0.8, 'success_oriented': 0.7},
            'travel': {'openness': 0.8, 'experience_seeking': 0.9},
            'charity': {'altruism': 0.9, 'social_responsibility': 0.8},
            'luxury': {'materialism': 0.7, 'status_seeking': 0.8},
            'health': {'self_care': 0.8, 'wellness_focused': 0.7}
        }
        
        for keyword, value_set in value_mappings.items():
            if keyword in category_lower:
                values.update(value_set)
                
        return values
    
    def _calculate_valence(self, emotions: Dict[str, float]) -> float:
        """Calculate emotional valence (positive/negative) from emotion indicators"""
        positive = emotions.get('positive_sentiment', 0)
        negative = emotions.get('negative_sentiment', 0)
        
        if positive + negative == 0:
            return 0.0
            
        return (positive - negative) / (positive + negative)
    
    def _calculate_arousal(self, emotions: Dict[str, float]) -> float:
        """Calculate emotional arousal (calm/excited) from emotion indicators"""
        exclamation = emotions.get('exclamation_intensity', 0)
        caps = emotions.get('caps_intensity', 0)
        
        return min(1.0, (exclamation * 2 + caps) / 2)
    
    def _calculate_dominance(self, emotions: Dict[str, float]) -> float:
        """Calculate emotional dominance from emotion indicators"""
        length = emotions.get('length', 0)
        caps = emotions.get('caps_intensity', 0)
        
        # Longer messages and caps usage indicate dominance
        return min(1.0, (length / 100.0 + caps) / 2)
    
    def _calculate_emotional_intensity(self, emotions: Dict[str, float]) -> float:
        """Calculate overall emotional intensity"""
        intensity_indicators = [
            emotions.get('exclamation_intensity', 0),
            emotions.get('caps_intensity', 0),
            emotions.get('positive_sentiment', 0) + emotions.get('negative_sentiment', 0)
        ]
        
        return sum(intensity_indicators) / len(intensity_indicators)
    
    def run_full_analysis(self) -> CompletePsychologicalProfile:
        """
        Run complete digital psychometrics analysis
        Returns comprehensive psychological profile
        """
        self.logger.info("Starting complete psychological profile analysis...")
        
        profile = CompletePsychologicalProfile()
        
        # Extract Facebook's psychological assessment
        profile.facebook_profile = self.ads_parser.extract_facebook_psychological_profile()
        
        # Extract vulnerabilities Facebook exploited
        profile.vulnerabilities = self.ads_parser.identify_manipulation_vulnerabilities()
        
        # Extract social behavior patterns
        profile.social_profile = self.activity_parser.extract_social_behavior_profile()
        
        # Extract behavioral vectors for personality analysis
        behavioral_vectors = self.extract_behavioral_vectors()
        
        if behavioral_vectors:
            # Compute OCEAN traits from behavioral vectors
            profile.ocean_traits = self._compute_ocean_traits(behavioral_vectors)
            
            # Extract emotional timeline and patterns
            profile.emotional_timeline = self._extract_emotional_timeline(behavioral_vectors)
            profile.mood_volatility = self._calculate_mood_volatility(profile.emotional_timeline)
            
        # Compare Facebook's assessment vs. actual analysis
        profile.facebook_vs_actual_discrepancy = self._compare_facebook_vs_actual(
            profile.facebook_profile, profile.ocean_traits
        )
        
        # Generate protective recommendations
        profile.protective_recommendations = self._generate_protective_recommendations(profile)
        
        # Set confidence scores
        profile.confidence_scores = self._calculate_confidence_scores(profile)
        
        self.logger.info("Psychological profile analysis complete")
        return profile
    
    def _compute_ocean_traits(self, behavioral_vectors: List[BehaviorVector]) -> OceanTraits:
        """Compute OCEAN personality traits from behavioral vectors"""
        traits = OceanTraits()
        
        if not behavioral_vectors:
            return traits
            
        # Aggregate cognitive, affective, and conative patterns
        total_vectors = len(behavioral_vectors)
        
        openness_indicators = []
        conscientiousness_indicators = []
        extraversion_indicators = []
        agreeableness_indicators = []
        neuroticism_indicators = []
        
        for vector in behavioral_vectors:
            # Openness from interest diversity and novel experiences
            openness_score = 0.0
            for key, value in vector.cognitive.items():
                if 'interest_' in key and ('art' in key or 'travel' in key or 'culture' in key):
                    openness_score += value * 0.2
            openness_indicators.append(openness_score)
            
            # Conscientiousness from communication patterns and organization
            conscientiousness_score = 0.0
            if 'response_speed' in vector.conative:
                conscientiousness_score += vector.conative['response_speed'] * 0.3
            conscientiousness_indicators.append(conscientiousness_score)
            
            # Extraversion from social engagement and communication
            extraversion_score = 0.0
            if 'initiation_tendency' in vector.conative:
                extraversion_score += vector.conative['initiation_tendency'] * 0.4
            if vector.affective.get('public_expression_level', 0) > 0:
                extraversion_score += 0.3
            extraversion_indicators.append(extraversion_score)
            
            # Agreeableness from positive interactions and helping behavior
            agreeableness_score = 0.0
            if vector.affective.get('valence', 0) > 0:
                agreeableness_score += vector.affective['valence'] * 0.3
            if 'help_seeking_behavior' in vector.conative:
                agreeableness_score += vector.conative['help_seeking_behavior'] * 0.2
            agreeableness_indicators.append(agreeableness_score)
            
            # Neuroticism from emotional volatility and anxiety
            neuroticism_score = 0.0
            if vector.affective.get('anxiety_level', 0) > 0:
                neuroticism_score += vector.affective['anxiety_level'] * 0.4
            if vector.affective.get('emotional_intensity', 0) > 0.7:
                neuroticism_score += 0.3
            neuroticism_indicators.append(neuroticism_score)
            
        # Average the scores
        if openness_indicators:
            traits.openness = min(1.0, sum(openness_indicators) / len(openness_indicators))
        if conscientiousness_indicators:
            traits.conscientiousness = min(1.0, sum(conscientiousness_indicators) / len(conscientiousness_indicators))
        if extraversion_indicators:
            traits.extraversion = min(1.0, sum(extraversion_indicators) / len(extraversion_indicators))
        if agreeableness_indicators:
            traits.agreeableness = min(1.0, sum(agreeableness_indicators) / len(agreeableness_indicators))
        if neuroticism_indicators:
            traits.neuroticism = min(1.0, sum(neuroticism_indicators) / len(neuroticism_indicators))
            
        return traits
    
    def _extract_emotional_timeline(self, behavioral_vectors: List[BehaviorVector]) -> List[Any]:
        """Extract emotional state timeline from behavioral vectors"""
        timeline = []
        
        for vector in behavioral_vectors:
            if vector.timestamp and vector.affective:
                from ..models.behavioral_vectors import EmotionalState
                
                emotional_state = EmotionalState(
                    valence=vector.affective.get('valence', 0.0),
                    arousal=vector.affective.get('arousal', 0.0),
                    dominance=vector.affective.get('dominance', 0.0),
                    timestamp=vector.timestamp
                )
                timeline.append(emotional_state)
                
        return sorted(timeline, key=lambda x: x.timestamp or datetime.min)
    
    def _calculate_mood_volatility(self, emotional_timeline: List[Any]) -> float:
        """Calculate mood volatility from emotional timeline"""
        if len(emotional_timeline) < 2:
            return 0.0
            
        valence_changes = []
        for i in range(1, len(emotional_timeline)):
            valence_change = abs(emotional_timeline[i].valence - emotional_timeline[i-1].valence)
            valence_changes.append(valence_change)
            
        return sum(valence_changes) / len(valence_changes) if valence_changes else 0.0
    
    def _compare_facebook_vs_actual(self, fb_profile: FacebookPsychProfile, 
                                  actual_traits: OceanTraits) -> Dict[str, float]:
        """Compare Facebook's assessment vs actual personality analysis"""
        discrepancies = {}
        
        # This would require mapping Facebook's categories to OCEAN traits
        # For now, return placeholder analysis
        discrepancies['overall_accuracy'] = 0.7  # Placeholder
        discrepancies['targeting_bias'] = 0.3    # How biased Facebook's view is
        
        return discrepancies
    
    def _generate_protective_recommendations(self, profile: CompletePsychologicalProfile) -> List[str]:
        """Generate recommendations to protect against manipulation"""
        recommendations = []
        
        # Based on identified vulnerabilities
        for vulnerability in profile.vulnerabilities:
            if vulnerability.vulnerability_type == 'emotional_vulnerability':
                recommendations.append("Be aware of emotional targeting during vulnerable periods")
            elif vulnerability.vulnerability_type == 'financial_vulnerability':
                recommendations.append("Implement financial decision waiting periods")
                
        # Based on personality traits
        if profile.ocean_traits.neuroticism > 0.7:
            recommendations.append("Monitor anxiety-inducing content exposure")
            
        if profile.ocean_traits.openness > 0.8:
            recommendations.append("Be cautious of novelty-based marketing manipulation")
            
        return recommendations
    
    def _calculate_confidence_scores(self, profile: CompletePsychologicalProfile) -> Dict[str, float]:
        """Calculate confidence scores for different aspects of analysis"""
        scores = {}
        
        # Data completeness affects confidence
        data_completeness = sum(self.data_validation.values()) / len(self.data_validation)
        scores['overall_confidence'] = data_completeness * 0.8
        
        # Specific component confidence
        scores['personality_confidence'] = 0.7 if profile.ocean_traits else 0.0
        scores['vulnerability_confidence'] = 0.8 if profile.vulnerabilities else 0.0
        scores['facebook_profile_confidence'] = 0.9 if profile.facebook_profile else 0.0
        
        return scores
