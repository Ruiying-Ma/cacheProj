# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
ALPHA = 0.7  # Weight for recency in resilience score
BETA = 0.3   # Weight for frequency in resilience score

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency, load distribution across cache lines, and a predictive resilience score for each cache entry. The resilience score predicts the likelihood of future accesses based on historical patterns.
access_frequency = defaultdict(int)
recency = {}
resilience_score = {}
load_distribution = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying entries with the lowest predictive resilience score, while also considering load distribution to ensure balanced cache usage. It aims to evict entries that are least likely to be accessed soon and are contributing to uneven load distribution.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = resilience_score[key] / (1 + load_distribution[key])
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency and recency of the accessed entry are updated. The predictive resilience score is recalculated using the updated access patterns, and load distribution metrics are adjusted to reflect the current state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] += 1
    recency[key] = cache_snapshot.access_count
    resilience_score[key] = ALPHA * recency[key] + BETA * access_frequency[key]
    load_distribution[key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency and recency. The predictive resilience score is set based on initial access patterns, and load distribution metrics are updated to account for the new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] = 1
    recency[key] = cache_snapshot.access_count
    resilience_score[key] = ALPHA * recency[key] + BETA * access_frequency[key]
    load_distribution[key] = 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates load distribution metrics to reflect the removal. It also adjusts the predictive resilience scores of remaining entries to ensure stability and continuous adaptation to changing access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del access_frequency[evicted_key]
    del recency[evicted_key]
    del resilience_score[evicted_key]
    del load_distribution[evicted_key]
    
    # Recalibrate load distribution and resilience scores
    for key in cache_snapshot.cache:
        load_distribution[key] = max(1, load_distribution[key] - 1)
        resilience_score[key] = ALPHA * recency[key] + BETA * access_frequency[key]