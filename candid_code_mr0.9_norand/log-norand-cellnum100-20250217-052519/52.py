# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import numpy as np

# Put tunable constant parameters below
INITIAL_PDF_VALUE = 0.1
INITIAL_SCORE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a probability density function (PDF) for each cached object, representing the likelihood of future accesses. It also keeps track of a stochastic optimization score and a reduced-dimensionality feature vector for each object, updated using Bayesian inference.
pdfs = {}
scores = {}
feature_vectors = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the object with the lowest stochastic optimization score, which is derived from the PDF and the reduced-dimensionality feature vector. This score represents the least likely object to be accessed in the near future.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        if scores[key] < min_score:
            min_score = scores[key]
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the PDF of the accessed object to reflect the increased likelihood of future accesses. The stochastic optimization score and the feature vector are also updated using Bayesian inference to incorporate the new access information.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    pdfs[key] += 0.1  # Increase the likelihood of future accesses
    scores[key] = 1 / pdfs[key]  # Update the score based on the new PDF value
    feature_vectors[key] = np.array([obj.size])  # Example feature vector update

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its PDF based on historical access patterns and assigns an initial stochastic optimization score. The feature vector is generated using dimensionality reduction techniques on the object's attributes.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    pdfs[key] = INITIAL_PDF_VALUE
    scores[key] = INITIAL_SCORE
    feature_vectors[key] = np.array([obj.size])  # Example feature vector initialization

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the PDFs and stochastic optimization scores of the remaining objects to account for the changed cache state. The feature vectors are also adjusted to maintain an accurate representation of the current cache contents.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in pdfs:
        del pdfs[evicted_key]
    if evicted_key in scores:
        del scores[evicted_key]
    if evicted_key in feature_vectors:
        del feature_vectors[evicted_key]
    
    # Recalibrate PDFs and scores for remaining objects
    for key in cache_snapshot.cache:
        pdfs[key] *= 0.9  # Example recalibration
        scores[key] = 1 / pdfs[key]  # Update the score based on the new PDF value