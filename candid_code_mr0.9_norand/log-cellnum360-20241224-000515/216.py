# Import anything you need below
from collections import defaultdict
import math

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for access frequency
BETA = 0.3   # Weight for recency
GAMMA = 0.1  # Weight for size
DELTA = 0.1  # Weight for dynamic quota

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency of access, object size, and a dynamic quota for each object type. It also tracks a load response score that adjusts based on system load and access patterns.
access_frequency = defaultdict(int)
recency = {}
dynamic_quota = defaultdict(float)
load_response_score = 1.0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by evaluating objects against a composite score derived from their access frequency, recency, size, and type quota. Objects with the lowest score, indicating low importance and high cost, are evicted first.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        freq = access_frequency[key]
        rec = recency[key]
        size = cached_obj.size
        quota = dynamic_quota[cached_obj.key]
        
        score = (ALPHA * freq) + (BETA * rec) - (GAMMA * size) - (DELTA * quota)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency and recency for the object are updated. The load response score is adjusted to reflect the current system load, potentially altering the dynamic quota for the object type.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    access_frequency[obj.key] += 1
    recency[obj.key] = cache_snapshot.access_count
    
    # Adjust load response score
    load_response_score = cache_snapshot.hit_count / (cache_snapshot.hit_count + cache_snapshot.miss_count)
    
    # Update dynamic quota
    dynamic_quota[obj.key] = load_response_score * (cache_snapshot.size / cache_snapshot.capacity)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy updates the object's initial access frequency and recency. It also recalculates the dynamic quota for the object type based on the current load response score and overall cache usage.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    access_frequency[obj.key] = 1
    recency[obj.key] = cache_snapshot.access_count
    
    # Update dynamic quota
    dynamic_quota[obj.key] = load_response_score * (cache_snapshot.size / cache_snapshot.capacity)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the dynamic quota for the affected object type, taking into account the updated load response score and the freed cache space. It also adjusts the load response score to reflect the change in system load.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Adjust load response score
    load_response_score = cache_snapshot.hit_count / (cache_snapshot.hit_count + cache_snapshot.miss_count)
    
    # Recalculate dynamic quota for the evicted object type
    dynamic_quota[evicted_obj.key] = load_response_score * (cache_snapshot.size / cache_snapshot.capacity)