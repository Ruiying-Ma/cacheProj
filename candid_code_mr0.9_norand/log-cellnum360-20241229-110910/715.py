# Import anything you need below
import math
from collections import defaultdict

# Put tunable constant parameters below
TEMPORAL_DECAY_INITIAL = 1.0
PREDICTIVE_SCORE_INITIAL = 0.5
ENTROPY_INITIAL = 0.0

# Put the metadata specifically maintained by the policy below. The policy maintains a quantum sequence index for each cache entry, a predictive score based on access patterns, a temporal decay factor, and an entropy measure of access frequency distribution.
quantum_sequence_index = {}
predictive_score = {}
temporal_decay = {}
access_frequency = defaultdict(int)
entropy = ENTROPY_INITIAL

def calculate_entropy():
    total_accesses = sum(access_frequency.values())
    if total_accesses == 0:
        return 0.0
    entropy = 0.0
    for freq in access_frequency.values():
        probability = freq / total_accesses
        if probability > 0:
            entropy -= probability * math.log2(probability)
    return entropy

def calculate_composite_score(key):
    qsi = quantum_sequence_index.get(key, 0)
    ps = predictive_score.get(key, PREDICTIVE_SCORE_INITIAL)
    td = temporal_decay.get(key, TEMPORAL_DECAY_INITIAL)
    return qsi + ps + td + entropy

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by calculating a composite score for each entry, which is a fusion of the quantum sequence index, predictive score, temporal decay, and entropy. The entry with the lowest composite score is chosen for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key in cache_snapshot.cache:
        score = calculate_composite_score(key)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the quantum sequence index is updated to reflect the new access order, the predictive score is adjusted based on recent access patterns, the temporal decay factor is reset, and the entropy measure is recalculated to account for the change in access frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    quantum_sequence_index[key] = cache_snapshot.access_count
    predictive_score[key] = min(1.0, predictive_score.get(key, PREDICTIVE_SCORE_INITIAL) + 0.1)
    temporal_decay[key] = TEMPORAL_DECAY_INITIAL
    access_frequency[key] += 1
    global entropy
    entropy = calculate_entropy()

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the quantum sequence index is initialized, the predictive score is set based on initial access predictions, the temporal decay factor is set to its initial state, and the entropy measure is updated to include the new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    quantum_sequence_index[key] = cache_snapshot.access_count
    predictive_score[key] = PREDICTIVE_SCORE_INITIAL
    temporal_decay[key] = TEMPORAL_DECAY_INITIAL
    access_frequency[key] += 1
    global entropy
    entropy = calculate_entropy()

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the quantum sequence indices of remaining entries are adjusted, the predictive scores are recalibrated to reflect the new cache state, the temporal decay factors are updated, and the entropy measure is recalculated to exclude the evicted entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in quantum_sequence_index:
        del quantum_sequence_index[evicted_key]
    if evicted_key in predictive_score:
        del predictive_score[evicted_key]
    if evicted_key in temporal_decay:
        del temporal_decay[evicted_key]
    if evicted_key in access_frequency:
        del access_frequency[evicted_key]
    
    global entropy
    entropy = calculate_entropy()