# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
DEFAULT_PRIORITY_LEVEL = 1
BANDWIDTH_ESTIMATION_FACTOR = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry including access frequency, last access timestamp, priority level, and estimated bandwidth usage. Additionally, it tracks overall cache load and peak load periods.
metadata = {
    'access_frequency': defaultdict(int),
    'last_access_timestamp': {},
    'priority_level': defaultdict(lambda: DEFAULT_PRIORITY_LEVEL),
    'estimated_bandwidth_usage': defaultdict(lambda: BANDWIDTH_ESTIMATION_FACTOR),
    'overall_cache_load': 0,
    'peak_load_periods': []
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first identifying entries with the lowest priority level. Among these, it selects the entry with the lowest access frequency and highest estimated bandwidth usage, especially during peak load periods.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_priority = float('inf')
    min_frequency = float('inf')
    max_bandwidth_usage = float('-inf')

    for key, cached_obj in cache_snapshot.cache.items():
        priority = metadata['priority_level'][key]
        frequency = metadata['access_frequency'][key]
        bandwidth_usage = metadata['estimated_bandwidth_usage'][key]

        if priority < min_priority:
            min_priority = priority
            min_frequency = frequency
            max_bandwidth_usage = bandwidth_usage
            candid_obj_key = key
        elif priority == min_priority:
            if frequency < min_frequency:
                min_frequency = frequency
                max_bandwidth_usage = bandwidth_usage
                candid_obj_key = key
            elif frequency == min_frequency and bandwidth_usage > max_bandwidth_usage:
                max_bandwidth_usage = bandwidth_usage
                candid_obj_key = key

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the access frequency and updates the last access timestamp for the accessed entry. It also adjusts the priority level based on recent access patterns and recalculates the estimated bandwidth usage.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['last_access_timestamp'][key] = cache_snapshot.access_count
    # Adjust priority level based on access patterns
    metadata['priority_level'][key] = min(metadata['priority_level'][key] + 1, 10)
    # Recalculate estimated bandwidth usage
    metadata['estimated_bandwidth_usage'][key] *= 0.9

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency to zero, sets the last access timestamp to the current time, assigns a default priority level, and estimates its bandwidth usage based on initial access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 0
    metadata['last_access_timestamp'][key] = cache_snapshot.access_count
    metadata['priority_level'][key] = DEFAULT_PRIORITY_LEVEL
    metadata['estimated_bandwidth_usage'][key] = BANDWIDTH_ESTIMATION_FACTOR

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the overall cache load and peak load metrics. It also adjusts the priority levels of remaining entries to prevent priority inversion and optimizes bandwidth allocation for future accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Recalibrate overall cache load
    metadata['overall_cache_load'] = cache_snapshot.size

    # Adjust priority levels to prevent priority inversion
    for key in cache_snapshot.cache:
        metadata['priority_level'][key] = max(metadata['priority_level'][key] - 1, 1)

    # Optimize bandwidth allocation
    for key in cache_snapshot.cache:
        metadata['estimated_bandwidth_usage'][key] *= 1.1