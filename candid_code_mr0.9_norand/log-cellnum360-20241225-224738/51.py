# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.4
RECENCY_WEIGHT = 0.4
PREDICTION_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains an efficiency index for each cache entry, which is a composite score based on access frequency, recency, and predicted future access patterns. It also tracks adaptive allocation metrics to dynamically adjust cache space for different data types, and load forecasting metrics to predict future cache demand.
efficiency_index = defaultdict(lambda: 0)
access_frequency = defaultdict(lambda: 0)
last_access_time = defaultdict(lambda: 0)
predicted_access = defaultdict(lambda: 0)
adaptive_allocation = defaultdict(lambda: 0)
load_forecasting = defaultdict(lambda: 0)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest efficiency index, ensuring that entries with low predicted future utility are removed first. It also considers adaptive allocation to ensure balanced resource distribution across data types.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_efficiency = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        index = efficiency_index[key]
        if index < min_efficiency:
            min_efficiency = index
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the efficiency index of the accessed entry is increased based on its current frequency and recency of access. Load forecasting metrics are updated to reflect the current access pattern, improving future predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    access_frequency[obj.key] += 1
    last_access_time[obj.key] = cache_snapshot.access_count
    efficiency_index[obj.key] = (FREQUENCY_WEIGHT * access_frequency[obj.key] +
                                 RECENCY_WEIGHT * last_access_time[obj.key] +
                                 PREDICTION_WEIGHT * predicted_access[obj.key])
    load_forecasting[obj.key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its efficiency index based on initial access predictions and updates adaptive allocation metrics to reflect the new distribution of data types. Load forecasting is adjusted to account for the new entry's potential impact on future demand.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    access_frequency[obj.key] = 1
    last_access_time[obj.key] = cache_snapshot.access_count
    predicted_access[obj.key] = 1  # Initial prediction
    efficiency_index[obj.key] = (FREQUENCY_WEIGHT * access_frequency[obj.key] +
                                 RECENCY_WEIGHT * last_access_time[obj.key] +
                                 PREDICTION_WEIGHT * predicted_access[obj.key])
    adaptive_allocation[obj.key] = obj.size
    load_forecasting[obj.key] = 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the efficiency indices of remaining entries to ensure balance and updates adaptive allocation metrics to reflect the freed space. Load forecasting is adjusted to improve future eviction decisions based on current cache dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    del efficiency_index[evicted_obj.key]
    del access_frequency[evicted_obj.key]
    del last_access_time[evicted_obj.key]
    del predicted_access[evicted_obj.key]
    del adaptive_allocation[evicted_obj.key]
    del load_forecasting[evicted_obj.key]
    
    for key in cache_snapshot.cache:
        efficiency_index[key] = (FREQUENCY_WEIGHT * access_frequency[key] +
                                 RECENCY_WEIGHT * last_access_time[key] +
                                 PREDICTION_WEIGHT * predicted_access[key])