# Import anything you need below
from collections import defaultdict
import math

# Put tunable constant parameters below
INITIAL_COMPUTATIONAL_VECTOR = 1
SYNCHRONIZATION_INCREMENT = 1
TEMPORAL_DECAY_FACTOR = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains a Computational Vector for each cache entry, representing the frequency and recency of access patterns. It also tracks a Synchronization Phase counter to align cache operations with system-wide events. A Predictive Loop is used to anticipate future access patterns based on historical data, and Temporal Execution timestamps are recorded to monitor the time since last access.
computational_vectors = defaultdict(lambda: INITIAL_COMPUTATIONAL_VECTOR)
temporal_execution_timestamps = {}
synchronization_phase = 0
predictive_loop = defaultdict(lambda: 0)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the cache entry with the lowest value in its Computational Vector, adjusted by the Synchronization Phase. Entries with outdated Temporal Execution timestamps are prioritized if Predictive Loop forecasts low future access probability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_value = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        cv_value = computational_vectors[key] - synchronization_phase
        time_since_last_access = cache_snapshot.access_count - temporal_execution_timestamps[key]
        predicted_access = predictive_loop[key]
        
        if predicted_access < 0.5:  # Arbitrary threshold for low future access probability
            cv_value *= TEMPORAL_DECAY_FACTOR ** time_since_last_access
        
        if cv_value < min_value:
            min_value = cv_value
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the corresponding entry's Computational Vector to reflect increased access frequency and updates the Temporal Execution timestamp to the current time. The Synchronization Phase is checked and adjusted if necessary to maintain alignment.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    computational_vectors[key] += 1
    temporal_execution_timestamps[key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its Computational Vector based on initial access patterns and sets the Temporal Execution timestamp to the current time. The Synchronization Phase is incremented to reflect the addition of a new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    computational_vectors[key] = INITIAL_COMPUTATIONAL_VECTOR
    temporal_execution_timestamps[key] = cache_snapshot.access_count
    global synchronization_phase
    synchronization_phase += SYNCHRONIZATION_INCREMENT

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the Synchronization Phase to account for the removed entry and adjusts the Predictive Loop to refine future access predictions. The Computational Vectors of remaining entries are normalized to maintain relative accuracy.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    del computational_vectors[key]
    del temporal_execution_timestamps[key]
    del predictive_loop[key]
    
    global synchronization_phase
    synchronization_phase -= SYNCHRONIZATION_INCREMENT
    
    # Normalize the computational vectors
    max_cv = max(computational_vectors.values(), default=1)
    for k in computational_vectors:
        computational_vectors[k] /= max_cv