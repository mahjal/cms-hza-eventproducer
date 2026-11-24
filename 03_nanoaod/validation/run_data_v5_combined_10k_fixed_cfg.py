import os
import sys
from pathlib import Path
import FWCore.ParameterSet.Config as cms

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from hzanano_data_nobtv_cfg import process

lfn = os.environ["HZA_INPUT_LFN"]

assert lfn.startswith("/store/"), f"Invalid input LFN: {lfn}"

process.source.fileNames = cms.untracked.vstring(
    "root://cms-xrd-global.cern.ch/" + lfn
)

process.maxEvents.input = cms.untracked.int32(100)

process.NANOAODoutput.fileName = cms.untracked.string(
    "file:hzanano_data_v5_combined_10k_fixed.root"
)

process.options.wantSummary = cms.untracked.bool(True)


# HZaNano V3: experimental PF variable slimming

for variable in (
    "trkP",
    "trkPt",
    "trkEta",
    "trkPhi"
):
    assert hasattr(
        process.customConstituentsExtTable.variables,
        variable
    ), f"Missing PF variable: {variable}"

    delattr(
        process.customConstituentsExtTable.variables,
        variable
    )

    print("Removed PF variable:", variable)


# ============================================================
# HZaNano V4: PF candidate multiplicity reduction
# ============================================================

# 1. Select loose charged PF candidates
process.hzaLooseChargedPFCands = cms.EDProducer(
    "HZaPackedCandidateDzSigPtrSelector",
    src = cms.InputTag("packedPFCandidates"),
    minPt = cms.double(0.4),
    maxAbsDzSig = cms.double(3.0)
)

# 2. Merge loose charged tracks with AK4 constituents
process.hzaSelectedPFCands = cms.EDProducer(
    "PackedCandidatePtrMerger",
    src = cms.VInputTag(
        cms.InputTag("hzaLooseChargedPFCands"),
        cms.InputTag(
            "finalJetsAK4Constituents",
            "constituents"
        )
    ),
    skipNulls = cms.bool(True),
    warnOnSkip = cms.bool(True)
)

# 3. Schedule the required modules
process.customizedPFCandsTask.add(
    process.hzaLooseChargedPFCands,
    process.finalJetsAK4Constituents,
    process.hzaSelectedPFCands
)

# 4. Use the same selected collection for both tables
process.customConstituentsExtTable.src = cms.InputTag(
    "hzaSelectedPFCands"
)

process.customAK4ConstituentsTable.candidates = cms.InputTag(
    "hzaSelectedPFCands"
)

print("HZaNano V4: PF candidate pruning enabled")

# Larger validation sample
process.maxEvents.input = cms.untracked.int32(100)

# V5a: inclusive lepton HLT event filter
from HLTrigger.HLTfilters.hltHighLevel_cfi import hltHighLevel

hzaHLTPaths = [
    "HLT_IsoMu24_v*",
    "HLT_IsoMu24_eta2p1_v*",
    "HLT_IsoMu27_v*",
    "HLT_Mu50_v*",
    "HLT_Mu55_v*",
    "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_v*",
    "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v*",
    "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8_v*",
    "HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL_DZ_v*",
    "HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL_DZ_Mass8_v*",
    "HLT_Ele30_WPTight_Gsf_v*",
    "HLT_Ele32_WPTight_Gsf_v*",
    "HLT_Ele35_WPTight_Gsf_v*",
    "HLT_Ele38_WPTight_Gsf_v*",
    "HLT_Ele40_WPTight_Gsf_v*",
    "HLT_DoubleEle25_CaloIdL_MW_v*",
    "HLT_DoubleEle27_CaloIdL_MW_v*",
    "HLT_DoubleEle33_CaloIdL_MW_v*",
    "HLT_DoubleEle24_eta2p1_WPTight_Gsf_v*",
    "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v*",
]

process.hzaHLTFilter = hltHighLevel.clone(
    TriggerResultsTag=cms.InputTag("TriggerResults", "", "HLT"),
    HLTPaths=cms.vstring(*hzaHLTPaths),
    andOr=cms.bool(True),
    throw=cms.bool(False)
)

process.hzaHLTPath = cms.Path(process.hzaHLTFilter)
process.schedule.insert(0, process.hzaHLTPath)

process.NANOAODoutput.SelectEvents = cms.untracked.PSet(
    SelectEvents=cms.vstring("hzaHLTPath")
)

process.maxEvents.input = cms.untracked.int32(100)
process.options.wantSummary = cms.untracked.bool(True)


# Combined HZaNano V5 validation
process.maxEvents.input = cms.untracked.int32(100)

print("HZaNano V5: HLT + dz significance pruning enabled")


# Larger combined V5 validation
process.maxEvents.input = cms.untracked.int32(10000)
