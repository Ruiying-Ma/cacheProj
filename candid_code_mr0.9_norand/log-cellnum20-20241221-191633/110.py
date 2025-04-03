# Import anything you need below
from collections import defaultdict, deque

# Put tunable constant parameters below
PARTITION_COUNT = 4  # Number of partitions
LOAD_FACTOR = 0.75   # Load factor for partition assignment

# Put the metadata specifically maintained by the policy below. The policy maintains a dynamic index table that maps cache blocks to partitions based on access frequency and load. Each partition has a priority score calculated from recent access patterns and load metrics. Additionally, a parallel processing queue tracks pending cache operations to optimize load distribution.
index_table = {}  # Maps object keys to partitions
partition_priority = [0] * PARTITION_COUNT  # Priority scores for each partition
partition_access_frequency = [defaultdict(int) for _ in range(PARTITION_COUNT)]  # Access frequency for each partition
partition_lru = [deque() for _ in range(PARTITION_COUNT)]  # LRU queue for each partition
parallel_processing_queue = defaultdict(deque)  # Tracks pending operations

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the partition with the lowest priority score and choosing the least recently used block within that partition. This approach balances between frequency and recency while considering current load conditions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    # Find the partition with the lowest priority score
    min_priority_partition = min(range(PARTITION_COUNT), key=lambda i: partition_priority[i])
    
    # Choose the least recently used block within that partition
    if partition_lru[min_priority_partition]:
        candid_obj_key = partition_lru[min_priority_partition].popleft()
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the access frequency for the corresponding block and updates the partition's priority score. The parallel processing queue is checked to adjust any pending operations related to the accessed block.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    partition = index_table[obj.key]
    partition_access_frequency[partition][obj.key] += 1
    partition_priority[partition] += 1  # Update priority score based on access frequency
    
    # Move the accessed block to the end of the LRU queue
    if obj.key in partition_lru[partition]:
        partition_lru[partition].remove(obj.key)
    partition_lru[partition].append(obj.key)
    
    # Adjust pending operations in the parallel processing queue
    if obj.key in parallel_processing_queue:
        parallel_processing_queue[obj.key].clear()

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns it to a partition based on current load and access frequency predictions. The index table is updated, and the partition's priority score is recalculated to reflect the new load distribution.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    # Assign to a partition based on load and access frequency
    partition = min(range(PARTITION_COUNT), key=lambda i: len(partition_lru[i]) + partition_access_frequency[i][obj.key] * LOAD_FACTOR)
    
    # Update index table and partition metadata
    index_table[obj.key] = partition
    partition_access_frequency[partition][obj.key] = 1
    partition_lru[partition].append(obj.key)
    partition_priority[partition] += 1  # Recalculate priority score

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy decreases the priority score of the affected partition and updates the index table to remove the evicted block. The parallel processing queue is adjusted to remove any pending operations for the evicted block.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    partition = index_table.pop(evicted_obj.key, None)
    if partition is not None:
        partition_priority[partition] -= 1  # Decrease priority score
        partition_access_frequency[partition].pop(evicted_obj.key, None)
        if evicted_obj.key in partition_lru[partition]:
            partition_lru[partition].remove(evicted_obj.key)
    
    # Remove any pending operations for the evicted block
    if evicted_obj.key in parallel_processing_queue:
        parallel_processing_queue.pop(evicted_obj.key, None)