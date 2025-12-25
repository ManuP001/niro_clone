"""Reading Evidence Pack Builder

Constructs a structured "evidence pack" from astro_features that the LLM can follow.
Ensures deterministic, short, and focused output with proper signal linking.

Includes tightened signal scoring to reduce noise and keep only high-quality signals.
Also captures ALL candidate signals for debug visibility.
"""

from typing import Dict, Any, List, Optional, Literal
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Global storage for candidate signals debug (keyed by run_id)
_candidate_signals_cache: Dict[str, Dict[str, Any]] = {}


def get_candidate_signals_debug(run_id: str) -> Optional[Dict[str, Any]]:
    """Get candidate signals debug data for a specific run."""
    return _candidate_signals_cache.get(run_id)


def get_latest_candidate_signals_debug(user_id: str = None) -> Optional[Dict[str, Any]]:
    """Get the most recent candidate signals debug data."""
    if not _candidate_signals_cache:
        return None
    
    # Get the most recent one by timestamp
    latest = None
    latest_ts = None
    for run_id, data in _candidate_signals_cache.items():
        if user_id and data.get('user_id') != user_id:
            continue
        ts = data.get('timestamp')
        if ts and (latest_ts is None or ts > latest_ts):
            latest = data
            latest_ts = ts
    return latest


def _extract_planet_from_signal(signal: Dict[str, Any]) -> str:
    """Extract planet name from signal evidence or claim."""
    planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
    
    evidence = signal.get('evidence', {})
    
    # Try evidence.planet first
    if isinstance(evidence, dict):
        planet = evidence.get('planet', '')
        if planet:
            # Normalize planet name
            for p in planets:
                if p.lower() == planet.lower():
                    return p
            return planet.title()
    
    claim = signal.get('claim', '')
    
    # Try to extract planet from claim
    for p in planets:
        if p.lower() in claim.lower():
            return p
    
    # For planet_strength type, try to parse the rule ID (e.g., "Rule3" might indicate a specific planet)
    sig_type = signal.get('type', '')
    if sig_type == 'planet_strength':
        # Check if there's house info which might help identify the planet
        if isinstance(evidence, dict):
            house = evidence.get('house')
            # Try to get from any nested structure
            for key in ['planet_name', 'planet', 'lord', 'significator']:
                if key in evidence:
                    val = evidence[key]
                    for p in planets:
                        if p.lower() in str(val).lower():
                            return p
    
    # Check applies_to for planet hints
    applies_to = signal.get('applies_to', '')
    for p in planets:
        if p.lower() in applies_to.lower():
            return p
    
    return 'Mixed'  # Instead of 'Unknown', use 'Mixed' for signals without clear planet


def _extract_house_from_signal(signal: Dict[str, Any]) -> Optional[int]:
    """Extract house number from signal evidence."""
    evidence = signal.get('evidence', {})
    if isinstance(evidence, dict):
        house = evidence.get('house')
        if house:
            try:
                return int(house)
            except (ValueError, TypeError):
                pass
    return None


def _humanize_signal_text(signal: Dict[str, Any]) -> str:
    """Generate human-readable text for a signal."""
    sig_type = signal.get('type', 'rule')
    claim = signal.get('claim', '')
    evidence = signal.get('evidence', {})
    polarity = signal.get('polarity', 'mixed')
    
    planet = _extract_planet_from_signal(signal)
    house = _extract_house_from_signal(signal)
    
    if sig_type == 'dasha':
        period = evidence.get('period', '') if isinstance(evidence, dict) else ''
        return f"{planet} Dasha period - {polarity} influence"
    elif sig_type == 'transit':
        if house:
            return f"{planet} transiting {house}th house - {polarity} effects"
        return f"{planet} transit - {polarity} influence"
    elif sig_type == 'yoga':
        return f"Yoga formed by {planet} - {claim}"
    elif sig_type == 'planet_strength':
        if house:
            return f"{planet} in {house}th house - strength indicator"
        return f"{planet} strength/dignity - {polarity}"
    else:
        return claim or f"{planet} {sig_type} - {polarity}"


