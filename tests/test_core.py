import importlib
import tempfile
import unittest
from pathlib import Path

import numpy as np


class CoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.core = importlib.import_module('experiments.sequence_attention.core')
        except ModuleNotFoundError:
            cls.core = None

    def require_core(self):
        self.assertIsNotNone(self.core, 'O núcleo do experimento ainda não foi implementado')

    def test_rejects_repeated_numbers_and_contest_gaps(self):
        self.require_core()
        header = 'contest,date,' + ','.join(f'n{i}' for i in range(1,16)) + '\n'
        cases = [
            '1,2026-01-01,' + ','.join(map(str, [1]*15)) + '\n',
            '1,2026-01-01,' + ','.join(map(str, range(1,16))) + '\n3,2026-01-03,' + ','.join(map(str, range(1,16))) + '\n',
            '1,invalid,' + ','.join(map(str, range(1,16))) + '\n',
        ]
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'bad.csv'
            for rows in cases:
                path.write_text(header+rows)
                with self.assertRaises(ValueError):
                    self.core.load_history(path)

    def test_future_rows_cannot_change_features_for_current_target(self):
        self.require_core()
        x = np.tile(np.r_[np.ones(15),np.zeros(10)], (600,1))
        changed = x.copy()
        changed[300:] = np.r_[np.zeros(10),np.ones(15)]
        a, b = self.core.causal_features(x), self.core.causal_features(changed)
        np.testing.assert_array_equal(a[:301], b[:301])
        self.assertFalse(np.array_equal(a[301:], b[301:]))

    def test_uniform_projection_and_extreme_logits(self):
        self.require_core()
        p = self.core.project_marginals(np.zeros((2,25)))
        np.testing.assert_allclose(p, 0.6, atol=1e-10)
        p = self.core.project_marginals(np.array([[-1000.]*10+[1000.]*15]))
        self.assertTrue(np.isfinite(p).all())
        self.assertTrue(((p>0)&(p<1)).all())
        np.testing.assert_allclose(p.sum(1),15,atol=1e-8)

    def test_folds_cover_each_target_once_without_train_overlap(self):
        self.require_core()
        folds=self.core.temporal_folds(3812,2000,300)
        covered=[]
        for train_end,stop in folds:
            self.assertLess(train_end,stop)
            covered.extend(range(train_end,stop))
        self.assertEqual(covered,list(range(2000,3812)))

    def test_context_excludes_target_and_has_known_order(self):
        self.require_core()
        x=np.arange(10*25).reshape(10,25)
        c=self.core.contexts(x,[5,7],3)
        np.testing.assert_array_equal(c[0],x[2:5])
        np.testing.assert_array_equal(c[1],x[4:7])

    def test_brier_reference_and_top15_tie_break_are_valid(self):
        self.require_core()
        y=np.array([[1]*15+[0]*10])
        m=self.core.score_predictions(np.full((1,25),0.6),y,[100])
        self.assertAlmostEqual(m['brier'][0],0.24)
        self.assertEqual(m['selected'].sum(),15)
        self.assertTrue(np.isin(m['selected'],[0,1]).all())

    def test_same_official_day_is_allowed_when_contests_increase(self):
        self.require_core()
        import io
        header='contest,date,'+','.join(f'n{i}' for i in range(1,16))+'\n'
        nums=','.join(map(str,range(1,16)))
        text=header+f'1,2026-01-01,{nums}\n2,2026-01-01,{nums}\n'
        try: result=self.core.load_history(io.StringIO(text))
        except ValueError as error: self.fail(f'Data diária igual não prova desordem entre concursos: {error}')
        self.assertEqual(result[1].shape,(2,25))

    def test_date_reconciliation_preserves_raw_and_rejects_changed_numbers(self):
        self.require_core()
        self.assertTrue(hasattr(self.core,'derive_checked_history'),'Reconciliação ainda não implementada')
        with tempfile.TemporaryDirectory() as d:
            raw=Path(d)/'raw.csv';out=Path(d)/'checked.csv'
            nums=','.join(map(str,range(1,16)))
            raw.write_text('contest,date,'+','.join(f'n{i}' for i in range(1,16))+'\n'+
                           f'1,2026-01-02,{nums}\n2,2026-01-01,{nums}\n')
            before=raw.read_bytes()
            check=dict(contest=2,provider_contest=2,official_date='2026-01-03',
                       numbers=list(range(1,16)),source_url='https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/2')
            edits=self.core.derive_checked_history(raw,[check],out)
            self.assertEqual(raw.read_bytes(),before)
            self.assertEqual(edits[0]['new_date'],'2026-01-03')
            self.assertEqual(self.core.load_history(out)[0].date.iloc[1],'2026-01-03')
            with self.assertRaises(FileExistsError): self.core.derive_checked_history(raw,[check],out)
            check['numbers']=list(range(2,17))
            with self.assertRaises(ValueError): self.core.derive_checked_history(raw,[check],Path(d)/'bad.csv')


if __name__=='__main__': unittest.main()
