# Import anything you need below
import time

# Put tunable constant parameters below
INITIAL_INTERACTION_PROPENSITY = 1.0
INITIAL_SEQUENTIAL_PATTERN_SCORE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, interaction propensity score, and a sequential access pattern score for each cached object.
metadata = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score based on the inverse of access frequency, the time since last access, the interaction propensity score, and the sequential access pattern score. The object with the lowest composite score is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        access_frequency = meta['access_frequency']
        last_access_time = meta['last_access_time']
        interaction_propensity = meta['interaction_propensity']
        sequential_pattern_score = meta['sequential_pattern_score']
        
        time_since_last_access = cache_snapshot.access_count - last_access_time
        composite_score = (1 / access_frequency) + time_since_last_access + interaction_propensity + sequential_pattern_score
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the access frequency is incremented, the last access time is updated to the current time, the interaction propensity score is recalculated based on recent interactions, and the sequential access pattern score is adjusted if the access follows a sequential pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    meta = metadata[key]
    
    meta['access_frequency'] += 1
    meta['last_access_time'] = cache_snapshot.access_count
    meta['interaction_propensity'] = calculate_interaction_propensity(meta)
    meta['sequential_pattern_score'] = calculate_sequential_pattern_score(meta, cache_snapshot)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the access frequency is initialized to 1, the last access time is set to the current time, the interaction propensity score is initialized based on initial interaction data, and the sequential access pattern score is set based on the initial access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata[key] = {
        'access_frequency': 1,
        'last_access_time': cache_snapshot.access_count,
        'interaction_propensity': INITIAL_INTERACTION_PROPENSITY,
        'sequential_pattern_score': INITIAL_SEQUENTIAL_PATTERN_SCORE
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the metadata for the evicted object is removed from the cache, and the composite scores for remaining objects are recalculated to ensure accurate future evictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata:
        del metadata[evicted_key]
    
    for key in cache_snapshot.cache:
        meta = metadata[key]
        meta['interaction_propensity'] = calculate_interaction_propensity(meta)
        meta['sequential_pattern_score'] = calculate_sequential_pattern_score(meta, cache_snapshot)

def calculate_interaction_propensity(meta):
    # Placeholder for actual interaction propensity calculation logic
    return meta['interaction_propensity']

def calculate_sequential_pattern_score(meta, cache_snapshot):
    # Placeholder for actual sequential pattern score calculation logic
    return meta['sequential_pattern_score']