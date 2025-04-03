# Import anything you need below
from collections import defaultdict
import math

# Put tunable constant parameters below
INITIAL_ENTROPY_SCORE = 0.5
PREDICTIVE_SCORE_WEIGHT = 0.5
FREQUENCY_WEIGHT = 0.3
LAST_ACCESS_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains a 'Temporal Signature' for each cache entry, which is a combination of the last access time, frequency of access, and a predictive score derived from recent access patterns. Additionally, an 'Entropy Score' is calculated to measure the randomness of access patterns for each entry.
temporal_signature = defaultdict(lambda: {'last_access': 0, 'frequency': 0, 'predictive_score': 0})
entropy_score = defaultdict(lambda: INITIAL_ENTROPY_SCORE)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the highest Entropy Score, indicating the least predictable access pattern, and the lowest Temporal Signature, suggesting infrequent and outdated access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_entropy = -1
    min_temporal_signature = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        ts = (temporal_signature[key]['last_access'] * LAST_ACCESS_WEIGHT +
              temporal_signature[key]['frequency'] * FREQUENCY_WEIGHT +
              temporal_signature[key]['predictive_score'] * PREDICTIVE_SCORE_WEIGHT)
        
        if entropy_score[key] > max_entropy or (entropy_score[key] == max_entropy and ts < min_temporal_signature):
            max_entropy = entropy_score[key]
            min_temporal_signature = ts
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Temporal Signature of the accessed entry is updated by increasing its frequency component and recalculating the predictive score based on the latest access pattern. The Entropy Score is adjusted to reflect the reduced randomness due to the recent access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    temporal_signature[key]['last_access'] = cache_snapshot.access_count
    temporal_signature[key]['frequency'] += 1
    temporal_signature[key]['predictive_score'] = calculate_predictive_score(key)
    entropy_score[key] = max(0, entropy_score[key] - 0.1)  # Reduce randomness

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its Temporal Signature is initialized with the current time, a frequency of one, and a predictive score based on initial access context. The Entropy Score is set to a neutral value, indicating no prior randomness.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    temporal_signature[key] = {
        'last_access': cache_snapshot.access_count,
        'frequency': 1,
        'predictive_score': calculate_predictive_score(key)
    }
    entropy_score[key] = INITIAL_ENTROPY_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the Entropy Scores of remaining entries to account for the removal of the evicted entry's influence on overall access patterns, ensuring the cache adapts to the new state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in temporal_signature:
        del temporal_signature[evicted_key]
    if evicted_key in entropy_score:
        del entropy_score[evicted_key]
    
    # Recalibrate entropy scores
    for key in cache_snapshot.cache:
        entropy_score[key] = min(1, entropy_score[key] + 0.05)  # Increase randomness

def calculate_predictive_score(key):
    # Placeholder for predictive score calculation logic
    # This could be based on historical access patterns, time of day, etc.
    return 0.5  # Example static value