def _score_signal(signal: Dict[str, Any], topic: Optional[str], time_context: str, intent: str = 'reflect') -> float:
    """
    Score a signal from 0.0 to 1.0 based on type, evidence quality, and relevance.
    
    Base scores by type:
    - dasha: 0.65
    - transit: 0.55
    - yoga: 0.50
    - planet_strength: 0.45
    - rule: 0.40
    
    Adjustments:
    - +0.15 if supportive + applies to topic
    - +0.10 if challenging AND future/compare/timing
    - +0.10 if time_window exists AND time_context=='future'
    - +0.10 if strong evidence (strength >= 0.75 or high dignity)
    - -0.20 if vague/incomplete evidence
    - -0.15 if applies_to generic but topic specific
    """
    sig_type = signal.get('type', 'rule')
    polarity = signal.get('polarity', 'mixed')
    applies_to = signal.get('applies_to', 'general')
    time_window = signal.get('time_window')
    evidence = signal.get('evidence', '')
    
    # Base score by type - more balanced to not over-favor dashas
    base_scores = {
        'dasha': 0.55,           # Reduced from 0.65
        'transit': 0.55,
        'yoga': 0.55,
        'planet_strength': 0.55,  # Increased from 0.45
        'rule': 0.50
    }
    score = base_scores.get(sig_type, 0.50)
    
    # Adjustment: polarity + topic match
    if polarity == 'supportive' and topic and applies_to in (topic, 'both'):
        score += 0.15
    
    # Adjustment: challenging + user wants cautions
    if polarity == 'challenging' and intent in ('timing', 'compare', 'advice'):
        score += 0.10
    
    # Adjustment: time window + future context
    if time_window and time_context == 'future':
        score += 0.10
    
    # Adjustment: past context - favor natal chart signals
    if time_context == 'past':
        if sig_type in ('planet_strength', 'yoga', 'rule'):
            score += 0.15  # Natal chart signals more relevant for past analysis
    
    # Adjustment: strong evidence quality
    if isinstance(evidence, dict) and len(evidence) >= 3:
        score += 0.10
    elif isinstance(evidence, str) and len(evidence) > 50:
        score += 0.10
    
    # Penalty: vague/incomplete evidence (reduced penalty)
    if isinstance(evidence, dict):
        missing_fields = [k for k in ['start_date', 'end_date', 'house', 'planet'] if k not in evidence or not evidence[k]]
        if len(missing_fields) >= 3:  # Increased threshold from 2 to 3
            score -= 0.10  # Reduced from 0.20
    elif isinstance(evidence, str) and len(evidence) < 5:  # Reduced from 10
        score -= 0.10
    
    # Penalty: generic applies_to on specific topic (reduced)
    if applies_to == 'general' and topic and topic != 'general':
        score -= 0.10  # Reduced from 0.15
    
    # Clamp to [0.0, 1.0]
    return max(0.0, min(1.0, score))


def _confidence_from_score(score: float) -> str:
    """Map score to confidence level"""
    if score >= 0.75:
        return 'high'
    elif score >= 0.60:
        return 'medium'
    else:
        return 'low'


def _priority_from_score(score: float) -> str:
    """Map score to priority level"""
    if score >= 0.80:
        return 'P0'
    elif score >= 0.65:
        return 'P1'
    else:
        return 'P2'


