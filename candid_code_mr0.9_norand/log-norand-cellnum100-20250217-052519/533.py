# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import time

# Put tunable constant parameters below
TEMPORAL_CLUSTER_THRESHOLD = 300  # seconds
ACCESS_FREQUENCY_DECAY = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, temporal clusters of access patterns, probabilistic models of future access likelihood, and contextual information such as time of day and user behavior patterns.
metadata = {
    'access_frequency': {},  # {obj.key: frequency}
    'last_access_time': {},  # {obj.key: last_access_time}
    'temporal_clusters': {},  # {obj.key: cluster_id}
    'contextual_info': {},  # {obj.key: context_info}
    'probabilistic_model': {}  # {obj.key: model_data}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by combining probabilistic models to predict future access likelihood, identifying objects with low predicted access probability, and considering temporal clusters to avoid evicting objects likely to be accessed soon in similar contexts.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        # Calculate the eviction score based on access frequency, last access time, and probabilistic model
        access_freq = metadata['access_frequency'].get(key, 0)
        last_access = metadata['last_access_time'].get(key, 0)
        cluster_id = metadata['temporal_clusters'].get(key, None)
        model_data = metadata['probabilistic_model'].get(key, None)
        
        # Example scoring function (this can be more complex based on actual probabilistic model)
        score = (1 / (access_freq + 1)) + (cache_snapshot.access_count - last_access)
        
        # Adjust score based on temporal clusters
        if cluster_id is not None and cluster_id == metadata['temporal_clusters'].get(obj.key, None):
            score *= 0.5  # Reduce score if in the same cluster
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency, last access time, and refines the probabilistic model for the accessed object. It also updates the temporal cluster to reflect the recent access and adjusts the contextual information based on the current context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Update access frequency
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    
    # Update last access time
    metadata['last_access_time'][key] = current_time
    
    # Update probabilistic model (placeholder for actual model update)
    metadata['probabilistic_model'][key] = metadata['probabilistic_model'].get(key, {})
    
    # Update temporal cluster
    if key not in metadata['temporal_clusters']:
        metadata['temporal_clusters'][key] = current_time // TEMPORAL_CLUSTER_THRESHOLD
    
    # Update contextual information (placeholder for actual context update)
    metadata['contextual_info'][key] = {'time_of_day': time.localtime().tm_hour}

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency, sets the last access time, and begins building its probabilistic model. It also assigns the object to a temporal cluster and records the contextual information at the time of insertion.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Initialize access frequency
    metadata['access_frequency'][key] = 1
    
    # Set last access time
    metadata['last_access_time'][key] = current_time
    
    # Initialize probabilistic model (placeholder for actual model initialization)
    metadata['probabilistic_model'][key] = {}
    
    # Assign to temporal cluster
    metadata['temporal_clusters'][key] = current_time // TEMPORAL_CLUSTER_THRESHOLD
    
    # Record contextual information (placeholder for actual context recording)
    metadata['contextual_info'][key] = {'time_of_day': time.localtime().tm_hour}

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the metadata associated with the evicted object, updates the temporal clusters to reflect the removal, and adjusts the probabilistic models and contextual information to account for the change in the cache contents.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    
    # Remove metadata associated with the evicted object
    if key in metadata['access_frequency']:
        del metadata['access_frequency'][key]
    if key in metadata['last_access_time']:
        del metadata['last_access_time'][key]
    if key in metadata['temporal_clusters']:
        del metadata['temporal_clusters'][key]
    if key in metadata['contextual_info']:
        del metadata['contextual_info'][key]
    if key in metadata['probabilistic_model']:
        del metadata['probabilistic_model'][key]
    
    # Update temporal clusters and probabilistic models (placeholder for actual updates)
    # This can involve recalculating clusters or adjusting models based on the new cache state