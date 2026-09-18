import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from production_os_worker import main


class _Client:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token
        self.calls = []

    def register(self, worker_id, capabilities, operator_token):
        self.calls.append(
            ("register", worker_id, tuple(capabilities), operator_token)
        )


class ProductionOSWorkerCLITests(unittest.TestCase):
    def test_main_registers_worker_and_runs_once(self):
        clients = []
        runs = []

        def factory(base_url, token):
            client = _Client(base_url, token)
            clients.append(client)
            return client

        def run_once_fn(client, **kwargs):
            runs.append((client, kwargs))
            return {"status": "idle"}

        env = {
            "PRODUCTION_OS_URL": "http://127.0.0.1:8787",
            "PRODUCTION_OS_WORKER_TOKEN": "worker-secret",
            "PRODUCTION_OS_OPERATOR_TOKEN": "operator-secret",
        }

        rc = main(
            [
                "--worker-id",
                "ai-dev-1",
                "--once",
                "--output-root",
                "studio-output/production-os",
            ],
            environ=env,
            client_factory=factory,
            run_once_fn=run_once_fn,
        )

        self.assertEqual(rc, 0)
        self.assertEqual(len(clients), 1)
        self.assertEqual(
            clients[0].calls,
            [
                (
                    "register",
                    "ai-dev-1",
                    ("software-development", "repo-analysis"),
                    "operator-secret",
                )
            ],
        )
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0][1]["worker_id"], "ai-dev-1")
        self.assertEqual(
            runs[0][1]["output_root"],
            Path("studio-output/production-os"),
        )

    def test_main_runs_bounded_cycles_until_queue_is_idle(self):
        clients = []
        calls = []
        outcomes = iter([
            {"status": "completed"},
            {"status": "completed"},
            {"status": "idle"},
        ])

        def factory(base_url, token):
            client = _Client(base_url, token)
            clients.append(client)
            return client

        def run_once_fn(client, **kwargs):
            calls.append(kwargs)
            return next(outcomes)

        rc = main(
            [
                "--worker-id", "ai-dev-1",
                "--cycles", "10",
                "--output-root", "studio-output/production-os",
            ],
            environ={
                "PRODUCTION_OS_URL": "http://127.0.0.1:8787",
                "PRODUCTION_OS_WORKER_TOKEN": "worker-secret",
                "PRODUCTION_OS_OPERATOR_TOKEN": "operator-secret",
            },
            client_factory=factory,
            run_once_fn=run_once_fn,
        )

        self.assertEqual(rc, 0)
        self.assertEqual(len(calls), 3)
        self.assertEqual(len(clients[0].calls), 1)

    def test_main_requires_all_control_plane_credentials(self):
        with self.assertRaisesRegex(
            RuntimeError,
            "PRODUCTION_OS_OPERATOR_TOKEN",
        ):
            main(
                ["--once"],
                environ={
                    "PRODUCTION_OS_URL": "http://127.0.0.1:8787",
                    "PRODUCTION_OS_WORKER_TOKEN": "worker-secret",
                },
                client_factory=lambda *args: self.fail(
                    "client must not be created"
                ),
                run_once_fn=lambda *args, **kwargs: self.fail(
                    "worker must not run"
                ),
            )


if __name__ == "__main__":
    unittest.main()
