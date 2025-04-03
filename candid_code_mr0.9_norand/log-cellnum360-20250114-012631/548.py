# Import anything you need below
import time

# Put tunable constant parameters below
ALPHA = 0.7  # Weight for access frequency
BETA = 0.2   # Weight for recency
GAMMA = 0.1  # Weight for synthesized data

# Put the metadata specifically maintained by the policy below. The policy maintains a statistical map of access frequencies, recency of access, and a synthesized score for each cache entry. It also keeps a feedback loop mechanism to adjust the weight of each factor dynamically based on hit/miss patterns.
access_frequency = {}
recency = {}
synthesized_score = {}
weights = {'alpha': ALPHA, 'beta': BETA, 'gamma': GAMMA}

def calculate_score(key):
    freq = access_frequency.get(key, 0)
    rec = recency.get(key, float('inf'))
    synth = synthesized_score.get(key, 0)
    return weights['alpha'] * freq + weights['beta'] * rec + weights['gamma'] * synth

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating an optimization heuristic score for each entry, which is a weighted combination of access frequency, recency, and synthesized data. The entry with the lowest score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key in cache_snapshot.cache:
        score = calculate_score(key)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency and recency metadata for the accessed entry are updated. The feedback loop mechanism adjusts the weights of the heuristic based on the current hit rate to optimize future decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] = access_frequency.get(key, 0) + 1
    recency[key] = cache_snapshot.access_count
    
    # Adjust weights based on hit rate
    hit_rate = cache_snapshot.hit_count / (cache_snapshot.hit_count + cache_snapshot.miss_count)
    weights['alpha'] = ALPHA * hit_rate
    weights['beta'] = BETA * (1 - hit_rate)
    weights['gamma'] = GAMMA

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency and recency metadata. The synthesized score is calculated, and the feedback loop mechanism updates the weights to reflect the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] = 1
    recency[key] = cache_snapshot.access_count
    synthesized_score[key] = 0  # Initialize synthesized score
    
    # Adjust weights based on hit rate
    hit_rate = cache_snapshot.hit_count / (cache_snapshot.hit_count + cache_snapshot.miss_count)
    weights['alpha'] = ALPHA * hit_rate
    weights['beta'] = BETA * (1 - hit_rate)
    weights['gamma'] = GAMMA

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the metadata of the evicted entry and recalculates the synthesized scores for the remaining entries. The feedback loop mechanism adjusts the weights to improve future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in access_frequency:
        del access_frequency[evicted_key]
    if evicted_key in recency:
        del recency[evicted_key]
    if evicted_key in synthesized_score:
        del synthesized_score[evicted_key]
    
    # Recalculate synthesized scores for remaining entries
    for key in cache_snapshot.cache:
        synthesized_score[key] = calculate_score(key)
    
    # Adjust weights based on hit rate
    hit_rate = cache_snapshot.hit_count / (cache_snapshot.hit_count + cache_snapshot.miss_count)
    weights['alpha'] = ALPHA * hit_rate
    weights['beta'] = BETA * (1 - hit_rate)
    weights['gamma'] = GAMMA