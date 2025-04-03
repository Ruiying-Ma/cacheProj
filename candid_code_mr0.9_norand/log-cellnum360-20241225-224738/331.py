# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 1.0
RECENCY_WEIGHT = 1.0
SIZE_WEIGHT = 1.0
ALGORITHM_VARIANCE_WEIGHT = 0.5
STRUCTURAL_INTEGRITY_WEIGHT = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains a 'Data Efficacy Score' for each cache entry, calculated using a Quantitative Mesh that considers access frequency, recency, and data size. Additionally, it tracks an 'Algorithmic Variance' metric to measure the predictability of access patterns, and a 'Structural Integrity' index to ensure cache stability and balance.
data_efficacy_scores = defaultdict(float)
access_frequencies = defaultdict(int)
last_access_times = defaultdict(int)
algorithmic_variance = 0.0
structural_integrity = 0.0

def calculate_data_efficacy_score(obj, current_time):
    frequency_score = FREQUENCY_WEIGHT * access_frequencies[obj.key]
    recency_score = RECENCY_WEIGHT * (current_time - last_access_times[obj.key])
    size_score = SIZE_WEIGHT * obj.size
    return frequency_score + recency_score - size_score

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest Data Efficacy Score, while also considering the Algorithmic Variance to avoid evicting entries that might become highly relevant soon. The Structural Integrity index is used to ensure that evictions do not destabilize the cache's balance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = data_efficacy_scores[key] + ALGORITHM_VARIANCE_WEIGHT * algorithmic_variance + STRUCTURAL_INTEGRITY_WEIGHT * structural_integrity
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Data Efficacy Score of the accessed entry is increased based on its recency and frequency of access. The Algorithmic Variance is recalculated to reflect the updated access pattern, and the Structural Integrity index is adjusted to maintain cache balance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    access_frequencies[obj.key] += 1
    last_access_times[obj.key] = cache_snapshot.access_count
    data_efficacy_scores[obj.key] = calculate_data_efficacy_score(obj, cache_snapshot.access_count)
    # Recalculate Algorithmic Variance and Structural Integrity
    algorithmic_variance = sum(data_efficacy_scores.values()) / len(data_efficacy_scores)
    structural_integrity = 1.0  # Placeholder for actual structural integrity calculation

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial Data Efficacy Score based on predicted access patterns. The Algorithmic Variance is updated to incorporate the new entry's potential impact on access predictability, and the Structural Integrity index is recalibrated to accommodate the new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    access_frequencies[obj.key] = 1
    last_access_times[obj.key] = cache_snapshot.access_count
    data_efficacy_scores[obj.key] = calculate_data_efficacy_score(obj, cache_snapshot.access_count)
    # Update Algorithmic Variance and Structural Integrity
    algorithmic_variance = sum(data_efficacy_scores.values()) / len(data_efficacy_scores)
    structural_integrity = 1.0  # Placeholder for actual structural integrity calculation

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalculates the Data Efficacy Scores of remaining entries to reflect the changed cache landscape. The Algorithmic Variance is updated to account for the removal's effect on access patterns, and the Structural Integrity index is adjusted to ensure continued cache stability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    if evicted_obj.key in data_efficacy_scores:
        del data_efficacy_scores[evicted_obj.key]
        del access_frequencies[evicted_obj.key]
        del last_access_times[evicted_obj.key]
    
    # Recalculate Data Efficacy Scores for remaining entries
    for key in cache_snapshot.cache:
        data_efficacy_scores[key] = calculate_data_efficacy_score(cache_snapshot.cache[key], cache_snapshot.access_count)
    
    # Update Algorithmic Variance and Structural Integrity
    algorithmic_variance = sum(data_efficacy_scores.values()) / len(data_efficacy_scores)
    structural_integrity = 1.0  # Placeholder for actual structural integrity calculation