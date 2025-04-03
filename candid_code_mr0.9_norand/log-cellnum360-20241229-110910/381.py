# Import anything you need below
from collections import defaultdict
import math

# Put tunable constant parameters below
BASELINE_FREQUENCY = 1
BASELINE_RECENCY = 1
NEUTRAL_IMPORTANCE = 1
INITIAL_ENTROPIC_SCORE = 1
TEMPORAL_FUSION_SHORT_TERM_WEIGHT = 0.5
TEMPORAL_FUSION_LONG_TERM_WEIGHT = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains a Resonance Map for each cache entry, which tracks the frequency and recency of access patterns. It also integrates a Cognitive Index that represents the perceived importance of each entry based on historical access patterns. Additionally, an Entropic Score is calculated to measure the randomness of access, and a Temporal Fusion metric is used to blend short-term and long-term access trends.
resonance_map = defaultdict(lambda: {'frequency': BASELINE_FREQUENCY, 'recency': BASELINE_RECENCY})
cognitive_index = defaultdict(lambda: NEUTRAL_IMPORTANCE)
entropic_score = defaultdict(lambda: INITIAL_ENTROPIC_SCORE)
temporal_fusion = defaultdict(lambda: TEMPORAL_FUSION_SHORT_TERM_WEIGHT * BASELINE_RECENCY + TEMPORAL_FUSION_LONG_TERM_WEIGHT * BASELINE_FREQUENCY)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the entry with the lowest combined score of Resonance Map, Cognitive Index, and Entropic Score, while considering Temporal Fusion to ensure a balance between recent and historical access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (resonance_map[key]['frequency'] + resonance_map[key]['recency'] +
                          cognitive_index[key] + entropic_score[key] +
                          temporal_fusion[key])
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Resonance Map is updated to reflect increased frequency and recency, the Cognitive Index is adjusted to increase the perceived importance, the Entropic Score is recalculated to account for reduced randomness, and the Temporal Fusion metric is updated to emphasize recent access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    resonance_map[key]['frequency'] += 1
    resonance_map[key]['recency'] = cache_snapshot.access_count
    cognitive_index[key] += 1
    entropic_score[key] = 1 / (resonance_map[key]['frequency'] + 1)
    temporal_fusion[key] = (TEMPORAL_FUSION_SHORT_TERM_WEIGHT * resonance_map[key]['recency'] +
                            TEMPORAL_FUSION_LONG_TERM_WEIGHT * resonance_map[key]['frequency'])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Resonance Map is initialized with baseline frequency and recency values, the Cognitive Index is set to a neutral importance level, the Entropic Score is calculated based on initial access patterns, and the Temporal Fusion metric is initialized to balance short-term and long-term trends.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    resonance_map[key] = {'frequency': BASELINE_FREQUENCY, 'recency': cache_snapshot.access_count}
    cognitive_index[key] = NEUTRAL_IMPORTANCE
    entropic_score[key] = INITIAL_ENTROPIC_SCORE
    temporal_fusion[key] = (TEMPORAL_FUSION_SHORT_TERM_WEIGHT * resonance_map[key]['recency'] +
                            TEMPORAL_FUSION_LONG_TERM_WEIGHT * resonance_map[key]['frequency'])

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the Resonance Map is adjusted to remove the evicted entry's influence, the Cognitive Index is recalibrated to reflect the change in cache composition, the Entropic Score is updated to account for the new randomness level, and the Temporal Fusion metric is recalculated to maintain equilibrium between recent and historical access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in resonance_map:
        del resonance_map[evicted_key]
    if evicted_key in cognitive_index:
        del cognitive_index[evicted_key]
    if evicted_key in entropic_score:
        del entropic_score[evicted_key]
    if evicted_key in temporal_fusion:
        del temporal_fusion[evicted_key]