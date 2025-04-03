# Import anything you need below
import math

# Put tunable constant parameters below
WEIGHT_FREQUENCY = 0.4
WEIGHT_RECENCY = 0.3
WEIGHT_PREDICTED_NEXT_ACCESS = 0.3

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted next access time using a predictive heuristic, and a dynamic priority score for each cached object.
metadata = {}

def calculate_priority_score(access_frequency, last_access_time, predicted_next_access_time, current_time):
    recency = current_time - last_access_time
    priority_score = (WEIGHT_FREQUENCY * access_frequency +
                      WEIGHT_RECENCY * recency +
                      WEIGHT_PREDICTED_NEXT_ACCESS * predicted_next_access_time)
    return priority_score

def predict_next_access_time(access_frequency):
    # Simple heuristic: predict next access time as inversely proportional to access frequency
    return 1 / (access_frequency + 1)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by dynamically calculating a priority score for each object, which is a weighted combination of access frequency, recency, and predicted next access time. The object with the lowest priority score is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    lowest_priority_score = math.inf
    current_time = cache_snapshot.access_count

    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        priority_score = calculate_priority_score(meta['access_frequency'], meta['last_access_time'], meta['predicted_next_access_time'], current_time)
        if priority_score < lowest_priority_score:
            lowest_priority_score = priority_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the last access time to the current time, increments the access frequency, and recalculates the predicted next access time using the predictive heuristic. The dynamic priority score is then updated based on these new values.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    meta = metadata[obj.key]
    meta['last_access_time'] = current_time
    meta['access_frequency'] += 1
    meta['predicted_next_access_time'] = predict_next_access_time(meta['access_frequency'])
    meta['priority_score'] = calculate_priority_score(meta['access_frequency'], meta['last_access_time'], meta['predicted_next_access_time'], current_time)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the last access time to the current time, sets the access frequency to 1, predicts the next access time using the heuristic, and calculates the initial dynamic priority score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    access_frequency = 1
    predicted_next_access_time = predict_next_access_time(access_frequency)
    priority_score = calculate_priority_score(access_frequency, current_time, predicted_next_access_time, current_time)
    
    metadata[obj.key] = {
        'last_access_time': current_time,
        'access_frequency': access_frequency,
        'predicted_next_access_time': predicted_next_access_time,
        'priority_score': priority_score
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy removes all associated metadata for the evicted object and recalculates the dynamic priority scores for the remaining objects to ensure they reflect the current cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    del metadata[evicted_obj.key]
    current_time = cache_snapshot.access_count

    for key, meta in metadata.items():
        meta['priority_score'] = calculate_priority_score(meta['access_frequency'], meta['last_access_time'], meta['predicted_next_access_time'], current_time)