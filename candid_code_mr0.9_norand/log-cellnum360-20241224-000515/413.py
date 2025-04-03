# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for access frequency
BETA = 0.3   # Weight for recency
GAMMA = 0.2  # Weight for proactive score

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency of access, and a proactive score that predicts future access patterns based on historical data. It also tracks a balance factor that ensures a mix of frequently and recently accessed items.
access_frequency = defaultdict(int)
recency = defaultdict(int)
proactive_score = defaultdict(float)
balance_factor = 1.0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each item, which integrates access frequency, recency, and the proactive score. The item with the lowest composite score, adjusted by the balance factor, is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        composite_score = (ALPHA * access_frequency[key] +
                           BETA * recency[key] +
                           GAMMA * proactive_score[key]) * balance_factor
        if composite_score < min_score:
            min_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency and recency of the accessed item are updated. The proactive score is recalibrated using recent access patterns, and the balance factor is adjusted to reflect the current cache dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    access_frequency[obj.key] += 1
    recency[obj.key] = cache_snapshot.access_count
    proactive_score[obj.key] = (access_frequency[obj.key] + recency[obj.key]) / 2
    # Adjust balance factor based on current cache dynamics
    balance_factor = 1 + (cache_snapshot.hit_count / (cache_snapshot.miss_count + 1))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency and recency to default values, assigns a proactive score based on initial predictions, and recalibrates the balance factor to maintain cache diversity.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    access_frequency[obj.key] = 1
    recency[obj.key] = cache_snapshot.access_count
    proactive_score[obj.key] = (access_frequency[obj.key] + recency[obj.key]) / 2
    # Recalibrate balance factor
    balance_factor = 1 + (cache_snapshot.hit_count / (cache_snapshot.miss_count + 1))

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy updates the balance factor to account for the removed item, recalibrates the proactive scores of remaining items to reflect the new cache state, and adjusts access frequency and recency metrics to maintain cache efficiency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Remove metadata of evicted object
    del access_frequency[evicted_obj.key]
    del recency[evicted_obj.key]
    del proactive_score[evicted_obj.key]
    
    # Recalibrate proactive scores for remaining items
    for key in cache_snapshot.cache:
        proactive_score[key] = (access_frequency[key] + recency[key]) / 2
    
    # Adjust balance factor
    balance_factor = 1 + (cache_snapshot.hit_count / (cache_snapshot.miss_count + 1))