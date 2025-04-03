# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASE_PRIORITY_SCORE = 1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry, including a priority score, a dynamic escalation counter, a temporal buffer timestamp, and a load synchronization flag. The priority score determines the importance of the entry, the dynamic escalation counter tracks recent access frequency, the temporal buffer timestamp records the last access time, and the load synchronization flag indicates if the entry is part of a synchronized load operation.
metadata = defaultdict(lambda: {
    'priority_score': BASE_PRIORITY_SCORE,
    'dynamic_escalation_counter': 0,
    'temporal_buffer_timestamp': 0,
    'load_synchronization_flag': False
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest priority score. In case of a tie, it considers the dynamic escalation counter, preferring to evict entries with lower access frequency. If still tied, it uses the oldest temporal buffer timestamp. Entries with an active load synchronization flag are protected from eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_priority = float('inf')
    min_escalation = float('inf')
    oldest_timestamp = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        if meta['load_synchronization_flag']:
            continue
        if (meta['priority_score'] < min_priority or
            (meta['priority_score'] == min_priority and meta['dynamic_escalation_counter'] < min_escalation) or
            (meta['priority_score'] == min_priority and meta['dynamic_escalation_counter'] == min_escalation and meta['temporal_buffer_timestamp'] < oldest_timestamp)):
            min_priority = meta['priority_score']
            min_escalation = meta['dynamic_escalation_counter']
            oldest_timestamp = meta['temporal_buffer_timestamp']
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the priority score of the accessed entry and increments its dynamic escalation counter. The temporal buffer timestamp is updated to the current time, and the load synchronization flag is checked to ensure it remains accurate.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['priority_score'] += 1
    meta['dynamic_escalation_counter'] += 1
    meta['temporal_buffer_timestamp'] = cache_snapshot.access_count
    # Assuming load synchronization flag remains unchanged on hit

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its priority score to a base level, sets the dynamic escalation counter to zero, records the current time in the temporal buffer timestamp, and sets the load synchronization flag based on whether the insertion is part of a synchronized load operation.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['priority_score'] = BASE_PRIORITY_SCORE
    meta['dynamic_escalation_counter'] = 0
    meta['temporal_buffer_timestamp'] = cache_snapshot.access_count
    # Assuming we have a way to determine if this is part of a synchronized load operation
    meta['load_synchronization_flag'] = False  # Set this based on actual condition

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy recalibrates the priority scores of remaining entries to ensure balance, resets the dynamic escalation counters to prevent bias, and clears any load synchronization flags that may have been affected by the eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    del metadata[evicted_obj.key]
    for key in cache_snapshot.cache:
        meta = metadata[key]
        meta['priority_score'] = max(BASE_PRIORITY_SCORE, meta['priority_score'] - 1)
        meta['dynamic_escalation_counter'] = 0
        meta['load_synchronization_flag'] = False