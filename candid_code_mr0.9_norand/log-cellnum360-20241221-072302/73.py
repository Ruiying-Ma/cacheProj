# Import anything you need below
from collections import defaultdict
import time

# Put tunable constant parameters below
LOAD_DECREASE_FACTOR = 0.9
INITIAL_PRIORITY = 1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for dynamic sharding, resource pooling, load prediction, and priority inversion. Each cache entry is tagged with a shard identifier, a resource pool identifier, a predicted load score, and a priority level.
shard_load_predictions = defaultdict(float)
object_metadata = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects an eviction victim by first identifying the shard with the highest load prediction. Within that shard, it chooses the entry with the lowest priority level. If multiple entries have the same priority, it selects the one with the oldest access time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    # Identify the shard with the highest load prediction
    highest_load_shard = max(shard_load_predictions, key=shard_load_predictions.get)
    
    # Find the entry with the lowest priority level in the identified shard
    lowest_priority = float('inf')
    oldest_access_time = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        metadata = object_metadata.get(key, {})
        if metadata.get('shard') == highest_load_shard:
            priority = metadata.get('priority', INITIAL_PRIORITY)
            last_access_time = metadata.get('last_access_time', 0)
            
            if priority < lowest_priority or (priority == lowest_priority and last_access_time < oldest_access_time):
                lowest_priority = priority
                oldest_access_time = last_access_time
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the load prediction score for the shard by slightly decreasing it, reflecting reduced load. It also increases the priority level of the accessed entry to prevent priority inversion and updates its last access time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    metadata = object_metadata.get(obj.key, {})
    shard = metadata.get('shard')
    
    if shard is not None:
        # Decrease the load prediction score for the shard
        shard_load_predictions[shard] *= LOAD_DECREASE_FACTOR
    
    # Increase the priority level of the accessed entry
    metadata['priority'] = metadata.get('priority', INITIAL_PRIORITY) + 1
    
    # Update the last access time
    metadata['last_access_time'] = cache_snapshot.access_count
    
    object_metadata[obj.key] = metadata

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns it to a shard based on current load predictions, updates the resource pool metadata to reflect the new allocation, and initializes its priority level and last access time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    # Assign the object to the shard with the lowest load prediction
    assigned_shard = min(shard_load_predictions, key=shard_load_predictions.get, default=0)
    
    # Update the resource pool metadata
    shard_load_predictions[assigned_shard] += obj.size
    
    # Initialize priority level and last access time
    object_metadata[obj.key] = {
        'shard': assigned_shard,
        'priority': INITIAL_PRIORITY,
        'last_access_time': cache_snapshot.access_count
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the policy recalculates the load prediction for the affected shard, adjusts the resource pool metadata to reflect the freed resources, and logs the priority level of the evicted entry to refine future priority inversion handling.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    metadata = object_metadata.pop(evicted_obj.key, {})
    shard = metadata.get('shard')
    
    if shard is not None:
        # Recalculate the load prediction for the affected shard
        shard_load_predictions[shard] -= evicted_obj.size
    
    # Log the priority level of the evicted entry
    # (This could be used for further analysis or adjustments in a real system)
    evicted_priority = metadata.get('priority', INITIAL_PRIORITY)
    # Log or store evicted_priority as needed