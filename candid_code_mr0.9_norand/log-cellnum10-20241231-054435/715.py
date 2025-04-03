# Import anything you need below
import math
from collections import defaultdict

# Put tunable constant parameters below
BASE_ENTROPIC_COHERENCE = 1.0
INITIAL_ACCESS_PROBABILITY = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive model for each cache object, estimating future access probabilities based on temporal access patterns. It also tracks entropic coherence, a measure of how predictable an object's access pattern is, and a heuristic score that combines these factors to optimize cache performance.
predictive_model = defaultdict(lambda: INITIAL_ACCESS_PROBABILITY)
entropic_coherence = defaultdict(lambda: BASE_ENTROPIC_COHERENCE)
heuristic_score = {}

def calculate_heuristic_score(key):
    # Combine access probability and entropic coherence to calculate heuristic score
    return predictive_model[key] * entropic_coherence[key]

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the object with the lowest heuristic score, which is calculated by combining the predicted access probability and entropic coherence. This approach ensures that objects with low future access likelihood and high unpredictability are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for key in cache_snapshot.cache:
        score = calculate_heuristic_score(key)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the predictive model for the accessed object to refine its future access probability. It also recalculates the entropic coherence to reflect the new access pattern and adjusts the heuristic score accordingly.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    # Update predictive model (e.g., increase probability)
    predictive_model[key] = min(1.0, predictive_model[key] + 0.1)
    # Recalculate entropic coherence (e.g., decrease unpredictability)
    entropic_coherence[key] = max(0.1, entropic_coherence[key] - 0.1)
    # Update heuristic score
    heuristic_score[key] = calculate_heuristic_score(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its predictive model based on initial access patterns and assigns a baseline entropic coherence value. The heuristic score is computed to establish its initial priority within the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    # Initialize predictive model
    predictive_model[key] = INITIAL_ACCESS_PROBABILITY
    # Assign baseline entropic coherence
    entropic_coherence[key] = BASE_ENTROPIC_COHERENCE
    # Compute initial heuristic score
    heuristic_score[key] = calculate_heuristic_score(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy updates the global predictive model to account for the removal of the object, potentially adjusting the models of remaining objects. It also recalibrates the entropic coherence of the cache to maintain overall system balance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    # Remove evicted object's metadata
    if evicted_key in predictive_model:
        del predictive_model[evicted_key]
    if evicted_key in entropic_coherence:
        del entropic_coherence[evicted_key]
    if evicted_key in heuristic_score:
        del heuristic_score[evicted_key]
    
    # Optionally adjust models of remaining objects (not implemented here)
    # Recalibrate entropic coherence of the cache (not implemented here)