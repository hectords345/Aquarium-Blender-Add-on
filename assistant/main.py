"""Entry point for running the assistant."""
from __future__ import annotations

import argparse
import logging
import threading

import uvicorn

from . import brain as brain_module, config, web


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-wake", action="store_true", help="PTT only")
    parser.add_argument("--stt-model", default="medium.en")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    if args.quiet:
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.no_wake:
        config.USE_PUSH_TO_TALK = True

    brain = brain_module.Brain(stt_model=args.stt_model)

    def _run_app():
        uvicorn.run(web.app, host="0.0.0.0", port=8000, log_level="warning")

    t = threading.Thread(target=_run_app, daemon=True)
    t.start()

    brain.run()


if __name__ == "__main__":  # pragma: no cover
    main()