def build_reading_pack(
    user_question: str,
    topic: Optional[str],
    time_context: str,
    astro_features: Dict[str, Any],
    missing_keys: List[str] = None,
    intent: str = 'reflect'
) -> Dict[str, Any]:
    """
    Build a compact, deterministic reading pack from astro_features.
    
    Args:
        user_question: Original user question
        topic: Topic label (career, relationship, health, finance, etc.)
        time_context: Time context (past, present, future, timeless)
        astro_features: Full astro features dict from astro_client
        missing_keys: Optional list of missing data keys from coverage validator
        intent: User intent (timing, compare, advice, etc.) for scoring
        
    Returns:
        Dict with:
        - question
        - topic
        - time_context
        - decision_frame (if compare intent)
        - signals (list of max 6 high-quality signals, min 2)
        - timing_windows (list of up to 3 windows)
        - data_gaps (empty if no missing keys)
    """
    
    if missing_keys is None:
        missing_keys = []
    
    # Start building the pack
    pack = {
        'question': user_question,
        'topic': topic or 'general',
        'time_context': time_context,
        'decision_frame': None,
        'signals': [],
        'timing_windows': [],
        'data_gaps': []
    }
    
    # 1. Compute data_gaps from coverage validator results
    # Only include truly important missing fields
    important_missing = []
    if missing_keys:
        critical_fields = {
            'ascendant', 'moon_sign', 'sun_sign', 'mahadasha', 'antardasha',
            'planets', 'houses', 'transits', 'yogas'
        }
        important_missing = [k for k in missing_keys if k in critical_fields]
    
    pack['data_gaps'] = important_missing  # Empty list if no missing
    
    # 2. Build initial signals from astro_features (before scoring)
    # Signals are tied to specific houses/planets based on topic
    raw_signals = []
    signal_id_counter = 0
    
    # Signal type: dasha (mahadasha + antardasha)
    if astro_features.get('mahadasha'):
        maha = astro_features['mahadasha']
        signal_id_counter += 1
        raw_signals.append({
            'id': f'S{signal_id_counter}',
            'type': 'dasha',
            'claim': f"Mahadasha of {maha.get('planet', 'Unknown')}",
            'evidence': {
                'planet': maha.get('planet'),
                'start_date': maha.get('start_date'),
                'end_date': maha.get('end_date'),
                'years_remaining': maha.get('years_remaining', 0)
            },
            'polarity': _dasha_polarity(maha.get('planet', '')),
            'applies_to': topic or 'both',
            'time_window': f"{maha.get('start_date')} to {maha.get('end_date')}" if maha.get('start_date') else None
        })
    
    if astro_features.get('antardasha'):
        anta = astro_features['antardasha']
        signal_id_counter += 1
        raw_signals.append({
            'id': f'S{signal_id_counter}',
            'type': 'dasha',
            'claim': f"Antardasha of {anta.get('planet', 'Unknown')}",
            'evidence': {
                'planet': anta.get('planet'),
                'start_date': anta.get('start_date'),
                'end_date': anta.get('end_date'),
                'years_remaining': anta.get('years_remaining', 0)
            },
            'polarity': _dasha_polarity(anta.get('planet', '')),
            'applies_to': topic or 'both',
            'time_window': f"{anta.get('start_date')} to {anta.get('end_date')}" if anta.get('start_date') else None
        })
    
    # Signal type: house and planet strengths (from focus_factors)
    focus_factors = astro_features.get('focus_factors', [])
    for factor in focus_factors[:8]:  # Increased limit for pre-filtering
        signal_id_counter += 1
        rule_id = factor.get('rule_id', f'Rule{signal_id_counter}')
        strength = factor.get('strength', 0)
        
        # Determine polarity from strength
        if strength >= 0.7:
            polarity = 'supportive'
        elif strength <= 0.3:
            polarity = 'challenging'
        else:
            polarity = 'mixed'
        
        raw_signals.append({
            'id': f'S{signal_id_counter}',
            'type': 'planet_strength',
            'claim': f"{rule_id} (strength: {strength})",
            'evidence': factor.get('interpretation', ''),
            'polarity': polarity,
            'applies_to': topic or 'both',
            'time_window': None
        })
    
    # Signal type: yoga (if any)
    yogas = astro_features.get('yogas', [])
    for yoga in yogas[:3]:  # Increased limit for pre-filtering
        signal_id_counter += 1
        yoga_name = yoga.get('name', 'Yoga')
        yoga_interpretation = yoga.get('interpretation', '')
        
        raw_signals.append({
            'id': f'S{signal_id_counter}',
            'type': 'yoga',
            'claim': yoga_name,
            'evidence': yoga_interpretation,
            'polarity': 'supportive',
            'applies_to': topic or 'both',
            'time_window': None
        })
    
    # Signal type: key rules
    key_rules = astro_features.get('key_rules', [])
    for rule in key_rules[:6]:  # Increased limit for pre-filtering
        signal_id_counter += 1
        rule_name = rule.get('name', 'Rule')
        rule_interpretation = rule.get('interpretation', '')
        
        raw_signals.append({
            'id': f'S{signal_id_counter}',
            'type': 'rule',
            'claim': rule_name,
            'evidence': rule_interpretation,
            'polarity': rule.get('polarity', 'mixed'),
            'applies_to': topic or 'both',
            'time_window': rule.get('timing', None)
        })
    
    # Signal type: transits
    transits = astro_features.get('transits', [])
    for transit in transits[:8]:  # Increased limit for pre-filtering
        signal_id_counter += 1
        planet = transit.get('planet', 'Planet')
        sign = transit.get('sign', '')
        house = transit.get('house', '')
        nature = transit.get('nature', 'mixed')
        
        raw_signals.append({
            'id': f'S{signal_id_counter}',
            'type': 'transit',
            'claim': f"{planet} transiting {sign} (house {house})",
            'evidence': {
                'planet': planet,
                'sign': sign,
                'house': house,
                'start_date': transit.get('start_date'),
                'end_date': transit.get('end_date')
            },
            'polarity': nature,
            'applies_to': topic or 'both',
            'time_window': f"{transit.get('start_date')} to {transit.get('end_date')}" if transit.get('start_date') else None
        })
    
    # 3. Score and filter signals
    scored_signals = []
    for idx, signal in enumerate(raw_signals):
        score_raw = _score_signal(signal, topic, time_context, intent)
        confidence = _confidence_from_score(score_raw)
        priority = _priority_from_score(score_raw)
        
        # Add scoring metadata to signal
        signal['score'] = round(score_raw, 2)
        signal['score_raw'] = round(score_raw, 2)  # Keep raw score for debug
        signal['confidence'] = confidence
        signal['priority'] = priority
        signal['original_index'] = idx  # Track original position
        
        scored_signals.append(signal)
    
    # Sort by score descending
    scored_signals.sort(key=lambda s: s['score'], reverse=True)
    
    # Filter: keep max 6, min 4, drop < 0.45 unless it's the only option
    final_signals = []
    kept_signal_indices = set()
    
    for signal in scored_signals:
        if len(final_signals) >= 6:
            break
        if signal['score'] >= 0.45 or len(final_signals) < 4:
            final_signals.append(signal)
            kept_signal_indices.add(signal['original_index'])
    
    # Reindex signal IDs sequentially (S1, S2, ...)
    for idx, signal in enumerate(final_signals, 1):
        signal['id'] = f'S{idx}'
        signal['score_final'] = signal['score']
    
    pack['signals'] = final_signals
    
    # === CANDIDATE SIGNALS DEBUG CAPTURE ===
    # Capture ALL candidates with detailed metadata for debug visibility
    candidate_signals_list = []
    for idx, signal in enumerate(scored_signals):
        is_kept = signal['original_index'] in kept_signal_indices
        kept_reason = None
        if is_kept:
            kept_reason = "score >= 0.45" if signal['score'] >= 0.45 else "min_signals_required"
        else:
            kept_reason = "score < 0.45 and max_signals_reached"
        
        candidate_signals_list.append({
            'signal_id': f"C{idx + 1}",
            'final_id': signal.get('id') if is_kept else None,
            'signal_type': signal.get('type', 'unknown'),
            'planet': _extract_planet_from_signal(signal),
            'house': _extract_house_from_signal(signal),
            'time_direction': time_context,
            'time_window': signal.get('time_window'),
            'score_raw': signal.get('score_raw', 0),
            'score_final': signal.get('score', 0),
            'kept': is_kept,
            'kept_reason': kept_reason,
            'text_human': _humanize_signal_text(signal),
            'claim': signal.get('claim', ''),
            'polarity': signal.get('polarity', 'mixed'),
            'applies_to': signal.get('applies_to', 'general'),
            'confidence': signal.get('confidence', 'low'),
            'priority': signal.get('priority', 'P2'),
        })
    
    # Build summary statistics
    planet_counts = {}
    type_counts = {}
    for cs in candidate_signals_list:
        planet = cs['planet']
        sig_type = cs['signal_type']
        planet_counts[planet] = planet_counts.get(planet, 0) + 1
        type_counts[sig_type] = type_counts.get(sig_type, 0) + 1
    
    top_10_by_score = sorted(candidate_signals_list, key=lambda x: x['score_final'], reverse=True)[:10]
    
    debug_summary = {
        'total_candidates': len(candidate_signals_list),
        'kept_count': len(final_signals),
        'dropped_count': len(candidate_signals_list) - len(final_signals),
        'top_10_by_score': [{'signal_id': s['signal_id'], 'planet': s['planet'], 'score': s['score_final'], 'kept': s['kept']} for s in top_10_by_score],
        'counts_by_planet': planet_counts,
        'counts_by_type': type_counts,
    }
    
    # Store in cache (will be saved to DB by orchestrator)
    pack['_candidate_signals_debug'] = {
        'candidates': candidate_signals_list,
        'summary': debug_summary,
        'topic': topic,
        'time_context': time_context,
        'intent': intent,
        'timestamp': datetime.utcnow().isoformat(),
    }
    
    # 4. Extract timing windows (max 3)
    timing_windows = astro_features.get('timing_windows', [])
    pack['timing_windows'] = timing_windows[:3]
    
    # Log signal scoring summary
    top_scores = [s.get('score', 0) for s in final_signals]
    logger.info(
        f"[SIGNAL_SCORING] topic={topic} kept={len(final_signals)} dropped={len(scored_signals) - len(final_signals)} "
        f"top_scores={top_scores}"
    )
    
    logger.info(
        f"Built reading_pack: topic={topic}, time_context={time_context}, intent={intent}, "
        f"signals={len(pack['signals'])}, timing_windows={len(pack['timing_windows'])}, "
        f"gaps={len(pack['data_gaps'])}, total_candidates={len(candidate_signals_list)}"
    )
    
    return pack


def _dasha_polarity(planet: str) -> str:
    """Determine dasha polarity based on planet"""
    supportive = {'jupiter', 'venus', 'sun', 'mercury'}
    challenging = {'saturn', 'rahu', 'ketu', 'mars'}
    
    planet_lower = planet.lower() if planet else ''
    
    if planet_lower in supportive:
        return 'supportive'
    elif planet_lower in challenging:
        return 'challenging'
    else:
        return 'mixed'
