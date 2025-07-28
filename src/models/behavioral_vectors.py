"""
Behavioral Vector Models for Digital Psychometrics
Defines core data structures for psychological profiling
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np


@dataclass
class BehaviorVector:
    """Core behavioral vector with cognitive, affective, and conative dimensions"""
    cognitive: Dict[str, float] = field(default_factory=dict)    # Beliefs, interests, values
    affective: Dict[str, float] = field(default_factory=dict)    # Emotional states, mood patterns  
    conative: Dict[str, float] = field(default_factory=dict)     # Intent, actions, decision patterns
    timestamp: Optional[datetime] = None
    confidence: float = 0.0


@dataclass
class OceanTraits:
    """Big Five personality traits (OCEAN model)"""
    openness: float = 0.0
    conscientiousness: float = 0.0
    extraversion: float = 0.0
    agreeableness: float = 0.0
    neuroticism: float = 0.0
    confidence: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'openness': self.openness,
            'conscientiousness': self.conscientiousness,
            'extraversion': self.extraversion,
            'agreeableness': self.agreeableness,
            'neuroticism': self.neuroticism
        }


@dataclass
class EmotionalState:
    """Emotional state representation"""
    valence: float = 0.0      # Positive/negative emotion (-1 to 1)
    arousal: float = 0.0      # Calm/excited (0 to 1)
    dominance: float = 0.0    # Submissive/dominant (-1 to 1)
    emotions: Dict[str, float] = field(default_factory=dict)  # joy, anger, fear, etc.
    timestamp: Optional[datetime] = None
    text_source: Optional[str] = None


@dataclass
class SocialBehaviorProfile:
    """Social interaction behavioral patterns"""
    network_centrality: float = 0.0
    communication_frequency: float = 0.0
    response_time_avg: float = 0.0
    initiation_vs_response_ratio: float = 0.0
    group_participation_level: float = 0.0
    social_boundary_management: Dict[str, int] = field(default_factory=dict)


@dataclass
class FacebookPsychProfile:
    """Facebook's inferred psychological profile from ad data"""
    targeting_categories: List[str] = field(default_factory=list)
    inferred_interests: Dict[str, float] = field(default_factory=dict)
    behavioral_segments: List[str] = field(default_factory=list)
    vulnerability_windows: List[Tuple[datetime, str]] = field(default_factory=list)
    ad_engagement_patterns: Dict[str, float] = field(default_factory=dict)


@dataclass
class PsychologicalVulnerability:
    """Identified psychological vulnerability"""
    vulnerability_type: str
    severity: float = 0.0
    triggers: List[str] = field(default_factory=list)
    exploitation_evidence: List[str] = field(default_factory=list)
    timing_patterns: List[datetime] = field(default_factory=list)


@dataclass
class CompletePsychologicalProfile:
    """Complete psychological profile combining all analysis"""
    # Core personality
    ocean_traits: OceanTraits = field(default_factory=OceanTraits)
    
    # Emotional patterns
    emotional_baseline: EmotionalState = field(default_factory=EmotionalState)
    emotional_timeline: List[EmotionalState] = field(default_factory=list)
    mood_volatility: float = 0.0
    
    # Social behavior
    social_profile: SocialBehaviorProfile = field(default_factory=SocialBehaviorProfile)
    
    # Facebook's perspective
    facebook_profile: FacebookPsychProfile = field(default_factory=FacebookPsychProfile)
    
    # Vulnerabilities and manipulation
    vulnerabilities: List[PsychologicalVulnerability] = field(default_factory=list)
    manipulation_susceptibility: Dict[str, float] = field(default_factory=dict)
    
    # Meta-analysis
    facebook_vs_actual_discrepancy: Dict[str, float] = field(default_factory=dict)
    identity_manipulation_indicators: List[str] = field(default_factory=list)
    protective_recommendations: List[str] = field(default_factory=list)
    
    # Analysis metadata
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    data_completeness: Dict[str, float] = field(default_factory=dict)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
