# Import anything you need below
from collections import deque, defaultdict

# Put tunable constant parameters below
CIRCUIT_THRESHOLD = 5  # Example threshold for circuit completion
LOAD_BALANCE_FACTOR = 0.1  # Example factor for load balancing

# Put the metadata specifically maintained by the policy below. The policy maintains a temporal order list of cache entries, a dynamic eviction threshold based on recent access patterns, a circuit completion counter for each entry to track its usage cycle, and a load equilibrium factor to balance cache load across different entries.
temporal_order = deque()  # To maintain the order of cache entries
circuit_completion_counter = defaultdict(int)  # To track usage cycles
load_equilibrium_factor = defaultdict(float)  # To balance cache load
dynamic_eviction_threshold = 0  # To determine eviction threshold

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying entries that have completed their usage cycle as indicated by the circuit completion counter, prioritizing those that exceed the dynamic eviction threshold and contribute to load imbalance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    for key in temporal_order:
        if (circuit_completion_counter[key] >= CIRCUIT_THRESHOLD and
            load_equilibrium_factor[key] > dynamic_eviction_threshold):
            candid_obj_key = key
            break

    if candid_obj_key is None:
        # Fallback to evict the least recently used if no candidate found
        candid_obj_key = temporal_order[0]

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the temporal order list is updated to move the accessed entry to the most recent position, the circuit completion counter for the entry is incremented, and the load equilibrium factor is adjusted to reflect the current access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    if key in temporal_order:
        temporal_order.remove(key)
    temporal_order.append(key)
    circuit_completion_counter[key] += 1
    load_equilibrium_factor[key] = (circuit_completion_counter[key] / cache_snapshot.access_count)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the temporal order list is updated to include the new entry at the most recent position, the circuit completion counter is initialized, and the load equilibrium factor is recalibrated to account for the new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    temporal_order.append(key)
    circuit_completion_counter[key] = 0
    load_equilibrium_factor[key] = 0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the temporal order list is updated to remove the evicted entry, the dynamic eviction threshold is recalculated based on the remaining entries, and the load equilibrium factor is adjusted to redistribute the cache load.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in temporal_order:
        temporal_order.remove(evicted_key)
    del circuit_completion_counter[evicted_key]
    del load_equilibrium_factor[evicted_key]

    # Recalculate dynamic eviction threshold
    if temporal_order:
        dynamic_eviction_threshold = sum(load_equilibrium_factor[key] for key in temporal_order) / len(temporal_order)
    else:
        dynamic_eviction_threshold = 0