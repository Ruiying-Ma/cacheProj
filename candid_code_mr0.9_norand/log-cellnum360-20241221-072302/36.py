# Import anything you need below
from collections import defaultdict, deque

# Put tunable constant parameters below
DEFAULT_PRIORITY_LEVEL = 1
EVENT_BUFFER_SIZE = 5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry, including load distribution metrics, priority levels, event buffer timestamps, and synchronized execution flags. Load distribution metrics track the frequency and recency of access, priority levels indicate the importance of the data, event buffer timestamps record the last few access times, and synchronized execution flags ensure coordinated updates across distributed systems.
cache_metadata = {
    'load_distribution': defaultdict(lambda: {'frequency': 0, 'recency': 0}),
    'priority_levels': defaultdict(lambda: DEFAULT_PRIORITY_LEVEL),
    'event_buffer': defaultdict(lambda: deque(maxlen=EVENT_BUFFER_SIZE)),
    'sync_flags': defaultdict(lambda: False)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first identifying entries with the lowest priority levels. Among these, it selects the entry with the least recent event buffer timestamp. If there is a tie, it considers the load distribution metrics to evict the entry with the least access frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_priority = min(cache_metadata['priority_levels'][key] for key in cache_snapshot.cache)
    candidates = [key for key in cache_snapshot.cache if cache_metadata['priority_levels'][key] == min_priority]
    
    if candidates:
        # Sort by least recent event buffer timestamp
        candidates.sort(key=lambda key: (cache_metadata['event_buffer'][key][0] if cache_metadata['event_buffer'][key] else float('inf')))
        # If there's a tie, sort by least access frequency
        candidates.sort(key=lambda key: cache_metadata['load_distribution'][key]['frequency'])
        candid_obj_key = candidates[0]
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the event buffer timestamps to include the current access time, increases the priority level of the accessed entry, and adjusts the load distribution metrics to reflect the increased frequency of access. The synchronized execution flag is checked to ensure consistent updates across distributed systems.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Update event buffer timestamps
    cache_metadata['event_buffer'][key].append(current_time)
    
    # Increase priority level
    cache_metadata['priority_levels'][key] += 1
    
    # Adjust load distribution metrics
    cache_metadata['load_distribution'][key]['frequency'] += 1
    cache_metadata['load_distribution'][key]['recency'] = current_time
    
    # Ensure synchronized execution flag
    cache_metadata['sync_flags'][key] = True

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the load distribution metrics and event buffer timestamps for the new entry. It sets a default priority level based on the object's initial importance and ensures the synchronized execution flag is set to coordinate with other systems.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Initialize load distribution metrics
    cache_metadata['load_distribution'][key] = {'frequency': 1, 'recency': current_time}
    
    # Initialize event buffer timestamps
    cache_metadata['event_buffer'][key].append(current_time)
    
    # Set default priority level
    cache_metadata['priority_levels'][key] = DEFAULT_PRIORITY_LEVEL
    
    # Ensure synchronized execution flag
    cache_metadata['sync_flags'][key] = True

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the load distribution metrics to account for the removed entry, adjusts priority levels of remaining entries if necessary, and clears the event buffer timestamps of the evicted entry. The synchronized execution flag is used to propagate these changes across distributed systems.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    
    # Clear metadata for evicted entry
    del cache_metadata['load_distribution'][evicted_key]
    del cache_metadata['priority_levels'][evicted_key]
    del cache_metadata['event_buffer'][evicted_key]
    del cache_metadata['sync_flags'][evicted_key]
    
    # Recalibrate load distribution metrics and adjust priority levels if necessary
    # This is a placeholder for any recalibration logic needed
    # Ensure synchronized execution flag for remaining entries
    for key in cache_snapshot.cache:
        cache_metadata['sync_flags'][key] = True