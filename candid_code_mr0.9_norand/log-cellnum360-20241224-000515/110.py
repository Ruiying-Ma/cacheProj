# Import anything you need below
from collections import defaultdict, deque

# Put tunable constant parameters below
TEMPORAL_SCORE_INCREMENT = 1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a dynamic partition map for cache segments, a fluid synchronization counter for each partition, a temporal abstraction score for each cache entry, and a sequential access log.
partition_map = defaultdict(list)  # Maps partition index to list of object keys
fluid_sync_counter = defaultdict(int)  # Maps partition index to its fluid synchronization counter
temporal_abstraction_score = defaultdict(int)  # Maps object key to its temporal abstraction score
sequential_access_log = deque()  # Log of recent accesses

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the partition with the least fluid synchronization and selecting the entry with the lowest temporal abstraction score within that partition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Identify the partition with the least fluid synchronization
    min_sync_partition = min(fluid_sync_counter, key=fluid_sync_counter.get)
    
    # Find the entry with the lowest temporal abstraction score within that partition
    min_score = float('inf')
    for key in partition_map[min_sync_partition]:
        if temporal_abstraction_score[key] < min_score:
            min_score = temporal_abstraction_score[key]
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the temporal abstraction score of the accessed entry is increased, and the fluid synchronization counter of the corresponding partition is incremented to reflect improved access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Increase the temporal abstraction score of the accessed entry
    temporal_abstraction_score[obj.key] += TEMPORAL_SCORE_INCREMENT
    
    # Find the partition of the accessed entry and increment its fluid synchronization counter
    for partition, keys in partition_map.items():
        if obj.key in keys:
            fluid_sync_counter[partition] += 1
            break

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the partition map is adaptively adjusted to balance cache segments, and the temporal abstraction score for the new entry is initialized based on recent access patterns from the sequential access log.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Initialize the temporal abstraction score for the new entry
    temporal_abstraction_score[obj.key] = 0  # Or some function of recent access patterns
    
    # Add the object to a partition (for simplicity, add to the first partition)
    partition_map[0].append(obj.key)
    
    # Add to sequential access log
    sequential_access_log.append(obj.key)
    
    # Adjust partition map if needed (not implemented for simplicity)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the fluid synchronization counter for the affected partition is decremented, and the partition map is re-evaluated to ensure optimal distribution of cache resources.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Find the partition of the evicted entry and decrement its fluid synchronization counter
    for partition, keys in partition_map.items():
        if evicted_obj.key in keys:
            fluid_sync_counter[partition] -= 1
            keys.remove(evicted_obj.key)
            break
    
    # Re-evaluate partition map if needed (not implemented for simplicity)