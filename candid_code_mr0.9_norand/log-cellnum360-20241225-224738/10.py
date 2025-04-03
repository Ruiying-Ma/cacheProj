# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.7
RECENCY_WEIGHT = 0.3

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency of access, and a dynamic priority score for each cache entry. The priority score is calculated based on a weighted combination of frequency and recency, adjusted by a resource allocation factor that considers the current system load and cache size.
metadata = {
    'frequency': defaultdict(int),
    'recency': {},
    'priority_score': {},
    'resource_allocation_factor': 1.0
}

def calculate_priority_score(frequency, recency, resource_allocation_factor):
    return (FREQUENCY_WEIGHT * frequency + RECENCY_WEIGHT * recency) * resource_allocation_factor

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache entry with the lowest priority score. In case of a tie, it evicts the least recently used entry among those with the lowest scores. This approach balances between frequently accessed and recently accessed data while considering system constraints.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_priority_score = float('inf')
    min_recency = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = metadata['priority_score'][key]
        recency = metadata['recency'][key]
        
        if score < min_priority_score or (score == min_priority_score and recency < min_recency):
            min_priority_score = score
            min_recency = recency
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the access frequency and updates the recency timestamp for the accessed entry. It then recalculates the priority score by applying the weighted combination of the updated frequency and recency, adjusted by the current resource allocation factor.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['frequency'][key] += 1
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['priority_score'][key] = calculate_priority_score(
        metadata['frequency'][key],
        metadata['recency'][key],
        metadata['resource_allocation_factor']
    )

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency to one and sets the recency timestamp to the current time. The priority score is calculated using the initial frequency and recency, with adjustments based on the current resource allocation factor to ensure optimal cache utilization.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['frequency'][key] = 1
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['priority_score'][key] = calculate_priority_score(
        metadata['frequency'][key],
        metadata['recency'][key],
        metadata['resource_allocation_factor']
    )

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the resource allocation factor based on the current cache occupancy and system load. This recalibration helps in dynamically adjusting the priority scores of remaining entries to better align with the updated cache conditions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    cache_occupancy_ratio = cache_snapshot.size / cache_snapshot.capacity
    system_load_factor = cache_snapshot.access_count / (cache_snapshot.hit_count + cache_snapshot.miss_count)
    metadata['resource_allocation_factor'] = 1.0 + cache_occupancy_ratio * system_load_factor
    
    for key in cache_snapshot.cache:
        metadata['priority_score'][key] = calculate_priority_score(
            metadata['frequency'][key],
            metadata['recency'][key],
            metadata['resource_allocation_factor']
        )