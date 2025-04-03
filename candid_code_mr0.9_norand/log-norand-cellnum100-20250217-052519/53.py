# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import math

# Put tunable constant parameters below
ANOMALY_THRESHOLD = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency of access, normalized access patterns, and anomaly scores for each cached object. It also keeps a predictive score indicating the likelihood of future access.
metadata = {
    'access_frequency': {},
    'recency_of_access': {},
    'normalized_access_pattern': {},
    'anomaly_score': {},
    'predictive_score': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying objects with the lowest predictive scores, while also considering anomaly scores to avoid evicting objects with unusual but potentially important access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = math.inf

    for key, cached_obj in cache_snapshot.cache.items():
        predictive_score = metadata['predictive_score'][key]
        anomaly_score = metadata['anomaly_score'][key]
        
        # Calculate the effective score considering anomaly
        effective_score = predictive_score - ANOMALY_THRESHOLD * anomaly_score
        
        if effective_score < min_score:
            min_score = effective_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency, recency of access, and recalculates the normalized access pattern and predictive score for the accessed object. The anomaly score is also updated based on real-time analytics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count

    # Update access frequency
    metadata['access_frequency'][key] += 1

    # Update recency of access
    metadata['recency_of_access'][key] = current_time

    # Recalculate normalized access pattern
    total_accesses = sum(metadata['access_frequency'].values())
    metadata['normalized_access_pattern'][key] = metadata['access_frequency'][key] / total_accesses

    # Recalculate predictive score
    metadata['predictive_score'][key] = metadata['normalized_access_pattern'][key] * (current_time - metadata['recency_of_access'][key])

    # Update anomaly score (simple example, can be more complex)
    metadata['anomaly_score'][key] = abs(metadata['normalized_access_pattern'][key] - metadata['predictive_score'][key])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency, recency of access, normalized access pattern, and predictive score. An initial anomaly score is also calculated based on the object's access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count

    # Initialize access frequency
    metadata['access_frequency'][key] = 1

    # Initialize recency of access
    metadata['recency_of_access'][key] = current_time

    # Initialize normalized access pattern
    total_accesses = sum(metadata['access_frequency'].values())
    metadata['normalized_access_pattern'][key] = metadata['access_frequency'][key] / total_accesses

    # Initialize predictive score
    metadata['predictive_score'][key] = metadata['normalized_access_pattern'][key] * (current_time - metadata['recency_of_access'][key])

    # Initialize anomaly score
    metadata['anomaly_score'][key] = abs(metadata['normalized_access_pattern'][key] - metadata['predictive_score'][key])

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy removes all associated metadata for the evicted object and recalibrates the predictive and anomaly scores for the remaining objects to ensure accuracy in future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key

    # Remove metadata for the evicted object
    del metadata['access_frequency'][evicted_key]
    del metadata['recency_of_access'][evicted_key]
    del metadata['normalized_access_pattern'][evicted_key]
    del metadata['anomaly_score'][evicted_key]
    del metadata['predictive_score'][evicted_key]

    # Recalibrate predictive and anomaly scores for remaining objects
    total_accesses = sum(metadata['access_frequency'].values())
    for key in metadata['access_frequency']:
        metadata['normalized_access_pattern'][key] = metadata['access_frequency'][key] / total_accesses
        metadata['predictive_score'][key] = metadata['normalized_access_pattern'][key] * (cache_snapshot.access_count - metadata['recency_of_access'][key])
        metadata['anomaly_score'][key] = abs(metadata['normalized_access_pattern'][key] - metadata['predictive_score'][key])