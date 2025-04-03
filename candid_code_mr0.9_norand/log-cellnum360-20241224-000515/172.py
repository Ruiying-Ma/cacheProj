# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
LOAD_BALANCE_FACTOR = 0.5  # This is a tunable parameter to adjust the load balancing factor

# Put the metadata specifically maintained by the policy below. The policy maintains a prioritization matrix that records the access frequency and recency of each cache item, an eviction frequency counter for each item, and a dynamic load balancing factor that adjusts based on current system load and cache hit/miss ratio.
prioritization_matrix = defaultdict(lambda: {'access_freq': 0, 'recency': 0, 'eviction_freq': 0})
dynamic_load_balancing_factor = LOAD_BALANCE_FACTOR

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying items with the highest eviction frequency and lowest priority score in the prioritization matrix, while also considering the dynamic load balancing factor to ensure optimal cache performance under varying system loads.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_priority_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        metadata = prioritization_matrix[key]
        priority_score = (metadata['access_freq'] * dynamic_load_balancing_factor) + metadata['recency'] - metadata['eviction_freq']
        
        if priority_score < min_priority_score:
            min_priority_score = priority_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the access frequency and updates the recency score of the accessed item in the prioritization matrix, while also adjusting the dynamic load balancing factor to reflect the improved cache efficiency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    metadata = prioritization_matrix[obj.key]
    metadata['access_freq'] += 1
    metadata['recency'] = cache_snapshot.access_count
    
    # Adjust dynamic load balancing factor
    hit_ratio = cache_snapshot.hit_count / (cache_snapshot.hit_count + cache_snapshot.miss_count)
    global dynamic_load_balancing_factor
    dynamic_load_balancing_factor = LOAD_BALANCE_FACTOR * hit_ratio

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency and recency in the prioritization matrix, sets its eviction frequency to zero, and recalibrates the dynamic load balancing factor to account for the new cache composition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    prioritization_matrix[obj.key] = {'access_freq': 1, 'recency': cache_snapshot.access_count, 'eviction_freq': 0}
    
    # Recalibrate dynamic load balancing factor
    hit_ratio = cache_snapshot.hit_count / (cache_snapshot.hit_count + cache_snapshot.miss_count)
    global dynamic_load_balancing_factor
    dynamic_load_balancing_factor = LOAD_BALANCE_FACTOR * hit_ratio

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy increments the eviction frequency of the evicted item, updates the prioritization matrix to remove the item, and recalibrates the dynamic load balancing factor to maintain optimal cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    prioritization_matrix[evicted_obj.key]['eviction_freq'] += 1
    del prioritization_matrix[evicted_obj.key]
    
    # Recalibrate dynamic load balancing factor
    hit_ratio = cache_snapshot.hit_count / (cache_snapshot.hit_count + cache_snapshot.miss_count)
    global dynamic_load_balancing_factor
    dynamic_load_balancing_factor = LOAD_BALANCE_FACTOR * hit_ratio