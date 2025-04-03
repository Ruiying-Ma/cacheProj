# Import anything you need below
import math
from collections import defaultdict

# Put tunable constant parameters below
BASE_EDV = 1.0
ACCESS_FREQUENCY_WEIGHT = 1.0
RECENCY_WEIGHT = 1.0
QHI_WEIGHT = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a Tensor Fusion Matrix (TFM) that combines access frequency, recency, and a Quantum Harmonics Index (QHI) for each cache entry. It also tracks an Entropic Decay Value (EDV) that models the temporal relevance of each entry.
tfm = defaultdict(lambda: {'access_frequency': 0, 'recency': 0, 'qhi': 0, 'edv': BASE_EDV})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest combined score from the TFM and EDV, ensuring that entries with low access frequency, recency, and quantum harmonics are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        tfm_entry = tfm[key]
        score = (ACCESS_FREQUENCY_WEIGHT * tfm_entry['access_frequency'] +
                 RECENCY_WEIGHT * tfm_entry['recency'] +
                 QHI_WEIGHT * tfm_entry['qhi'] +
                 tfm_entry['edv'])
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the TFM by increasing the access frequency and recency components for the accessed entry, recalculates the QHI based on the recursive synthesis loop, and adjusts the EDV to reflect increased temporal relevance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    tfm_entry = tfm[obj.key]
    tfm_entry['access_frequency'] += 1
    tfm_entry['recency'] = cache_snapshot.access_count
    tfm_entry['qhi'] = math.log1p(tfm_entry['access_frequency'] * tfm_entry['recency'])
    tfm_entry['edv'] *= 0.9  # Decay the EDV to reflect increased relevance

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its TFM with default values, computes an initial QHI using the tensor fusion algorithm, and sets the EDV to a baseline level to start tracking its temporal relevance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    tfm[obj.key] = {
        'access_frequency': 1,
        'recency': cache_snapshot.access_count,
        'qhi': math.log1p(1 * cache_snapshot.access_count),
        'edv': BASE_EDV
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the TFM for remaining entries to account for the removal, updates the QHI to reflect the new cache state, and adjusts the EDV to maintain balance in temporal relevance across the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    del tfm[evicted_obj.key]
    
    for key in cache_snapshot.cache:
        tfm_entry = tfm[key]
        tfm_entry['qhi'] = math.log1p(tfm_entry['access_frequency'] * tfm_entry['recency'])
        tfm_entry['edv'] *= 1.1  # Slightly increase EDV to maintain balance