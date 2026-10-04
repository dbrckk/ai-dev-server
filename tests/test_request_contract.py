import copy
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from core import StudioError, request_check


BASE={
    "id":"demo-v1",
    "target_repo":"owner/app",
    "app_name":"demo_app",
    "brief":"Build a complete polished mobile application.",
    "enabled":True,
}


class RequestContractTests(unittest.TestCase):
    def test_optional_production_os_skill_learning_contract_is_preserved(self):
        contract = {'schema': 'production-os/learned-skill/v1', 'result_field': 'learned_skill',
                    'max_procedure_steps': 12, 'optional': True}
        value = copy.deepcopy(BASE)
        value['tool_contracts'] = {'skill_learning': contract}
        self.assertEqual(request_check(value)['tool_contracts']['skill_learning'], contract)

    def test_skill_learning_contract_does_not_accept_mandatory_or_arbitrary_contracts(self):
        for key, invalid in (('schema', 'unknown'), ('result_field', '../unsafe'),
                             ('max_procedure_steps', 0), ('max_procedure_steps', 13),
                             ('max_procedure_steps', True), ('optional', False), ('command', 'arbitrary')):
            with self.subTest(key=key, invalid=invalid):
                value = copy.deepcopy(BASE)
                value['tool_contracts'] = {'skill_learning': {
                    'schema': 'production-os/learned-skill/v1', 'result_field': 'learned_skill',
                    'max_procedure_steps': 12, 'optional': True, key: invalid}}
                with self.assertRaisesRegex(StudioError, 'skill learning tool contract'):
                    request_check(value)

    def test_legacy_request_does_not_gain_play_publish_field(self):
        value=request_check(copy.deepcopy(BASE))
        self.assertNotIn("play_publish",value)

    def test_play_publish_opt_in_is_normalized(self):
        value=copy.deepcopy(BASE)
        value["play_publish"]={"enabled":True,"track":"beta"}
        checked=request_check(value)
        self.assertEqual(
            checked["play_publish"],
            {"enabled":True,"track":"beta","commit":False},
        )

    def test_commit_requires_enabled(self):
        value=copy.deepcopy(BASE)
        value["play_publish"]={"enabled":False,"track":"internal","commit":True}
        with self.assertRaisesRegex(StudioError,"commit requires enabled"):
            request_check(value)

    def test_invalid_track_is_rejected(self):
        value=copy.deepcopy(BASE)
        value["play_publish"]={"enabled":True,"track":"staging","commit":False}
        with self.assertRaisesRegex(StudioError,"track"):
            request_check(value)


if __name__=="__main__":
    unittest.main()
