# Import anything you need below
import math
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_QFI = 1.0
INITIAL_ASS = 1.0
INITIAL_EFB = 1.0
INITIAL_PMC = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a Quantum Flux Index (QFI) for each cache entry, an Adaptive Signal Strength (ASS) value, an Entropic Frequency Bias (EFB) score, and a Predictive Modulation Coefficient (PMC). QFI tracks the quantum-like behavior of access patterns, ASS adapts to the signal strength of access frequency, EFB measures the entropy of access intervals, and PMC predicts future access likelihood.
metadata = defaultdict(lambda: {
    'QFI': BASELINE_QFI,
    'ASS': INITIAL_ASS,
    'EFB': INITIAL_EFB,
    'PMC': INITIAL_PMC,
    'last_access': 0
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest combined score of QFI, ASS, EFB, and PMC. This ensures that entries with the least potential for future access are evicted, balancing between recent access patterns and predicted future needs.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        qfi = metadata[key]['QFI']
        ass = metadata[key]['ASS']
        efb = metadata[key]['EFB']
        pmc = metadata[key]['PMC']
        
        score = qfi + ass + efb + pmc
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the QFI is incremented to reflect increased access probability, the ASS is adjusted based on the current access frequency, the EFB is recalculated to account for the new access interval, and the PMC is updated using a predictive model to enhance future access likelihood estimation.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata[key]['QFI'] += 1
    metadata[key]['ASS'] = 1 / (cache_snapshot.access_count - metadata[key]['last_access'] + 1)
    metadata[key]['EFB'] = -math.log(metadata[key]['ASS'])
    metadata[key]['PMC'] = metadata[key]['QFI'] * metadata[key]['ASS']
    metadata[key]['last_access'] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the QFI is initialized to a baseline value, the ASS is set based on initial access frequency assumptions, the EFB is calculated using initial entropy estimates, and the PMC is initialized using historical data patterns to predict future access potential.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata[key] = {
        'QFI': BASELINE_QFI,
        'ASS': INITIAL_ASS,
        'EFB': INITIAL_EFB,
        'PMC': INITIAL_PMC,
        'last_access': cache_snapshot.access_count
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the QFI of remaining entries is recalibrated to reflect the new cache state, the ASS is adjusted to account for the change in cache dynamics, the EFB is updated to reflect the altered entropy landscape, and the PMC is recalculated to refine future access predictions based on the new cache composition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    del metadata[evicted_obj.key]
    
    for key in cache_snapshot.cache:
        metadata[key]['QFI'] *= 0.9
        metadata[key]['ASS'] *= 1.1
        metadata[key]['EFB'] = -math.log(metadata[key]['ASS'])
        metadata[key]['PMC'] = metadata[key]['QFI'] * metadata[key]['ASS']