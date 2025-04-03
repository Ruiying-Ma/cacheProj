# Import anything you need below
from collections import deque, defaultdict
import time

# Put tunable constant parameters below
AGE_THRESHOLD = 5  # Example threshold for promoting an object to a higher-level queue

# Put the metadata specifically maintained by the policy below. The policy maintains a hierarchical queue structure with multiple levels, each representing different aging stages. Each cache entry is associated with a timestamp indicating its last access time and a batch identifier to group entries accessed within a similar timeframe.
hierarchical_queues = defaultdict(deque)  # Dictionary of deques for each level
batch_timestamps = defaultdict(dict)  # Dictionary to store timestamps for each batch
object_metadata = {}  # Dictionary to store metadata for each object

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by first identifying the oldest batch in the lowest hierarchy queue. Within this batch, the entry with the oldest timestamp is chosen for eviction, ensuring that both aging and cache locality are considered.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    for level in sorted(hierarchical_queues.keys()):
        if hierarchical_queues[level]:
            oldest_batch = hierarchical_queues[level][0]
            oldest_obj_key = min(batch_timestamps[oldest_batch], key=batch_timestamps[oldest_batch].get)
            candid_obj_key = oldest_obj_key
            break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the entry's timestamp is updated to the current time, and it is moved to a higher-level queue if it surpasses a predefined age threshold, promoting it to a fresher batch.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    current_time = cache_snapshot.access_count
    obj_key = obj.key
    obj_metadata = object_metadata[obj_key]
    obj_metadata['timestamp'] = current_time
    
    # Check if the object should be promoted
    if current_time - obj_metadata['batch_time'] > AGE_THRESHOLD:
        current_level = obj_metadata['level']
        new_level = current_level + 1
        hierarchical_queues[current_level].remove(obj_metadata['batch'])
        hierarchical_queues[new_level].append(obj_metadata['batch'])
        obj_metadata['level'] = new_level
        obj_metadata['batch_time'] = current_time

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the entry is placed in the lowest-level queue with the current timestamp and a new batch identifier. This ensures that new entries start at the base level and age naturally through the hierarchy.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    current_time = cache_snapshot.access_count
    obj_key = obj.key
    batch_id = f"batch_{current_time}_{obj_key}"
    
    # Initialize metadata for the new object
    object_metadata[obj_key] = {
        'timestamp': current_time,
        'batch': batch_id,
        'level': 0,
        'batch_time': current_time
    }
    
    # Add to the lowest-level queue
    hierarchical_queues[0].append(batch_id)
    batch_timestamps[batch_id][obj_key] = current_time

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy checks if the batch from which the entry was evicted is empty. If so, it removes the batch from the queue, maintaining efficient batch management and freeing up space for new entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_obj_key = evicted_obj.key
    evicted_metadata = object_metadata.pop(evicted_obj_key, None)
    
    if evicted_metadata:
        batch_id = evicted_metadata['batch']
        level = evicted_metadata['level']
        
        # Remove the evicted object from the batch timestamps
        if batch_id in batch_timestamps:
            del batch_timestamps[batch_id][evicted_obj_key]
            if not batch_timestamps[batch_id]:
                # If the batch is empty, remove it
                hierarchical_queues[level].remove(batch_id)
                del batch_timestamps[batch_id]