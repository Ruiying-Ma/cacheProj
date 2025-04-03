# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
DEFAULT_PRIORITY = 1
DEFAULT_LATENCY = 10
DEFAULT_REPLICATION_FACTOR = 1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry, including priority level, access latency, replication factor, and load distribution metrics. Priority levels are assigned based on the importance of the data, latency tracks the time taken for access, replication factor indicates the number of copies across the system, and load distribution metrics assess the current load on the cache.
metadata = {
    'priority': defaultdict(lambda: DEFAULT_PRIORITY),
    'latency': defaultdict(lambda: DEFAULT_LATENCY),
    'replication_factor': defaultdict(lambda: DEFAULT_REPLICATION_FACTOR),
    'load_distribution': defaultdict(int)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first considering entries with the lowest priority level. Among these, it selects the entry with the highest latency and lowest replication factor, ensuring that the load distribution remains balanced by not evicting entries from heavily loaded cache segments.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_priority = float('inf')
    max_latency = -1
    min_replication_factor = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        priority = metadata['priority'][key]
        latency = metadata['latency'][key]
        replication_factor = metadata['replication_factor'][key]
        load = metadata['load_distribution'][key]

        if priority < min_priority:
            min_priority = priority
            max_latency = latency
            min_replication_factor = replication_factor
            candid_obj_key = key
        elif priority == min_priority:
            if latency > max_latency or (latency == max_latency and replication_factor < min_replication_factor):
                max_latency = latency
                min_replication_factor = replication_factor
                candid_obj_key = key

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the priority level of the accessed entry and updates its latency to reflect the current access time. It also adjusts the load distribution metrics to account for the reduced load due to the hit.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['priority'][key] += 1
    metadata['latency'][key] = cache_snapshot.access_count
    metadata['load_distribution'][key] -= 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial priority level based on the object's importance, sets the initial latency to a default value, and updates the replication factor to reflect the number of copies. It also recalibrates the load distribution metrics to incorporate the new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['priority'][key] = DEFAULT_PRIORITY
    metadata['latency'][key] = DEFAULT_LATENCY
    metadata['replication_factor'][key] = DEFAULT_REPLICATION_FACTOR
    metadata['load_distribution'][key] += 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy decreases the overall load distribution metrics to reflect the reduced cache load. It also adjusts the replication factor of remaining entries if necessary to maintain optimal replication across the system.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    metadata['load_distribution'][evicted_key] -= 1
    del metadata['priority'][evicted_key]
    del metadata['latency'][evicted_key]
    del metadata['replication_factor'][evicted_key]
    del metadata['load_distribution'][evicted_key]