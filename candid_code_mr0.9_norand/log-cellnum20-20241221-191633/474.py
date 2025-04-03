# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_FREQUENCY = 1
NEUTRAL_CONSISTENCY_SCORE = 0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a temporal access pattern score for each cache entry, a predictive access frequency model, an adaptive iteration counter for recent access trends, and a consistency score indicating the stability of access patterns.
temporal_access_pattern_score = defaultdict(int)
predictive_access_frequency = defaultdict(lambda: BASELINE_FREQUENCY)
adaptive_iteration_counter = defaultdict(int)
consistency_score = defaultdict(lambda: NEUTRAL_CONSISTENCY_SCORE)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest combined score of temporal access pattern and predictive access frequency, adjusted by the consistency score to ensure stable patterns are favored.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (temporal_access_pattern_score[key] + 
                          predictive_access_frequency[key] - 
                          consistency_score[key])
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the temporal access pattern score is incremented, the predictive model is updated to reflect increased likelihood of future access, and the consistency score is adjusted to reflect the stability of the access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    temporal_access_pattern_score[key] += 1
    predictive_access_frequency[key] += 1
    consistency_score[key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the temporal access pattern score is initialized, the predictive model is updated to include the new entry with a baseline frequency, and the consistency score is set to a neutral value to allow for adaptive learning.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    temporal_access_pattern_score[key] = 0
    predictive_access_frequency[key] = BASELINE_FREQUENCY
    consistency_score[key] = NEUTRAL_CONSISTENCY_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the adaptive iteration counter is reset for the evicted entry, and the consistency model is updated to reflect the change in cache composition, potentially adjusting scores of remaining entries to maintain balance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    adaptive_iteration_counter[evicted_key] = 0
    del temporal_access_pattern_score[evicted_key]
    del predictive_access_frequency[evicted_key]
    del consistency_score[evicted_key]
    
    # Adjust consistency scores of remaining entries
    for key in cache_snapshot.cache:
        consistency_score[key] = max(0, consistency_score[key] - 1)