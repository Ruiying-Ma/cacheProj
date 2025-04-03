# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASE_LAYER = 0
LATENCY_WEIGHT = 1.0
PRIORITY_INCREMENT = 1.0
FREQUENT_ACCESS_THRESHOLD = 5
RESOURCE_ALLOCATION_FACTOR = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a Latency Index for each cache entry, a Predictive Priority score based on access patterns, a Dynamic Layer indicating the entry's current cache layer, and a Resource Allocation metric reflecting the entry's resource usage.
latency_index = defaultdict(lambda: float('inf'))
predictive_priority = defaultdict(float)
dynamic_layer = defaultdict(lambda: BASE_LAYER)
resource_allocation = defaultdict(float)
access_frequency = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest Predictive Priority score, considering entries in the lowest Dynamic Layer first, and using the Latency Index to break ties by evicting the entry with the highest latency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_priority = float('inf')
    min_layer = float('inf')
    max_latency = -1

    for key, cached_obj in cache_snapshot.cache.items():
        if (dynamic_layer[key] < min_layer or
            (dynamic_layer[key] == min_layer and predictive_priority[key] < min_priority) or
            (dynamic_layer[key] == min_layer and predictive_priority[key] == min_priority and latency_index[key] > max_latency)):
            candid_obj_key = key
            min_priority = predictive_priority[key]
            min_layer = dynamic_layer[key]
            max_latency = latency_index[key]
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Latency Index is updated to reflect the current access latency, the Predictive Priority score is increased based on recent access patterns, the Dynamic Layer is adjusted upwards if the entry is frequently accessed, and Resource Allocation is recalibrated to reflect current usage.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    latency_index[obj.key] = cache_snapshot.access_count
    predictive_priority[obj.key] += PRIORITY_INCREMENT
    access_frequency[obj.key] += 1

    if access_frequency[obj.key] >= FREQUENT_ACCESS_THRESHOLD:
        dynamic_layer[obj.key] += 1
        access_frequency[obj.key] = 0

    resource_allocation[obj.key] = obj.size * RESOURCE_ALLOCATION_FACTOR

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Latency Index is initialized based on initial access latency, the Predictive Priority score is set using historical data if available, the Dynamic Layer is set to the base layer, and Resource Allocation is calculated based on the object's initial resource footprint.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    latency_index[obj.key] = cache_snapshot.access_count
    predictive_priority[obj.key] = 0  # Assuming no historical data
    dynamic_layer[obj.key] = BASE_LAYER
    resource_allocation[obj.key] = obj.size * RESOURCE_ALLOCATION_FACTOR
    access_frequency[obj.key] = 0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the policy recalibrates the Predictive Priority scores of remaining entries to reflect the change in cache dynamics, adjusts the Dynamic Layer of entries that were in the same layer as the evicted entry, and redistributes Resource Allocation to optimize for remaining entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        if dynamic_layer[key] == dynamic_layer[evicted_obj.key]:
            dynamic_layer[key] = max(BASE_LAYER, dynamic_layer[key] - 1)
        predictive_priority[key] *= 0.9  # Decay factor for recalibration
        resource_allocation[key] = cache_snapshot.cache[key].size * RESOURCE_ALLOCATION_FACTOR