# Import anything you need below
import math
from collections import defaultdict

# Put tunable constant parameters below
DEFAULT_ENTROPIC_VARIANCE = 1.0
INITIAL_FORECAST_SCORE = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains a forecast score for each cache entry, calculated using algorithmic forecasting and data interpolation based on past access patterns. It also tracks the entropic variance of access intervals to measure unpredictability.
forecast_scores = defaultdict(lambda: INITIAL_FORECAST_SCORE)
entropic_variances = defaultdict(lambda: DEFAULT_ENTROPIC_VARIANCE)
last_access_times = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest forecast score, indicating the least likelihood of being accessed soon, while also considering entries with high entropic variance as potential candidates for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = forecast_scores[key] - entropic_variances[key]
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy recalculates the forecast score for the accessed entry using updated access data and adjusts the entropic variance to reflect the new access interval.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    key = obj.key
    
    if key in last_access_times:
        interval = current_time - last_access_times[key]
        entropic_variances[key] = math.log(interval + 1)
    
    forecast_scores[key] = 1 / (1 + entropic_variances[key])
    last_access_times[key] = current_time

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its forecast score based on initial access predictions and sets its entropic variance to a default value, which will be adjusted as more access data becomes available.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    forecast_scores[key] = INITIAL_FORECAST_SCORE
    entropic_variances[key] = DEFAULT_ENTROPIC_VARIANCE
    last_access_times[key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the forecast scores and entropic variances of remaining entries to account for the changed cache state, ensuring that predictions remain accurate and relevant.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in forecast_scores:
        del forecast_scores[evicted_key]
    if evicted_key in entropic_variances:
        del entropic_variances[evicted_key]
    if evicted_key in last_access_times:
        del last_access_times[evicted_key]
    
    # Recalibrate scores and variances for remaining entries
    for key in cache_snapshot.cache:
        forecast_scores[key] *= 0.9  # Example recalibration factor
        entropic_variances[key] *= 0.9  # Example recalibration factor