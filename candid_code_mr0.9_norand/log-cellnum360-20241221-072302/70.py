# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
HIGH_LOAD_THRESHOLD = 0.8  # Threshold to determine high load conditions

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry including priority level, last access timestamp, access frequency, and reserved bandwidth. It also tracks global metrics like current load and average access delay.
metadata = {
    'priority_level': defaultdict(int),
    'last_access_timestamp': defaultdict(int),
    'access_frequency': defaultdict(int),
    'reserved_bandwidth': defaultdict(int),
    'current_load': 0,
    'average_access_delay': 0
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects a victim by first identifying entries with the lowest priority level. Among these, it chooses the entry with the lowest access frequency. If there's a tie, it evicts the entry with the oldest last access timestamp.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_priority = min(metadata['priority_level'][key] for key in cache_snapshot.cache)
    candidates = [key for key in cache_snapshot.cache if metadata['priority_level'][key] == min_priority]
    
    if candidates:
        min_frequency = min(metadata['access_frequency'][key] for key in candidates)
        candidates = [key for key in candidates if metadata['access_frequency'][key] == min_frequency]
        
        if candidates:
            oldest_timestamp = min(metadata['last_access_timestamp'][key] for key in candidates)
            candid_obj_key = next(key for key in candidates if metadata['last_access_timestamp'][key] == oldest_timestamp)
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the access frequency and updates the last access timestamp of the entry. It also checks if the current load is high and adjusts the priority level to prevent priority inversion.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    metadata['access_frequency'][obj.key] += 1
    metadata['last_access_timestamp'][obj.key] = cache_snapshot.access_count
    
    current_load = cache_snapshot.size / cache_snapshot.capacity
    if current_load > HIGH_LOAD_THRESHOLD:
        metadata['priority_level'][obj.key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its priority level based on current load conditions, sets the access frequency to one, and records the current timestamp. It also reserves bandwidth for the entry if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    current_load = cache_snapshot.size / cache_snapshot.capacity
    metadata['priority_level'][obj.key] = 1 if current_load > HIGH_LOAD_THRESHOLD else 0
    metadata['access_frequency'][obj.key] = 1
    metadata['last_access_timestamp'][obj.key] = cache_snapshot.access_count
    metadata['reserved_bandwidth'][obj.key] = obj.size  # Example reservation logic

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the policy recalculates the average access delay and adjusts global load metrics. It also releases any reserved bandwidth associated with the evicted entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    # Recalculate average access delay
    total_accesses = cache_snapshot.hit_count + cache_snapshot.miss_count
    if total_accesses > 0:
        metadata['average_access_delay'] = cache_snapshot.miss_count / total_accesses
    
    # Adjust global load metrics
    metadata['current_load'] = cache_snapshot.size / cache_snapshot.capacity
    
    # Release reserved bandwidth
    if evicted_obj.key in metadata['reserved_bandwidth']:
        del metadata['reserved_bandwidth'][evicted_obj.key]
    
    # Clean up metadata for evicted object
    del metadata['priority_level'][evicted_obj.key]
    del metadata['last_access_timestamp'][evicted_obj.key]
    del metadata['access_frequency'][evicted_obj.key]