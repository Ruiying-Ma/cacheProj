# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for frequency
BETA = 0.3   # Weight for recency
GAMMA = 0.2  # Weight for dynamic factor

# Put the metadata specifically maintained by the policy below. The policy maintains a multi-level metadata structure that includes access frequency, recency, and a dynamic weight factor for each cache entry. It also tracks hierarchical access patterns and load distribution across different cache levels.
metadata = {
    'frequency': defaultdict(int),
    'recency': {},
    'dynamic_weight': defaultdict(float),
    'access_pattern': defaultdict(list),
    'load_distribution': defaultdict(int)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects an eviction victim by calculating a composite score for each entry, which combines access frequency, recency, and the dynamic weight factor. Entries with the lowest scores are considered for eviction, with additional consideration for balancing load across cache levels.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        frequency = metadata['frequency'][key]
        recency = cache_snapshot.access_count - metadata['recency'][key]
        dynamic_weight = metadata['dynamic_weight'][key]
        
        score = (ALPHA * frequency) + (BETA * recency) + (GAMMA * dynamic_weight)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency and recency of the accessed entry are updated. The dynamic weight factor is adjusted based on the observed access pattern, and the load distribution metadata is recalibrated to reflect the current access trends.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['frequency'][key] += 1
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['dynamic_weight'][key] = (metadata['frequency'][key] / (cache_snapshot.access_count + 1))
    metadata['load_distribution'][key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its metadata with default values and updates the hierarchical access pattern to include the new entry. The load distribution is also adjusted to account for the new entry's impact on cache levels.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['frequency'][key] = 1
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['dynamic_weight'][key] = 0.0
    metadata['access_pattern'][key].append(cache_snapshot.access_count)
    metadata['load_distribution'][key] = 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the dynamic weight factors of remaining entries to ensure balanced load distribution. The hierarchical access pattern is updated to remove the evicted entry, and the overall load distribution is adjusted accordingly.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['frequency']:
        del metadata['frequency'][evicted_key]
    if evicted_key in metadata['recency']:
        del metadata['recency'][evicted_key]
    if evicted_key in metadata['dynamic_weight']:
        del metadata['dynamic_weight'][evicted_key]
    if evicted_key in metadata['access_pattern']:
        del metadata['access_pattern'][evicted_key]
    if evicted_key in metadata['load_distribution']:
        del metadata['load_distribution'][evicted_key]
    
    # Recalibrate dynamic weights
    for key in cache_snapshot.cache:
        metadata['dynamic_weight'][key] = (metadata['frequency'][key] / (cache_snapshot.access_count + 1))