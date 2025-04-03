# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.7
RECENCY_WEIGHT = 0.3

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency of access, and a dynamic priority score for each cached item. The priority score is calculated based on a weighted combination of frequency and recency, adjusted by a resource allocation factor that considers the current load and available cache space.
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
    The policy chooses the eviction victim by selecting the item with the lowest priority score. In case of a tie, it considers the resource allocation factor to decide which item would free up the most resources relative to its priority score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_priority_score = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        priority_score = metadata['priority_score'][key]
        if priority_score < min_priority_score:
            min_priority_score = priority_score
            candid_obj_key = key
        elif priority_score == min_priority_score:
            # Consider resource allocation factor
            if cached_obj.size / priority_score > cache_snapshot.cache[candid_obj_key].size / min_priority_score:
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency is incremented, and the recency of access is updated to the current time. The priority score is recalculated using the updated frequency and recency, factoring in the current resource allocation status.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
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
    After inserting a new object, the policy initializes its access frequency to one and sets its recency to the current time. The priority score is calculated based on these initial values and the current resource allocation factor.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
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
    After evicting an item, the policy recalibrates the resource allocation factor to reflect the newly available cache space. It also adjusts the priority scores of remaining items to ensure they are balanced with the updated resource allocation context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Recalibrate resource allocation factor
    metadata['resource_allocation_factor'] = cache_snapshot.capacity / (cache_snapshot.size + obj.size)
    
    # Adjust priority scores of remaining items
    for key in cache_snapshot.cache:
        metadata['priority_score'][key] = calculate_priority_score(
            metadata['frequency'][key],
            metadata['recency'][key],
            metadata['resource_allocation_factor']
        )