# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_SCORE = 1.0
LATENCY_WEIGHT = 0.5
FREQUENCY_WEIGHT = 0.3
RECENCY_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive score for each cache entry, calculated using a combination of historical access patterns, access latency, and a dynamic scaling factor that adjusts based on current system load. It also tracks a usage profile for each entry, which includes frequency and recency of access.
predictive_scores = defaultdict(lambda: BASELINE_SCORE)
usage_profiles = defaultdict(lambda: {'frequency': 0, 'recency': 0})
dynamic_scaling_factor = 1.0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest predictive score, which indicates the least likelihood of being accessed soon. This score is dynamically adjusted to prioritize entries with higher access latency and lower usage profiles.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = predictive_scores[key]
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the predictive score of the accessed entry by updating its usage profile to reflect increased frequency and recency. The dynamic scaling factor is also adjusted to reflect the current system load, ensuring the score remains relevant.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    usage_profiles[key]['frequency'] += 1
    usage_profiles[key]['recency'] = cache_snapshot.access_count
    
    # Update predictive score
    predictive_scores[key] = (
        LATENCY_WEIGHT * obj.size +
        FREQUENCY_WEIGHT * usage_profiles[key]['frequency'] +
        RECENCY_WEIGHT * usage_profiles[key]['recency']
    ) * dynamic_scaling_factor

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its predictive score based on initial access latency and a baseline usage profile. The dynamic scaling factor is recalibrated to account for the new entry, ensuring balanced cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    usage_profiles[key] = {'frequency': 1, 'recency': cache_snapshot.access_count}
    
    # Initialize predictive score
    predictive_scores[key] = (
        LATENCY_WEIGHT * obj.size +
        FREQUENCY_WEIGHT * usage_profiles[key]['frequency'] +
        RECENCY_WEIGHT * usage_profiles[key]['recency']
    ) * dynamic_scaling_factor

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the dynamic scaling factor to reflect the reduced cache load. It also updates the usage profiles of remaining entries to ensure their predictive scores accurately represent their current likelihood of access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Recalibrate dynamic scaling factor
    dynamic_scaling_factor = cache_snapshot.size / cache_snapshot.capacity
    
    # Update predictive scores for remaining entries
    for key, cached_obj in cache_snapshot.cache.items():
        usage_profiles[key]['recency'] = cache_snapshot.access_count
        predictive_scores[key] = (
            LATENCY_WEIGHT * cached_obj.size +
            FREQUENCY_WEIGHT * usage_profiles[key]['frequency'] +
            RECENCY_WEIGHT * usage_profiles[key]['recency']
        ) * dynamic_scaling_factor