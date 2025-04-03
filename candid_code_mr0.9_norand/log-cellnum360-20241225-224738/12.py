# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
MEMORY_ALLOCATION_PRIORITY = {
    'default': 1  # Default priority for all objects
}

# Put the metadata specifically maintained by the policy below. The policy maintains a hierarchical structure of metadata including access frequency, recency, and memory allocation priority. It also tracks cache coherency states to ensure consistency across cache levels.
metadata = {
    'access_frequency': defaultdict(int),
    'recency': {},
    'memory_priority': {},
    'coherency_state': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache line with the lowest combined score of access frequency and recency, while also considering memory allocation priority and ensuring cache coherency is maintained.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        frequency = metadata['access_frequency'][key]
        recency = metadata['recency'][key]
        priority = metadata['memory_priority'].get(key, MEMORY_ALLOCATION_PRIORITY['default'])
        score = frequency + recency - priority
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the access frequency and updates the recency metadata for the accessed cache line, while also checking and updating the cache coherency state if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    metadata['access_frequency'][obj.key] += 1
    metadata['recency'][obj.key] = cache_snapshot.access_count
    # Check and update cache coherency state if necessary
    metadata['coherency_state'][obj.key] = 'consistent'

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency and recency metadata, assigns a memory allocation priority based on the object's type, and sets the initial cache coherency state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    metadata['access_frequency'][obj.key] = 1
    metadata['recency'][obj.key] = cache_snapshot.access_count
    metadata['memory_priority'][obj.key] = MEMORY_ALLOCATION_PRIORITY.get('default', 1)
    metadata['coherency_state'][obj.key] = 'consistent'

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the policy adjusts the hierarchical structure to reflect the removal, recalibrates memory allocation priorities if needed, and ensures that cache coherency states are updated to prevent stale data across cache levels.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    # Remove metadata for the evicted object
    if evicted_obj.key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_obj.key]
    if evicted_obj.key in metadata['recency']:
        del metadata['recency'][evicted_obj.key]
    if evicted_obj.key in metadata['memory_priority']:
        del metadata['memory_priority'][evicted_obj.key]
    if evicted_obj.key in metadata['coherency_state']:
        del metadata['coherency_state'][evicted_obj.key]
    
    # Recalibrate memory allocation priorities if needed
    # (In this simple implementation, we assume priorities are static)
    
    # Ensure cache coherency states are updated
    for key in metadata['coherency_state']:
        metadata['coherency_state'][key] = 'consistent'