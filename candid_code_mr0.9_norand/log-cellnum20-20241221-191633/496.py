# Import anything you need below
from collections import defaultdict, deque

# Put tunable constant parameters below
LATENCY_WEIGHT = 0.5  # Weight for latency in partition scoring
FREQUENCY_WEIGHT = 0.5  # Weight for frequency in partition scoring

# Put the metadata specifically maintained by the policy below. The policy maintains a deterministic index for each cache entry, partitions data into distinct groups based on access patterns, and tracks access frequency and latency for each partition to ensure equilibrium.
partitions = defaultdict(lambda: {
    'objects': deque(),  # Stores objects in the order of access
    'access_count': 0,  # Total access count for the partition
    'total_latency': 0,  # Total latency for the partition
    'average_latency': 0  # Average latency for the partition
})

object_to_partition = {}  # Maps object keys to their partition

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects an eviction victim by identifying the partition with the highest latency and least access frequency, then evicts the least recently used item within that partition to restore access equilibrium.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    # Calculate partition scores based on latency and frequency
    partition_scores = {}
    for partition_id, data in partitions.items():
        if data['access_count'] > 0:
            score = (LATENCY_WEIGHT * data['average_latency']) - (FREQUENCY_WEIGHT * data['access_count'])
            partition_scores[partition_id] = score

    # Find the partition with the highest score
    if partition_scores:
        victim_partition_id = max(partition_scores, key=partition_scores.get)
        victim_partition = partitions[victim_partition_id]

        # Evict the least recently used item in the victim partition
        if victim_partition['objects']:
            candid_obj_key = victim_partition['objects'].popleft()
            del object_to_partition[candid_obj_key]

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency and recalculates the average latency for the partition of the accessed item, ensuring the partition's equilibrium is maintained.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    partition_id = object_to_partition[obj.key]
    partition = partitions[partition_id]

    # Update access frequency
    partition['access_count'] += 1

    # Update latency
    current_time = cache_snapshot.access_count
    latency = current_time - partition['total_latency']
    partition['total_latency'] += latency
    partition['average_latency'] = partition['total_latency'] / partition['access_count']

    # Move the object to the end to mark it as recently used
    partition['objects'].remove(obj.key)
    partition['objects'].append(obj.key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns it to a partition based on its access pattern, updates the partition's access frequency, and recalculates the average latency to maintain equilibrium.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    # For simplicity, assign all objects to a single partition
    partition_id = 'default_partition'
    object_to_partition[obj.key] = partition_id
    partition = partitions[partition_id]

    # Add the object to the partition
    partition['objects'].append(obj.key)

    # Update access frequency
    partition['access_count'] += 1

    # Update latency
    current_time = cache_snapshot.access_count
    partition['total_latency'] += current_time
    partition['average_latency'] = partition['total_latency'] / partition['access_count']

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy updates the access frequency and recalculates the average latency for the affected partition, ensuring that the partition's equilibrium is adjusted accordingly.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    partition_id = object_to_partition.get(evicted_obj.key)
    if partition_id:
        partition = partitions[partition_id]

        # Update access frequency
        partition['access_count'] -= 1

        # Update latency
        current_time = cache_snapshot.access_count
        partition['total_latency'] -= current_time
        if partition['access_count'] > 0:
            partition['average_latency'] = partition['total_latency'] / partition['access_count']
        else:
            partition['average_latency'] = 0