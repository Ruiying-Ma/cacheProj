# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
RESOURCE_ALLOCATION_BOOST = 10
INITIAL_RESOURCE_ALLOCATION = 5

# Put the metadata specifically maintained by the policy below. The policy maintains a sequential iteration index, a task synchronization counter, a resource allocation score, and an event queue timestamp for each cache entry.
metadata = {
    'sequential_index': defaultdict(int),
    'task_sync_counter': defaultdict(int),
    'resource_allocation_score': defaultdict(int),
    'event_queue_timestamp': defaultdict(int)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest resource allocation score, breaking ties by the oldest event queue timestamp.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    oldest_timestamp = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = metadata['resource_allocation_score'][key]
        timestamp = metadata['event_queue_timestamp'][key]
        
        if score < min_score or (score == min_score and timestamp < oldest_timestamp):
            min_score = score
            oldest_timestamp = timestamp
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the sequential iteration index is incremented, the task synchronization counter is increased to reflect the access, the resource allocation score is boosted, and the event queue timestamp is updated to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['sequential_index'][key] += 1
    metadata['task_sync_counter'][key] += 1
    metadata['resource_allocation_score'][key] += RESOURCE_ALLOCATION_BOOST
    metadata['event_queue_timestamp'][key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the sequential iteration index is set to the next available position, the task synchronization counter is initialized, the resource allocation score is set based on initial access patterns, and the event queue timestamp is set to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['sequential_index'][key] = len(cache_snapshot.cache)
    metadata['task_sync_counter'][key] = 0
    metadata['resource_allocation_score'][key] = INITIAL_RESOURCE_ALLOCATION
    metadata['event_queue_timestamp'][key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the sequential iteration index is adjusted to maintain continuity, the task synchronization counter is reset, the resource allocation score is recalibrated, and the event queue timestamp is cleared for the evicted entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    del metadata['sequential_index'][evicted_key]
    del metadata['task_sync_counter'][evicted_key]
    del metadata['resource_allocation_score'][evicted_key]
    del metadata['event_queue_timestamp'][evicted_key]