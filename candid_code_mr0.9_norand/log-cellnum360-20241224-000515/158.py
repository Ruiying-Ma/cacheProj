# Import anything you need below
from collections import defaultdict
import math

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.5
RECENCY_WEIGHT = 0.3
PREDICTIVE_WEIGHT = 0.2
FREQUENCY_SCALING_FACTOR = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a dynamic priority score for each cache entry, which is calculated based on access frequency, recency, and a predictive score derived from historical access patterns. It also tracks a frequency scaling factor that adjusts the weight of recent accesses over time.
access_frequency = defaultdict(int)
last_access_time = {}
dynamic_priority_score = {}
predictive_model = defaultdict(float)

def calculate_priority_score(key, current_time):
    frequency_score = access_frequency[key] * FREQUENCY_SCALING_FACTOR
    recency_score = 1 / (current_time - last_access_time[key] + 1)
    predictive_score = predictive_model[key]
    return (FREQUENCY_WEIGHT * frequency_score +
            RECENCY_WEIGHT * recency_score +
            PREDICTIVE_WEIGHT * predictive_score)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the cache entry with the lowest dynamic priority score. This score is recalculated periodically to reflect changes in access patterns and predictive analytics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_priority_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = calculate_priority_score(key, cache_snapshot.access_count)
        if score < min_priority_score:
            min_priority_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency of the entry is incremented, and the dynamic priority score is recalculated using the updated frequency and recency data. The frequency scaling factor is adjusted to give more weight to recent accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] += 1
    last_access_time[key] = cache_snapshot.access_count
    dynamic_priority_score[key] = calculate_priority_score(key, cache_snapshot.access_count)
    global FREQUENCY_SCALING_FACTOR
    FREQUENCY_SCALING_FACTOR *= 1.01  # Slightly increase to give more weight to recent accesses

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency and recency data, and calculates an initial dynamic priority score using predictive analytics based on similar past entries. The frequency scaling factor is updated to reflect the current cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] = 1
    last_access_time[key] = cache_snapshot.access_count
    # Initialize predictive score based on historical data
    predictive_model[key] = predictive_model.get(key, 0.5)  # Default predictive score
    dynamic_priority_score[key] = calculate_priority_score(key, cache_snapshot.access_count)
    global FREQUENCY_SCALING_FACTOR
    FREQUENCY_SCALING_FACTOR = max(1.0, FREQUENCY_SCALING_FACTOR * 0.99)  # Adjust scaling factor

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the frequency scaling factor to ensure it remains balanced with the current cache size and access patterns. It also updates the predictive model with data from the evicted entry to improve future predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    # Update predictive model with evicted entry data
    predictive_model[key] = dynamic_priority_score[key]
    # Recalibrate frequency scaling factor
    global FREQUENCY_SCALING_FACTOR
    FREQUENCY_SCALING_FACTOR = max(1.0, FREQUENCY_SCALING_FACTOR * 0.98)  # Adjust scaling factor