class DocumentIngestionError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class UnsupportedDocumentError(DocumentIngestionError):
    def __init__(self, message: str) -> None:
        super().__init__("unsupported_document_type", message)


class DocumentLimitError(DocumentIngestionError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(code, message)


class InvalidDocumentError(DocumentIngestionError):
    def __init__(self, message: str) -> None:
        super().__init__("invalid_document", message)


class DocumentRecognitionError(Exception):
    code = "document_recognition_failed"


class RecognitionConfigurationError(DocumentRecognitionError):
    code = "document_recognizer_not_configured"


class RecognitionTimeoutError(DocumentRecognitionError):
    code = "document_recognition_timeout"


class RecognitionProviderError(DocumentRecognitionError):
    code = "document_recognition_provider_error"


class RecognitionResponseError(DocumentRecognitionError):
    code = "document_recognition_invalid_response"


class DocumentSegmentationError(Exception):
    code = "document_segmentation_failed"


class SegmentationConfigurationError(DocumentSegmentationError):
    code = "document_segmenter_not_configured"


class SegmentationTimeoutError(DocumentSegmentationError):
    code = "document_segmentation_timeout"


class SegmentationProviderError(DocumentSegmentationError):
    code = "document_segmentation_provider_error"


class SegmentationResponseError(DocumentSegmentationError):
    code = "document_segmentation_invalid_response"
