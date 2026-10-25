import importlib
import unittest

import numpy as np


def small_config():
    return dict(context=4,d_model=8,heads=2,layers=1,feedforward=16,
                dropout=0.0,seeds=[17],validation_size=8,epochs=8,
                patience=3,batch_size=32,learning_rate=0.03,weight_decay=0.01,
                logistic_C=0.01,frequency_prior=100.,recent_window=25,
                torch_threads=1,shuffle_seed=20261025)


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try: cls.models=importlib.import_module('experiments.sequence_attention.models')
        except ModuleNotFoundError: cls.models=None

    def require_models(self):
        self.assertIsNotNone(self.models,'Os modelos ainda não foram implementados')

    def test_transformer_learns_simple_signal_and_excludes_future(self):
        self.require_models()
        x=np.tile(np.r_[np.ones(15),np.zeros(10)],(80,1))
        config=small_config()
        a,ma=self.models.fit_transformer(x,60,config,17)
        changed=x.copy(); changed[60:]=1-changed[60:]
        b,mb=self.models.fit_transformer(changed,60,config,17)
        ctx=x[56:60][None]
        pa=self.models.predict_transformer(a,ctx)
        pb=self.models.predict_transformer(b,ctx)
        np.testing.assert_allclose(pa,pb,rtol=0,atol=0)
        self.assertLess(ma['best_validation_loss'],0.5)
        self.assertLess(ma['max_training_target_index'],52)
        self.assertLess(ma['max_validation_target_index'],60)

    def test_future_test_targets_cannot_change_first_prediction(self):
        self.require_models()
        rng=np.random.default_rng(99)
        x=np.zeros((90,25))
        for row in x: row[rng.choice(25,15,replace=False)]=1
        changed=x.copy(); changed[60:]=np.roll(changed[60:],1,axis=1)
        a,_=self.models.predict_fold(x,60,65,small_config())
        b,_=self.models.predict_fold(changed,60,65,small_config())
        for key in a:
            np.testing.assert_allclose(a[key][0],b[key][0],rtol=0,atol=0)
            self.assertTrue(np.isfinite(a[key]).all())
            np.testing.assert_allclose(a[key].sum(1),15,atol=1e-8)


if __name__=='__main__': unittest.main()
