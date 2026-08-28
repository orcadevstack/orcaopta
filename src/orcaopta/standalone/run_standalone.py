# run_standalone.py

import uvicorn

from src.orcaopta.standalone.bootstrap import StandaloneOrcaopta


def main():
    # 1. Boot Orcaopta in standalone mode
    orca = StandaloneOrcaopta().start()

    # 2. Start the API (FastAPI app)
    # Make sure src/orcaopta/api.py exposes: app = FastAPI(...)
    uvicorn.run(
        "src.orcaopta.api:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()
