# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
WEIGHT_FREQUENCY = 1.0
WEIGHT_RECENCY = 1.0
WEIGHT_SIZE = 1.0
WEIGHT_DISTRIBUTED_SCORE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, data size, and a distributed access pattern score that reflects the object's usage across different nodes in the distributed system.
metadata = {
    'access_frequency': defaultdict(int),
    'last_access_timestamp': {},
    'data_size': {},
    'distributed_access_pattern_score': defaultdict(float)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each object, which is a weighted sum of its access frequency, recency, size, and distributed access pattern score. The object with the lowest score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        frequency = metadata['access_frequency'][key]
        recency = cache_snapshot.access_count - metadata['last_access_timestamp'][key]
        size = metadata['data_size'][key]
        distributed_score = metadata['distributed_access_pattern_score'][key]
        
        score = (WEIGHT_FREQUENCY * frequency +
                 WEIGHT_RECENCY * recency +
                 WEIGHT_SIZE * size +
                 WEIGHT_DISTRIBUTED_SCORE * distributed_score)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency is incremented, the last access timestamp is updated to the current time, and the distributed access pattern score is recalculated based on the latest access patterns across nodes.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['last_access_timestamp'][key] = cache_snapshot.access_count
    # Recalculate distributed access pattern score (placeholder logic)
    metadata['distributed_access_pattern_score'][key] = 1.0 / (1 + metadata['access_frequency'][key])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the access frequency is initialized to 1, the last access timestamp is set to the current time, the data size is recorded, and the distributed access pattern score is initialized based on initial access predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_timestamp'][key] = cache_snapshot.access_count
    metadata['data_size'][key] = obj.size
    # Initialize distributed access pattern score (placeholder logic)
    metadata['distributed_access_pattern_score'][key] = 1.0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy recalibrates the distributed access pattern scores of remaining objects to reflect the change in the cache landscape and potential shifts in access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Remove metadata for evicted object
    del metadata['access_frequency'][evicted_key]
    del metadata['last_access_timestamp'][evicted_key]
    del metadata['data_size'][evicted_key]
    del metadata['distributed_access_pattern_score'][evicted_key]
    
    # Recalibrate distributed access pattern scores (placeholder logic)
    for key in cache_snapshot.cache:
        metadata['distributed_access_pattern_score'][key] *= 0.9