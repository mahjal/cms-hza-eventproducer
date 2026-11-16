# HZaNano AK8 Slimming — Run 2024 Data Validation

**Validation date:** 16 November 2026  
**Status:** Small-sample end-to-end integration test passed  
**Dataset:** Run 2024C Muon0  
**CMSSW release:** CMSSW_15_0_18

## 1. Overview

This study validates an optimized HZaNano configuration for the exclusive search H → Za, with Z → ℓ⁺ℓ⁻ and a → hadrons.

The objective is to reduce NanoAOD output size by removing unnecessary AK8 jet and subjet information while preserving the collections required for the HZa analysis.

The optimized configuration retains:

- AK4 BTV extensions
- AllPF candidates and associated information
- Muon and electron collections
- HLT and L1 trigger information
- Event identifiers and other required analysis variables

The following content is removed:

- AK8 BTV extensions
- Standard NanoAOD FatJet and SubJet output tables

This validation tests whether the optimized NanoAOD can be processed through the existing HZaEventProducer and HZaAnalyzer workflow.

## 2. Implementation

### 2.1 HZaNano customization

The customization is implemented in:

`03_nanoaod/customizations/PhysicsTools/HZaNano/python/custom_hza_cff.py`

The function `HZaBTVNanoAOD_allPF_noAK8(process)` configures:

```python
switches = cms.PSet(
    btvNano_addAK4_switch=cms.untracked.bool(True),
    btvNano_addAK8_switch=cms.untracked.bool(False),
    btvNano_addallPF_switch=cms.untracked.bool(True),
    TaggerInput=cms.string("btvSF"),
)
```

The AK8 BTV switch alone does not remove the standard NanoAOD FatJet and SubJet tables.

### 2.2 Data configuration

The tested configuration is stored in:

`03_nanoaod/validation/hzanano_data_noak8_cfg.py`

It uses:

- Era: `Run3_2024`
- Conditions: `150X_dataRun3_v2`
- Data mode: `--data`
- NanoAOD output tier: `NANOAOD`
- Four processing threads

The standard AK8 output tables are explicitly removed:

```python
process.jetAK8TablesTask.remove(process.fatJetTable)
process.jetAK8TablesTask.remove(process.subJetTable)
```

The Data configuration does not apply the MC-only generator-truth customization.

The committed configuration contains placeholder input/output filenames. These must be replaced with appropriate paths when reproducing the test.

## 3. Validation sample

**CMS dataset:**

`/Muon0/Run2024C-MINIv6NANOv15-v1/MINIAOD`

The initial validation used 100 events from one MiniAOD file.

The following processing chain was tested:


The following processing chain was tested:

```text
Run2024C Muon0 MiniAOD
          |
          v
    Custom HZaNano
     (without AK8)
          |
          v
   HZaEventProducer
          |
          v
      HZaAnalyzer
          |
          v
  Analysis ROOT output
```



The NanoAOD production was performed on LXPLUS.

The producer and analyzer compatibility checks were performed on DESY NAF.

## 4. NanoAOD validation results

The custom NanoAOD production completed successfully.

| Quantity | Result |
|---|---:|
| Processed MiniAOD events | 100 |
| NanoAOD `Events` entries | 100 |
| NanoAOD branches | 2,809 |
| NanoAOD file size | Approximately 7.8 MB |
| FatJet/SubJet branches remaining | 0 |
| `cmsRun` exit code | 0 |

The following required branches were checked and found:

- `run`, `luminosityBlock`, `event`
- `Muon_pt`
- `Electron_pt`
- `PFCands_pt`
- `PFCands_charge`
- `HLT_IsoMu24`

Additional PF-candidate, lepton, and trigger branches were inspected during validation.

No branches matching the standard FatJet/SubJet collections remained:

- `FatJet_*`
- `SubJet_*`
- `nFatJet`
- `nSubJet`

**Result:** The optimized NanoAOD file was produced successfully, and the checked analysis-required information remained available.

This is a branch-presence validation, not yet a full event-by-event comparison with an unslimmed Data baseline.

## 5. HZaEventProducer validation

The optimized NanoAOD was transferred to DESY NAF and processed using `HZaEventProducer` in collision-data mode.

No `--isMC` argument was supplied.

The producer applied the 2024 Golden JSON certification.

### Results

| Quantity | Result |
|---|---:|
| Input NanoAOD events | 100 |
| Golden JSON accepted events | 100 |
| Golden JSON acceptance | 100% |
| Producer output entries | 1 |
| `HZaEvents` branches | 99 |
| Producer exit code | 0 |

The producer log reported:

```text
GoldenJSON: 100 / 100 events pass (100%)

Batch 1 complete. Total entries so far: 1

=== Processing Complete ===

Total events written: 1
```

