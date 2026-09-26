# Terrain-relative self-transfer v1

Date: 2026-09-26

## Question

Does the individual-specific place-by-height signal persist when the vertical coordinate is
height above ground level (AGL), rather than GPS height above mean sea level?

The AGL field (`height_true`) is documented in the archived analysis table as GPS height minus
terrain elevation from a 30-m ASTER DEM.

## Primary 5-km result

Using the same leave-one-session-out logic and fixed physical height bands:

- evaluable individuals: 6
- conditional identity gain: **+0.33656 nats/fix**
- positive individual conditional gains: **4/6**
- marginal AGL identity gain: **-0.25490**
- identity × location increment: **+0.59146**

Individual conditional gains:

- Bat3: -0.0298
- Bat4: -0.1436
- Bat5: +0.1301
- Bat6: +1.4810
- Bat7: +0.0980
- Bat8: +0.4836

The key result is the decomposition: an individual's overall AGL distribution is not more
predictive than other bats' AGL distributions on average, but the **place-specific AGL pattern**
carries strong individual information.

## Spatial scale

- 2.5 km: conditional gain **+0.76560**, 5/5 positive; identity × location +0.67532
- 5 km: conditional gain **+0.33656**, 4/6 positive; identity × location +0.59146
- 10 km: conditional gain **-0.04500**, 4/7 positive; identity × location +0.17482

As with the MSL result, individuality is a fine-scale property and is largely erased by coarse
horizontal aggregation.

## Ecological interpretation

The signal is not a simple preferred altitude above ground. It is a repeatable **vertical route
relative to local terrain**.

Bat7 is especially informative: it was non-repeatable under the original 5-km MSL endpoint but
becomes positive under AGL. This is consistent with an individual that may repeat height relative
to terrain while absolute elevation changes with the route/topography.

Conversely, Bat3 and Bat4 were strong/positive in the original MSL analysis but are weak or
negative in AGL conditional gain. This suggests that individuals may differ in the coordinate
frame in which their 3-D route is most repeatable.

That coordinate-frame interpretation is exploratory and requires a matched decomposition of
terrain elevation, AGL, and MSL on the same annotated rows.

## Claim ceiling

This supports repeatable individual organization of **flight height above ground** under the
archived tracking design. It still does not identify foraging, intrinsic personality, learned
routes, or causal response to wind.
