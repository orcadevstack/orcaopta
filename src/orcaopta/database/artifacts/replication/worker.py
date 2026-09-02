import time
import traceback
from sqlalchemy.orm import Session

from orcaopta.security.encryption import EncryptionService
from orcaopta.database.core.session import SessionLocal
from orcaopta.database.core.models import ReplicationLog
from orcaopta.database.artifacts.replication.manager import ReplicationManager

enc = EncryptionService()


# ---------------------------------------------------------
# Log replication attempt (encrypted)
# ---------------------------------------------------------
def log_replication(source: str, target: str, status: str, message: str):
    db: Session = SessionLocal()

    try:
        encrypted_msg = enc.encrypt("ORCAOPTA_REPLICATION_KEY", message)

        entry = ReplicationLog(
            source_node=source,
            target_node=target,
            status=status,
            message=encrypted_msg,
        )

        db.add(entry)
        db.commit()

    except Exception as e:
        print(f"[ReplicationWorker] Failed to log replication: {e}")

    finally:
        db.close()


# ---------------------------------------------------------
# Worker loop (enterprise-grade)
# ---------------------------------------------------------
def run_worker():
    manager = ReplicationManager()

    print("🔁 Replication Worker started (encrypted mode)")

    while True:
        try:
            results = manager.run()  # manager returns list of replication results

            if results:
                for result in results:
                    log_replication(
                        source=result["source"],
                        target=result["target"],
                        status=result["status"],
                        message=result["message"],
                    )

        except Exception as e:
            err = traceback.format_exc()
            print(f"[ReplicationWorker] ERROR:\n{err}")
            log_replication(
                source="local",
                target="internal",
                status="failed",
                message=f"Worker crashed: {err}",
            )

        # Prevent CPU burn
        time.sleep(2)


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------
if __name__ == "__main__":
    run_worker()
