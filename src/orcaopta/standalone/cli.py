import argparse
from src.orcaopta.standalone.bootstrap import StandaloneOrcaopta
from src.orcaopta.core.config import load_config

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["standalone", "cluster"], default="standalone")
    args = parser.parse_args()

    cfg = load_config()

    if args.mode == "standalone":
        StandaloneOrcaopta().start()
    else:
        print("Cluster mode not implemented yet.")

if __name__ == "__main__":
    main()
