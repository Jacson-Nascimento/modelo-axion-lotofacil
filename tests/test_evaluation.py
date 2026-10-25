import importlib
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np


class EvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try: cls.engine=importlib.import_module('experiments.sequence_attention.run')
        except ModuleNotFoundError: cls.engine=None

    def require_run(self):
        self.assertIsNotNone(self.engine,'A avaliação ainda não foi implementada')

    def test_bootstrap_zero_gain_cannot_be_declared_significant(self):
        self.require_run()
        r=self.engine.bootstrap_summary(np.zeros(100),replicates=199,block=10,seed=7)
        self.assertEqual(r['p_one_sided'],1.)
        self.assertEqual(r['ci95'],[0.,0.])

    def test_holm_controls_family_and_keeps_input_order(self):
        self.require_run()
        np.testing.assert_allclose(self.engine.holm([0.01,0.04,0.03]),[0.03,0.06,0.06])

    def test_existing_result_directory_is_never_overwritten(self):
        self.require_run()
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'run'; path.mkdir()
            sentinel=path/'original.txt';sentinel.write_text('preservado')
            with self.assertRaises(FileExistsError): self.engine.prepare_output(path)
            self.assertEqual(sentinel.read_text(),'preservado')

    def test_tiny_pipeline_emits_all_model_scores_and_provenance(self):
        self.require_run()
        from test_models import small_config
        rng=np.random.default_rng(9)
        with tempfile.TemporaryDirectory() as d:
            history=Path(d)/'history.csv'
            rows=['contest,date,'+','.join(f'n{i}' for i in range(1,16))]
            import datetime
            for i in range(90):
                nums=np.sort(rng.choice(25,15,False)+1)
                date=datetime.date(2020,1,1)+datetime.timedelta(days=i)
                rows.append(f'{i+1},{date},'+','.join(map(str,nums)))
            history.write_text('\n'.join(rows)+'\n')
            config=small_config()|dict(outer_start=60,outer_block=15,bootstrap_replicates=99,
                                     bootstrap_block=5,bootstrap_seed=9,historical_only=True)
            out=Path(d)/'output'
            result=self.engine.run(config,history,out)
            self.assertEqual(result['evaluation_draws'],30)
            self.assertFalse(result['prospective'])
            self.assertFalse(result['promoted_to_betting'])
            self.assertEqual(len(result['models']),6)
            self.assertTrue((out/'predictions.csv.gz').exists())
            manifest=json.loads((out/'manifest.json').read_text())
            self.assertEqual(len(manifest['data_sha256']),64)
            self.assertEqual(manifest['config'],config)


if __name__=='__main__': unittest.main()
