from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

def setup_tracing(
    endpoint: str = "http://localhost:5000/v1/traces",
    experiment_id: str = "0"
):
    provider = TracerProvider()

    exporter = OTLPSpanExporter(
        endpoint=endpoint,
        headers={
            "x-orcaopta-experiment-id": experiment_id
        }
    )

    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)

    return trace.get_tracer("orcaopta")
