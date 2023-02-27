#!/usr/bin/env python3
"""Nvidia Operator Charm."""
import logging

from nvidia_ops_manager import NvidiaDriverOpsError, NvidiaOpsManager
from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus, WaitingStatus

logger = logging.getLogger()


class NvidiaDriverOperator(CharmBase):
    """Nvidia Charmed Operator."""

    def __init__(self, *args):
        """Initialize the charm."""
        super().__init__(*args)

        self._nvidia_ops_manager = NvidiaOpsManager()

        event_handler_bindings = {
            self.on.install: self._on_install,
            self.on.remove: self._on_remove,
        }
        for event, handler in event_handler_bindings.items():
            self.framework.observe(event, handler)

    def _on_install(self, event):
        """Install nvidia drivers."""
        install_msg = "Installing nvidia drivers..."
        logger.info(install_msg)
        self.unit.status = WaitingStatus(install_msg)

        try:
            self._nvidia_ops_manager.install()
        except NvidiaDriverOpsError as e:
            logger.error(e)
            self.unit.status = BlockedStatus(e)
            event.defer()
            return

        # Set the workload version and status.
        self.unit.set_workload_version(self._nvidia_ops_manager.version())
        self.unit.status = ActiveStatus("Ready")

    def _on_remove(self, event):
        """Remove nvidia drivers."""
        msg = "Removing Nvidia drivers..."
        logger.info(msg)
        self.unit.status = WaitingStatus(msg)

        try:
            self._nvidia_ops_manager.remove()
        except NvidiaDriverOpsError as e:
            logger.error(e)
            self.unit.status = BlockedStatus(e)
            event.defer()
            return


if __name__ == "__main__":
    main(NvidiaDriverOperator)