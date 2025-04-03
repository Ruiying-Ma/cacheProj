# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQUENCY = 1.0
WEIGHT_RECENCY = 1.0
WEIGHT_RESOURCE_COST = 1.0
WEIGHT_LOAD_BALANCE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, resource cost of serving the data, and a load balancing score that reflects the distribution of cache hits across different nodes in a distributed system.
metadata = {
    'access_frequency': defaultdict(int),
    'last_access_time': {},
    'resource_cost': {},
    'load_balancing_score': defaultdict(float)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cached item, which is a weighted sum of its access frequency, recency, resource cost, and load balancing score. The item with the lowest composite score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_frequency = metadata['access_frequency'][key]
        recency = cache_snapshot.access_count - metadata['last_access_time'][key]
        resource_cost = metadata['resource_cost'][key]
        load_balancing_score = metadata['load_balancing_score'][key]
        
        composite_score = (
            WEIGHT_ACCESS_FREQUENCY * access_frequency +
            WEIGHT_RECENCY * recency +
            WEIGHT_RESOURCE_COST * resource_cost +
            WEIGHT_LOAD_BALANCE * load_balancing_score
        )
        
        if composite_score < min_score:
            min_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency and last access time of the item are updated. Additionally, the load balancing score is adjusted to reflect the current distribution of cache hits, ensuring that no single node becomes a bottleneck.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    # Adjust load balancing score (simplified as incrementing for demonstration)
    metadata['load_balancing_score'][key] += 1.0

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency and last access time. The resource cost is assessed based on the object's size and retrieval complexity, and the load balancing score is updated to account for the new distribution of cached items.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['resource_cost'][key] = obj.size  # Assuming size as a proxy for resource cost
    metadata['load_balancing_score'][key] = 1.0  # Initial load balancing score

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the load balancing scores across the system to ensure even distribution of cache hits. It also adjusts the resource allocation metrics to reflect the freed resources, optimizing for future cache insertions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Remove metadata for evicted object
    del metadata['access_frequency'][evicted_key]
    del metadata['last_access_time'][evicted_key]
    del metadata['resource_cost'][evicted_key]
    del metadata['load_balancing_score'][evicted_key]
    
    # Recalibrate load balancing scores (simplified as normalizing for demonstration)
    total_hits = sum(metadata['access_frequency'].values())
    for key in metadata['load_balancing_score']:
        metadata['load_balancing_score'][key] = metadata['access_frequency'][key] / total_hits if total_hits > 0 else 0.0