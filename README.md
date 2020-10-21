# scan_vis

A program to visualise whatever that is related to the smmpl.
All parameters can be adjusted in smmpl_vis.global_imports.params_smmpl_vis

## Current features

### Animated view

Performs a 3D plot and a 2d projection plot of smmpl processed profiles and the scan pattern computed.

```python -m smmpl_vis```

### MPLNET product plot

Plots the lidar products in a fashion similar to MPLNET.

```python -m smmpl_vis.mplnet_plot```


---

# Feature Requests

- scan_event live data update

- Make a never ending realtime function, which limits the number of
  objects in the queue.