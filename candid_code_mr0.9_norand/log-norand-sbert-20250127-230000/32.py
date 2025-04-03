# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
import math

# Put tunable constant parameters below
INITIAL_BAYESIAN_PROB = 0.5
NEUTRAL_DIFFUSION_SCORE = 1.0
BAYESIAN_UPDATE_FACTOR = 0.1
DIFFUSION_UPDATE_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a Bayesian probability distribution for each cache entry's likelihood of being accessed, a timestamp of the last access, and a diffusion score representing the spread of access patterns over time.
metadata = {
    'bayesian_prob': {},  # key -> Bayesian probability
    'last_access': {},    # key -> last access timestamp
    'diffusion_score': {} # key -> diffusion score
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache entry with the lowest Bayesian probability of being accessed next, adjusted by the diffusion score to account for recent access patterns and the timestamp to ensure synchronous computation.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        bayesian_prob = metadata['bayesian_prob'].get(key, INITIAL_BAYESIAN_PROB)
        last_access = metadata['last_access'].get(key, 0)
        diffusion_score = metadata['diffusion_score'].get(key, NEUTRAL_DIFFUSION_SCORE)
        
        score = bayesian_prob * diffusion_score * (cache_snapshot.access_count - last_access)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the Bayesian probability distribution to increase the likelihood of future access, refreshes the timestamp to the current time, and adjusts the diffusion score to reflect the recent access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['bayesian_prob'][key] = min(1.0, metadata['bayesian_prob'].get(key, INITIAL_BAYESIAN_PROB) + BAYESIAN_UPDATE_FACTOR)
    metadata['last_access'][key] = cache_snapshot.access_count
    metadata['diffusion_score'][key] = max(0.0, metadata['diffusion_score'].get(key, NEUTRAL_DIFFUSION_SCORE) - DIFFUSION_UPDATE_FACTOR)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its Bayesian probability distribution with a moderate likelihood, sets the timestamp to the current time, and assigns a neutral diffusion score to allow the entry to adapt to access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['bayesian_prob'][key] = INITIAL_BAYESIAN_PROB
    metadata['last_access'][key] = cache_snapshot.access_count
    metadata['diffusion_score'][key] = NEUTRAL_DIFFUSION_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the Bayesian probability distributions of remaining entries to account for the removal, updates the diffusion scores to reflect the new cache state, and synchronizes timestamps to maintain consistent computation.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['bayesian_prob']:
        del metadata['bayesian_prob'][evicted_key]
    if evicted_key in metadata['last_access']:
        del metadata['last_access'][evicted_key]
    if evicted_key in metadata['diffusion_score']:
        del metadata['diffusion_score'][evicted_key]
    
    # Recalibrate Bayesian probabilities and diffusion scores
    for key in cache_snapshot.cache:
        metadata['bayesian_prob'][key] = max(0.0, metadata['bayesian_prob'].get(key, INITIAL_BAYESIAN_PROB) * (1 - BAYESIAN_UPDATE_FACTOR))
        metadata['diffusion_score'][key] = min(1.0, metadata['diffusion_score'].get(key, NEUTRAL_DIFFUSION_SCORE) + DIFFUSION_UPDATE_FACTOR)