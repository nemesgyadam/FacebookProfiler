"""
Activity Data Parser - Extract behavioral patterns from Facebook activity
Focuses on messages, posts, and social interactions for psychological profiling
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import re

from .json_parser import FacebookDataParser
from ..models.behavioral_vectors import (
    EmotionalState, 
    SocialBehaviorProfile, 
    BehaviorVector
)


class ActivityDataParser(FacebookDataParser):
    """Parser for your_facebook_activity directory"""
    
    def __init__(self, data_root: Path):
        super().__init__(data_root)
        self.activity_dir = self.data_root / 'your_facebook_activity'
        self.logger = logging.getLogger(__name__)
        
    def parse_messages_data(self) -> Dict[str, Any]:
        """
        Parse messages directory - richest behavioral data
        Extract communication patterns, emotional expressions, social dynamics
        """
        messages_dir = self.activity_dir / 'messages'
        if not messages_dir.exists():
            return {}
            
        message_data = {
            'conversations': [],
            'communication_patterns': {},
            'emotional_timeline': [],
            'social_dynamics': {}
        }
        
        # Parse inbox conversations
        inbox_dir = messages_dir / 'inbox'
        if inbox_dir.exists():
            for conv_dir in inbox_dir.iterdir():
                if conv_dir.is_dir():
                    conv_data = self._parse_conversation(conv_dir)
                    if conv_data:
                        message_data['conversations'].append(conv_data)
                        
        # Parse AI conversations separately
        ai_convs_file = messages_dir / 'ai_conversations.json'
        if ai_convs_file.exists():
            ai_data = self.safe_load_json(ai_convs_file)
            if ai_data:
                message_data['ai_conversations'] = self._extract_ai_conversation_insights(ai_data)
                
        return message_data
        
    def _parse_conversation(self, conv_dir: Path) -> Optional[Dict[str, Any]]:
        """Parse individual conversation directory"""
        message_file = conv_dir / 'message_1.json'
        if not message_file.exists():
            return None
            
        data = self.safe_load_json(message_file)
        if not data:
            return None
            
        conversation = {
            'participants': data.get('participants', []),
            'messages': [],
            'thread_type': data.get('thread_type', 'Regular'),
            'title': data.get('title', 'Unknown')
        }
        
        # Extract messages with psychological indicators
        for msg in data.get('messages', []):
            if 'content' in msg:
                parsed_msg = {
                    'content': msg['content'],
                    'sender_name': msg.get('sender_name', 'Unknown'),
                    'timestamp': self.parse_facebook_timestamp(msg.get('timestamp_ms')),
                    'type': msg.get('type', 'Generic'),
                    'emotional_indicators': self._extract_emotional_indicators(msg.get('content', '')),
                    'response_time': None  # Will calculate later
                }
                conversation['messages'].append(parsed_msg)
                
        # Calculate response times and communication patterns
        conversation['communication_analysis'] = self._analyze_conversation_patterns(
            conversation['messages']
        )
        
        return conversation
        
    def _extract_emotional_indicators(self, text: str) -> Dict[str, float]:
        """
        Extract emotional indicators from text content
        Basic sentiment analysis and emotional markers
        """
        if not text:
            return {}
            
        indicators = {
            'exclamation_intensity': text.count('!') / max(len(text), 1),
            'question_intensity': text.count('?') / max(len(text), 1),
            'caps_intensity': sum(1 for c in text if c.isupper()) / max(len(text), 1),
            'length': len(text),
            'contains_emotions': 0.0
        }
        
        # Basic emotional keywords
        positive_words = ['happy', 'good', 'great', 'awesome', 'love', 'amazing', 'wonderful']
        negative_words = ['sad', 'bad', 'terrible', 'hate', 'angry', 'frustrated', 'upset']
        anxiety_words = ['worried', 'anxious', 'stressed', 'nervous', 'scared', 'afraid']
        
        text_lower = text.lower()
        indicators['positive_sentiment'] = sum(1 for word in positive_words if word in text_lower)
        indicators['negative_sentiment'] = sum(1 for word in negative_words if word in text_lower)
        indicators['anxiety_markers'] = sum(1 for word in anxiety_words if word in text_lower)
        
        return indicators
        
    def _analyze_conversation_patterns(self, messages: List[Dict]) -> Dict[str, Any]:
        """
        Analyze communication patterns within a conversation
        Response times, initiation patterns, emotional dynamics
        """
        if not messages:
            return {}
            
        # Sort messages by timestamp
        sorted_messages = sorted(messages, key=lambda x: x.get('timestamp') or datetime.min)
        
        analysis = {
            'total_messages': len(messages),
            'user_messages': 0,
            'response_times': [],
            'initiation_count': 0,
            'emotional_evolution': []
        }
        
        user_name = None  # We'll need to infer the user's name
        previous_msg = None
        
        for msg in sorted_messages:
            sender = msg.get('sender_name', 'Unknown')
            
            # Infer user identity (they'll have the most messages typically)
            if user_name is None:
                # This is a simplification - in real implementation we'd be smarter
                user_name = sender
                
            if sender == user_name:
                analysis['user_messages'] += 1
                
                # Calculate response time if this follows someone else's message
                if previous_msg and previous_msg.get('sender_name') != user_name:
                    if msg.get('timestamp') and previous_msg.get('timestamp'):
                        response_time = (msg['timestamp'] - previous_msg['timestamp']).total_seconds()
                        analysis['response_times'].append(response_time)
                        
            # Track emotional evolution
            emotional_state = self._extract_emotional_indicators(msg.get('content', ''))
            if emotional_state:
                analysis['emotional_evolution'].append({
                    'timestamp': msg.get('timestamp'),
                    'emotions': emotional_state
                })
                
            previous_msg = msg
            
        # Calculate average response time
        if analysis['response_times']:
            analysis['avg_response_time'] = sum(analysis['response_times']) / len(analysis['response_times'])
        else:
            analysis['avg_response_time'] = 0
            
        return analysis
        
    def _extract_ai_conversation_insights(self, ai_data: Dict) -> Dict[str, Any]:
        """
        Extract insights from AI conversations
        Shows what topics user discussed with AI, psychological patterns
        """
        insights = {
            'conversation_topics': [],
            'psychological_patterns': {},
            'help_seeking_behavior': {}
        }
        
        for conversation in ai_data.get('conversations', []):
            for message in conversation.get('messages', []):
                content = message.get('content', '')
                if content:
                    # Identify help-seeking patterns
                    if any(word in content.lower() for word in ['help', 'advice', 'what should', 'how do']):
                        insights['help_seeking_behavior']['frequency'] = insights['help_seeking_behavior'].get('frequency', 0) + 1
                        
                    # Extract psychological themes
                    psych_themes = self._identify_psychological_themes(content)
                    for theme in psych_themes:
                        insights['psychological_patterns'][theme] = insights['psychological_patterns'].get(theme, 0) + 1
                        
        return insights
        
    def _identify_psychological_themes(self, text: str) -> List[str]:
        """Identify psychological themes in text content"""
        themes = []
        text_lower = text.lower()
        
        theme_keywords = {
            'anxiety': ['anxious', 'worried', 'nervous', 'panic', 'stress'],
            'depression': ['depressed', 'sad', 'hopeless', 'empty', 'worthless'],
            'relationships': ['relationship', 'dating', 'partner', 'love', 'breakup'],
            'career': ['job', 'work', 'career', 'professional', 'employment'],
            'family': ['family', 'parents', 'siblings', 'relatives'],
            'self_improvement': ['improve', 'better', 'growth', 'develop', 'change'],
            'trauma': ['trauma', 'abuse', 'hurt', 'pain', 'healing']
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
                
        return themes
        
    def parse_posts_data(self) -> Dict[str, Any]:
        """
        Parse posts directory - public persona and content sharing patterns
        """
        posts_dir = self.activity_dir / 'posts'
        if not posts_dir.exists():
            return {}
            
        posts_data = {
            'posts': [],
            'posting_patterns': {},
            'content_themes': {},
            'engagement_patterns': {}
        }
        
        # Parse post files
        for post_file in posts_dir.glob('*.json'):
            data = self.safe_load_json(post_file)
            if data:
                for post in data.get('status_updates_v2', []):
                    parsed_post = self._parse_individual_post(post)
                    if parsed_post:
                        posts_data['posts'].append(parsed_post)
                        
        # Analyze posting patterns
        posts_data['posting_patterns'] = self._analyze_posting_patterns(posts_data['posts'])
        
        return posts_data
        
    def _parse_individual_post(self, post_data: Dict) -> Optional[Dict[str, Any]]:
        """Parse individual post data"""
        if 'data' not in post_data:
            return None
            
        post = {
            'timestamp': self.parse_facebook_timestamp(post_data.get('timestamp')),
            'content': '',
            'attachments': [],
            'privacy': post_data.get('privacy', 'Unknown')
        }
        
        # Extract post content
        for data_item in post_data.get('data', []):
            if 'post' in data_item:
                post['content'] = data_item['post']
                break
                
        # Extract emotional and thematic content
        post['emotional_analysis'] = self._extract_emotional_indicators(post['content'])
        post['themes'] = self._identify_psychological_themes(post['content'])
        
        return post
        
    def _analyze_posting_patterns(self, posts: List[Dict]) -> Dict[str, Any]:
        """Analyze temporal and thematic posting patterns"""
        if not posts:
            return {}
            
        patterns = {
            'posting_frequency': {},
            'time_of_day_patterns': {},
            'emotional_patterns': {},
            'theme_evolution': {}
        }
        
        # Analyze posting times
        posting_hours = []
        for post in posts:
            if post.get('timestamp'):
                hour = post['timestamp'].hour
                posting_hours.append(hour)
                
        # Calculate hourly posting distribution
        for hour in range(24):
            patterns['time_of_day_patterns'][hour] = posting_hours.count(hour)
            
        return patterns
        
    def extract_social_behavior_profile(self) -> SocialBehaviorProfile:
        """
        Extract comprehensive social behavior profile from activity data
        """
        profile = SocialBehaviorProfile()
        
        # Parse messages for communication patterns
        message_data = self.parse_messages_data()
        
        if message_data.get('conversations'):
            total_conversations = len(message_data['conversations'])
            total_messages = sum(conv.get('communication_analysis', {}).get('user_messages', 0) 
                               for conv in message_data['conversations'])
            
            profile.communication_frequency = total_messages / max(total_conversations, 1)
            
            # Calculate average response time across all conversations
            all_response_times = []
            for conv in message_data['conversations']:
                response_times = conv.get('communication_analysis', {}).get('response_times', [])
                all_response_times.extend(response_times)
                
            if all_response_times:
                profile.response_time_avg = sum(all_response_times) / len(all_response_times)
                
        # Parse posts for public engagement patterns
        posts_data = self.parse_posts_data()
        if posts_data.get('posts'):
            profile.group_participation_level = len(posts_data['posts']) / 365.0  # Posts per day average
            
        return profile
