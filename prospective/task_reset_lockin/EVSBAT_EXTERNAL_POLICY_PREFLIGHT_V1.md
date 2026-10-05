# evsBat external policy validation structural preflight v1

## Status

**PROSPECTIVE EXTERNAL VALIDATION OF A FIXED POST-PRIMARY POLICY REPRESENTATION.**

Branch:
`prospective/task-reset-lockin-v1`

This programme is distinct from the failed same-individual morphology linkage.

No obstacle-flight A–E identity is required or inferred.

## External source

Figshare article:
`29150924`, evsBat raw data, version 2.

Archive:
`rawdata.zip`, file id `58421782`.

Independent *Rhinolophus nippon* source-native individual identifiers exposed by the archive directory:

- 2670
- 2681
- 2860
- 2868
- 2899

These are treated as a new five-individual cohort.

## Fixed representation imported from the obstacle-flight programme

No axis may be redefined from evsBat outcomes.

If compatible 3-D tracks exist, use the exact eight movement features:

1. median 3-D speed;
2. p90 3-D speed;
3. median absolute vertical speed;
4. p90 absolute vertical speed;
5. median absolute horizontal turning rate;
6. p90 absolute horizontal turning rate;
7. path efficiency;
8. vertical range.

And the exact transparent axes:

`FlightIntensity = mean(z1,z2,z3,z4)`

`ManeuveringExtent = mean(-z1,z5,z6,z7,z8)`.

If the public track schema cannot reproduce these quantities, STOP this external test rather than redesigning the axes.

## Stage 1 — selected-member ZIP metadata

Before opening pickle content, authorize central-directory metadata only for entries matching exactly:

`rawdata/chamber/event_camera/R_nippon/particle_tracking_results_kiku_<ID>_*.pkl`

where ID is one of the five source-native identifiers above.

For those candidate members only, report:
- path;
- compression method;
- CRC32;
- compressed size;
- uncompressed size;
- local-header offset.

Do not open member payloads at this stage.

## Stage 2 — one-member schema probe

After Stage 1:

- choose the **smallest uncompressed candidate pickle** deterministically;
- freeze its exact path/CRC/size before payload opening;
- extract only that member;
- inspect the pickle with `pickletools` without executing it.

Allowed outputs:
- pickle protocol;
- referenced module/class names;
- string keys/column names matching a strict whitelist relevant to:
  - time;
  - timestamp/frame;
  - x/y/z;
  - position/coordinate;
  - trajectory/track;
  - velocity.

Do not report numeric trajectory values.

If static pickle inspection cannot establish schema, a separately frozen safe-load amendment is required.

## Structural pass condition

Proceed toward external validation only if public files reproducibly support:

- >=4 *R. nippon* individuals;
- >=3 independent trajectory members per included individual;
- time/order;
- three spatial dimensions or a source-documented 3-D track representation;
- enough rows per trajectory to compute the frozen features.

## External claim ceiling

A positive result may support:

> the fixed two-axis movement-policy representation recurs in an independent *R. nippon* cohort and recording system.

It cannot establish:
- the same individual-specific theta values across studies;
- morphology as the cause;
- cross-species universality;
- developmental origin.
