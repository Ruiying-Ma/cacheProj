# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_FREQUENCY = 1
BASELINE_RECENCY = 0
NEUTRAL_HEURISTIC_SCORE = 0
HEURISTIC_INCREMENT = 1
HEURISTIC_DECREMENT = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a dynamic profile for each cache entry, including access frequency, recency, and a heuristic score that adapts based on past eviction success. It also tracks load modulation metrics to adjust behavior under varying system loads and temporal patterns to identify time-based access trends.
cache_metadata = {
    'frequency': defaultdict(lambda: BASELINE_FREQUENCY),
    'recency': defaultdict(lambda: BASELINE_RECENCY),
    'heuristic_score': defaultdict(lambda: NEUTRAL_HEURISTIC_SCORE),
    'temporal_patterns': defaultdict(int),
    'load_modulation': 0
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects an eviction victim by combining the heuristic score with temporal analysis, prioritizing entries with low access frequency and recency. During high load, it favors evicting entries with less temporal relevance, adapting dynamically to current system conditions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (cache_metadata['heuristic_score'][key] +
                 cache_metadata['frequency'][key] +
                 cache_metadata['recency'][key] +
                 cache_metadata['temporal_patterns'][key])
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the access frequency and updates the recency timestamp of the entry. It also adjusts the heuristic score positively, reflecting the entry's continued relevance, and recalibrates temporal patterns to refine future predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    cache_metadata['frequency'][key] += 1
    cache_metadata['recency'][key] = cache_snapshot.access_count
    cache_metadata['heuristic_score'][key] += HEURISTIC_INCREMENT
    cache_metadata['temporal_patterns'][key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its dynamic profile with baseline frequency and recency values, assigns a neutral heuristic score, and incorporates it into the load modulation metrics to ensure balanced cache behavior.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    cache_metadata['frequency'][key] = BASELINE_FREQUENCY
    cache_metadata['recency'][key] = cache_snapshot.access_count
    cache_metadata['heuristic_score'][key] = NEUTRAL_HEURISTIC_SCORE
    cache_metadata['temporal_patterns'][key] = 0
    cache_metadata['load_modulation'] += obj.size

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy updates the heuristic scores of remaining entries based on the success of the eviction decision, recalibrates load modulation metrics to reflect the new cache state, and refines temporal analysis to improve future eviction choices.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    for key in cache_snapshot.cache:
        if key != evicted_key:
            cache_metadata['heuristic_score'][key] -= HEURISTIC_DECREMENT
            cache_metadata['temporal_patterns'][key] -= 1
    
    cache_metadata['load_modulation'] -= evicted_obj.size