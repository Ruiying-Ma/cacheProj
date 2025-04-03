# Import anything you need below
import math

# Put tunable constant parameters below
DEFAULT_PREDICTIVE_SCORE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, and a predictive score based on historical access patterns. It also tracks statistical fluctuations in access patterns to adjust predictions dynamically.
metadata = {
    'access_frequency': {},
    'last_access_time': {},
    'predictive_score': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by combining temporal coherence and predictive modeling. It calculates a composite score for each cache entry, factoring in the likelihood of future access based on historical data and recent access patterns. The entry with the lowest composite score is chosen for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = math.inf
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_freq = metadata['access_frequency'].get(key, 0)
        last_access = metadata['last_access_time'].get(key, 0)
        predictive_score = metadata['predictive_score'].get(key, DEFAULT_PREDICTIVE_SCORE)
        
        # Composite score calculation
        composite_score = (predictive_score / (access_freq + 1)) + (cache_snapshot.access_count - last_access)
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the last access time and increments the access frequency for the accessed entry. It also recalculates the predictive score using the updated access pattern data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    
    # Recalculate predictive score (simple example, can be more complex)
    metadata['predictive_score'][key] = 1.0 / (metadata['access_frequency'][key] + 1)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its metadata with a default predictive score, sets the last access time to the current time, and sets the access frequency to one. It also updates the statistical model to include the new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['access_frequency'][key] = 1
    metadata['predictive_score'][key] = DEFAULT_PREDICTIVE_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy removes its metadata and adjusts the statistical model to account for the removal. It recalibrates the predictive scores of remaining entries to ensure accuracy in future predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['last_access_time']:
        del metadata['last_access_time'][evicted_key]
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['predictive_score']:
        del metadata['predictive_score'][evicted_key]
    
    # Recalibrate predictive scores (simple example, can be more complex)
    for key in metadata['predictive_score']:
        metadata['predictive_score'][key] = 1.0 / (metadata['access_frequency'][key] + 1)