# Import anything you need below
from collections import defaultdict, deque

# Put tunable constant parameters below
INITIAL_PRIORITY = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a priority access queue that orders cache entries based on access frequency and recency, a real-time index that maps cache entries to their priority levels, and an event synchronization log that records access patterns and load conditions.
priority_queue = deque()  # A deque to maintain the order of cache entries based on priority
priority_index = {}  # A dictionary to map cache entries to their priority levels
event_log = []  # A list to record access patterns and load conditions

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest priority in the priority access queue, considering both its access frequency and recency, while also factoring in current load conditions from the event synchronization log.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    if priority_queue:
        # Find the object with the lowest priority
        candid_obj_key = priority_queue.popleft()
        del priority_index[candid_obj_key]
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the priority access queue by moving the accessed entry to a higher priority position, updates the real-time index to reflect the new priority level, and logs the access event in the event synchronization log.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    if obj.key in priority_index:
        # Remove the object from its current position
        priority_queue.remove(obj.key)
        # Increase its priority
        priority_index[obj.key] += 1
        # Reinsert it at the end to reflect higher priority
        priority_queue.append(obj.key)
    # Log the access event
    event_log.append((cache_snapshot.access_count, 'hit', obj.key))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy adds the entry to the priority access queue with an initial priority based on current load conditions, updates the real-time index with this initial priority, and records the insertion event in the event synchronization log.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    # Add the object to the priority queue with initial priority
    priority_queue.append(obj.key)
    priority_index[obj.key] = INITIAL_PRIORITY
    # Log the insertion event
    event_log.append((cache_snapshot.access_count, 'insert', obj.key))

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the evicted entry from the priority access queue, deletes its mapping from the real-time index, and logs the eviction event in the event synchronization log to adjust future load prioritization strategies.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in priority_index:
        # Remove the evicted object from the priority queue
        priority_queue.remove(evicted_obj.key)
        # Delete its mapping from the real-time index
        del priority_index[evicted_obj.key]
    # Log the eviction event
    event_log.append((cache_snapshot.access_count, 'evict', evicted_obj.key))