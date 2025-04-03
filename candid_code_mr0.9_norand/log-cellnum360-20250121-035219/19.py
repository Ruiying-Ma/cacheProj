# Import anything you need below
import math
import time

# Put tunable constant parameters below
INITIAL_CONFIDENCE_INTERVAL = 1.0
INITIAL_BAYESIAN_PROBABILITY = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, confidence intervals for access predictions, and Bayesian probability estimates for future accesses. It also tracks data sparsity to identify less frequently accessed data.
metadata = {
    'access_frequency': {},
    'last_access_time': {},
    'confidence_interval': {},
    'bayesian_probability': {},
    'data_sparsity': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a score for each cache entry based on its access frequency, recency, and Bayesian probability of future access. Entries with lower scores, indicating lower likelihood of future access, are chosen for eviction. Data sparsity is also considered to avoid evicting sparse but important data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_freq = metadata['access_frequency'].get(key, 0)
        last_access = metadata['last_access_time'].get(key, 0)
        bayesian_prob = metadata['bayesian_probability'].get(key, INITIAL_BAYESIAN_PROBABILITY)
        data_sparsity = metadata['data_sparsity'].get(key, 1)
        
        # Calculate score
        score = (access_freq + 1) * (cache_snapshot.access_count - last_access) * (1 - bayesian_prob) * data_sparsity
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency and last access time for the accessed entry. It also recalculates the confidence interval and Bayesian probability estimate for future accesses based on the new access data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Update access frequency and last access time
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = current_time
    
    # Recalculate confidence interval and Bayesian probability
    access_freq = metadata['access_frequency'][key]
    metadata['confidence_interval'][key] = 1.0 / math.sqrt(access_freq)
    metadata['bayesian_probability'][key] = access_freq / (cache_snapshot.hit_count + cache_snapshot.miss_count)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency, last access time, and Bayesian probability estimate. It also sets an initial confidence interval for future access predictions and updates the overall data sparsity metrics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Initialize metadata
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = current_time
    metadata['confidence_interval'][key] = INITIAL_CONFIDENCE_INTERVAL
    metadata['bayesian_probability'][key] = INITIAL_BAYESIAN_PROBABILITY
    metadata['data_sparsity'][key] = 1  # Initial sparsity value

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy updates the data sparsity metrics to reflect the removal. It also adjusts the confidence intervals and Bayesian probability estimates for the remaining entries to account for the change in the cache composition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove metadata for evicted object
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['last_access_time']:
        del metadata['last_access_time'][evicted_key]
    if evicted_key in metadata['confidence_interval']:
        del metadata['confidence_interval'][evicted_key]
    if evicted_key in metadata['bayesian_probability']:
        del metadata['bayesian_probability'][evicted_key]
    if evicted_key in metadata['data_sparsity']:
        del metadata['data_sparsity'][evicted_key]
    
    # Adjust confidence intervals and Bayesian probabilities for remaining entries
    total_accesses = cache_snapshot.hit_count + cache_snapshot.miss_count
    for key in cache_snapshot.cache:
        access_freq = metadata['access_frequency'].get(key, 0)
        metadata['confidence_interval'][key] = 1.0 / math.sqrt(access_freq)
        metadata['bayesian_probability'][key] = access_freq / total_accesses