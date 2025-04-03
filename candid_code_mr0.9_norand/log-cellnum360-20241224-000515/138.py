# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
DEFAULT_PRIORITY = 1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry including priority level, last context switch timestamp, execution cycle count, and task allocation identifier. Priority level indicates the importance of the entry, context switch timestamp tracks the last time the entry was accessed, execution cycle count records how many cycles the entry has been in the cache, and task allocation identifier links the entry to a specific task or process.
metadata = defaultdict(lambda: {
    'priority_level': DEFAULT_PRIORITY,
    'last_context_switch': 0,
    'execution_cycle_count': 0,
    'task_allocation_id': None
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first considering entries with the lowest priority level. Among these, it selects the entry with the oldest context switch timestamp. If there is a tie, the entry with the highest execution cycle count is chosen. This ensures that less important and less recently used entries are evicted first, while also considering how long entries have been in the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_priority = float('inf')
    oldest_timestamp = float('inf')
    max_execution_cycle = -1

    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        if (meta['priority_level'] < min_priority or
            (meta['priority_level'] == min_priority and meta['last_context_switch'] < oldest_timestamp) or
            (meta['priority_level'] == min_priority and meta['last_context_switch'] == oldest_timestamp and meta['execution_cycle_count'] > max_execution_cycle)):
            min_priority = meta['priority_level']
            oldest_timestamp = meta['last_context_switch']
            max_execution_cycle = meta['execution_cycle_count']
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the context switch timestamp to the current time to reflect recent access. The execution cycle count is incremented to indicate another cycle of usage. The priority level and task allocation identifier remain unchanged as they are static attributes.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['last_context_switch'] = cache_snapshot.access_count
    meta['execution_cycle_count'] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the context switch timestamp to the current time, sets the execution cycle count to zero, assigns a default priority level based on the task allocation identifier, and links the entry to the relevant task or process using the task allocation identifier.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['last_context_switch'] = cache_snapshot.access_count
    meta['execution_cycle_count'] = 0
    meta['priority_level'] = DEFAULT_PRIORITY  # Assuming task allocation identifier is not provided
    meta['task_allocation_id'] = obj.key  # Assuming task allocation identifier is obj.key

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy does not need to update any metadata for the evicted entry itself. However, it may adjust the priority levels of remaining entries if the evicted entry was part of a task with dynamic priority adjustments, ensuring the cache reflects the current task priorities.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Assuming no dynamic priority adjustments are needed in this implementation
    pass