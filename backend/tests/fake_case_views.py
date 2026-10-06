from app.analysis.view_model import CaseViewModel


class EmptyClaimExtractor:
    def batch_extract_json(self, texts, structures, **kwargs):
        return [{name: [] for name in structures} for text in texts]


def empty_view_model():
    return CaseViewModel(EmptyClaimExtractor())
