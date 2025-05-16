from abstract_utilities import (os,
                                get_date,
                                mkdirs,
                                safe_json_loads,
                                safe_read_from_json)
import json

class SaveManager:
    """
    Manages the saving of data. This class should provide methods to specify where (e.g., what database or file) and how (e.g., in what format) data should be saved.
    """
    def __init__(self, data={},title:str=None,directory:str=None,model:str='default')->None:
        self.title=title
        self.model=model
        self.date = get_date()
        if isinstance(directory,list):
            abs_path = directory[0]
            if not os.path.isabs(directory[0]):
                abs_path = os.path.join(os.getcwd(), directory[0])
                mkdirs(abs_path)
            path = abs_path
            for child in directory[1:]:
                path = os.path.join(path, child)
                mkdirs(path)
            self.directory=path
        else:
            self.directory = mkdirs(directory or os.path.join(os.getcwd(), 'response_data'))
            self.directory = mkdirs(os.path.join(self.directory, self.date))
            self.directory = mkdirs(os.path.join(self.directory, self.model))
        self.file_name = self.create_unique_file_name()
        self.file_path = os.path.join(self.directory, self.file_name)
        if data:
            self.data = safe_json_loads(data)
            self.data['file_path']=self.file_path
            self.data['title']=self.title
            self.data['model']=self.model
            self.save_to_file(data = data,file_path = self.file_path)
    def create_unique_file_name(self) -> str:
        # Sanitize and shorten the title
        sanitized_title = self.sanitize_title(self.title)

        # Generate base file name
        base_name = f"{sanitized_title}.json"
        
        # Check for uniqueness and append index if needed
        unique_name = base_name
        index = 1
        while os.path.exists(os.path.join(self.directory, unique_name)):
            unique_name = f"{sanitized_title}_{index}.json"
            index += 1

        return unique_name
    @staticmethod
    def sanitize_title(title: str) -> str:
        if title:
            # Replace spaces and special characters
            title = str(title).replace(" ", "_").replace(":", "_")

            # Limit the length of the title
            max_length = 30
            if len(title) > max_length:
                title = title[:max_length]

            return title
    def save_to_file(self, data:dict, file_path:str)->None:
        # Assuming `data` is already a dictionary, we convert it to a JSON string and save.
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    
    @staticmethod
    def read_saved_json(file_path:str)->dict:
        # Use 'safe_read_from_json' which is presumed to handle errors and return JSON
        return safe_read_from_json(file_path)
    
    @staticmethod
    def read_saved_json(file_path:str)->dict:
        # Use 'safe_read_from_json' which is presumed to handle errors and return JSON
        return safe_read_from_json(file_path)