The output `HZaEvents` tree was opened successfully with ROOT.

**Result:** The existing event producer can process the optimized collision-data NanoAOD.

The one-event preselection yield is not a signal-efficiency measurement.

## 6. HZaAnalyzer validation

The producer output was processed with `HZaAnalyzer` using:

```text
Maximum events: -1
Minimum a pT: 15.0 GeV
Minimum |DeltaPhi(a,Z)|: 2.5
Maximum track isolation: 0.10
```

An initial runtime failure occurred because the existing analyzer executable had an embedded RPATH pointing to `/usr/lib64/root`, while the environment used ROOT from CERN LCG_110.

An isolated analyzer executable was compiled against LCG_110 ROOT 6.40.02.

Two checks were performed:

1. A schema-only test with zero `HZaEvents` entries.
2. A real-data test with the single event produced by HZaEventProducer.

Both completed with exit code 0.

### Real-data analyzer results

| Quantity | Result |
|---|---:|
| Input events | 1 |
| Events processed | 1 |
| Final selected candidates | 0 |
| Output `outTree` entries | 0 |
| Output `outTree` branches | 82 |
| Output ROOT file size | Approximately 178 KB |
| Analyzer exit code | 0 |

The analyzer log reported:

```text
Processed events                    : 1
Selected events, unweighted         : 0
Best a candidates: all / truth accepted: 0 / 0
Best H candidates: all / truth accepted: 0 / 0

Finished 1 events.
```

No final selected candidates were found in this small sample.

This does not indicate an analyzer failure, but the test does not yet demonstrate reconstruction of a fully selected Data candidate.

## 7. Data blinding

The analyzer contains nominal Data-specific blinding checks for the Higgs signal region:

\[
122 < m_H < 128\ \mathrm{GeV}.
\]

The nominal event-selection logic excludes Data candidates in the blinded interval before the final selected-candidate output is filled.

The implementation also contains independent control-region diagnostics, including same-sign categories.

A complete blinding regression audit is still required before using the optimized configuration for a full collision-data physics analysis.

## 8. ROOT integrity checks

The final integrity check opened all three ROOT files and inspected the expected trees.

```text
Slimmed HZaNano
  Tree: Events
    Entries: 100
      Branches: 2809
        AK8 branches remaining: 0
	  Missing required branches: []

Producer
  Tree: HZaEvents
    Entries: 1
      Branches: 99

Analyzer
  Tree: outTree
    Entries: 0
      Branches: 82

PASS: All ROOT integrity checks
```

ROOT emitted nonfatal dictionary warnings concerning several CMSSW metadata classes. These warnings did not prevent the required trees and branches from being accessed.

## 9. Validation artifacts

The ROOT files and runtime logs are stored on the analysis systems and are not committed to Git.

### LXPLUS

Validation directory:

`/afs/cern.ch/user/m/mjalalva/eos/hza_data_validation/test_2024C_Muon0/`

### DESY NAF

Validation directory:

`/data/dust/user/jalalvan/hza/data_validation_20261116/`

Relevant files include:

```text
hzanano_data_noak8_test.root
producer_test.log
root_validation.txt

output/producer_test/
  Run2024C_Muon0_noAK8_HZa_presel.root

analyzer_data_test.log
analyzer_data_test.root
```

These paths record where the validation was performed and are specific to the test environment.

## 10. Remaining validation

The next steps are:

1. Produce a standard, unslimmed HZaNano from exactly the same MiniAOD input events.
2. Compare all retained branches event by event between the standard and slimmed outputs.
3. Measure the Data file-size reduction relative to the standard configuration.
4. Compare HZaEventProducer outputs and event-level selection results.
5. Compare HZaAnalyzer cutflows and reconstructed distributions.
6. Validate the configuration using larger collision-data samples and additional Muon/EGamma streams.
7. Complete the Data blinding regression audit.
8. Verify reproducibility of the ROOT build environment for batch production.

The Data storage reduction has not yet been measured against an unslimmed baseline.

A previous MC prototype showed a 1.74% file-size reduction, but that result must not be interpreted as the measured Data reduction.

## 11. Conclusion

The AK8-slimmed HZaNano configuration successfully completed a small-sample end-to-end integration test using Run 2024C Muon0 collision data.

The optimized output:

- Contains no standard FatJet/SubJet branches.
- Preserves the checked lepton, PF-candidate, trigger and event-identification branches.
- Can be processed by HZaEventProducer.
- Can be processed by HZaAnalyzer with a consistent ROOT environment.
- Produces readable ROOT output files.

**The technical compatibility test passed.**

Full physics-content equivalence, quantitative storage savings on Data, larger-scale production stability, and the complete Data blinding regression audit remain to be established.
~