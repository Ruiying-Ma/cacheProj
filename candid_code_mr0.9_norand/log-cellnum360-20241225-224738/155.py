# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.4
RECENCY_WEIGHT = 0.4
CONTEXTUAL_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains a dynamic priority score for each cache entry, which is calculated using a combination of access frequency, recency, and contextual relevance. It also tracks a contextual profile of access patterns to adapt to shifts in workload behavior.
priority_scores = defaultdict(lambda: 0)
access_frequencies = defaultdict(lambda: 0)
last_access_times = defaultdict(lambda: 0)
contextual_profile = defaultdict(lambda: 0)

def calculate_priority_score(key, current_time):
    frequency_score = access_frequencies[key]
    recency_score = current_time - last_access_times[key]
    contextual_score = contextual_profile[key]
    return (FREQUENCY_WEIGHT * frequency_score) - (RECENCY_WEIGHT * recency_score) + (CONTEXTUAL_WEIGHT * contextual_score)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the cache entry with the lowest dynamic priority score, ensuring that entries with higher contextual relevance and recent access are retained. It periodically reassesses the contextual profile to adjust the weight of each factor in the priority score.
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
    Upon a cache hit, the policy increases the priority score of the accessed entry by boosting its recency and frequency components. It also updates the contextual profile to reflect the current access pattern, allowing the system to adapt to changes in workload behavior.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    access_frequencies[key] += 1
    last_access_times[key] = cache_snapshot.access_count
    priority_scores[key] = calculate_priority_score(key, cache_snapshot.access_count)
    contextual_profile[key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its priority score based on the current contextual profile, giving it a baseline relevance. The contextual profile is updated to account for the new entry, ensuring the cache adapts to the evolving access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    access_frequencies[key] = 1
    last_access_times[key] = cache_snapshot.access_count
    priority_scores[key] = calculate_priority_score(key, cache_snapshot.access_count)
    contextual_profile[key] += 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the contextual profile to reduce the weight of the evicted entry's characteristics, promoting a more accurate reflection of the current workload. It also adjusts the priority scores of remaining entries to maintain a balanced cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in contextual_profile:
        del contextual_profile[evicted_key]
    
    for key in cache_snapshot.cache:
        priority_scores[key] = calculate_priority_score(key, cache_snapshot.access_count)