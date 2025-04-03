# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for temporal coherence
BETA = 0.5   # Weight for access frequency

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, and a distributed coherence score for each cache entry. It also keeps track of the processing load on each node in the distributed framework.
metadata = {
    'access_frequency': {},  # Dictionary to store access frequency of each object
    'last_access_timestamp': {},  # Dictionary to store last access timestamp of each object
    'distributed_coherence_score': {},  # Dictionary to store distributed coherence score of each object
    'processing_load': 0  # Variable to store the processing load on the node
}

def calculate_coherence_score(access_frequency, last_access_timestamp, current_time):
    # Calculate the distributed coherence score based on access frequency and temporal coherence
    temporal_coherence = current_time - last_access_timestamp
    return ALPHA * temporal_coherence + BETA * access_frequency

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest distributed coherence score, factoring in both temporal coherence and access frequency. If multiple candidates have the same score, the entry with the oldest last access timestamp is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    oldest_timestamp = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = metadata['distributed_coherence_score'][key]
        timestamp = metadata['last_access_timestamp'][key]
        
        if score < min_score or (score == min_score and timestamp < oldest_timestamp):
            min_score = score
            oldest_timestamp = timestamp
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the access frequency, updates the last access timestamp, and recalculates the distributed coherence score for the accessed entry. It also adjusts the processing load metadata to reflect the current state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Update access frequency
    metadata['access_frequency'][key] += 1
    
    # Update last access timestamp
    metadata['last_access_timestamp'][key] = current_time
    
    # Recalculate distributed coherence score
    metadata['distributed_coherence_score'][key] = calculate_coherence_score(
        metadata['access_frequency'][key],
        metadata['last_access_timestamp'][key],
        current_time
    )
    
    # Adjust processing load metadata
    metadata['processing_load'] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency, sets the current timestamp as the last access time, and calculates an initial distributed coherence score. It also updates the processing load metadata to account for the new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Initialize access frequency
    metadata['access_frequency'][key] = 1
    
    # Set last access timestamp
    metadata['last_access_timestamp'][key] = current_time
    
    # Calculate initial distributed coherence score
    metadata['distributed_coherence_score'][key] = calculate_coherence_score(
        metadata['access_frequency'][key],
        metadata['last_access_timestamp'][key],
        current_time
    )
    
    # Update processing load metadata
    metadata['processing_load'] += 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the metadata associated with the evicted entry and recalculates the distributed coherence scores for the remaining entries. It also updates the processing load metadata to reflect the removal.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove metadata associated with the evicted entry
    del metadata['access_frequency'][evicted_key]
    del metadata['last_access_timestamp'][evicted_key]
    del metadata['distributed_coherence_score'][evicted_key]
    
    # Recalculate distributed coherence scores for the remaining entries
    current_time = cache_snapshot.access_count
    for key in cache_snapshot.cache:
        metadata['distributed_coherence_score'][key] = calculate_coherence_score(
            metadata['access_frequency'][key],
            metadata['last_access_timestamp'][key],
            current_time
        )
    
    # Update processing load metadata
    metadata['processing_load'] -= 1