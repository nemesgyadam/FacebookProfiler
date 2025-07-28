#!/usr/bin/env python3
"""
Smart analyzer for Facebook ad_preferences.json data.
"""
import json
import os
import html
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import Counter


class AdPreferencesAnalyzer:
    """Analyzes and presents Facebook ad preferences data in a user-friendly format."""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.label_values = data.get('label_values', [])
    
    def analyze(self) -> Dict[str, Any]:
        """Perform comprehensive analysis of ad preferences data."""
        return {
            'privacy_settings': self._analyze_privacy_settings(),
            'hidden_ads': self._analyze_hidden_ads(),
            'interests': self._analyze_interests(),
            'custom_audiences': self._analyze_custom_audiences(),
            'psychological_profile': self._analyze_psychological_profile(),
            'summary': self._generate_summary()
        }
    
    def _analyze_privacy_settings(self) -> Dict[str, Any]:
        """Analyze privacy and opt-out settings."""
        privacy_settings = {
            'opt_outs': [],
            'opt_ins': [],
            'scores': {}
        }
        
        opt_out_keywords = [
            'opted out', 'opt-out', 'opt out', 'Is opted out'
        ]
        
        for item in self.label_values:
            label = item.get('label', '')
            value = item.get('value', '')
            
            # Check for opt-out settings
            if any(keyword in label for keyword in opt_out_keywords):
                setting = {
                    'setting': label.replace('Is opted out of ', '').replace('Is opted out from ', ''),
                    'status': value == 'True',
                    'category': self._categorize_privacy_setting(label)
                }
                
                if value == 'True':
                    privacy_settings['opt_outs'].append(setting)
                else:
                    privacy_settings['opt_ins'].append(setting)
        
        # Calculate privacy scores
        total_settings = len(privacy_settings['opt_outs']) + len(privacy_settings['opt_ins'])
        if total_settings > 0:
            privacy_settings['scores'] = {
                'privacy_score': len(privacy_settings['opt_outs']) / total_settings * 100,
                'total_settings': total_settings,
                'protected_count': len(privacy_settings['opt_outs']),
                'exposed_count': len(privacy_settings['opt_ins'])
            }
        
        return privacy_settings
    
    def _categorize_privacy_setting(self, label: str) -> str:
        """Categorize privacy settings into meaningful groups."""
        label_lower = label.lower()
        
        if any(word in label_lower for word in ['interest', 'topic']):
            return 'Interests & Topics'
        elif any(word in label_lower for word in ['job', 'employer', 'education', 'school']):
            return 'Professional Info'
        elif any(word in label_lower for word in ['relationship', 'religious', 'political']):
            return 'Personal Beliefs'
        elif any(word in label_lower for word in ['third party', 'off meta', 'tracking']):
            return 'External Tracking'
        else:
            return 'General'
    
    def _analyze_hidden_ads(self) -> Dict[str, Any]:
        """Analyze hidden/blocked ads data."""
        hidden_ads = {
            'ads': [],
            'stats': {},
            'timeline': []
        }
        
        # Find hidden ads in the data structure
        # First, look for the specific dict item that contains hidden ads
        for item in self.data.get('label_values', []):
            if item.get('label') == 'Hidden ads and events' and 'dict' in item:
                # Direct match for hidden ads section
                for ad_entry in item.get('dict', []):
                    if isinstance(ad_entry, dict) and 'dict' in ad_entry:
                        ad_data = self._parse_ad_entry(ad_entry['dict'])
                        if ad_data:
                            hidden_ads['ads'].append(ad_data)
        
        # If we didn't find a direct match, look for the unnamed dict at the end
        if not hidden_ads['ads']:
            for item in self.data.get('label_values', []):
                if 'dict' in item and not item.get('label'):
                    # This is likely the unnamed dict containing hidden ads
                    for ad_entry in item.get('dict', []):
                        if isinstance(ad_entry, dict) and 'dict' in ad_entry:
                            ad_data = self._parse_ad_entry(ad_entry['dict'])
                            if ad_data and ad_data.get('event') == 'Hide an Ad':
                                hidden_ads['ads'].append(ad_data)
        
        # Generate statistics
        if hidden_ads['ads']:
            hidden_ads['stats'] = self._calculate_ad_stats(hidden_ads['ads'])
            hidden_ads['timeline'] = self._create_ad_timeline(hidden_ads['ads'])
        
        return hidden_ads
    
    def _parse_ad_entry(self, ad_dict: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Parse individual ad entry."""
        ad_data = {}
        
        for field in ad_dict:
            label = field.get('label', '')
            
            if label == 'Event':
                ad_data['event'] = field.get('value', '')
            elif label == 'Ad title':
                ad_data['title'] = field.get('value', '')
            elif label == 'Creation time':
                timestamp = field.get('timestamp_value', 0)
                if timestamp:
                    ad_data['timestamp'] = timestamp
                    ad_data['date'] = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
        
        return ad_data if ad_data else None
    
    def _calculate_ad_stats(self, ads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics about hidden ads."""
        if not ads:
            return {}
        
        # Title analysis
        titles = [ad.get('title', '') for ad in ads]
        title_counter = Counter(titles)
        
        # Date analysis
        dates = [ad.get('date', '')[:10] for ad in ads if ad.get('date')]  # Just the date part
        date_counter = Counter(dates)
        
        return {
            'total_hidden': len(ads),
            'unique_titles': len(title_counter),
            'most_hidden_ad': title_counter.most_common(1)[0] if title_counter else None,
            'most_active_day': date_counter.most_common(1)[0] if date_counter else None,
            'date_range': {
                'first': min(dates) if dates else None,
                'last': max(dates) if dates else None
            }
        }
    
    def _create_ad_timeline(self, ads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create timeline of ad hiding activity."""
        timeline = []
        
        # Group by date
        date_groups = {}
        for ad in ads:
            date = ad.get('date', '')[:10] if ad.get('date') else 'Unknown'
            if date not in date_groups:
                date_groups[date] = []
            date_groups[date].append(ad)
        
        # Create timeline entries
        for date, ads_on_date in sorted(date_groups.items()):
            timeline.append({
                'date': date,
                'count': len(ads_on_date),
                'ads': ads_on_date[:5]  # Show max 5 ads per date
            })
        
        return timeline[-10:]  # Show last 10 entries
    
    def _analyze_interests(self) -> Dict[str, Any]:
        """Analyze interest-related data."""
        interests = {
            'added': [],
            'removed': [],
            'reported': [],
            'opted_in': [],
            'custom_preferences': {}
        }
        
        for item in self.label_values:
            label = item.get('label', '')
            
            if 'Added interests' in label:
                interests['added'] = item.get('vec', [])
            elif 'Removed interests' in label:
                interests['removed'] = item.get('vec', [])
            elif 'Reported interests' in label:
                interests['reported'] = item.get('vec', [])
            elif 'Opted-in Ad Interests' in label:
                interests['opted_in'] = item.get('vec', [])
            elif 'User ad interests preferences' in label:
                interests['custom_preferences'] = item.get('dict', {})
        
        return interests
    
    def _analyze_custom_audiences(self) -> Dict[str, Any]:
        """Analyze custom audience settings."""
        audiences = {
            'opt_outs': [],
            'inclusions': [],
            'exclusions': [],
            'third_party': {}
        }
        
        for item in self.label_values:
            label = item.get('label', '')
            
            if 'Datafile custom audience opt-out' in label:
                audiences['opt_outs'] = item.get('vec', [])
            elif 'Datafile Custom Audience inclusion opt-out' in label:
                audiences['inclusions'] = item.get('vec', [])
            elif 'Datafile Custom Audience exclusion opt-out' in label:
                audiences['exclusions'] = item.get('vec', [])
            elif 'third party' in label.lower():
                audiences['third_party'][label] = item.get('value', item.get('vec', []))
        
        return audiences
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate overall summary and insights."""
        privacy = self._analyze_privacy_settings()
        hidden_ads = self._analyze_hidden_ads()
        
        insights = []
        
        # Privacy insights
        if privacy.get('scores', {}).get('privacy_score', 0) >= 70:
            insights.append("🔒 You have strong privacy protection with most ad targeting disabled.")
        elif privacy.get('scores', {}).get('privacy_score', 0) >= 40:
            insights.append("🟡 You have moderate privacy protection, consider reviewing more settings.")
        else:
            insights.append("⚠️ Your privacy protection is limited, many ad targeting options are enabled.")
        
        # Hidden ads insights
        total_hidden = hidden_ads.get('stats', {}).get('total_hidden', 0)
        if total_hidden > 50:
            insights.append(f"🚫 You've hidden {total_hidden} ads, indicating active curation of your ad experience.")
        elif total_hidden > 10:
            insights.append(f"👀 You've hidden {total_hidden} ads, showing some ad management activity.")
        
        return {
            'insights': insights,
            'privacy_score': privacy.get('scores', {}).get('privacy_score', 0),
            'total_hidden_ads': total_hidden,
            'protection_level': self._get_protection_level(privacy.get('scores', {}).get('privacy_score', 0))
        }
    
    def _get_protection_level(self, score: float) -> str:
        """Get human-readable protection level."""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Moderate"
        elif score >= 20:
            return "Basic"
        else:
            return "Minimal"
    
    def _fix_encoding(self, text: str) -> str:
        """Fix Unicode encoding issues in text."""
        if not isinstance(text, str):
            return str(text)
        
        # Fix common Unicode issues
        text = text.replace('\u00c3\u00a1', 'á')  # á
        text = text.replace('\u00c3\u00a9', 'é')  # é
        text = text.replace('\u00c3\u00ad', 'í')  # í
        text = text.replace('\u00c3\u00b3', 'ó')  # ó
        text = text.replace('\u00c3\u00ba', 'ú')  # ú
        text = text.replace('\u00c3\u00bc', 'ü')  # ü
        text = text.replace('\u00c3\u00b6', 'ö')  # ö
        text = text.replace('\u00c3\u0091', 'Ñ')  # Ñ
        
        # Try to decode HTML entities
        try:
            text = html.unescape(text)
        except:
            pass
        
        # Fix double-encoded characters
        replacements = {
            'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
            'Ã¼': 'ü', 'Ã¶': 'ö', 'Ã¤': 'ä', 'Ã ': 'à', 'Ã¨': 'è',
            'Ã¬': 'ì', 'Ã²': 'ò', 'Ã¹': 'ù', 'Ã§': 'ç', 'Ã±': 'ñ'
        }
        
        for wrong, correct in replacements.items():
            text = text.replace(wrong, correct)
        
        return text
    
    def _analyze_psychological_profile(self) -> Dict[str, Any]:
        """Analyze psychological profile based on ad behavior and preferences."""
        profile = {
            'ad_avoidance_patterns': self._analyze_ad_avoidance(),
            'interest_categories': self._categorize_interests(),
            'privacy_personality': self._analyze_privacy_personality(),
            'engagement_style': self._analyze_engagement_style(),
            'psychological_insights': []
        }
        
        # Generate psychological insights
        profile['psychological_insights'] = self._generate_psychological_insights(profile)
        
        return profile
    
    def _analyze_ad_avoidance(self) -> Dict[str, Any]:
        """Analyze patterns in hidden/avoided ads for psychological insights."""
        hidden_ads = self._analyze_hidden_ads()
        
        avoidance_patterns = {
            'frequency': 'Low',
            'consistency': 'Inconsistent',
            'categories_avoided': [],
            'behavioral_pattern': 'Passive'
        }
        
        total_hidden = hidden_ads.get('stats', {}).get('total_hidden', 0)
        
        if total_hidden > 100:
            avoidance_patterns['frequency'] = 'Very High'
            avoidance_patterns['behavioral_pattern'] = 'Highly Selective'
        elif total_hidden > 50:
            avoidance_patterns['frequency'] = 'High'
            avoidance_patterns['behavioral_pattern'] = 'Selective'
        elif total_hidden > 20:
            avoidance_patterns['frequency'] = 'Moderate'
            avoidance_patterns['behavioral_pattern'] = 'Somewhat Selective'
        elif total_hidden > 5:
            avoidance_patterns['frequency'] = 'Low'
            avoidance_patterns['behavioral_pattern'] = 'Occasional'
        
        # Analyze ad titles for categories
        if hidden_ads.get('ads'):
            titles = [self._fix_encoding(ad.get('title', '')) for ad in hidden_ads['ads']]
            categories = self._categorize_ad_titles(titles)
            avoidance_patterns['categories_avoided'] = categories
        
        return avoidance_patterns
    
    def _categorize_ad_titles(self, titles: List[str]) -> List[Dict[str, Any]]:
        """Categorize ad titles to understand avoidance patterns."""
        categories = {
            'Gaming': ['game', 'play', 'level', 'battle', 'strategy', 'mobile game'],
            'E-commerce': ['buy', 'sale', 'discount', 'shop', 'store', 'price'],
            'Dating': ['dating', 'match', 'relationship', 'meet', 'single'],
            'Health & Fitness': ['health', 'fitness', 'diet', 'workout', 'medical'],
            'Technology': ['tech', 'software', 'app', 'digital', 'online'],
            'Finance': ['money', 'investment', 'loan', 'bank', 'insurance'],
            'Education': ['course', 'learn', 'education', 'training', 'skill'],
            'Entertainment': ['movie', 'music', 'show', 'entertainment', 'video']
        }
        
        category_counts = {cat: 0 for cat in categories.keys()}
        
        for title in titles:
            title_lower = title.lower()
            for category, keywords in categories.items():
                if any(keyword in title_lower for keyword in keywords):
                    category_counts[category] += 1
                    break
        
        # Return sorted categories by count
        return [{'category': cat, 'count': count, 'percentage': count/len(titles)*100 if titles else 0} 
                for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True) 
                if count > 0]
    
    def _categorize_interests(self) -> Dict[str, Any]:
        """Extract and categorize user interests for psychological profiling."""
        # This would analyze interests from the data structure
        # Looking for interest categories in the nested dict structures
        interest_categories = {
            'Technology & Gaming': [],
            'Entertainment & Media': [],
            'Health & Lifestyle': [],
            'Business & Professional': [],
            'Arts & Culture': [],
            'Sports & Recreation': [],
            'Food & Dining': [],
            'Other': []
        }
        
        # Extract interests from the complex nested structure
        for item in self.label_values:
            if 'dict' in item and isinstance(item['dict'], list):
                for entry in item['dict']:
                    if isinstance(entry, dict) and 'dict' in entry:
                        for field in entry['dict']:
                            if field.get('label') == 'Name':
                                interest = self._fix_encoding(field.get('value', ''))
                                category = self._categorize_single_interest(interest)
                                interest_categories[category].append(interest)
        
        return interest_categories
    
    def _categorize_single_interest(self, interest: str) -> str:
        """Categorize a single interest into psychological categories."""
        interest_lower = interest.lower()
        
        tech_keywords = ['computer', 'software', 'gaming', 'tech', 'digital', 'internet', 'app']
        entertainment_keywords = ['music', 'movie', 'tv', 'show', 'entertainment', 'comedy', 'drama']
        health_keywords = ['health', 'fitness', 'medical', 'wellness', 'diet', 'exercise']
        business_keywords = ['business', 'marketing', 'finance', 'professional', 'work', 'career']
        arts_keywords = ['art', 'culture', 'museum', 'literature', 'book', 'writing', 'design']
        sports_keywords = ['sport', 'football', 'basketball', 'soccer', 'tennis', 'running']
        food_keywords = ['food', 'cooking', 'restaurant', 'cuisine', 'recipe', 'dining']
        
        if any(keyword in interest_lower for keyword in tech_keywords):
            return 'Technology & Gaming'
        elif any(keyword in interest_lower for keyword in entertainment_keywords):
            return 'Entertainment & Media'
        elif any(keyword in interest_lower for keyword in health_keywords):
            return 'Health & Lifestyle'
        elif any(keyword in interest_lower for keyword in business_keywords):
            return 'Business & Professional'
        elif any(keyword in interest_lower for keyword in arts_keywords):
            return 'Arts & Culture'
        elif any(keyword in interest_lower for keyword in sports_keywords):
            return 'Sports & Recreation'
        elif any(keyword in interest_lower for keyword in food_keywords):
            return 'Food & Dining'
        else:
            return 'Other'
    
    def _analyze_privacy_personality(self) -> Dict[str, Any]:
        """Analyze privacy behavior to infer personality traits."""
        privacy_settings = self._analyze_privacy_settings()
        privacy_score = privacy_settings.get('scores', {}).get('privacy_score', 0)
        
        personality = {
            'privacy_type': 'Unknown',
            'traits': [],
            'likely_concerns': []
        }
        
        if privacy_score >= 80:
            personality['privacy_type'] = 'Privacy Maximalist'
            personality['traits'] = ['Highly cautious', 'Values personal data', 'Tech-savvy', 'Control-oriented']
            personality['likely_concerns'] = ['Data misuse', 'Identity theft', 'Manipulation', 'Surveillance']
        elif privacy_score >= 60:
            personality['privacy_type'] = 'Privacy Conscious'
            personality['traits'] = ['Moderately cautious', 'Selective sharing', 'Balanced approach']
            personality['likely_concerns'] = ['Personal data safety', 'Unwanted targeting']
        elif privacy_score >= 40:
            personality['privacy_type'] = 'Privacy Aware'
            personality['traits'] = ['Some awareness', 'Occasional concern', 'Convenience-focused']
            personality['likely_concerns'] = ['Major privacy violations']
        else:
            personality['privacy_type'] = 'Privacy Permissive'
            personality['traits'] = ['Open to sharing', 'Convenience over privacy', 'Trusting']
            personality['likely_concerns'] = ['None apparent']
        
        return personality
    
    def _analyze_engagement_style(self) -> Dict[str, Any]:
        """Analyze engagement patterns to understand user behavior style."""
        hidden_ads = self._analyze_hidden_ads()
        total_hidden = hidden_ads.get('stats', {}).get('total_hidden', 0)
        
        style = {
            'engagement_type': 'Passive',
            'activity_level': 'Low',
            'decision_making': 'Reactive'
        }
        
        if total_hidden > 50:
            style['engagement_type'] = 'Highly Active'
            style['activity_level'] = 'High'
            style['decision_making'] = 'Proactive'
        elif total_hidden > 20:
            style['engagement_type'] = 'Moderately Active'
            style['activity_level'] = 'Medium'
            style['decision_making'] = 'Selective'
        elif total_hidden > 5:
            style['engagement_type'] = 'Occasionally Active'
            style['activity_level'] = 'Low-Medium'
            style['decision_making'] = 'Occasional'
        
        return style
    
    def _generate_psychological_insights(self, profile: Dict[str, Any]) -> List[str]:
        """Generate therapeutic and mental health insights based on the complete profile."""
        insights = []
        
        # Mental Health & Behavioral Patterns
        privacy_type = profile['privacy_personality']['privacy_type']
        if privacy_type == 'Privacy Maximalist':
            insights.append("🧠 **Control-Seeking Behavior**: Your extensive privacy settings suggest a strong need for autonomy and control over your digital environment, which can be a healthy coping mechanism.")
            insights.append("🔒 **Digital Boundaries**: Your systematic approach to privacy indicates well-developed personal boundaries, suggesting good self-awareness and protective instincts.")
        elif privacy_type == 'Privacy Permissive':
            insights.append("🤝 **Social Openness**: Your permissive privacy settings suggest comfort with social connectivity and trust in digital platforms.")
            insights.append("🌐 **Low Digital Anxiety**: Your open approach may indicate lower levels of digital-related stress or paranoia.")
        
        # Stress & Coping Indicators
        avoidance = profile['ad_avoidance_patterns']
        if avoidance['frequency'] in ['Very High', 'High']:
            insights.append("⚠️ **Potential Digital Overwhelm**: High ad avoidance may indicate feelings of being overwhelmed by digital marketing pressures or information overload.")
            insights.append("🛡️ **Active Coping Strategy**: Your systematic ad curation demonstrates proactive stress management and environmental control as coping mechanisms.")
        elif avoidance['frequency'] == 'Moderate':
            insights.append("⚖️ **Balanced Digital Engagement**: Moderate ad management suggests a healthy balance between engagement and boundary-setting.")
        else:
            insights.append("🍃 **Organic Digital Experience**: Low ad avoidance may indicate comfort with serendipitous discoveries and lower need for environmental control.")
        
        # Social & Emotional Indicators
        privacy_settings = self._analyze_privacy_settings()
        sensitive_opts = sum(1 for opt in privacy_settings['opt_outs'] 
                           if any(word in opt['setting'].lower() 
                                for word in ['religious', 'political', 'relationship']))
        
        if sensitive_opts >= 2:
            insights.append("💭 **Social Boundary Preference**: Strong boundaries around sensitive topics (religious, political, relationship) suggest a preference for keeping personal beliefs private, which may indicate past negative experiences or strong personal values.")
        
        # Therapeutic Insights
        total_hidden = len(self._analyze_hidden_ads().get('ads', []))
        if total_hidden > 50:
            insights.append("📊 **High Curatorial Behavior**: Extensive ad hiding suggests a strong need to curate your environment, which can be therapeutic but may also indicate underlying anxiety or perfectionist tendencies.")
        elif total_hidden > 20:
            insights.append("🎯 **Selective Engagement**: Moderate ad curation indicates healthy discrimination in digital consumption, suggesting good self-advocacy skills.")
        
        # Positive Mental Health Indicators
        if privacy_type in ['Privacy Conscious', 'Privacy Maximalist']:
            insights.append("✨ **Self-Advocacy Strength**: Your proactive privacy management demonstrates excellent self-advocacy and awareness of your needs and boundaries.")
        
        # Digital Literacy & Agency
        engagement = profile['engagement_style']
        if engagement['decision_making'] == 'Proactive':
            insights.append("🚀 **High Digital Agency**: Your proactive approach to digital management indicates strong self-determination and confidence in navigating digital spaces.")
        
        return insights
