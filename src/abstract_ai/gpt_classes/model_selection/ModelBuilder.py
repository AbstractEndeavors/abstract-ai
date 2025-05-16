from .all_models import XAI_MODELS,OPENAI_MODELS
class ModelManager:
    """
    This class manages the selection and querying of models available for use.

    Attributes:
        selected_model_name (str): The name of the currently selected model.
        selected_endpoint (str): The endpoint associated with the currently selected model.
        selected_max_tokens (int): The maximum tokens associated with the currently selected model.
        default_model_info (dict): Information about the default model, including its name, endpoint, and maximum tokens.
        all_models (list): A list of all available models.

    Methods:
        get_all_values(key): Retrieves all unique values associated with the specified key from all available models.
        _get_endpoint_by_model(model_name): Returns the endpoint associated with the specified model.
        _get_models_by_endpoint(endpoint): Returns all models associated with the specified endpoint.
        _get_max_tokens_by_model(model_name): Returns the maximum tokens associated with the specified model.
    """
    def __init__(self, input_model_name:str=None, input_endpoint:str=None, default_selection:bool=True)->None:
        
        self.all_models = XAI_MODELS+OPENAI_MODELS
        self.all_model_names=self.get_all_values('model')
        self.all_endpoints=self.get_all_values('endpoint')
        self.default_model_info = {'model': 'gpt-4', 'endpoint': 'https://api.openai.com/v1/chat/completions', 'tokens': 8192}
        self.models_get_info_endpoint = "/v1/models"
        self.selected_model_name = input_model_name
        self.selected_endpoint = input_endpoint
        self.selected_max_tokens = None

        if not self.selected_model_name and not self.selected_endpoint and default_selection:
            self.selected_model_name = self.default_model_info['model']
            self.selected_endpoint = self.default_model_info['endpoint']
            self.selected_max_tokens = self.default_model_info['tokens']
        elif self.selected_model_name:
            self.selected_endpoint = self._get_endpoint_by_model(self.selected_model_name)
            self.selected_max_tokens = self._get_max_tokens_by_model(self.selected_model_name)
        elif self.selected_endpoint:
            # Assuming there could be multiple models for an endpoint.
            model_names_for_endpoint = self._get_models_by_endpoint(self.selected_endpoint)
            if model_names_for_endpoint:
                self.selected_model_name = model_names_for_endpoint[0]  # Default to the first model.
                self.selected_max_tokens = self._get_max_tokens_by_model(self.selected_model_name)
        if self.selected_model_name:
            self.selected_endpoint = self._get_endpoint_by_model(self.selected_model_name)
            self.selected_max_tokens = self._get_max_tokens_by_model(self.selected_model_name)
            if not self.selected_endpoint or not self.selected_max_tokens:
                # If model name not found and default_selection is True, revert to default model
                if default_selection:
                    self.selected_model_name = self.default_model_info['model']
                    self.selected_endpoint = self.default_model_info['endpoint']
                    self.selected_max_tokens = self.default_model_info['tokens']
    def get_all_values(self,key:str)->list:
        all_values = []
        for value in self.all_models:
            if key in value:
                if value[key] not in all_values:
                    all_values.append(value[key])
        return all_values
    
    def _get_all_values(self, key:str)->list:
        return list(set([value[key] for value in self.all_models if key in value]))

    def _get_endpoint_by_model(self, model_name:str)->(dict or None):
        for model in self.all_models:
            if model["model"] == model_name:
                return model["endpoint"]
        return None

    def _get_models_by_endpoint(self, endpoint:str)->list:
        return [model["model"] for model in self.all_models if model["endpoint"] == endpoint]

    def _get_max_tokens_by_model(self, model_name:str)->(dict or None):
        for model in self.all_models:
            if model["model"] == model_name:
                return model["tokens"]
        return None
