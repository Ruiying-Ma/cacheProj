# Import anything you need below
from collections import defaultdict
import math

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for access frequency
BETA = 0.3   # Weight for recency
GAMMA = 0.2  # Weight for synergy calibration
DELTA = 0.1  # Weight for algorithmic forecast

# Put the metadata specifically maintained by the policy below. The policy maintains an efficiency parameter for each cache entry, which is a composite score derived from access frequency, recency, and a synergy calibration factor that measures the entry's interaction with other cache entries. Additionally, an algorithmic forecast value predicts future access patterns based on historical data.
efficiency_params = defaultdict(lambda: {'frequency': 0, 'recency': 0, 'synergy': 0, 'forecast': 0})

def calculate_efficiency(key):
    params = efficiency_params[key]
    return (ALPHA * params['frequency'] +
            BETA * params['recency'] +
            GAMMA * params['synergy'] -
            DELTA * params['forecast'])

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest efficiency parameter, adjusted by the algorithmic forecast. This ensures that entries with low current utility and low predicted future utility are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_efficiency = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        efficiency = calculate_efficiency(key)
        if efficiency < min_efficiency:
            min_efficiency = efficiency
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the efficiency parameter of the accessed entry is increased, reflecting its increased utility. The synergy calibration is adjusted based on the entry's interaction with other recently accessed entries, and the algorithmic forecast is updated to reflect the new access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    efficiency_params[key]['frequency'] += 1
    efficiency_params[key]['recency'] = cache_snapshot.access_count
    # Update synergy calibration
    for other_key in cache_snapshot.cache:
        if other_key != key:
            efficiency_params[other_key]['synergy'] += 1
    # Update algorithmic forecast
    efficiency_params[key]['forecast'] = math.log(1 + efficiency_params[key]['frequency'])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its efficiency parameter based on initial access expectations and synergy calibration with existing entries. The algorithmic forecast is updated to incorporate the new entry's potential impact on future access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    efficiency_params[key]['frequency'] = 1
    efficiency_params[key]['recency'] = cache_snapshot.access_count
    # Initialize synergy calibration
    for other_key in cache_snapshot.cache:
        if other_key != key:
            efficiency_params[other_key]['synergy'] += 1
    # Initialize algorithmic forecast
    efficiency_params[key]['forecast'] = 0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the synergy factors of remaining entries to account for the removed entry's absence. The algorithmic forecast is adjusted to reflect the change in cache composition, ensuring future predictions remain accurate.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Recalibrate synergy factors
    for key in cache_snapshot.cache:
        efficiency_params[key]['synergy'] = max(0, efficiency_params[key]['synergy'] - 1)
    # Adjust algorithmic forecast
    for key in cache_snapshot.cache:
        efficiency_params[key]['forecast'] = math.log(1 + efficiency_params[key]['frequency'])
    # Remove evicted object's metadata
    if evicted_key in efficiency_params:
        del efficiency_params[evicted_key]