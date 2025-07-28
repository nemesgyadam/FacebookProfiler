"""
Digital Emotion Recognition - Affective computing for psychological analysis
Analyzes emotional patterns and manipulation timing from Facebook data
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import re
from collections import defaultdict

from ..models.behavioral_vectors import EmotionalState


class DigitalEmotionRecognition:
    """Analyzes emotional patterns and affective manipulation from Facebook data"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Emotion detection patterns
        self.EMOTION_PATTERNS = {
            'positive': {
                'keywords': ['happy', 'joy', 'excited', 'great', 'awesome', 'love', 'wonderful', 'amazing'],
                'intensity_multipliers': {'!': 1.2, '!!': 1.5, '!!!': 2.0},
                'emoji_patterns': ['😊', '😄', '🎉', '❤️', '😍', '🥰']
            },
            'negative': {
                'keywords': ['sad', 'angry', 'frustrated', 'hate', 'terrible', 'awful', 'depressed', 'upset'],
                'intensity_multipliers': {'!': 1.2, '!!': 1.5, '!!!': 2.0},
                'emoji_patterns': ['😢', '😭', '😠', '😡', '💔', '😞']
            },
            'anxiety': {
                'keywords': ['worried', 'anxious', 'nervous', 'stress', 'overwhelmed', 'panic', 'scared'],
                'intensity_multipliers': {'!': 1.3, '!!': 1.6, '!!!': 2.2},
                'emoji_patterns': ['😰', '😨', '😟', '😧']
            },
            'loneliness': {
                'keywords': ['alone', 'lonely', 'isolated', 'empty', 'nobody', 'abandoned'],
                'intensity_multipliers': {'!': 1.4, '!!': 1.7, '!!!': 2.3},
                'emoji_patterns': ['😔', '💔', '😢']
            }
        }
        
        # Manipulation timing patterns
        self.MANIPULATION_WINDOWS = {
            'vulnerability_hours': [(22, 2), (3, 6)],  # Late night and early morning
            'stress_days': ['Monday', 'Sunday'],  # Beginning and end of week
            'emotional_seasons': {
                'valentine_loneliness': [(2, 10), (2, 16)],  # Around Valentine's Day
                'holiday_depression': [(12, 20), (1, 5)],   # Holiday season
                'new_year_anxiety': [(12, 28), (1, 15)]     # New Year pressure
            }
        }
        
    def analyze_emotional_timeline(self, messages_data: Dict, posts_data: Dict) -> List[EmotionalState]:
        """
        Create emotional timeline from messages and posts data
        """
        emotional_timeline = []
        
        # Analyze messages for emotional patterns
        if messages_data.get('conversations'):
            for conversation in messages_data['conversations']:
                emotional_evolution = conversation.get('communication_analysis', {}).get('emotional_evolution', [])
                
                for emotion_point in emotional_evolution:
                    timestamp = emotion_point.get('timestamp')
                    if timestamp:
                        emotional_state = self._extract_emotional_state(emotion_point, 'message')
                        emotional_timeline.append(emotional_state)
                        
        # Analyze posts for emotional patterns
        if posts_data.get('posts'):
            for post in posts_data['posts']:
                timestamp = post.get('timestamp')
                if timestamp:
                    emotional_state = self._extract_emotional_state(post, 'post')
                    emotional_timeline.append(emotional_state)
                    
        # Sort by timestamp
        emotional_timeline.sort(key=lambda x: x.timestamp or datetime.min)
        
        return emotional_timeline
    
    def _extract_emotional_state(self, data: Dict, source: str) -> EmotionalState:
        """Extract emotional state from message or post data"""
        timestamp = data.get('timestamp')
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                timestamp = datetime.now()
                
        # Extract text content
        text_content = ""
        if source == 'message':
            text_content = data.get('content', '')
        elif source == 'post':
            text_content = data.get('text', '') or data.get('content', '')
            
        # Analyze emotional content
        emotions = self._analyze_text_emotions(text_content)
        
        # Calculate VAD (Valence, Arousal, Dominance) model
        valence = self._calculate_valence(emotions)
        arousal = self._calculate_arousal(emotions, text_content)
        dominance = self._calculate_dominance(text_content, source)
        
        return EmotionalState(
            valence=valence,
            arousal=arousal,
            dominance=dominance,
            timestamp=timestamp
        )
    
    def _analyze_text_emotions(self, text: str) -> Dict[str, float]:
        """Analyze emotional content in text"""
        if not text:
            return {}
            
        text_lower = text.lower()
        emotions = {}
        
        for emotion_type, patterns in self.EMOTION_PATTERNS.items():
            emotion_score = 0.0
            
            # Check for emotional keywords
            for keyword in patterns['keywords']:
                if keyword in text_lower:
                    emotion_score += 1.0
                    
            # Check for intensity multipliers
            for multiplier, factor in patterns['intensity_multipliers'].items():
                if multiplier in text:
                    emotion_score *= factor
                    
            # Check for emoji patterns
            for emoji in patterns['emoji_patterns']:
                if emoji in text:
                    emotion_score += 0.5
                    
            emotions[emotion_type] = min(1.0, emotion_score / 3.0)  # Normalize
            
        return emotions
    
    def _calculate_valence(self, emotions: Dict[str, float]) -> float:
        """Calculate emotional valence (positive/negative)"""
        positive = emotions.get('positive', 0.0)
        negative = emotions.get('negative', 0.0) + emotions.get('anxiety', 0.0) + emotions.get('loneliness', 0.0)
        
        if positive + negative == 0:
            return 0.0
            
        return (positive - negative) / (positive + negative)
    
    def _calculate_arousal(self, emotions: Dict[str, float], text: str) -> float:
        """Calculate emotional arousal (calm/excited)"""
        # High arousal emotions
        high_arousal = emotions.get('anxiety', 0.0) + emotions.get('positive', 0.0) * 0.7
        
        # Text intensity indicators
        exclamation_count = text.count('!')
        caps_ratio = sum(1 for c in text if c.isupper()) / max(1, len(text))
        
        text_intensity = min(1.0, (exclamation_count * 0.2 + caps_ratio * 2))
        
        return min(1.0, high_arousal + text_intensity)
    
    def _calculate_dominance(self, text: str, source: str) -> float:
        """Calculate emotional dominance"""
        dominance = 0.0
        
        # Longer messages indicate more dominance
        length_factor = min(1.0, len(text) / 200.0)
        dominance += length_factor * 0.4
        
        # Posts are more dominant than private messages
        if source == 'post':
            dominance += 0.3
            
        # Question marks indicate less dominance
        question_ratio = text.count('?') / max(1, len(text.split()))
        dominance -= question_ratio * 0.2
        
        return max(0.0, min(1.0, dominance))
    
    def identify_manipulation_timing(self, emotional_timeline: List[EmotionalState]) -> List[Tuple[datetime, str, float]]:
        """
        Identify when user was most vulnerable to emotional manipulation
        """
        manipulation_windows = []
        
        for emotional_state in emotional_timeline:
            if not emotional_state.timestamp:
                continue
                
            vulnerability_score = 0.0
            manipulation_type = ""
            
            # Check for vulnerable emotional states
            if emotional_state.valence < -0.5:  # Very negative emotions
                vulnerability_score += 0.4
                manipulation_type = "negative_emotional_state"
                
            if emotional_state.arousal > 0.7:  # High arousal (anxiety, excitement)
                vulnerability_score += 0.3
                manipulation_type += "_high_arousal"
                
            # Check for vulnerable timing
            hour = emotional_state.timestamp.hour
            day_of_week = emotional_state.timestamp.strftime('%A')
            
            # Vulnerable hours (late night, early morning)
            for start_hour, end_hour in self.MANIPULATION_WINDOWS['vulnerability_hours']:
                if start_hour <= hour <= 23 or 0 <= hour <= end_hour:
                    vulnerability_score += 0.2
                    manipulation_type += "_vulnerable_hours"
                    
            # Vulnerable days
            if day_of_week in self.MANIPULATION_WINDOWS['stress_days']:
                vulnerability_score += 0.1
                manipulation_type += "_stress_day"
                
            # Seasonal emotional vulnerabilities
            month = emotional_state.timestamp.month
            day = emotional_state.timestamp.day
            
            for season, date_ranges in self.MANIPULATION_WINDOWS['emotional_seasons'].items():
                for start_month_day, end_month_day in date_ranges:
                    start_month, start_day = start_month_day
                    end_month, end_day = end_month_day
                    
                    if ((month == start_month and day >= start_day) or 
                        (month == end_month and day <= end_day) or
                        (start_month < month < end_month)):
                        vulnerability_score += 0.2
                        manipulation_type += f"_{season}"
                        
            if vulnerability_score > 0.3:  # Threshold for significant vulnerability
                manipulation_windows.append((
                    emotional_state.timestamp,
                    manipulation_type.strip('_'),
                    vulnerability_score
                ))
                
        return manipulation_windows
    
    def analyze_emotional_manipulation_patterns(self, 
                                               emotional_timeline: List[EmotionalState],
                                               fb_targeting_data: Dict) -> Dict[str, List[str]]:
        """
        Analyze how Facebook targeted emotional vulnerabilities
        """
        manipulation_patterns = defaultdict(list)
        
        # Identify manipulation windows
        manipulation_windows = self.identify_manipulation_timing(emotional_timeline)
        
        # Cross-reference with Facebook targeting data
        for timestamp, manipulation_type, score in manipulation_windows:
            
            # Check if Facebook showed ads during vulnerable periods
            manipulation_patterns['vulnerability_targeting'].append(
                f"Vulnerable period detected: {timestamp.strftime('%Y-%m-%d %H:%M')} - {manipulation_type} (score: {score:.2f})"
            )
            
            # Analyze what types of ads were likely shown during vulnerable periods
            if score > 0.6:  # High vulnerability
                manipulation_patterns['high_risk_targeting'].append(
                    f"High vulnerability exploitation window: {timestamp.strftime('%Y-%m-%d %H:%M')}"
                )
                
        # Analyze emotional state changes after potential ad exposure
        for i in range(1, len(emotional_timeline)):
            current_state = emotional_timeline[i]
            previous_state = emotional_timeline[i-1]
            
            # Look for sudden emotional changes that might indicate manipulation
            valence_change = abs(current_state.valence - previous_state.valence)
            arousal_change = abs(current_state.arousal - previous_state.arousal)
            
            if valence_change > 0.4 or arousal_change > 0.4:
                manipulation_patterns['emotional_volatility'].append(
                    f"Significant emotional change detected: {current_state.timestamp.strftime('%Y-%m-%d %H:%M')}"
                )
                
        return dict(manipulation_patterns)
    
    def calculate_emotional_resilience(self, emotional_timeline: List[EmotionalState]) -> Dict[str, float]:
        """
        Calculate emotional resilience metrics
        """
        if len(emotional_timeline) < 2:
            return {'overall_resilience': 0.5}
            
        resilience_metrics = {}
        
        # Calculate emotional stability (low volatility = high stability)
        valence_changes = []
        arousal_changes = []
        
        for i in range(1, len(emotional_timeline)):
            valence_change = abs(emotional_timeline[i].valence - emotional_timeline[i-1].valence)
            arousal_change = abs(emotional_timeline[i].arousal - emotional_timeline[i-1].arousal)
            
            valence_changes.append(valence_change)
            arousal_changes.append(arousal_change)
            
        # Stability (inverse of volatility)
        valence_volatility = sum(valence_changes) / len(valence_changes)
        arousal_volatility = sum(arousal_changes) / len(arousal_changes)
        
        resilience_metrics['emotional_stability'] = 1.0 - min(1.0, (valence_volatility + arousal_volatility) / 2)
        
        # Recovery speed (how quickly user returns to baseline after negative events)
        negative_periods = [state for state in emotional_timeline if state.valence < -0.3]
        recovery_times = []
        
        for neg_state in negative_periods:
            # Find next positive state
            neg_index = emotional_timeline.index(neg_state)
            for i in range(neg_index + 1, len(emotional_timeline)):
                if emotional_timeline[i].valence > 0.0:
                    recovery_time = (emotional_timeline[i].timestamp - neg_state.timestamp).total_seconds() / 3600  # Hours
                    recovery_times.append(min(168, recovery_time))  # Cap at 1 week
                    break
                    
        if recovery_times:
            avg_recovery_hours = sum(recovery_times) / len(recovery_times)
            # Faster recovery = higher resilience (inverse relationship)
            resilience_metrics['recovery_speed'] = max(0.0, 1.0 - (avg_recovery_hours / 168))  # Normalize to week
        else:
            resilience_metrics['recovery_speed'] = 0.5  # Default if no data
            
        # Overall resilience score
        resilience_metrics['overall_resilience'] = (
            resilience_metrics['emotional_stability'] * 0.6 + 
            resilience_metrics['recovery_speed'] * 0.4
        )
        
        return resilience_metrics
