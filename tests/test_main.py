
import unittest
from unittest.mock import patch

from campusflow.service import TicketService
from campusflow.storage import TicketStorage
from main import create_new_ticket


class TestCreateNewTicket(unittest.TestCase):
    def test_next_id_uses_highest_existing_id(self):
        storage = TicketStorage()
        service = TicketService(storage)

        service.create(
            "T001", "Wi-Fi is down", "Network", "high", 15
        )
        service.create(
            "T003", "Printer is broken", "Hardware", "low", 1
        )

        user_inputs = [
            "Projector is broken",
            "Hardware",
            "medium",
            "5",
        ]

        with patch("builtins.input", side_effect=user_inputs):
            with patch("builtins.print"):
                create_new_ticket(service)

        created_ticket = service.get("T004")
        self.assertEqual(created_ticket["title"], "Projector is broken")
        self.assertEqual(
            [ticket["id"] for ticket in service.get_all()],
            ["T001", "T003", "T004"],
        )


    def test_next_id_uses_highest_existing_id_after_reload(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as folder:
            storage_path = Path(folder) / "tickets.json"
            storage = TicketStorage(storage_path)
            service = TicketService(storage)

            service.create(
                "T001", "Wi-Fi is down", "Network", "high", 15
            )
            service.create(
                "T003", "Printer is broken", "Hardware", "low", 1
            )

            reloaded_storage = TicketStorage(storage_path)
            reloaded_service = TicketService(reloaded_storage)

            user_inputs = [
                "Projector is broken",
                "Hardware",
                "medium",
                "5",
            ]

            with patch("builtins.input", side_effect=user_inputs):
                with patch("builtins.print"):
                    create_new_ticket(reloaded_service)

            created_ticket = reloaded_service.get("T004")
            self.assertEqual(
                [ticket["id"] for ticket in reloaded_service.get_all()],
                ["T001", "T003", "T004"],
            )
            self.assertEqual(
                created_ticket["title"], "Projector is broken"
            )


if __name__ == "__main__":
    unittest.main()
