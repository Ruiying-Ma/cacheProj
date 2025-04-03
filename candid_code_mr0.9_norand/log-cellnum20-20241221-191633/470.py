# Import anything you need below
import math
from collections import defaultdict

# Put tunable constant parameters below
LATENCY_HARMONIC_INCREMENT = 0.1
BASELINE_ENTROPY = 1.0
INITIAL_PREDICTIVE_SYNERGY = 1.0
LOAD_EQUILIBRIUM_FACTOR = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a harmonic latency score for each cache entry, an entropy value representing access unpredictability, a predictive synergy score indicating future access likelihood, and a load equilibrium factor to balance cache load.
latency_harmonic_scores = defaultdict(float)
entropy_values = defaultdict(float)
predictive_synergy_scores = defaultdict(float)
load_equilibrium_factor = LOAD_EQUILIBRIUM_FACTOR

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest combined score of latency harmonics and predictive synergy, adjusted by entropy modulation and load equilibrium to ensure balanced cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (latency_harmonic_scores[key] + predictive_synergy_scores[key]) / (entropy_values[key] * load_equilibrium_factor)
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the latency harmonic score is slightly increased to reflect reduced access time, the entropy value is recalibrated based on recent access patterns, and the predictive synergy score is updated to reflect increased likelihood of future access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    latency_harmonic_scores[key] += LATENCY_HARMONIC_INCREMENT
    entropy_values[key] = BASELINE_ENTROPY / (1 + math.log(cache_snapshot.access_count))
    predictive_synergy_scores[key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the latency harmonic score based on initial access latency, sets a baseline entropy value, and calculates an initial predictive synergy score based on historical access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    latency_harmonic_scores[key] = 1.0 / (1 + cache_snapshot.access_count)
    entropy_values[key] = BASELINE_ENTROPY
    predictive_synergy_scores[key] = INITIAL_PREDICTIVE_SYNERGY

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the load equilibrium factor to ensure balanced cache distribution and adjusts the entropy modulation to reflect changes in access patterns due to the eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    global load_equilibrium_factor
    load_equilibrium_factor = cache_snapshot.size / cache_snapshot.capacity
    entropy_values.pop(evicted_obj.key, None)
    latency_harmonic_scores.pop(evicted_obj.key, None)
    predictive_synergy_scores.pop(evicted_obj.key, None)