# Import anything you need below
import time

# Put tunable constant parameters below
DECAY_RATE = 0.1
INITIAL_SCORE = 10
RESOURCE_PRIORITY = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive score for each cache entry, calculated using a combination of historical access patterns, time since last access, and resource allocation priority. It also tracks a decay factor that reduces the predictive score over time if the entry is not accessed.
cache_metadata = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest predictive score, factoring in both the decay factor and the resource allocation priority. This ensures that entries with low likelihood of future access and low priority are evicted first.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        metadata = cache_metadata.get(key, {})
        score = metadata.get('score', INITIAL_SCORE)
        decay_factor = metadata.get('decay_factor', DECAY_RATE)
        priority = metadata.get('priority', RESOURCE_PRIORITY)
        
        # Calculate effective score
        effective_score = score * (1 - decay_factor) * priority
        
        if effective_score < min_score:
            min_score = effective_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive score of the accessed entry is increased based on the frequency and recency of access, and the decay factor is reset to reflect the renewed interest in the entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    if key in cache_metadata:
        cache_metadata[key]['score'] += 1
        cache_metadata[key]['decay_factor'] = 0

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its predictive score based on initial access patterns and assigns a decay factor. The resource allocation priority is also set according to the system's current optimization goals.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    cache_metadata[key] = {
        'score': INITIAL_SCORE,
        'decay_factor': DECAY_RATE,
        'priority': RESOURCE_PRIORITY
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy recalibrates the decay factors and predictive scores of remaining entries to ensure balanced resource allocation and to adjust for any shifts in access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in cache_metadata:
        del cache_metadata[evicted_key]
    
    for key in cache_snapshot.cache:
        if key in cache_metadata:
            cache_metadata[key]['decay_factor'] += DECAY_RATE