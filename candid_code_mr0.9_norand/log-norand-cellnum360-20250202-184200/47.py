# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
import time

# Put tunable constant parameters below
INITIAL_PREDICTIVE_INVALIDATION_SCORE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, data replication status, and predictive invalidation scores for each cache line.
metadata = {
    'access_frequency': {},  # key -> access frequency
    'last_access_time': {},  # key -> last access time
    'predictive_invalidation_score': {},  # key -> predictive invalidation score
    'data_replication_status': {}  # key -> data replication status
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a combined score derived from the least frequently accessed, least recently accessed, and lowest predictive invalidation score, while ensuring cache coherence and considering data replication status.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        access_freq = metadata['access_frequency'].get(key, 0)
        last_access = metadata['last_access_time'].get(key, 0)
        invalidation_score = metadata['predictive_invalidation_score'].get(key, INITIAL_PREDICTIVE_INVALIDATION_SCORE)
        
        # Combined score: lower is better for eviction
        combined_score = access_freq + (cache_snapshot.access_count - last_access) + invalidation_score
        
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency and last access time for the cache line, recalculates the predictive invalidation score based on recent access patterns, and checks for any necessary coherence actions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    # Recalculate predictive invalidation score (example: simple decay model)
    metadata['predictive_invalidation_score'][key] = max(0, metadata['predictive_invalidation_score'].get(key, INITIAL_PREDICTIVE_INVALIDATION_SCORE) - 0.1)
    # Check for coherence actions (not implemented in this example)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency and last access time, sets an initial predictive invalidation score, and updates the data replication status to ensure coherence across the system.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predictive_invalidation_score'][key] = INITIAL_PREDICTIVE_INVALIDATION_SCORE
    metadata['data_replication_status'][key] = True  # Example status, assuming True means replicated

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy logs the eviction to adjust future predictive invalidation scores, updates the data replication status to reflect the removal, and ensures coherence by invalidating the evicted data in other caches if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    key = evicted_obj.key
    # Log the eviction (example: increase invalidation score)
    metadata['predictive_invalidation_score'][key] = metadata['predictive_invalidation_score'].get(key, INITIAL_PREDICTIVE_INVALIDATION_SCORE) + 1
    # Update data replication status
    metadata['data_replication_status'][key] = False  # Example status, assuming False means not replicated
    # Ensure coherence by invalidating the evicted data in other caches (not implemented in this example)