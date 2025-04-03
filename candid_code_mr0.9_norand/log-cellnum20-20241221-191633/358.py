# Import anything you need below
import math
from collections import defaultdict

# Put tunable constant parameters below
BASE_PREDICTIVE_SCORE = 1.0
INITIAL_ENTROPY = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, causal relationships between data objects, predictive scores for future accesses, and entropy levels to measure uncertainty in access patterns.
access_frequency = defaultdict(int)
causal_relationships = defaultdict(lambda: defaultdict(int))
predictive_scores = defaultdict(lambda: BASE_PREDICTIVE_SCORE)
entropy_levels = defaultdict(lambda: INITIAL_ENTROPY)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by evaluating a combination of low predictive scores, weak causal relationships, low access frequency, and high entropy, prioritizing objects that are least likely to be accessed soon.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (predictive_scores[key] * access_frequency[key]) / (1 + entropy_levels[key])
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the access frequency, updates the causal relationships based on recent access patterns, recalculates the predictive score to reflect the likelihood of future accesses, and adjusts the entropy to reflect reduced uncertainty.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] += 1
    predictive_scores[key] += 0.1  # Increase predictive score slightly
    entropy_levels[key] *= 0.9  # Reduce entropy to reflect reduced uncertainty

    # Update causal relationships
    for other_key in cache_snapshot.cache:
        if other_key != key:
            causal_relationships[key][other_key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency, establishes initial causal relationships with recently accessed objects, assigns a baseline predictive score, and sets an initial entropy level based on current cache dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] = 1
    predictive_scores[key] = BASE_PREDICTIVE_SCORE
    entropy_levels[key] = INITIAL_ENTROPY

    # Establish initial causal relationships
    for other_key in cache_snapshot.cache:
        if other_key != key:
            causal_relationships[key][other_key] = 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the causal relationships and predictive scores of remaining objects, adjusts the overall entropy to reflect the change in cache composition, and updates any global statistics related to access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key

    # Remove metadata of evicted object
    if evicted_key in access_frequency:
        del access_frequency[evicted_key]
    if evicted_key in predictive_scores:
        del predictive_scores[evicted_key]
    if evicted_key in entropy_levels:
        del entropy_levels[evicted_key]
    if evicted_key in causal_relationships:
        del causal_relationships[evicted_key]

    # Recalibrate causal relationships and predictive scores
    for key in cache_snapshot.cache:
        if evicted_key in causal_relationships[key]:
            del causal_relationships[key][evicted_key]
        predictive_scores[key] *= 0.95  # Slightly reduce predictive scores
        entropy_levels[key] *= 1.05  # Slightly increase entropy