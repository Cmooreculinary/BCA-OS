import json
import os
import unittest

from fastapi.testclient import TestClient

os.environ.setdefault("CONRAD_ACCESS_TOKEN", "founder-test-access")

from mcp_bridge import app as production  # noqa: E402

server = production.server


class IntakeEndpointTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(production.app)
        self.headers = {"Authorization": "Bearer founder-test-access"}
        self.records = []
        self.audit_records = []
        self.original_store = server.intake_store
        self.original_read_recent = server.intake_read_recent
        self.original_read = server.intake_read

        async def fake_store(record, audit_record):
            self.records.append(record.copy())
            self.audit_records.append(audit_record.copy())

        async def fake_read_recent(limit=10):
            return self.records[:limit]

        async def fake_read(intake_id):
            for record in self.records:
                if record["intake_id"] == intake_id:
                    return record
            return None

        server.intake_store = fake_store
        server.intake_read_recent = fake_read_recent
        server.intake_read = fake_read

    def tearDown(self):
        server.intake_store = self.original_store
        server.intake_read_recent = self.original_read_recent
        server.intake_read = self.original_read

    def post_intake(self, content):
        response = self.client.post(
            "/intake",
            json={"content": content},
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def test_health_endpoint(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["status"], "ok")

    def test_venue_iq_product_idea_routes_to_ideas_and_backlog(self):
        receipt = self.post_intake(
            "Venue IQ should compare the current BEO against the previous approved version and display every change."
        )

        self.assertEqual(receipt["classification"], "product_feature_idea")
        self.assertEqual(receipt["project"], "Venue IQ")
        destination = f"{receipt['primary_destination']} {receipt['secondary_destination']}"
        self.assertRegex(destination, r"ideas|product backlog")
        self.assertTrue(receipt["approval_required"])

    def test_margin_iq_product_idea_routes_to_ideas_and_backlog(self):
        receipt = self.post_intake(
            "Margin IQ should alert the operator when labor percentage is drifting above target."
        )

        self.assertEqual(receipt["classification"], "product_feature_idea")
        self.assertEqual(receipt["project"], "Margin IQ")
        destination = f"{receipt['primary_destination']} {receipt['secondary_destination']}"
        self.assertRegex(destination, r"ideas|product backlog")
        self.assertTrue(receipt["approval_required"])

    def test_technical_bug_routes_to_issue_queue_and_incidents(self):
        receipt = self.post_intake("Foodtruck Apollo checkout returns a 500 error after Stripe payment.")

        self.assertEqual(receipt["classification"], "technical_bug")
        self.assertEqual(receipt["project"], "Foodtruck Apollo")
        destination = f"{receipt['primary_destination']} {receipt['secondary_destination']}"
        self.assertRegex(destination, r"incidents|issue queue")

    def test_founder_private_note_routes_to_private_vault(self):
        receipt = self.post_intake(
            "This is private founder strategy and must not be available to staff or customers."
        )

        self.assertEqual(receipt["sensitivity"], "FOUNDER_ONLY")
        self.assertEqual(receipt["primary_destination"], "Founder Private Vault")

    def test_staff_task_routes_to_tasks(self):
        receipt = self.post_intake("Assign the Venue IQ landing-page review to the design team.")

        self.assertEqual(receipt["classification"], "staff_task")
        self.assertIn("tasks", receipt["primary_destination"])

    def test_fake_api_key_is_quarantined_and_not_echoed_or_stored(self):
        fake_key = "sk-proj-FAKEKEYFORTESTINGONLY1234567890ABCDE"
        receipt = self.post_intake(f"Please wire this API key into the app: {fake_key}")

        self.assertEqual(receipt["status"], "quarantined")
        self.assertEqual(receipt["sensitivity"], "SECRET")
        self.assertEqual(receipt["primary_destination"], "secret_manager_required")

        response_text = json.dumps(receipt)
        records_text = json.dumps(self.records)
        audit_text = json.dumps(self.audit_records)
        self.assertNotIn(fake_key, response_text)
        self.assertNotIn(fake_key, records_text)
        self.assertNotIn(fake_key, audit_text)
        self.assertIn("[REDACTED_SECRET]", records_text)

    def test_recent_and_id_retrieval_routes_return_records(self):
        receipt = self.post_intake("Venue IQ should add a client-visible change summary.")

        recent = self.client.get("/intake/recent", headers=self.headers)
        self.assertEqual(recent.status_code, 200, recent.text)
        self.assertEqual(recent.json()["entries"][0]["intake_id"], receipt["intake_id"])

        detail = self.client.get(
            f"/intake/{receipt['intake_id']}",
            headers=self.headers,
        )
        self.assertEqual(detail.status_code, 200, detail.text)
        self.assertEqual(detail.json()["intake_id"], receipt["intake_id"])


if __name__ == "__main__":
    unittest.main()
