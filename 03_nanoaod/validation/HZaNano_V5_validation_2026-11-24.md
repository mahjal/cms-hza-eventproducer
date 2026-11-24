# HZaNano V5: HLT and PF pruning validation

**Date:** 2026-11-24
**Dataset:** Run2024C Muon0, first 10,000 input MiniAOD events
**Environment:** CMSSW_15_0_18 for HZaNano production (LXPLUS); LCG_110 ROOT 6.40.02 for the validation Analyzer (NAF)
**Status:** PASS for the tested 10k-event Run2024C Muon0 sample; larger and independent-channel tests remain necessary.

## Motivation and changes

V5 extends the previously tested V4 HZaNano configuration:

1. **Data HLT prefilter:** Keep an event if the inclusive muon or electron HLT group passes: `HLT_Mu_any || HLT_EG_any`. The groups represent the 20 individual 2024 trigger paths used by the EventProducer. This filtering changes the event population; comparisons with V4 must be made on common event IDs.
2. **Charged PF pruning:** Retain charged packed candidates with `pT >= 0.4 GeV`, available track details, valid positive finite `dzError`, and `abs(dz/dzError) < 3.01` at HZaNano production. Combine this subset with *all* `finalJetsAK4Constituents` to preserve AK4 jet constituent associations. The C++ packed-candidate selector explicitly checks `hasTrackDetails()` before accessing `dzError()`.
3. **Offline GoodTrack threshold unchanged:** The EventProducer/physics-side `|dz/dzError| < 3.0` requirement is not relaxed. The production threshold of 3.01 is a safety margin around reduced-precision NanoAOD `dz` and `dzErr` values, not a change to the physics selection.

## Input and validation event counts

| Stage | V4 | V5 |
|---|---:|---:|
| HZaNano events | 10,000 | 5,338 |
| EventProducer `HZaEvents` entries | 451 | 373 |
| EventProducer entries restricted to V5 event IDs | 373 | 373 |
| HZaAnalyzer input entries in matched comparison | 373 | 373 |
| Analyzer best candidates kept | 41 | 41 |

All 5,338 V5 NanoAOD event IDs matched the independently evaluated HLT OR on V4. The EventProducer's Golden JSON accepted all 10,000 V4 and all 5,338 V5 input entries in this test. The EventProducer preselection then produced 451 V4 and 373 V5 entries.

## PF content and associations

On the 5,338 common HLT-selected NanoAOD events:

| Check | Result |
|---|---:|
| V4 PF candidates | 4,999,829 |
| V5 PF candidates | 310,349 |
| PF candidate multiplicity reduction | 93.7928% |
| AK4 constituent links checked | 102,430 |
| AK4 links with changed/missing candidate identity or association | 0 |
| Offline GoodTrack proxy candidates, V4 | 43,506 |
| Offline GoodTrack proxy candidates, V5 | 43,506 |
| GoodTrack proxy differences on matched events | 0 |

**Precision boundary diagnostic:** Recalculating `abs(dz/dzErr) < 3.01` from the stored NanoAOD floating-point branches showed 18 boundary discrepancies (11 expected-but-absent and 7 unexpected-present candidates), all within approximately 0.00152 of the 3.01 threshold. This is consistent with reduced branch precision relative to the original `pat::PackedCandidate` selection; the diagnostic does not by itself prove the underlying floating-point mechanism. The production margin preserved all GoodTrack proxy candidates under the unchanged offline criterion in this sample.

## EventProducer validation

The *same* `HZaEventProducer` executable was run independently over the V4 and V5 NanoAOD inputs. Events were aligned by `(run, luminosityBlock, event)`, and V4 output events were restricted to the event IDs present in V5 NanoAOD.

- V4 reconstructed events on common HLT IDs: **373**
- V5 reconstructed events: **373**
- Missing or unexpected event IDs: **0**
- Output branch schemas: **99 / 99 identical**
- Branch-level value differences across the 373 events: **0** (exact comparison, treating matching NaNs as equal)

**Result: PASS.** This is a full comparison of the stored EventProducer output fields, not merely a proxy track-selection check.

## Analyzer validation

The original V4 EventProducer TTree was filtered using native ROOT cloning to retain exactly the 373 V5 reconstructed event IDs, preserving the original TTree/branch layout. Both inputs were analyzed with the *same* validation-built HZaAnalyzer using:

