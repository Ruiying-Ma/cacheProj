# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_PREDICTIVE_SCORE = 1.0
HIT_BOOST_FACTOR = 1.5
DECAY_FACTOR = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains a Predictive Score for each object, a Data Retention Index (DRI), and an Adaptive Release Schedule (ARS) that prioritizes objects based on structured criteria such as access frequency, recency, and predicted future access patterns.
predictive_scores = defaultdict(lambda: INITIAL_PREDICTIVE_SCORE)
access_frequencies = defaultdict(int)
last_access_times = defaultdict(int)

def calculate_predictive_score(key, cache_snapshot):
    # Calculate the Predictive Score using DRI and ARS
    frequency = access_frequencies[key]
    recency = cache_snapshot.access_count - last_access_times[key]
    return predictive_scores[key] * (frequency / (recency + 1))

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the object with the lowest Predictive Score, which is calculated using the DRI and ARS, ensuring that objects with lower future access probability and lower priority are evicted first.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key in cache_snapshot.cache:
        score = calculate_predictive_score(key, cache_snapshot)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Predictive Score of the accessed object is increased based on its DRI and ARS, reflecting its increased likelihood of future access, and its position in the structured prioritization is adjusted accordingly.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    access_frequencies[key] += 1
    last_access_times[key] = cache_snapshot.access_count
    predictive_scores[key] *= HIT_BOOST_FACTOR

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial Predictive Score based on its DRI and ARS, and integrates it into the structured prioritization, ensuring it is positioned relative to existing objects based on predicted access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    access_frequencies[key] = 1
    last_access_times[key] = cache_snapshot.access_count
    predictive_scores[key] = INITIAL_PREDICTIVE_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the Predictive Scores of remaining objects, adjusting their DRI and ARS to reflect the new cache state, and updates the structured prioritization to maintain optimal cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in predictive_scores:
        del predictive_scores[evicted_key]
        del access_frequencies[evicted_key]
        del last_access_times[evicted_key]
    
    # Decay the predictive scores of remaining objects
    for key in cache_snapshot.cache:
        predictive_scores[key] *= DECAY_FACTOR