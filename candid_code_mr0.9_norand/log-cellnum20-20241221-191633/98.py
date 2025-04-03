# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
REDUNDANCY_WEIGHT = 1.0
FREQUENCY_WEIGHT = 1.0
AFFINITY_WEIGHT = 1.0
LOAD_DISTRIBUTION_WEIGHT = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including query frequency, data redundancy score, shard affinity, and load distribution index for each cached object.
query_frequency = defaultdict(int)
data_redundancy_score = defaultdict(float)
shard_affinity = defaultdict(float)
load_distribution_index = 0.0

def calculate_data_redundancy(obj, cache_snapshot):
    # Example calculation: count similar objects in cache
    return sum(1 for o in cache_snapshot.cache.values() if o.size == obj.size)

def calculate_shard_affinity(obj):
    # Example calculation: based on some property of the object
    return hash(obj.key) % 10

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the object with the lowest combined score of query frequency, data redundancy, and shard affinity, while considering the load distribution index to ensure balanced cache utilization.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (FREQUENCY_WEIGHT * query_frequency[key] +
                 REDUNDANCY_WEIGHT * data_redundancy_score[key] +
                 AFFINITY_WEIGHT * shard_affinity[key])
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the query frequency for the object is incremented, the data redundancy score is recalculated based on current cache contents, and the shard affinity is adjusted to reflect recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    query_frequency[obj.key] += 1
    data_redundancy_score[obj.key] = calculate_data_redundancy(obj, cache_snapshot)
    shard_affinity[obj.key] = calculate_shard_affinity(obj)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its query frequency to one, calculates its data redundancy score by comparing it with existing cache objects, and assigns a shard affinity based on the source of the data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    query_frequency[obj.key] = 1
    data_redundancy_score[obj.key] = calculate_data_redundancy(obj, cache_snapshot)
    shard_affinity[obj.key] = calculate_shard_affinity(obj)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy recalibrates the load distribution index to reflect the new cache state and adjusts the shard affinity of remaining objects to maintain balanced access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    global load_distribution_index
    load_distribution_index = sum(obj.size for obj in cache_snapshot.cache.values()) / cache_snapshot.capacity
    
    for key in cache_snapshot.cache:
        shard_affinity[key] = calculate_shard_affinity(cache_snapshot.cache[key])