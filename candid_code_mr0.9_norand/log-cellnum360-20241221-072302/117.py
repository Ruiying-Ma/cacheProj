# Import anything you need below
import math

# Put tunable constant parameters below
BASELINE_ACCESS_FREQUENCY = 1
INITIAL_PREDICTED_FUTURE_ACCESS = 10
RESOURCE_USAGE_WEIGHT = 0.5
ACCESS_FREQUENCY_WEIGHT = 0.3
PREDICTED_FUTURE_ACCESS_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, predicted future access time, and resource usage patterns. It also tracks a dynamic priority score for each cache entry based on these factors.
metadata = {}

def calculate_priority_score(obj_key):
    data = metadata[obj_key]
    return (RESOURCE_USAGE_WEIGHT * data['resource_usage'] +
            ACCESS_FREQUENCY_WEIGHT * data['access_frequency'] +
            PREDICTED_FUTURE_ACCESS_WEIGHT * data['predicted_future_access'])

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache entry, which combines the predicted future access time, current access frequency, and resource usage. The entry with the lowest score is selected for eviction, allowing the cache to adaptively scale resources and prioritize entries with higher predicted utility.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = math.inf
    
    for key in cache_snapshot.cache:
        score = calculate_priority_score(key)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the last access timestamp and increments the access frequency for the hit entry. It also recalculates the predicted future access time using temporal analytics, adjusting the dynamic priority score accordingly.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    data = metadata[obj.key]
    data['last_access_timestamp'] = cache_snapshot.access_count
    data['access_frequency'] += 1
    # Recalculate predicted future access time (simple model for demonstration)
    data['predicted_future_access'] = data['access_frequency'] + 5

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its metadata with a baseline access frequency, current timestamp, and an initial prediction for future access. The dynamic priority score is set based on these initial values, allowing the entry to compete fairly with existing entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    metadata[obj.key] = {
        'access_frequency': BASELINE_ACCESS_FREQUENCY,
        'last_access_timestamp': cache_snapshot.access_count,
        'predicted_future_access': INITIAL_PREDICTED_FUTURE_ACCESS,
        'resource_usage': obj.size
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy adjusts the resource usage patterns to reflect the freed resources. It also recalibrates the priority scores of remaining entries to ensure optimal resource scaling and predictive caching efficiency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Remove metadata of evicted object
    if evicted_obj.key in metadata:
        del metadata[evicted_obj.key]
    
    # Recalibrate priority scores (simple recalibration for demonstration)
    for key in metadata:
        data = metadata[key]
        data['resource_usage'] = cache_snapshot.cache[key].size