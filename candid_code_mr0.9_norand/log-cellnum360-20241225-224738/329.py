# Import anything you need below
import collections

# Put tunable constant parameters below
PREDICTIVE_SCORE_INCREMENT = 1.0
INITIAL_PREDICTIVE_SCORE = 1.0
NEUTRAL_COHERENCY_FACTOR = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, and a predictive score based on historical access patterns. It also tracks a coherency factor that estimates the likelihood of data being accessed soon based on recent trends.
metadata = collections.defaultdict(lambda: {
    'access_frequency': 0,
    'last_access_timestamp': 0,
    'predictive_score': INITIAL_PREDICTIVE_SCORE,
    'coherency_factor': NEUTRAL_COHERENCY_FACTOR
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache entry, which combines low access frequency, older timestamps, and low predictive scores. Entries with the lowest composite scores are selected for eviction, ensuring strategic optimization of cache space.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        composite_score = (meta['access_frequency'] * 0.3 +
                           (cache_snapshot.access_count - meta['last_access_timestamp']) * 0.3 +
                           meta['predictive_score'] * 0.2 +
                           meta['coherency_factor'] * 0.2)
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency is incremented, the last access timestamp is updated to the current time, and the predictive score is adjusted upwards to reflect increased likelihood of future access. The coherency factor is recalibrated based on recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['access_frequency'] += 1
    meta['last_access_timestamp'] = cache_snapshot.access_count
    meta['predictive_score'] += PREDICTIVE_SCORE_INCREMENT
    # Recalibrate coherency factor based on recent access patterns
    meta['coherency_factor'] = min(1.0, meta['coherency_factor'] + 0.1)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency to one, sets the last access timestamp to the current time, and assigns an initial predictive score based on similar past entries. The coherency factor is set to a neutral value, awaiting further access data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    metadata[obj.key] = {
        'access_frequency': 1,
        'last_access_timestamp': cache_snapshot.access_count,
        'predictive_score': INITIAL_PREDICTIVE_SCORE,
        'coherency_factor': NEUTRAL_COHERENCY_FACTOR
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the predictive scores and coherency factors of remaining entries to reflect the removal of the evicted entry, ensuring that the cache adapts incrementally to the new data landscape.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Recalibrate predictive scores and coherency factors
    for key in cache_snapshot.cache:
        if key != evicted_obj.key:
            meta = metadata[key]
            meta['predictive_score'] = max(0, meta['predictive_score'] - 0.1)
            meta['coherency_factor'] = max(0, meta['coherency_factor'] - 0.05)
    
    # Remove metadata for evicted object
    if evicted_obj.key in metadata:
        del metadata[evicted_obj.key]