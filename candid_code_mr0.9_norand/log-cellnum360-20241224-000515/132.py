# Import anything you need below
import time

# Put tunable constant parameters below
DEFAULT_LATENCY_THRESHOLD = 100  # Default latency threshold value
INITIAL_CRITICAL_PATH_SCORE = 1  # Initial critical path score for new objects

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a critical path score for each cache entry, a load shedding counter, a latency threshold value, and a synchronization buffer timestamp. The critical path score predicts the importance of the entry in the execution path, while the load shedding counter tracks the frequency of access under high load conditions. The latency threshold value helps in determining the urgency of access, and the synchronization buffer timestamp records the last synchronization time with the main memory.
metadata = {
    'critical_path_score': {},  # Maps obj.key to its critical path score
    'load_shedding_counter': {},  # Maps obj.key to its load shedding counter
    'latency_threshold': {},  # Maps obj.key to its latency threshold
    'sync_buffer_timestamp': {}  # Maps obj.key to its synchronization buffer timestamp
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first identifying entries with the lowest critical path score. Among these, it selects the entry with the highest load shedding counter, indicating it is less critical under high load. If there is a tie, the entry with the oldest synchronization buffer timestamp is evicted, ensuring that more recently synchronized data is retained.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_critical_path_score = float('inf')
    for key in cache_snapshot.cache:
        score = metadata['critical_path_score'].get(key, float('inf'))
        if score < min_critical_path_score:
            min_critical_path_score = score

    candidates = [key for key in cache_snapshot.cache if metadata['critical_path_score'].get(key, float('inf')) == min_critical_path_score]

    if candidates:
        max_load_shedding_counter = -1
        for key in candidates:
            counter = metadata['load_shedding_counter'].get(key, -1)
            if counter > max_load_shedding_counter:
                max_load_shedding_counter = counter

        candidates = [key for key in candidates if metadata['load_shedding_counter'].get(key, -1) == max_load_shedding_counter]

    if candidates:
        oldest_timestamp = float('inf')
        for key in candidates:
            timestamp = metadata['sync_buffer_timestamp'].get(key, float('inf'))
            if timestamp < oldest_timestamp:
                oldest_timestamp = timestamp
                candid_obj_key = key

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the critical path score of the accessed entry is incremented, reflecting its importance. The load shedding counter is reset to zero, indicating successful access under current load. The latency threshold is adjusted based on the time taken to access the entry, and the synchronization buffer timestamp is updated to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['critical_path_score'][key] = metadata['critical_path_score'].get(key, 0) + 1
    metadata['load_shedding_counter'][key] = 0
    metadata['latency_threshold'][key] = DEFAULT_LATENCY_THRESHOLD  # Adjust as needed
    metadata['sync_buffer_timestamp'][key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the critical path score is initialized based on predicted importance. The load shedding counter is set to zero, indicating no recent high-load accesses. The latency threshold is set to a default value, and the synchronization buffer timestamp is initialized to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['critical_path_score'][key] = INITIAL_CRITICAL_PATH_SCORE
    metadata['load_shedding_counter'][key] = 0
    metadata['latency_threshold'][key] = DEFAULT_LATENCY_THRESHOLD
    metadata['sync_buffer_timestamp'][key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the policy recalibrates the critical path scores of remaining entries to ensure they reflect current execution paths. The load shedding counters are incremented for all entries, indicating increased pressure on the cache. The latency thresholds are adjusted to reflect the new cache state, and synchronization buffer timestamps are left unchanged.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    for key in cache_snapshot.cache:
        metadata['critical_path_score'][key] = max(1, metadata['critical_path_score'].get(key, 1) - 1)
        metadata['load_shedding_counter'][key] = metadata['load_shedding_counter'].get(key, 0) + 1
        metadata['latency_threshold'][key] = DEFAULT_LATENCY_THRESHOLD  # Adjust as needed