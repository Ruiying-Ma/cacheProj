# Import anything you need below
import time

# Put tunable constant parameters below
LATENCY_SENSITIVITY = 1.0  # This is a tunable parameter for latency sensitivity

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, predicted next access time, and a heuristic score for each cache entry. The heuristic score is calculated based on a combination of access patterns and latency sensitivity of the data.
metadata = {}

def calculate_heuristic_score(access_frequency, last_access_time, predicted_next_access_time, latency_sensitivity):
    # Heuristic score calculation based on access patterns and latency sensitivity
    current_time = time.time()
    time_since_last_access = current_time - last_access_time
    time_until_next_access = predicted_next_access_time - current_time
    score = (access_frequency / (time_since_last_access + 1)) * latency_sensitivity / (time_until_next_access + 1)
    return score

def predict_next_access_time(access_frequency, last_access_time):
    # Simple prediction algorithm for next access time
    current_time = time.time()
    return current_time + (current_time - last_access_time) / (access_frequency + 1)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache entry with the lowest heuristic score, which is a function of predicted next access time, access frequency, and latency sensitivity. This ensures that entries with low likelihood of imminent reuse and low latency impact are evicted first.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    lowest_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        score = calculate_heuristic_score(meta['access_frequency'], meta['last_access_time'], meta['predicted_next_access_time'], meta['latency_sensitivity'])
        if score < lowest_score:
            lowest_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the last access timestamp and increments the access frequency for the accessed entry. It also recalculates the predicted next access time using temporal prediction algorithms and updates the heuristic score accordingly.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = time.time()
    metadata[key]['access_frequency'] += 1
    metadata[key]['last_access_time'] = current_time
    metadata[key]['predicted_next_access_time'] = predict_next_access_time(metadata[key]['access_frequency'], current_time)
    metadata[key]['heuristic_score'] = calculate_heuristic_score(
        metadata[key]['access_frequency'],
        metadata[key]['last_access_time'],
        metadata[key]['predicted_next_access_time'],
        metadata[key]['latency_sensitivity']
    )

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the metadata for the new entry, setting the initial access frequency to 1, recording the current timestamp as the last access time, predicting the next access time, and calculating the initial heuristic score based on the object's latency sensitivity and predicted access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = time.time()
    metadata[key] = {
        'access_frequency': 1,
        'last_access_time': current_time,
        'predicted_next_access_time': predict_next_access_time(1, current_time),
        'latency_sensitivity': LATENCY_SENSITIVITY,
        'heuristic_score': calculate_heuristic_score(1, current_time, predict_next_access_time(1, current_time), LATENCY_SENSITIVITY)
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the metadata associated with the evicted entry and may adjust the heuristic scores of remaining entries if the eviction impacts the overall cache dynamics, ensuring optimal memory allocation and latency minimization.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata:
        del metadata[evicted_key]
    
    # Optionally adjust heuristic scores of remaining entries if needed
    for key, meta in metadata.items():
        meta['heuristic_score'] = calculate_heuristic_score(
            meta['access_frequency'],
            meta['last_access_time'],
            meta['predicted_next_access_time'],
            meta['latency_sensitivity']
        )