from django import forms

from app.utils.llms import LLMs
from app.enums import OptimizationMetric, LLMName, LLMType
from app.constants import SEMANTIC_ROUTES


class ModelForm(forms.Form):
    model = forms.ChoiceField(choices=[(model.value, model.name) for model in LLMName], required=True)
    provider = forms.CharField(required=True)
    api_key = forms.CharField(required=False)
    api_base = forms.CharField(required=False)

    def clean_model(self):
        split = self.cleaned_data['model'].split("/")
        if len(split) != 2:
            raise forms.ValidationError("Invalid model name format")
        
        model = split[-1]
        if model not in LLMName:
            raise forms.ValidationError("Invalid model name")
        
        if len(split) == 2:
            provider = split[0]
        else:
            provider = None

        self.cleaned_data['model'] = model
        self.cleaned_data['provider'] = provider

        return self.cleaned_data


class SemanticForm(forms.Form):
    name = forms.CharField(required=True)
    model_type = forms.ChoiceField(choices=[(llm_type.value, llm_type.name) for llm_type in LLMType], required=True)
    utterances = forms.JSONField(required=True)

    def clean_utterances(self):
        utterances = self.cleaned_data['utterances']
        if not isinstance(utterances, list):
            raise forms.ValidationError("Utterances must be a list")
        return utterances
    

class ChatCompletionExtraBodyForm(forms.Form):
    models = forms.JSONField(required=True)
    optimization_metric = forms.ChoiceField(choices=[(metric.value, metric.name) for metric in OptimizationMetric], required=False)
    semantics = forms.JSONField(required=False)

    def clean_models(self):
        models = self.cleaned_data['models']
        cleaned_models = {}
        for model_type, model in models.items():
            model_form = ModelForm(model)
            if not model_form.is_valid():
                raise forms.ValidationError(model_form.errors)
            cleaned_models[model_type] = model_form.cleaned_data


    def clean_semantics(self):
        semantics = self.cleaned_data['semantics']
        if not isinstance(semantics, list):
            raise forms.ValidationError("Semantics must be a list")
        
        for semantic in semantics:
            semantic_form = SemanticForm(semantic)
            if not semantic_form.is_valid():
                raise forms.ValidationError(semantic_form.errors)
            
        return semantics