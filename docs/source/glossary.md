# Glossary

```{glossary}
Atlas
    A parcellation image that maps connectivity matrix rows and columns to brain regions or networks.

[BEP017](https://bids.neuroimaging.io/extensions/beps/bep_017.html)
    A BIDS Extension Proposal that defines conventions for storing imaging-derived connectivity data.

[BIDS](https://bids.neuroimaging.io/index.html)
    The Brain Imaging Data Structure, a standard layout for organizing neuroimaging datasets and derivatives.

Connectivity matrix
    A region-by-region table of connectivity values, usually correlations, that summarizes relationships between brain regions for one subject, task, or run.

DMN
    The default mode network, one of the Yeo 7 resting-state networks used by Wonkyconn's network organization metrics.

Gradient similarity
    A group-level metric comparing connectivity gradients from the input data with packaged reference gradient templates.

[HALFpipe](https://github.com/HALFpipe/HALFpipe)
    A pipeline for fMRI preprocessing and analysis. Wonkyconn supports HALFpipe-style derivative layouts.

QC-FC
    Quality-control functional connectivity, a test of whether connectivity edge weights are associated with head motion.

    Power, J. D., Schlaggar, B. L., & Petersen, S. E. (2015). Recent progress and outstanding issues in motion correction in resting state fMRI. NeuroImage, 105, 536–551. [https://doi.org/10.1016/j.neuroimage.2014.10.044](https://doi.org/10.1016/j.neuroimage.2014.10.044)


[Yeo 7 networks](https://bids.neuroimaging.io/index.html)
    A seven-network functional brain parcellation used by Wonkyconn to summarize within-network connectivity and DMN-related metrics.
    Yeo, B. T. T., Krienen, F. M., Sepulcre, J., Sabuncu, M. R., Lashkari, D., Hollinshead, M., Roffman, J. L., Smoller, J. W., Zöllei, L., Polimeni, J. R., Fischl, B., Liu, H., & Buckner, R. L. (2011). The organization of the human cerebral cortex estimated by intrinsic functional connectivity. Journal of Neurophysiology, 106(3), 1125–1165. [https://doi.org/10.1152/jn.00338.2011](https://doi.org/10.1152/jn.00338.2011)

```
