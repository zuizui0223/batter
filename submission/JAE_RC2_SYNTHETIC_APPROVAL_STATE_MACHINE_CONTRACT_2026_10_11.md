# Synthetic publication approval transition test — fixed before running (2026-10-11)

This is an editorial **code-only unit test**, not a biological, human authorization or journal submission result.

The test will use the real immutable JAE RC2 manuscript bytes in read-only mode and generate any fictitious author policy / source rights records only in isolated temporary files that are deleted after tests. No fabricated approvals will be committed to the repo. It will invoke only Python unittest mocking, not network APIs, tags, DOI creation or author communications.

Prior live negative gate is verified by GitHub Actions 38107448547 (success as correct HOLD).

Fixed scenarios:

1. Synthetic ten-DOI author-signoff fixture and policy approval can pass their respective *logic* validators (this does not mean real approval).
2. The exact frozen RC2 manuscript plus one synthetic approved AI Methods or Acknowledgements paragraph can pass the diff validator; an unexpected changed numerical result, removed text or extra paragraph must fail.
3. Mocked integrated editorial checker can reach READY only after policy, exact ten source rights, journal-facing approval/placement and both native upload/Zenodo checks pass. One failure at each independent stage must return HOLD.
4. Strict checker nonzero on actual missing approvals (verified already in live 38107448547).
5. The actual CI must not have assertions forcing author signoff to remain absent forever: when real files are eventually approved, CI must be able to test the correct alternate branch.

Any simulated READY is prominently labelled FICTIONAL_STATE_MACHINE_TEST, not a real journal-ready evaluation. Original manuscript SHA remains c4ef51a7f3f291a6f203d303dbf73f5b54fb7683 and no releases are minted.
