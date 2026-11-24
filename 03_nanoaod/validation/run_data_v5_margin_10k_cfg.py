import FWCore.ParameterSet.Config as cms
from run_data_v5_combined_10k_fixed_cfg import process

process.hzaLooseChargedPFCands.maxAbsDzSig = cms.double(3.01)

process.NANOAODoutput.fileName = cms.untracked.string(
    "file:hzanano_data_v5_margin_10k.root"
)

print("HZaNano V5: production dz significance threshold = 3.01")
