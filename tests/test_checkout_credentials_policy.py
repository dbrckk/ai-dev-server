import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))

from replacement_ci_policy import validate_step_inputs_env_text


class CheckoutCredentialsPolicyTests(unittest.TestCase):
    def test_checkout_persist_credentials_false_is_accepted(self):
        text=(
            "jobs:\n"
            "  validate:\n"
            "    steps:\n"
            "      - name: Checkout\n"
            "        uses: actions/checkout@sha\n"
            "        with:\n"
            "          persist-credentials: false\n"
        )
        result=validate_step_inputs_env_text(text)
        self.assertTrue(result["valid"],result)

    def test_checkout_missing_persist_credentials_is_rejected(self):
        text=(
            "jobs:\n"
            "  validate:\n"
            "    steps:\n"
            "      - name: Checkout\n"
            "        uses: actions/checkout@sha\n"
        )
        result=validate_step_inputs_env_text(text)
        self.assertFalse(result["valid"])

    def test_checkout_persist_credentials_true_is_rejected(self):
        text=(
            "jobs:\n"
            "  validate:\n"
            "    steps:\n"
            "      - name: Checkout\n"
            "        uses: actions/checkout@sha\n"
            "        with:\n"
            "          persist-credentials: true\n"
        )
        result=validate_step_inputs_env_text(text)
        self.assertFalse(result["valid"])

    def test_checkout_extra_input_is_rejected(self):
        text=(
            "jobs:\n"
            "  validate:\n"
            "    steps:\n"
            "      - name: Checkout\n"
            "        uses: actions/checkout@sha\n"
            "        with:\n"
            "          persist-credentials: false\n"
            "          fetch-depth: 0\n"
        )
        result=validate_step_inputs_env_text(text)
        self.assertFalse(result["valid"])


if __name__=="__main__":
    unittest.main()
