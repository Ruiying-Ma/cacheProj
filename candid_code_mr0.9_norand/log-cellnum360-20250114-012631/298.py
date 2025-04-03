# Import anything you need below
import time

# Put tunable constant parameters below
INITIAL_PREDICTIVE_SCORE = 0.5
ADAPTIVE_THRESHOLD = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, synthesized data patterns, adaptive thresholds for eviction, and a predictive model score for each cache entry.
metadata = {
    'access_frequency': {},
    'last_access_time': {},
    'predictive_model_score': {},
    'adaptive_threshold': ADAPTIVE_THRESHOLD
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by combining adaptive thresholds with predictive model scores, prioritizing entries with low access frequency, older last access times, and lower predictive scores, while ensuring temporal coherence.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_freq = metadata['access_frequency'].get(key, 0)
        last_access = metadata['last_access_time'].get(key, 0)
        predictive_score = metadata['predictive_model_score'].get(key, INITIAL_PREDICTIVE_SCORE)
        
        score = (access_freq * 0.3) + (last_access * 0.3) + (predictive_score * 0.4)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency, last access time, and recalculates the predictive model score for the accessed entry, while adjusting adaptive thresholds based on recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predictive_model_score'][key] = calculate_predictive_score(key)
    adjust_adaptive_threshold()

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency, sets the current time as the last access time, synthesizes initial data patterns, and computes an initial predictive model score, while recalibrating adaptive thresholds.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predictive_model_score'][key] = INITIAL_PREDICTIVE_SCORE
    adjust_adaptive_threshold()

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy updates the adaptive thresholds based on the characteristics of the evicted entry and recent access patterns, and recalculates predictive model scores for remaining entries to maintain temporal coherence.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['last_access_time']:
        del metadata['last_access_time'][evicted_key]
    if evicted_key in metadata['predictive_model_score']:
        del metadata['predictive_model_score'][evicted_key]
    
    adjust_adaptive_threshold()
    for key in cache_snapshot.cache:
        metadata['predictive_model_score'][key] = calculate_predictive_score(key)

def calculate_predictive_score(key):
    '''
    This function calculates the predictive model score for a given key.
    - Args:
        - `key`: The key of the object.
    - Return: `score`: The predictive model score.
    '''
    access_freq = metadata['access_frequency'].get(key, 0)
    last_access = metadata['last_access_time'].get(key, 0)
    return (access_freq * 0.5) + (last_access * 0.5)

def adjust_adaptive_threshold():
    '''
    This function adjusts the adaptive threshold based on recent access patterns.
    - Return: `None`
    '''
    total_accesses = sum(metadata['access_frequency'].values())
    if total_accesses > 0:
        metadata['adaptive_threshold'] = total_accesses / len(metadata['access_frequency'])
    else:
        metadata['adaptive_threshold'] = ADAPTIVE_THRESHOLD