```text
maxEvents = -1
minAPt = 15.0 GeV
minDPhiAZ = 2.5
maxTrackIso = 0.10
```

The Analyzer was separately compiled against LCG_110 ROOT 6.40.02 to avoid mixing `/usr/lib64/root` with the active LCG ROOT libraries. The existing production Analyzer executable was not overwritten.

Selected comparison counters:

| Counter | V4 matched | V5 |
|---|---:|---:|
| All events | 373 | 373 |
| Valid Z candidate | 234 | 234 |
| Initial track pairs | 229 | 229 |
| Pass track pT | 215 | 215 |
| Pass a pT | 189 | 189 |
| Pass track-pair delta-phi | 134 | 134 |
| Pass track isolation | 132 | 132 |
| Pass delta-phi(a,Z) | 41 | 41 |
| Best candidate kept | 41 | 41 |

The OS/SS pair-survival counters were identical. Comparison of the produced ROOT histogram objects gave:

- Histograms in each file: **368**
- Missing or extra histograms: **0**
- Histograms with differing class, bin edges, contents (including under-/overflow), or variances: **0**
- Histogram comparison exit code: **0**

**Result: PASS — 368/368 histograms identical.** The histogram checker did not assert equivalence of arbitrary non-histogram ROOT objects or graphical/display metadata.

## Storage interpretation

The observed NanoAOD file sizes were approximately **156 MB** for V4 with 10,000 events and **18 MB** for V5 with 5,338 HLT-selected events. These sizes are **not a same-event storage comparison**, because V5 includes HLT event filtering as well as PF pruning. The established same-event metric is the **93.7928% reduction in PF-candidate count**; measure bytes/event on matched events separately before claiming a particular per-event file-size saving.

## Reproducibility: validation files and logs

NAF validation root:

```text
/data/dust/user/jalalvan/hza/data_validation_20261124/v5_10k/
```

Key files:

```text
inputs/V4_10k.root
inputs/V5_margin_10k.root
inputs/v4_10k.list
inputs/v5_margin_10k.list
producer/V4/V4_10k_HZa_presel.root
producer/V5/V5_margin_10k_HZa_presel.root
producer/matched/V4_matched_native.root
analyzer/V4_matched_native_HZaAnalyzer.root
analyzer/V5_matched_HZaAnalyzer.root
logs/V4_EventProducer.log
logs/V5_EventProducer.log
logs/compare_eventproducer_v4_v5.log
logs/V4_matched_native_Analyzer.log
logs/V5_matched_Analyzer.log
logs/compare_analyzer_histograms.log
```

Test code includes `compare_eventproducer_v4_v5.py`, `make_matched_native.cxx`, and `compare_analyzer_histograms.py` from the validation directory. Local scratch files and ROOT outputs should **not** be committed to the source repository; place reusable scripts under `test/` or `validation/`, adapting hard-coded absolute paths to CLI arguments in a follow-up cleanup.

The production configuration and plugin sources live in the **LXPLUS CMSSW development area**, including `PhysicsTools/HZaPFSelection/plugins/HZaPackedCandidateDzSigPtrSelector.cc` and the V5 data cfg. Record the exact repository commit SHA and cfg filename after committing. Do not assume the production and NAF analysis repositories are the same.

## Limitations and follow-up

- This validates a **10k-event Run2024C Muon0 data sample**, not every 2024 era, EGamma channel, or full Run 3 sample.
- The inclusive HLT OR preserves the tested Data selection; MC trigger acceptance/weighting is a separate task.
- The GoodTrack-proxy test does not replace the full EventProducer check; the latter passed independently.
- The numerical `dz`-significance boundary interpretation is a precision-consistent hypothesis, not a proof from unrounded MiniAOD value-by-value comparisons.
- Validate on larger Muon and EGamma samples and additional run eras; then produce a production-wide storage and physics-equivalence report.
- Retain data blinding and existing Analyzer configurations in any subsequent comparisons.

**Conclusion:** Within the tested Run2024C Muon0 sample and matched HLT event population, V5 preserves all 99 stored EventProducer branches and all 368 inspected Analyzer histograms exactly, while reducing stored PF candidate multiplicity by approximately 93.8%.
