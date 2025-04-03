# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_PREDICTIVE_SCORE = 1.0
BASELINE_ADAPTIVE_RESONANCE = 1.0
TEMPORAL_HARMONY_BASELINE = 1.0
FREQUENCY_WEIGHT = 0.5
RECENCY_WEIGHT = 0.5
ADAPTIVE_ADJUSTMENT_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a 'Predictive Insight Score' for each cache entry, which is a composite score derived from access frequency, recency, and a predictive model that anticipates future access patterns. It also tracks 'Adaptive Resonance Levels' that adjust based on the cache's current hit/miss ratio, and 'Temporal Harmony Index' that aligns cache entries with temporal access patterns.
predictive_insight_scores = defaultdict(lambda: INITIAL_PREDICTIVE_SCORE)
adaptive_resonance_levels = defaultdict(lambda: BASELINE_ADAPTIVE_RESONANCE)
temporal_harmony_indices = defaultdict(lambda: TEMPORAL_HARMONY_BASELINE)
access_frequencies = defaultdict(int)
last_access_times = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest Predictive Insight Score, adjusted by the Adaptive Resonance Level to ensure dynamic adaptation to changing access patterns. The Temporal Harmony Index is used to break ties, favoring entries that least align with current temporal access trends.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (predictive_insight_scores[key] * adaptive_resonance_levels[key])
        if score < min_score or (score == min_score and temporal_harmony_indices[key] < temporal_harmony_indices[candid_obj_key]):
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Predictive Insight Score of the accessed entry is increased based on its current frequency and recency, while the Adaptive Resonance Level is adjusted to reflect the improved hit ratio. The Temporal Harmony Index is recalibrated to better align with the observed access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    access_frequencies[key] += 1
    last_access_times[key] = cache_snapshot.access_count
    
    frequency_score = FREQUENCY_WEIGHT * access_frequencies[key]
    recency_score = RECENCY_WEIGHT * (cache_snapshot.access_count - last_access_times[key])
    predictive_insight_scores[key] += frequency_score + recency_score
    
    hit_ratio = cache_snapshot.hit_count / (cache_snapshot.hit_count + cache_snapshot.miss_count)
    adaptive_resonance_levels[key] += ADAPTIVE_ADJUSTMENT_FACTOR * hit_ratio
    
    temporal_harmony_indices[key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its Predictive Insight Score based on initial access predictions and sets its Adaptive Resonance Level to a baseline value. The Temporal Harmony Index is set to reflect the current temporal access pattern, ensuring new entries are harmonized with ongoing trends.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    predictive_insight_scores[key] = INITIAL_PREDICTIVE_SCORE
    adaptive_resonance_levels[key] = BASELINE_ADAPTIVE_RESONANCE
    temporal_harmony_indices[key] = cache_snapshot.access_count
    access_frequencies[key] = 1
    last_access_times[key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the Adaptive Resonance Levels across the cache to account for the change in cache composition. The Predictive Insight Scores of remaining entries are adjusted to reflect the new cache dynamics, and the Temporal Harmony Index is updated to maintain alignment with temporal access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del predictive_insight_scores[evicted_key]
    del adaptive_resonance_levels[evicted_key]
    del temporal_harmony_indices[evicted_key]
    del access_frequencies[evicted_key]
    del last_access_times[evicted_key]
    
    for key in cache_snapshot.cache:
        hit_ratio = cache_snapshot.hit_count / (cache_snapshot.hit_count + cache_snapshot.miss_count)
        adaptive_resonance_levels[key] += ADAPTIVE_ADJUSTMENT_FACTOR * hit_ratio
        predictive_insight_scores[key] *= 0.9  # Decay factor to adjust scores
        temporal_harmony_indices[key] = cache_snapshot.access_count