# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
PCI_WEIGHT = 1.0
TAR_WEIGHT = 1.0
QCM_WEIGHT = 1.0
HAR_WEIGHT = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a FIFO queue, a Predictive Clustering Index (PCI) for access patterns, a Temporal Anomaly Resolution (TAR) score for access times, a Quantum-Causal Mapping (QCM) for causal relationships, and a Heuristic Adaptation Ratio (HAR) for dynamic factor adjustment.
fifo_queue = []
pci = {}
tar = {}
qcm = {}
har = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy identifies clusters with the lowest PCI scores, then selects the object with the highest TAR score within those clusters. If there is a tie, the QCM is used to determine the least causally impactful object, adjusted by the HAR. The selected object is then evicted from the front of the FIFO queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    # Identify clusters with the lowest PCI scores
    min_pci_score = min(pci.values())
    candidate_clusters = [key for key, value in pci.items() if value == min_pci_score]
    
    # Select the object with the highest TAR score within those clusters
    max_tar_score = -1
    for key in candidate_clusters:
        if tar[key] > max_tar_score:
            max_tar_score = tar[key]
            candid_obj_key = key
    
    # If there is a tie, use QCM to determine the least causally impactful object
    if candidate_clusters.count(candid_obj_key) > 1:
        min_qcm_score = float('inf')
        for key in candidate_clusters:
            if qcm[key] < min_qcm_score:
                min_qcm_score = qcm[key]
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    The PCI is updated to reflect the current access pattern, the TAR score is adjusted for the recent access time, the QCM is recalculated for updated causal relationships, and the HAR is fine-tuned based on recent evictions. The FIFO queue remains unchanged.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    pci[key] = pci.get(key, 0) + 1
    tar[key] = cache_snapshot.access_count
    qcm[key] = qcm.get(key, 0) + 1
    har[key] = har.get(key, 1.0) * HAR_WEIGHT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    The new object is added to the rear of the FIFO queue. The PCI is updated to include the new access pattern, the TAR score is initialized, the QCM is updated for new causal relationships, and the HAR is adjusted for the new cache composition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    fifo_queue.append(key)
    pci[key] = 1
    tar[key] = cache_snapshot.access_count
    qcm[key] = 1
    har[key] = 1.0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    The evicted object is removed from the front of the FIFO queue. The PCI is recalculated to remove the evicted pattern, TAR scores are normalized, the QCM is updated to remove causal links, and the HAR is adjusted based on the eviction's success.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    fifo_queue.remove(evicted_key)
    del pci[evicted_key]
    del tar[evicted_key]
    del qcm[evicted_key]
    del har[evicted_key]
    
    # Normalize TAR scores
    max_tar = max(tar.values(), default=1)
    for key in tar:
        tar[key] /= max_tar
    
    # Adjust HAR based on eviction's success
    for key in har:
        har[key] *= HAR_WEIGHT