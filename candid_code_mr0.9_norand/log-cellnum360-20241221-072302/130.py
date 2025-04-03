# Import anything you need below
import time

# Put tunable constant parameters below
DEFAULT_LATENCY_CALIBRATION = 1.0
INITIAL_PERSISTENCE_SCORE = 1.0
RESOURCE_OPTIMIZATION_FACTOR = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a persistence score for each cache entry, a latency calibration factor, an event synchronization timestamp, and a resource optimization index. The persistence score reflects the likelihood of future access, the latency calibration factor adjusts based on access speed, the event synchronization timestamp tracks the last access time, and the resource optimization index measures resource usage efficiency.
metadata = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest combined score of persistence and resource optimization index, adjusted by the latency calibration factor. This ensures that entries with low future access probability and inefficient resource usage are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        combined_score = (meta['persistence_score'] + meta['resource_optimization_index']) / meta['latency_calibration']
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the persistence score of the accessed entry is increased, the latency calibration factor is adjusted based on the time taken to access the entry, the event synchronization timestamp is updated to the current time, and the resource optimization index is recalculated to reflect improved efficiency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['persistence_score'] += 1
    meta['latency_calibration'] *= 0.9  # Simulate faster access
    meta['event_sync_timestamp'] = cache_snapshot.access_count
    meta['resource_optimization_index'] *= 1.1  # Simulate improved efficiency

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the persistence score is initialized based on historical access patterns, the latency calibration factor is set to a default value, the event synchronization timestamp is set to the current time, and the resource optimization index is calculated based on initial resource allocation.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    metadata[obj.key] = {
        'persistence_score': INITIAL_PERSISTENCE_SCORE,
        'latency_calibration': DEFAULT_LATENCY_CALIBRATION,
        'event_sync_timestamp': cache_snapshot.access_count,
        'resource_optimization_index': RESOURCE_OPTIMIZATION_FACTOR * obj.size
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy recalibrates the latency factor for remaining entries to ensure balanced access speed, updates the event synchronization timestamps to reflect the eviction event, and adjusts the resource optimization index to account for freed resources, potentially boosting the scores of remaining entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key, meta in metadata.items():
        if key != evicted_obj.key:
            meta['latency_calibration'] *= 1.05  # Recalibrate latency factor
            meta['event_sync_timestamp'] = cache_snapshot.access_count
            meta['resource_optimization_index'] *= 1.05  # Boost efficiency score
    # Remove metadata for evicted object
    if evicted_obj.key in metadata:
        del metadata[evicted_obj.key]