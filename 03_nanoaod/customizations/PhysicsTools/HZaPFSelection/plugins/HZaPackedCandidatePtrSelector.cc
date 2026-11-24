#include <memory>
#include <vector>
#include <cmath>

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/Common/interface/Handle.h"
#include "DataFormats/Common/interface/Ptr.h"
#include "DataFormats/PatCandidates/interface/PackedCandidate.h"

class HZaPackedCandidatePtrSelector :
    public edm::global::EDProducer<> {

public:

    explicit HZaPackedCandidatePtrSelector(
        const edm::ParameterSet& cfg
    ) :
        token_(consumes<pat::PackedCandidateCollection>(
            cfg.getParameter<edm::InputTag>("src")
        )),
        minPt_(cfg.getParameter<double>("minPt"))
    {
        produces<std::vector<
            edm::Ptr<pat::PackedCandidate>>>();
    }

    void produce(
        edm::StreamID,
        edm::Event& event,
        const edm::EventSetup&
    ) const override {

        edm::Handle<pat::PackedCandidateCollection> input;
        event.getByToken(token_, input);

        auto output = std::make_unique<
            std::vector<edm::Ptr<pat::PackedCandidate>>
        >();

        output->reserve(input->size());

        for (std::size_t i = 0; i < input->size(); ++i) {

            const auto& cand = (*input)[i];

            if (cand.charge() == 0) continue;
            if (cand.pt() < minPt_) continue;

            output->emplace_back(input, i);
        }

        event.put(std::move(output));
    }

private:

    const edm::EDGetTokenT<
        pat::PackedCandidateCollection
    > token_;

    const double minPt_;
};

DEFINE_FWK_MODULE(HZaPackedCandidatePtrSelector);
