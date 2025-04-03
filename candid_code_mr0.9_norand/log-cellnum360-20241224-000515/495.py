# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_ACCESS_PROBABILITY = 0.5
FREQUENCY_WEIGHT = 0.4
RECENCY_WEIGHT = 0.3
PREDICTIVE_WEIGHT = 0.3

# Put the metadata specifically maintained by the policy below. The policy maintains a harmonized dataset of access patterns, predictive layers for future access probabilities, and a cognitive synthesis score for each cache entry, refined through algorithmic adjustments.
access_frequency = defaultdict(int)
last_access_time = {}
predictive_access_probability = defaultdict(lambda: INITIAL_ACCESS_PROBABILITY)
cognitive_synthesis_score = {}

def calculate_cognitive_synthesis_score(key, current_time):
    frequency_score = access_frequency[key]
    recency_score = current_time - last_access_time[key]
    predictive_score = predictive_access_probability[key]
    return (FREQUENCY_WEIGHT * frequency_score) - (RECENCY_WEIGHT * recency_score) + (PREDICTIVE_WEIGHT * predictive_score)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest cognitive synthesis score, which is calculated by combining historical access frequency, recency, and predicted future access likelihood.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    current_time = cache_snapshot.access_count
    for key in cache_snapshot.cache:
        score = calculate_cognitive_synthesis_score(key, current_time)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access pattern dataset is updated to reflect the new access, the predictive layers are adjusted to increase the future access probability of the hit entry, and the cognitive synthesis score is recalculated to reflect these changes.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    current_time = cache_snapshot.access_count
    access_frequency[key] += 1
    last_access_time[key] = current_time
    predictive_access_probability[key] = min(1.0, predictive_access_probability[key] + 0.1)
    cognitive_synthesis_score[key] = calculate_cognitive_synthesis_score(key, current_time)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the access pattern dataset is initialized for the new entry, predictive layers are set based on initial access assumptions, and a baseline cognitive synthesis score is assigned.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    current_time = cache_snapshot.access_count
    access_frequency[key] = 1
    last_access_time[key] = current_time
    predictive_access_probability[key] = INITIAL_ACCESS_PROBABILITY
    cognitive_synthesis_score[key] = calculate_cognitive_synthesis_score(key, current_time)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the access pattern dataset is purged of the evicted entry's data, predictive layers are recalibrated to account for the reduced cache size, and cognitive synthesis scores are adjusted for remaining entries to reflect the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    del access_frequency[evicted_key]
    del last_access_time[evicted_key]
    del predictive_access_probability[evicted_key]
    del cognitive_synthesis_score[evicted_key]
    
    current_time = cache_snapshot.access_count
    for key in cache_snapshot.cache:
        cognitive_synthesis_score[key] = calculate_cognitive_synthesis_score(key, current_time)