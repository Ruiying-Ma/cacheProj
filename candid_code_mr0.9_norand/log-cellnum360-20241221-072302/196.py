# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_PRIORITY_SCORE = 1
PRIORITY_INCREMENT = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a temporal partitioning index, a predictive priority score for each cache entry, a load vectorization map indicating access patterns, and a dynamic buffer size for each partition.
temporal_partitioning_index = {}
predictive_priority_score = defaultdict(lambda: INITIAL_PRIORITY_SCORE)
load_vectorization_map = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest predictive priority score within the least recently used temporal partition, while considering the current load vectorization map to minimize disruption to access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    # Find the least recently used temporal partition
    min_time = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        if temporal_partitioning_index[key] < min_time:
            min_time = temporal_partitioning_index[key]
    
    # Find the object with the lowest predictive priority score in the least recently used partition
    min_priority_score = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        if temporal_partitioning_index[key] == min_time:
            if predictive_priority_score[key] < min_priority_score:
                min_priority_score = predictive_priority_score[key]
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the temporal partitioning index is updated to reflect the current time, the predictive priority score is increased based on recent access patterns, and the load vectorization map is adjusted to reflect the current access frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    # Update temporal partitioning index
    temporal_partitioning_index[obj.key] = cache_snapshot.access_count
    
    # Increase predictive priority score
    predictive_priority_score[obj.key] += PRIORITY_INCREMENT
    
    # Update load vectorization map
    load_vectorization_map[obj.key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the temporal partitioning index is updated to include the new entry, the predictive priority score is initialized based on historical data, and the load vectorization map is updated to account for the new entry's potential impact on access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    # Update temporal partitioning index
    temporal_partitioning_index[obj.key] = cache_snapshot.access_count
    
    # Initialize predictive priority score
    predictive_priority_score[obj.key] = INITIAL_PRIORITY_SCORE
    
    # Update load vectorization map
    load_vectorization_map[obj.key] = 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the temporal partitioning index is adjusted to remove the evicted entry, the predictive priority scores of remaining entries are recalibrated, and the load vectorization map is updated to reflect the change in cache composition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    # Remove evicted entry from temporal partitioning index
    if evicted_obj.key in temporal_partitioning_index:
        del temporal_partitioning_index[evicted_obj.key]
    
    # Recalibrate predictive priority scores
    for key in predictive_priority_score:
        predictive_priority_score[key] = max(INITIAL_PRIORITY_SCORE, predictive_priority_score[key] - 1)
    
    # Update load vectorization map
    if evicted_obj.key in load_vectorization_map:
        del load_vectorization_map[evicted_obj.key]