import ast
import csv
import importlib.util
import json
import re
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT.parent / "L300-unify-data" / "data"
spec = importlib.util.spec_from_file_location("sentiment", ROOT / "code" / "score_feedback_foundry.py")
if spec is None or spec.loader is None:
    raise RuntimeError("Couldn't load the supplied sentiment script.")
sentiment = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sentiment)

notebook = json.loads((ROOT / "notebooks" / "07-integrate-litware.ipynb").read_text(encoding="utf-8"))
scope = {}
exec(compile("".join(notebook["cells"][1]["source"]), "litware-notebook", "exec"), scope)
load_litware = scope["load_litware"]


class ChallengeAssetTests(unittest.TestCase):
    def test_sentiment_labels(self):
        for label in ["positive", "negative", "neutral", "mixed"]:
            self.assertEqual(sentiment.normalize_sentiment(f" {label.upper()}\n"), label)

    def test_invalid_sentiment_is_not_a_success(self):
        for label in ["", "positive.", "mostly positive", "neutral\nnegative"]:
            with self.assertRaises(ValueError):
                sentiment.normalize_sentiment(label)

    def test_sentiment_request_uses_supported_reasoning_parameters(self):
        client = Mock()
        client.responses.create.return_value = SimpleNamespace(status="completed", output_text="positive")
        self.assertEqual(sentiment.score_sentiment(client, "sentiment-model", "Product", "Feedback"), "positive")
        request = client.responses.create.call_args.kwargs
        self.assertEqual(request["model"], "sentiment-model")
        self.assertEqual(request["reasoning"], {"effort": "minimal"})
        self.assertEqual(request["max_output_tokens"], 4096)
        self.assertNotIn("temperature", request)

    def test_incomplete_response_cannot_be_persisted_as_valid_sentiment(self):
        client = Mock()
        for status in ["incomplete", "failed", "cancelled", None]:
            client.responses.create.return_value = SimpleNamespace(status=status, output_text="positive")
            with self.assertRaisesRegex(ValueError, "response status"):
                sentiment.score_sentiment(client, "sentiment-model", "Product", "Feedback")

    def test_model_endpoint(self):
        endpoint = "https://example.openai.azure.com/openai/v1/"
        self.assertEqual(sentiment.model_endpoint(endpoint), endpoint)
        for invalid in ["http://example.openai.azure.com/openai/v1/", "https://example.com/openai/v1/",
                        "https://example.openai.azure.com/openai/v1/?key=secret"]:
            with self.assertRaises(ValueError):
                sentiment.model_endpoint(invalid)

    def test_connection_string_escapes_values(self):
        text = sentiment.connection_string("tcp:server,1433", "database};UID=other")
        self.assertIn("DATABASE={database}};UID=other};", text)
        self.assertIn("Encrypt=yes;TrustServerCertificate=no;", text)
        self.assertNotIn("Authentication=", text)

    def test_litware_counts_and_expected_results(self):
        tables = load_litware(DATA / "litware", {"P101", "P104", "P113"}, date(2026, 11, 26))
        self.assertEqual([len(tables[name]) for name in [
            "litware_plant", "litware_product_mapping", "litware_capacity_plan",
            "litware_product_qualification", "litware_capacity_assessment"
        ]], [3, 4, 18, 6, 18])
        assessment = tables["litware_capacity_assessment"]
        self.assertEqual(sum(row["AvailableCapacityUnits"] for row in assessment if row["CaldovaProductID"] == "P101"), 54000)
        self.assertEqual(sum(row["EligibleCapacityUnits"] for row in assessment), 12000)
        self.assertEqual(sum(row["EligibleCapacityUnits"] for row in assessment if row["LitwarePlantID"] != "LPL001"), 0)
        self.assertEqual(len({row["QualificationID"] for row in tables["litware_product_qualification"]}), 6)
        self.assertEqual([row["CaldovaProductID"] for row in tables["litware_product_mapping"] if row["LitwareProductID"] == "LPR004"], [None])

    def changed_fixture(self, column, value):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        for path in (DATA / "litware").glob("*.csv"):
            (root / path.name).write_bytes(path.read_bytes())
        path = root / "litware_capacity_plan.csv"
        with path.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            fields = reader.fieldnames
            rows = list(reader)
        if fields is None:
            raise RuntimeError("Missing CSV headers.")
        rows[0][column] = value
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        return root

    def test_orphan_capacity_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "matching qualification"):
            load_litware(self.changed_fixture("LitwarePlantID", "UNKNOWN"), {"P101", "P104", "P113"}, date(2026, 11, 26))

    def test_invalid_arithmetic_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "arithmetic"):
            load_litware(self.changed_fixture("AvailableCapacityUnits", "4001"), {"P101", "P104", "P113"}, date(2026, 11, 26))

    def test_overlapping_windows_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "overlapping"):
            load_litware(self.changed_fixture("WindowEndDate", "2026-11-08"), {"P101", "P104", "P113"}, date(2026, 11, 26))

    def test_invalid_mapping_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "mapping"):
            load_litware(DATA / "litware", {"P104", "P113"}, date(2026, 11, 26))

    def test_code_cells_compile(self):
        paths = list((ROOT.parent / "L300-unify-data" / "notebooks").glob("*.ipynb"))
        paths.extend((ROOT / "notebooks").glob("*.ipynb"))
        for path in paths:
            content = json.loads(path.read_text(encoding="utf-8"))
            for index, cell in enumerate(content["cells"]):
                if cell["cell_type"] == "code":
                    compile("".join(cell["source"]), f"{path.name}:cell-{index}", "exec")

    def test_enrichment_runtime_settings(self):
        path = ROOT.parent / "L300-unify-data" / "notebooks" / "05-enrich-caldova-feedback.ipynb"
        content = json.loads(path.read_text(encoding="utf-8"))
        settings = ast.parse("".join(content["cells"][1]["source"]))
        settings.body = [node for node in settings.body if not isinstance(node, (ast.Import, ast.ImportFrom))]
        configuration = Mock()
        exec(compile(settings, path.name, "exec"), {"aifunc": SimpleNamespace(default_conf=configuration)})
        configuration.set_deployment_name.assert_called_once_with("gpt-5-mini")
        configuration.set_reasoning_effort.assert_called_once_with("low")
        configuration.reset_temperature.assert_called_once_with()

    @unittest.skipUnless(shutil.which("pwsh"), "PowerShell 7 is required to exercise the package builder.")
    def test_package_excludes_replay_guards_and_local_artifacts(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "L300-unify-data"
            challenge = base / "L400-unify-data"
            for directory in ["code", "data", "notebooks", "event-simulator"]:
                folder = source / directory
                folder.mkdir(parents=True)
                (folder / "fixture.txt").write_text("source", encoding="utf-8")
            for directory in ["code", "notebooks"]:
                folder = challenge / directory
                folder.mkdir(parents=True)
                (folder / "fixture.txt").write_text("override", encoding="utf-8")
            for name in [".replay-prime.state", ".replay-full.state"]:
                (source / "event-simulator" / name).write_text("completed", encoding="utf-8")
            for name in ["tests", "__pycache__", ".venv"]:
                folder = source / "event-simulator" / name
                folder.mkdir()
                (folder / "local.txt").write_text("local", encoding="utf-8")
            script = challenge / "build-package.ps1"
            shutil.copyfile(ROOT / "build-package.ps1", script)
            result = subprocess.run(
                ["pwsh", "-NoProfile", "-File", str(script)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            with zipfile.ZipFile(challenge / "L400-unify-data.zip") as archive:
                self.assertIsNone(archive.testzip())
                names = archive.namelist()
                self.assertTrue(names)
                for name in names:
                    self.assertNotIn(".state", name)
                    self.assertFalse({"tests", "__pycache__", ".venv"} & set(Path(name).parts))
                self.assertEqual(archive.read("code/fixture.txt"), b"override")

    def test_solution_timings_and_expandable_help(self):
        lab = (ROOT.parents[1] / "Instructions" / "Labs" / "L400-unify-data-challenge.md").read_text(encoding="utf-8")
        timings = [int(value) for value in re.findall(r"\*\*Estimated time:\*\* (\d+) minutes\.", lab)]
        self.assertEqual(timings, [100, 110, 135, 15])
        self.assertEqual(sum(timings), 360)
        self.assertEqual(lab.count('<details markdown="block">'), 10)
        self.assertEqual(lab.count("</details>"), 10)
        self.assertNotIn("Build the shared data foundation", lab)

    def test_solution_source_boundaries(self):
        lab = (ROOT.parents[1] / "Instructions" / "Labs" / "L400-unify-data-challenge.md").read_text(encoding="utf-8")
        business = lab.split("## Task 01:", 1)[1].split("## Task 02:", 1)[0]
        operations = lab.split("## Task 02:", 1)[1].split("## Task 03:", 1)[0]
        ontology = lab.split("## Task 03:", 1)[1].split("## Task 04:", 1)[0]
        self.assertIn("SET Channel = 'Email'", business)
        self.assertIn("SET Channel = 'Portal'", business)
        self.assertNotIn("caldova_events", business)
        self.assertNotIn("score_feedback_foundry.py", business)
        self.assertNotIn("curate_caldova_tables.ipynb", operations)
        self.assertIn("Reuse these tables; don't rerun the planning notebook", operations)
        self.assertEqual(lab.count("create `caldova-challenge-<initials>`"), 1)
        self.assertNotIn("caldova-business-<initials>", lab)
        self.assertNotIn("from the operations workspace", lab)
        self.assertNotIn("caldova_customer_db", operations)
        self.assertNotIn("caldova_business_data_agent", operations)
        for excluded in ["OperationalEvent", "operational_events", "caldova_events", "caldova_foundry_ops"]:
            self.assertNotIn(excluded, ontology)
        self.assertIn("11 entity types and 13 bound relationship types", ontology)
        self.assertIn("FROM dbo.customer_feedback_enriched", ontology)

    def test_supported_delivery_configuration(self):
        lab = (ROOT.parents[1] / "Instructions" / "Labs" / "L400-unify-data-challenge.md").read_text(encoding="utf-8")
        self.assertIn("**Optimize your business processes**", lab)
        self.assertIn("**Pass-through** authentication", lab)
        self.assertIn("**Maximum duration = 1 minute**", lab)
        self.assertIn("**Use mapping table?**", lab)
        self.assertIn("**Background mode**", lab)
        self.assertIn("Select only the 11 ontology-bound tables", lab)
        self.assertNotIn("Save and publish the ontology", lab)
        self.assertNotIn("gpt-4.1-mini", lab)
        self.assertIn("or an environment-provider-approved comparable small reasoning model", lab)
        self.assertIn("supports Foundry Agent Service and Fabric IQ tool calling", lab)
        self.assertIn("supports the OpenAI Responses API and the supplied client's `minimal` reasoning effort", lab)
        self.assertIn("Enrichment project sentiment deployment name", lab)


if __name__ == "__main__":
    unittest.main()
