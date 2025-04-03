# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
DEFAULT_PRIORITY = 1
CONSISTENCY_VERIFIED = True

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, priority level, and consistency status for each cache entry. It also tracks the load distribution across distributed cache nodes to ensure balanced utilization.
metadata = {
    'access_frequency': defaultdict(int),
    'last_access_time': {},
    'priority_level': defaultdict(lambda: DEFAULT_PRIORITY),
    'consistency_status': defaultdict(lambda: CONSISTENCY_VERIFIED),
    'load_distribution': defaultdict(int)  # Assuming a single node for simplicity
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim based on a weighted score that combines low access frequency, older last access time, lower priority level, and consistency status. It also considers the load on each cache node, preferring to evict from nodes with higher load to maintain balance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        frequency = metadata['access_frequency'][key]
        last_access = metadata['last_access_time'][key]
        priority = metadata['priority_level'][key]
        consistency = metadata['consistency_status'][key]
        
        # Calculate a weighted score for eviction
        score = (1 / (frequency + 1)) + last_access + (1 / (priority + 1)) + (0 if consistency else 1)
        
        # Consider load distribution (assuming single node for simplicity)
        load = metadata['load_distribution'][key]
        score += load
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the access frequency, updates the last access time to the current time, and verifies the consistency status of the cache entry. It also adjusts the priority level based on the frequency of access and the importance of the data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['consistency_status'][key] = CONSISTENCY_VERIFIED
    metadata['priority_level'][key] = min(metadata['priority_level'][key] + 1, 10)  # Example priority adjustment

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to one, sets the last access time to the current time, assigns a default priority level, and marks the consistency status as verified. It also updates the load distribution metadata to reflect the new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['priority_level'][key] = DEFAULT_PRIORITY
    metadata['consistency_status'][key] = CONSISTENCY_VERIFIED
    metadata['load_distribution'][key] += obj.size

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalculates the load distribution across cache nodes to ensure balance. It also logs the eviction event to adjust future priority levels and consistency checks for similar data patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['load_distribution']:
        metadata['load_distribution'][evicted_key] -= evicted_obj.size
        if metadata['load_distribution'][evicted_key] <= 0:
            del metadata['load_distribution'][evicted_key]
    
    # Log eviction event (for simplicity, just print)
    print(f"Evicted object with key: {evicted_key}")