"""
Facebook Digital Psychometrics Analysis - Main Driver Script
Complete psychological profile analysis from Facebook data export
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any
import argparse

from src.analysis import (
    DigitalPsychometricsEngine,
    FacebookTargetingReverseEngineer,
    DigitalEmotionRecognition,
    PsychologicalVulnerabilityMapper
)


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('fb_analysis.log'),
            logging.StreamHandler()
        ]
    )


def analyze_facebook_profile(data_path: str, output_path: str = None, verbose: bool = False) -> Dict[str, Any]:
    """
    Run complete Facebook psychological profile analysis
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("Facebook Digital Psychometrics Analysis Starting")
    logger.info("=" * 60)
    
    try:
        # Initialize analysis engine
        logger.info(f"Initializing analysis engine with data path: {data_path}")
        engine = DigitalPsychometricsEngine(data_path)
        
        # Validate data structure
        logger.info("Validating Facebook data structure...")
        if not any(engine.data_validation.values()):
            logger.error("No valid Facebook data found. Please check data path.")
            return {"error": "Invalid Facebook data structure"}
            
        logger.info(f"Data validation: {engine.data_validation}")
        
        # Run complete psychological analysis
        logger.info("Running complete psychological profile analysis...")
        psychological_profile = engine.run_full_analysis()
        
        # Initialize additional analyzers
        targeting_reverser = FacebookTargetingReverseEngineer()
        emotion_analyzer = DigitalEmotionRecognition()
        vulnerability_mapper = PsychologicalVulnerabilityMapper()
        
        # Enhanced analysis
        logger.info("Performing enhanced Facebook targeting analysis...")
        
        # Reverse engineer Facebook's psychological assessment
        facebook_traits = targeting_reverser.reverse_engineer_facebook_psychology(
            psychological_profile.facebook_profile
        )
        
        # Identify manipulation tactics
        manipulation_tactics = targeting_reverser.identify_facebook_manipulation_tactics(
            psychological_profile.facebook_profile
        )
        
        # Calculate manipulation susceptibility
        susceptibility = targeting_reverser.calculate_manipulation_susceptibility(
            psychological_profile.facebook_profile,
            psychological_profile.ocean_traits
        )
        
        # Generate resistance strategies
        resistance_strategies = targeting_reverser.generate_targeting_resistance_strategies(
            manipulation_tactics,
            susceptibility
        )
        
        # Analyze emotional timeline if available
        emotional_timeline = []
        if hasattr(psychological_profile, 'emotional_timeline'):
            emotional_timeline = psychological_profile.emotional_timeline
            
        # Identify manipulation timing
        manipulation_windows = emotion_analyzer.identify_manipulation_timing(emotional_timeline)
        
        # Calculate emotional resilience
        resilience_metrics = emotion_analyzer.calculate_emotional_resilience(emotional_timeline)
        
        # Generate vulnerability protection plan
        protection_plan = vulnerability_mapper.generate_vulnerability_protection_plan(
            psychological_profile.vulnerabilities
        )
        
        # Calculate exploitation success rates  
        exploitation_rates = vulnerability_mapper.calculate_exploitation_success_rate(
            psychological_profile.vulnerabilities,
            psychological_profile.facebook_profile
        )
        
        # Compile comprehensive analysis results
        analysis_results = {
            "analysis_metadata": {
                "timestamp": str(engine.base_parser.analysis_timestamp),
                "data_path": str(data_path),
                "data_validation": engine.data_validation,
                "confidence_scores": psychological_profile.confidence_scores
            },
            "personality_analysis": {
                "ocean_traits": {
                    "openness": psychological_profile.ocean_traits.openness,
                    "conscientiousness": psychological_profile.ocean_traits.conscientiousness,
                    "extraversion": psychological_profile.ocean_traits.extraversion,
                    "agreeableness": psychological_profile.ocean_traits.agreeableness,
                    "neuroticism": psychological_profile.ocean_traits.neuroticism
                },
                "facebook_inferred_traits": {
                    "openness": facebook_traits.openness,
                    "conscientiousness": facebook_traits.conscientiousness,
                    "extraversion": facebook_traits.extraversion,
                    "agreeableness": facebook_traits.agreeableness,
                    "neuroticism": facebook_traits.neuroticism
                },
                "discrepancy_analysis": psychological_profile.facebook_vs_actual_discrepancy
            },
            "facebook_psychological_profile": {
                "inferred_interests": dict(psychological_profile.facebook_profile.inferred_interests),
                "behavioral_segments": psychological_profile.facebook_profile.behavioral_segments,
                "targeting_categories": psychological_profile.facebook_profile.targeting_categories,
                "ad_engagement_patterns": dict(psychological_profile.facebook_profile.ad_engagement_patterns),
                "vulnerability_windows": [
                    (ts.isoformat() if ts else None, desc) 
                    for ts, desc in psychological_profile.facebook_profile.vulnerability_windows
                ]
            },
            "vulnerability_analysis": {
                "identified_vulnerabilities": [
                    {
                        "type": vuln.vulnerability_type,
                        "severity": vuln.severity,
                        "exploitation_method": vuln.exploitation_method,
                        "facebook_evidence": vuln.facebook_exploitation_evidence
                    }
                    for vuln in psychological_profile.vulnerabilities
                ],
                "exploitation_success_rates": exploitation_rates,
                "protection_strategies": protection_plan
            },
            "manipulation_analysis": {
                "identified_tactics": manipulation_tactics,
                "manipulation_susceptibility": susceptibility,
                "manipulation_windows": [
                    {
                        "timestamp": ts.isoformat(),
                        "type": manipulation_type,
                        "vulnerability_score": score
                    }
                    for ts, manipulation_type, score in manipulation_windows
                ],
                "resistance_strategies": resistance_strategies
            },
            "emotional_analysis": {
                "mood_volatility": psychological_profile.mood_volatility,
                "resilience_metrics": resilience_metrics,
                "emotional_timeline_length": len(emotional_timeline)
            },
            "social_behavior": {
                "communication_patterns": psychological_profile.social_profile.communication_patterns if psychological_profile.social_profile else {},
                "relationship_dynamics": psychological_profile.social_profile.relationship_dynamics if psychological_profile.social_profile else {},
                "social_network_analysis": psychological_profile.social_profile.social_network_analysis if psychological_profile.social_profile else {}
            },
            "protective_recommendations": psychological_profile.protective_recommendations
        }
        
        # Save results if output path specified
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w') as f:
                json.dump(analysis_results, f, indent=2, default=str)
                
            logger.info(f"Analysis results saved to: {output_file}")
            
        # Print summary
        print_analysis_summary(analysis_results)
        
        logger.info("Facebook psychological profile analysis completed successfully")
        return analysis_results
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        return {"error": str(e)}


