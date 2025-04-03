# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
DEFAULT_PRIORITY_LEVEL = 1
LATENCY_IMPACT_FACTOR = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry, including access frequency, last access time, priority level, and estimated latency impact. It also tracks overall cache usage and memory allocation efficiency.
metadata = {
    'access_frequency': defaultdict(int),
    'last_access_time': {},
    'priority_level': defaultdict(lambda: DEFAULT_PRIORITY_LEVEL),
    'estimated_latency_impact': {},
    'overall_cache_usage': 0,
    'memory_allocation_efficiency': 0
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by prioritizing entries with the lowest priority level and highest estimated latency impact. It dynamically adjusts based on current cache usage and memory allocation efficiency, ensuring minimal performance degradation.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_priority = float('inf')
    max_latency_impact = -float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        priority = metadata['priority_level'][key]
        latency_impact = metadata['estimated_latency_impact'][key]
        
        if (priority < min_priority) or (priority == min_priority and latency_impact > max_latency_impact):
            min_priority = priority
            max_latency_impact = latency_impact
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the access frequency, updates the last access time, and recalculates the priority level and estimated latency impact for the accessed entry, ensuring it reflects current usage patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['priority_level'][key] = metadata['access_frequency'][key] / (cache_snapshot.access_count - metadata['last_access_time'][key] + 1)
    metadata['estimated_latency_impact'][key] = obj.size * LATENCY_IMPACT_FACTOR

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its metadata with a default priority level, access frequency of one, current time as the last access time, and an estimated latency impact based on initial memory allocation.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['priority_level'][key] = DEFAULT_PRIORITY_LEVEL
    metadata['estimated_latency_impact'][key] = obj.size * LATENCY_IMPACT_FACTOR

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates overall cache usage and memory allocation efficiency metrics, potentially adjusting the priority levels of remaining entries to optimize future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    metadata['overall_cache_usage'] = cache_snapshot.size
    metadata['memory_allocation_efficiency'] = cache_snapshot.size / cache_snapshot.capacity
    
    # Adjust priority levels based on new cache state
    for key in cache_snapshot.cache:
        metadata['priority_level'][key] = metadata['access_frequency'][key] / (cache_snapshot.access_count - metadata['last_access_time'][key] + 1)