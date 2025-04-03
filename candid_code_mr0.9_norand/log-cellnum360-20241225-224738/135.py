# Import anything you need below
import time
import threading

# Put tunable constant parameters below
DEFAULT_LATENCY_SCORE = 100  # Default latency prediction score for new entries

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a latency prediction score for each cache entry, a consistency timestamp to ensure data validity, and a resource synchronization flag to manage concurrent access.
metadata = {
    'latency_scores': {},  # Maps object keys to their latency prediction scores
    'consistency_timestamps': {},  # Maps object keys to their consistency timestamps
    'resource_sync_flags': {}  # Maps object keys to their resource synchronization flags
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on the lowest latency prediction score, ensuring that the least impactful entry in terms of access speed is removed, while also considering the consistency timestamp to avoid evicting recently updated entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    current_time = cache_snapshot.access_count

    for key, cached_obj in cache_snapshot.cache.items():
        latency_score = metadata['latency_scores'].get(key, DEFAULT_LATENCY_SCORE)
        consistency_timestamp = metadata['consistency_timestamps'].get(key, 0)

        # Choose the object with the lowest latency score and not recently updated
        if latency_score < min_score and (current_time - consistency_timestamp) > 0:
            min_score = latency_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the latency prediction score is adjusted based on the actual access time, the consistency timestamp is refreshed to the current time, and the resource synchronization flag is checked to ensure no concurrent updates are pending.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count

    # Adjust latency prediction score (for simplicity, decrement by 1)
    metadata['latency_scores'][key] = metadata['latency_scores'].get(key, DEFAULT_LATENCY_SCORE) - 1

    # Refresh consistency timestamp
    metadata['consistency_timestamps'][key] = current_time

    # Check resource synchronization flag
    if metadata['resource_sync_flags'].get(key, False):
        # Handle pending updates if necessary
        pass

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the latency prediction score is initialized based on historical data or a default value, the consistency timestamp is set to the current time, and the resource synchronization flag is set to indicate the entry is ready for access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count

    # Initialize latency prediction score
    metadata['latency_scores'][key] = DEFAULT_LATENCY_SCORE

    # Set consistency timestamp
    metadata['consistency_timestamps'][key] = current_time

    # Set resource synchronization flag
    metadata['resource_sync_flags'][key] = False

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the metadata for the evicted entry is cleared, and the latency prediction scores of remaining entries are recalibrated to reflect the new cache state, while ensuring consistency timestamps remain accurate and resource synchronization flags are reset as needed.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key

    # Clear metadata for the evicted entry
    metadata['latency_scores'].pop(evicted_key, None)
    metadata['consistency_timestamps'].pop(evicted_key, None)
    metadata['resource_sync_flags'].pop(evicted_key, None)

    # Recalibrate latency prediction scores for remaining entries
    for key in cache_snapshot.cache.keys():
        metadata['latency_scores'][key] = max(metadata['latency_scores'][key] - 1, 0)

    # Reset resource synchronization flags as needed
    for key in cache_snapshot.cache.keys():
        metadata['resource_sync_flags'][key] = False