# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
DEFAULT_PRIORITY = 1
DEFAULT_TREND = 0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, priority level, and predicted future access trend for each cache entry. It also tracks overall cache workload distribution to dynamically adjust priorities.
metadata = {
    'access_frequency': defaultdict(int),
    'last_access_time': {},
    'priority_level': defaultdict(lambda: DEFAULT_PRIORITY),
    'predicted_trend': defaultdict(lambda: DEFAULT_TREND),
    'workload_distribution': defaultdict(int)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by considering entries with the lowest priority level and least predicted future access trend, while also balancing the workload distribution across different priority levels to ensure resource efficiency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_priority = float('inf')
    min_trend = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        priority = metadata['priority_level'][key]
        trend = metadata['predicted_trend'][key]
        
        if (priority < min_priority) or (priority == min_priority and trend < min_trend):
            min_priority = priority
            min_trend = trend
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency and last access time for the entry are updated. The priority level may be adjusted based on the current workload distribution and predictive trend analysis to optimize resource allocation.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['last_access_time'][key] = cache_snapshot.access_count

    # Adjust priority level based on workload distribution and trend
    current_priority = metadata['priority_level'][key]
    current_trend = metadata['predicted_trend'][key]
    # Example adjustment logic (can be more complex based on actual trend analysis)
    if current_trend > 0:
        metadata['priority_level'][key] = min(current_priority + 1, 10)  # Cap priority level
    else:
        metadata['priority_level'][key] = max(current_priority - 1, 1)  # Minimum priority level

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its metadata with a default priority level and predicted trend. It then recalibrates the workload distribution and adjusts the priority levels of existing entries if necessary to maintain resource efficiency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['priority_level'][key] = DEFAULT_PRIORITY
    metadata['predicted_trend'][key] = DEFAULT_TREND

    # Recalibrate workload distribution
    for key in cache_snapshot.cache:
        priority = metadata['priority_level'][key]
        metadata['workload_distribution'][priority] += 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy updates the workload distribution and recalibrates the priority levels of remaining entries to ensure balanced resource allocation and optimize future cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    priority = metadata['priority_level'].pop(evicted_key, None)
    if priority is not None:
        metadata['workload_distribution'][priority] -= 1

    # Recalibrate priority levels
    for key in cache_snapshot.cache:
        current_priority = metadata['priority_level'][key]
        # Example recalibration logic
        if metadata['workload_distribution'][current_priority] < 1:
            metadata['priority_level'][key] = max(current_priority - 1, 1)
        elif metadata['workload_distribution'][current_priority] > 5:
            metadata['priority_level'][key] = min(current_priority + 1, 10)