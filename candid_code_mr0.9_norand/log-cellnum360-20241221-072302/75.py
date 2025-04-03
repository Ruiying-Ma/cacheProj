# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
PRIORITY_INCREMENT = 1
LOAD_SCORE_INCREMENT = 1
INITIAL_ACCESS_FREQUENCY = 0
INITIAL_PRIORITY_LEVEL = 0
INITIAL_LOAD_SCORE = 0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry including access frequency, last access timestamp, priority level, and a load score. It also tracks a global threshold for access frequency and load balance across cache entries.
metadata = defaultdict(lambda: {
    'access_frequency': INITIAL_ACCESS_FREQUENCY,
    'last_access_timestamp': 0,
    'priority_level': INITIAL_PRIORITY_LEVEL,
    'load_score': INITIAL_LOAD_SCORE
})
global_access_frequency_threshold = 1

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first identifying entries below the global access frequency threshold. Among these, it selects the entry with the lowest priority level and highest load score, ensuring balanced load distribution.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_priority = float('inf')
    max_load_score = float('-inf')

    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        if meta['access_frequency'] < global_access_frequency_threshold:
            if (meta['priority_level'] < min_priority) or \
               (meta['priority_level'] == min_priority and meta['load_score'] > max_load_score):
                min_priority = meta['priority_level']
                max_load_score = meta['load_score']
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency and last access timestamp of the entry are updated. If the access frequency exceeds the global threshold, the priority level is increased, and the load score is adjusted to reflect the new access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['access_frequency'] += 1
    meta['last_access_timestamp'] = cache_snapshot.access_count

    if meta['access_frequency'] > global_access_frequency_threshold:
        meta['priority_level'] += PRIORITY_INCREMENT
        meta['load_score'] += LOAD_SCORE_INCREMENT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency, last access timestamp, and load score. The global threshold is recalibrated if necessary to maintain optimal load equalization across the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    metadata[obj.key] = {
        'access_frequency': INITIAL_ACCESS_FREQUENCY,
        'last_access_timestamp': cache_snapshot.access_count,
        'priority_level': INITIAL_PRIORITY_LEVEL,
        'load_score': INITIAL_LOAD_SCORE
    }
    # Recalibrate global threshold if necessary
    recalculate_global_threshold(cache_snapshot)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the policy recalculates the global access frequency threshold and adjusts the load scores of remaining entries to ensure continued load equalization and efficient cache utilization.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Remove metadata of evicted object
    if evicted_obj.key in metadata:
        del metadata[evicted_obj.key]
    
    # Recalculate global threshold
    recalculate_global_threshold(cache_snapshot)

    # Adjust load scores of remaining entries
    for key in cache_snapshot.cache:
        metadata[key]['load_score'] = max(INITIAL_LOAD_SCORE, metadata[key]['load_score'] - LOAD_SCORE_INCREMENT)

def recalculate_global_threshold(cache_snapshot):
    '''
    Recalculates the global access frequency threshold based on current cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
    - Return: `None`
    '''
    global global_access_frequency_threshold
    if cache_snapshot.cache:
        total_access_frequency = sum(meta['access_frequency'] for meta in metadata.values())
        global_access_frequency_threshold = max(1, total_access_frequency // len(cache_snapshot.cache))