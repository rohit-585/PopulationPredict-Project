# forms.py (dynamic version)
from django import forms
import pickle
import os


MODELS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
with open(os.path.join(MODELS_PATH, 'Population_models.pkl'), 'rb') as f:
    population_models = pickle.load(f)


STATE_CHOICES = [(state, state) for state in sorted(population_models.keys())]

class PredictionForm(forms.Form):
    state = forms.ChoiceField(choices=STATE_CHOICES, label='Select State')
    year = forms.IntegerField(label='Enter Year (1951–2100)', min_value=1951, max_value=2100)