def print_analysis_summary(results: Dict[str, Any]):
    """Print a human-readable summary of the analysis"""
    print("\n" + "=" * 80)
    print("FACEBOOK DIGITAL PSYCHOMETRICS ANALYSIS SUMMARY")
    print("=" * 80)
    
    # Personality Analysis
    print("\n🧠 PERSONALITY ANALYSIS (OCEAN Traits)")
    print("-" * 40)
    personality = results["personality_analysis"]["ocean_traits"]
    for trait, score in personality.items():
        bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
        print(f"{trait.capitalize():15} │{bar}│ {score:.2f}")
    
    # Facebook vs Actual Comparison
    print("\n📊 FACEBOOK'S ASSESSMENT vs ACTUAL ANALYSIS")
    print("-" * 50)
    fb_traits = results["personality_analysis"]["facebook_inferred_traits"]
    actual_traits = results["personality_analysis"]["ocean_traits"]
    
    for trait in fb_traits.keys():
        fb_score = fb_traits[trait]
        actual_score = actual_traits[trait]
        difference = abs(fb_score - actual_score)
        accuracy = "✓" if difference < 0.2 else "⚠" if difference < 0.4 else "✗"
        print(f"{trait.capitalize():15} │ FB: {fb_score:.2f} │ Actual: {actual_score:.2f} │ {accuracy}")
    
    # Vulnerability Analysis
    print("\n🛡️ VULNERABILITY ANALYSIS")
    print("-" * 30)
    vulnerabilities = results["vulnerability_analysis"]["identified_vulnerabilities"]
    
    if vulnerabilities:
        for vuln in vulnerabilities:
            severity_bar = "🔴" if vuln["severity"] > 0.7 else "🟡" if vuln["severity"] > 0.4 else "🟢"
            print(f"{severity_bar} {vuln['type'].replace('_', ' ').title()}: {vuln['severity']:.2f}")
    else:
        print("No significant vulnerabilities identified")
    
    # Manipulation Analysis
    print("\n🎯 MANIPULATION ANALYSIS")
    print("-" * 25)
    manipulation = results["manipulation_analysis"]
    
    print("Susceptibility Scores:")
    for tactic, score in manipulation["manipulation_susceptibility"].items():
        risk_level = "HIGH" if score > 0.7 else "MEDIUM" if score > 0.4 else "LOW"
        print(f"  {tactic.replace('_', ' ').title()}: {score:.2f} ({risk_level})")
    
    # Key Recommendations
    print("\n💡 KEY PROTECTIVE RECOMMENDATIONS")
    print("-" * 35)
    recommendations = results["protective_recommendations"]
    
    for i, recommendation in enumerate(recommendations[:5], 1):  # Show top 5
        print(f"{i}. {recommendation}")
    
    if len(recommendations) > 5:
        print(f"   ... and {len(recommendations) - 5} more recommendations")
    
    # Data Quality
    print("\n📈 ANALYSIS CONFIDENCE")
    print("-" * 22)
    confidence = results["analysis_metadata"]["confidence_scores"]
    
    for metric, score in confidence.items():
        confidence_level = "HIGH" if score > 0.7 else "MEDIUM" if score > 0.4 else "LOW"
        print(f"{metric.replace('_', ' ').title()}: {score:.2f} ({confidence_level})")
    
    print("\n" + "=" * 80)
    print("Analysis complete. Full results saved to output file.")
    print("=" * 80)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Analyze Facebook profile data for psychological insights"
    )
    parser.add_argument(
        "data_path",
        help="Path to Facebook data export directory"
    )
    parser.add_argument(
        "-o", "--output",
        default="fb_psychological_profile.json",
        help="Output file path for analysis results"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Validate data path
    data_path = Path(args.data_path)
    if not data_path.exists():
        print(f"Error: Data path does not exist: {data_path}")
        return 1
        
    if not data_path.is_dir():
        print(f"Error: Data path is not a directory: {data_path}")
        return 1
    
    # Run analysis
    results = analyze_facebook_profile(
        str(data_path),
        args.output,
        args.verbose
    )
    
    if "error" in results:
        print(f"Analysis failed: {results['error']}")
        return 1
        
    return 0


if __name__ == "__main__":
    exit(main())
