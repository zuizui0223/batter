# Synthetic numerical check V1

Executed with Python scipy sparse Laplacian, 24 x 12 x 12 six-neighbour voxel lattice. Ground flat or rounded 6*exp(-((x-12)/3)^2)*(.65+.35*cos(y/2)); valid z>=ground. Source (1,6,2), sink (22,6,2). Unit current. Edge conductance exp(-beta*(mean endpoint AGL/11-.5)), beta=-3,0,3; equal species weights, trait distances .5,1,.5. Node score = normalized sum of absolute incident edge currents, not occupancy. Grounded sink sparse solve. Both Kirchhoff residual and energy identity error <1e-9 for all six solves.

|Landscape|R beta -3,0,3|Overlap pairs 01,02,12|Qspace|Rao Q|
|---|---|---|---|---|
|Flat|1.433743,0.649129,0.276361|.785942,.553604,.750440|.150712|.444444|
|Ridge|1.479684,.684461,.301077|.790012,.571672,.768023|.144291|.444444|

Single synthetic scenario, not ecological evidence. Trait coefficients arbitrary; mean accessibility not controlled; ridge also changes accessible volume. Qspace is proposed descriptive index. Next: save executable solver, analytic resistor tests, vary ridge geometry, volume-matched controls, endpoints and trait coefficients, then audit empirical data. No real-data result yet.
