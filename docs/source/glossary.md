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

[Yeo 7 networks](https://bids.neuroimaging.io/index.html)
    A seven-network functional brain parcellation used by Wonkyconn to summarize within-network connectivity and DMN-related metrics.
```
