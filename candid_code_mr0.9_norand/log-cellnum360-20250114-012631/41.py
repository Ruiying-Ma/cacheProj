# Import anything you need below
import time

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for access frequency
BETA = 0.3   # Weight for temporal coherence
GAMMA = 0.1  # Weight for predicted future access time
DELTA = 0.1  # Weight for synaptic latency

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted future access time, and a synaptic latency score which measures the time difference between predicted and actual accesses.
metadata = {}

def calculate_composite_score(obj_key):
    data = metadata[obj_key]
    access_frequency = data['access_frequency']
    last_access_time = data['last_access_time']
    predicted_future_access_time = data['predicted_future_access_time']
    synaptic_latency = data['synaptic_latency']
    
    current_time = time.time()
    temporal_coherence = current_time - last_access_time
    
    composite_score = (ALPHA * access_frequency +
                       BETA * temporal_coherence +
                       GAMMA * predicted_future_access_time +
                       DELTA * synaptic_latency)
    return composite_score

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache entry based on its access frequency, temporal coherence, predicted future access time, and synaptic latency. The entry with the lowest composite score is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    lowest_score = float('inf')
    
    for key in cache_snapshot.cache:
        score = calculate_composite_score(key)
        if score < lowest_score:
            lowest_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency by incrementing it, updates the last access time to the current time, adjusts the predicted future access time based on recent access patterns, and recalculates the synaptic latency score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    current_time = time.time()
    data = metadata[obj.key]
    
    data['access_frequency'] += 1
    data['last_access_time'] = current_time
    data['predicted_future_access_time'] = current_time + (current_time - data['last_access_time']) / data['access_frequency']
    data['synaptic_latency'] = abs(data['predicted_future_access_time'] - current_time)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access time to the current time, predicts the future access time based on initial patterns, and sets an initial synaptic latency score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    current_time = time.time()
    metadata[obj.key] = {
        'access_frequency': 1,
        'last_access_time': current_time,
        'predicted_future_access_time': current_time + 1,  # Initial prediction
        'synaptic_latency': 0  # Initial latency
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalculates the composite scores for the remaining entries to ensure they reflect the most current state of the cache, and adjusts the synaptic latency scores based on the eviction impact.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    del metadata[evicted_obj.key]
    
    for key in cache_snapshot.cache:
        data = metadata[key]
        current_time = time.time()
        data['synaptic_latency'] = abs(data['predicted_future_access_time'] - current_time)