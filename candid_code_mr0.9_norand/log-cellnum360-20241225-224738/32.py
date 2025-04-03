# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_VERSION = 1
INITIAL_CONSISTENCY_SCORE = 0.5  # Example initial score, can be adjusted

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a version number for each cached object, a replication count indicating how many replicas of the object exist across the system, and a consistency score that reflects the object's synchronization state with its replicas.
metadata = {
    'version': defaultdict(lambda: INITIAL_VERSION),
    'replication_count': defaultdict(int),
    'consistency_score': defaultdict(lambda: INITIAL_CONSISTENCY_SCORE)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a combination of the lowest consistency score and the highest replication count, prioritizing objects that are well-replicated and least synchronized.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    max_replication = -1

    for key, cached_obj in cache_snapshot.cache.items():
        score = metadata['consistency_score'][key]
        replication = metadata['replication_count'][key]

        if (score < min_score) or (score == min_score and replication > max_replication):
            min_score = score
            max_replication = replication
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the version number of the accessed object and recalculates its consistency score based on the latest synchronization state with its replicas.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['version'][key] += 1
    # Recalculate consistency score based on some logic, here we just increment for example
    metadata['consistency_score'][key] = min(1.0, metadata['consistency_score'][key] + 0.1)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its version number to 1, sets its replication count based on current system data, and assigns an initial consistency score reflecting its synchronization state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['version'][key] = INITIAL_VERSION
    # Set replication count based on some system data, here we assume a default value
    metadata['replication_count'][key] = 1  # Example value
    metadata['consistency_score'][key] = INITIAL_CONSISTENCY_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy updates the replication count of remaining objects to reflect the removal and recalculates their consistency scores to ensure accurate synchronization states.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    # Remove metadata for evicted object
    del metadata['version'][evicted_key]
    del metadata['replication_count'][evicted_key]
    del metadata['consistency_score'][evicted_key]

    # Update replication count and consistency score for remaining objects
    for key in cache_snapshot.cache:
        # Adjust replication count and consistency score based on some logic
        metadata['replication_count'][key] = max(1, metadata['replication_count'][key] - 1)
        metadata['consistency_score'][key] = max(0.0, metadata['consistency_score'][key] - 0.1)