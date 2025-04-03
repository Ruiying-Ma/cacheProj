# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 1.0
RECENCY_WEIGHT = 1.0
SIZE_WEIGHT = 0.1
EFFICIENCY_PROJECTION_DECAY = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains a dynamic score for each cache entry, calculated using Essential Metrics such as access frequency, recency, and size. It also tracks an Efficiency Projection for each entry, predicting future utility based on past access patterns and current workload characteristics.
cache_metadata = {
    'frequency': defaultdict(int),
    'recency': {},
    'efficiency_projection': defaultdict(float),
}

def calculate_dynamic_score(key, cache_snapshot):
    frequency = cache_metadata['frequency'][key]
    recency = cache_metadata['recency'][key]
    size = cache_snapshot.cache[key].size
    efficiency_projection = cache_metadata['efficiency_projection'][key]
    
    dynamic_score = (FREQUENCY_WEIGHT * frequency +
                     RECENCY_WEIGHT * recency -
                     SIZE_WEIGHT * size +
                     efficiency_projection)
    return dynamic_score

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest combined score of current utility and Efficiency Projection, ensuring Adaptive Synergy with the workload by considering both immediate and future needs.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key in cache_snapshot.cache:
        score = calculate_dynamic_score(key, cache_snapshot)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the entry's dynamic score by boosting its recency and frequency metrics, and refines the Efficiency Projection by incorporating the latest access pattern data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    cache_metadata['frequency'][key] += 1
    cache_metadata['recency'][key] = cache_snapshot.access_count
    cache_metadata['efficiency_projection'][key] *= EFFICIENCY_PROJECTION_DECAY

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its dynamic score based on initial Essential Metrics and sets a baseline Efficiency Projection, which is then adjusted as more access data becomes available.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    cache_metadata['frequency'][key] = 1
    cache_metadata['recency'][key] = cache_snapshot.access_count
    cache_metadata['efficiency_projection'][key] = 0.0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the Efficiency Projection for remaining entries to reflect the changed cache landscape, ensuring that future decisions are informed by the most current state of the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in cache_metadata['frequency']:
        del cache_metadata['frequency'][evicted_key]
    if evicted_key in cache_metadata['recency']:
        del cache_metadata['recency'][evicted_key]
    if evicted_key in cache_metadata['efficiency_projection']:
        del cache_metadata['efficiency_projection'][evicted_key]
    
    # Recalibrate efficiency projections for remaining entries
    for key in cache_snapshot.cache:
        cache_metadata['efficiency_projection'][key] *= EFFICIENCY_PROJECTION_DECAY