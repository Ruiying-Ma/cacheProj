# Import anything you need below
import time

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.4
LAST_ACCESS_WEIGHT = 0.3
PREDICTED_ACCESS_WEIGHT = 0.3

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including data retrieval frequency, last access timestamp, predicted future access time, and an adaptive priority score for each cached object.
metadata = {}

def calculate_priority(frequency, last_access, predicted_access, current_time):
    return (FREQUENCY_WEIGHT * frequency +
            LAST_ACCESS_WEIGHT * (current_time - last_access) +
            PREDICTED_ACCESS_WEIGHT * predicted_access)

def predict_next_access(frequency):
    # Simple prediction: assume next access will be in inverse proportion to frequency
    return 1 / frequency if frequency > 0 else float('inf')

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on the lowest adaptive priority score, which is calculated using a combination of low retrieval frequency, old last access timestamp, and distant predicted future access time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    lowest_priority = float('inf')
    current_time = cache_snapshot.access_count

    for key, cached_obj in cache_snapshot.cache.items():
        freq = metadata[key]['frequency']
        last_access = metadata[key]['last_access']
        predicted_access = metadata[key]['predicted_access']
        priority = calculate_priority(freq, last_access, predicted_access, current_time)
        
        if priority < lowest_priority:
            lowest_priority = priority
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the last access timestamp to the current time, increments the data retrieval frequency, and recalculates the adaptive priority score based on the updated frequency and timestamp.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    key = obj.key
    
    metadata[key]['frequency'] += 1
    metadata[key]['last_access'] = current_time
    metadata[key]['predicted_access'] = predict_next_access(metadata[key]['frequency'])
    metadata[key]['priority'] = calculate_priority(
        metadata[key]['frequency'],
        metadata[key]['last_access'],
        metadata[key]['predicted_access'],
        current_time
    )

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the last access timestamp to the current time, sets the data retrieval frequency to one, predicts the next access time based on historical patterns, and calculates the initial adaptive priority score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    key = obj.key
    
    metadata[key] = {
        'frequency': 1,
        'last_access': current_time,
        'predicted_access': predict_next_access(1),
        'priority': calculate_priority(1, current_time, predict_next_access(1), current_time)
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy removes all associated metadata for the evicted object and recalculates the adaptive priority scores for the remaining objects to ensure accurate future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata:
        del metadata[evicted_key]
    
    current_time = cache_snapshot.access_count
    for key, cached_obj in cache_snapshot.cache.items():
        metadata[key]['priority'] = calculate_priority(
            metadata[key]['frequency'],
            metadata[key]['last_access'],
            metadata[key]['predicted_access'],
            current_time
        )