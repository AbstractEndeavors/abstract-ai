from abstract_utilities import (os,
                                get_date,
                                mkdirs,
                                safe_json_loads,
                                safe_read_from_json)
import errno
import json
from typing import Optional, Union
from pydantic import BaseModel, ConfigDict


class SavedRecord(BaseModel):
    """Envelope written to disk alongside the caller's payload."""
    model_config = ConfigDict(extra="allow")  # allow arbitrary payload fields
    title: str
    model: str
    date: str
    file_path: str


class SaveManager:
    """Saves JSON payloads to a date/model-organized directory tree.

    Construction does NOT touch disk. Call save() to actually write.
    Path resolution is deterministic: same inputs → same target directory.
    Unique-name allocation uses O_CREAT|O_EXCL, so concurrent savers
    can't collide on the same filename.
    """

    DEFAULT_ROOT_NAME = "response_data"
    MAX_TITLE_LEN = 30
    MAX_NAME_ATTEMPTS = 10000

    def __init__(
        self,
        title: Optional[str] = None,
        directory: Optional[Union[str, list]] = None,
        model: str = "default",
    ) -> None:
        self.title = self.sanitize_title(title)
        self.model = model
        self.date = get_date()
        self.directory = self._resolve_directory(directory)

    # --- public ------------------------------------------------------------

    def save(self, data: Union[dict, str]) -> str:
        """Write `data` to a uniquely-named file in self.directory.

        Returns the full file path.
        """
        if isinstance(data, str):
            data = safe_json_loads(data)
        if not isinstance(data, dict):
            raise TypeError(f"data must be dict or JSON string, got {type(data).__name__}")

        os.makedirs(self.directory, exist_ok=True)
        file_path, fd = self._open_unique()

        record = SavedRecord(
            title=self.title,
            model=self.model,
            date=self.date,
            file_path=file_path,
            **data,                  # caller's payload merges in
        )

        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(record.model_dump(), f, ensure_ascii=False, indent=4)
        except Exception:
            # Don't leave an empty file behind on serialization failure
            try:
                os.unlink(file_path)
            except OSError:
                pass
            raise

        return file_path

    @staticmethod
    def read_saved_json(file_path: str) -> dict:
        return safe_read_from_json(file_path)

    @staticmethod
    def sanitize_title(title) -> str:
        if not title:
            return "untitled"
        title = str(title).replace(" ", "_").replace(":", "_")
        return title[: SaveManager.MAX_TITLE_LEN]

    # --- internals ---------------------------------------------------------

    def _resolve_directory(self, directory: Optional[Union[str, list]]) -> str:
        """Decide the target directory. Does NOT create it (save() does).

        list  → joined as-is, no date/model nesting (caller controls layout)
        str   → <directory>/<date>/<model>
        None  → <cwd>/response_data/<date>/<model>
        """
        if isinstance(directory, list):
            if not directory:
                raise ValueError("directory list cannot be empty")
            head = directory[0]
            if not os.path.isabs(head):
                head = os.path.join(os.getcwd(), head)
            return os.path.join(head, *directory[1:])

        root = directory or os.path.join(os.getcwd(), self.DEFAULT_ROOT_NAME)
        return os.path.join(root, self.date, self.model)

    def _open_unique(self) -> tuple[str, int]:
        """Atomically allocate a unique file. Returns (path, open fd)."""
        base = f"{self.title}.json"
        for index in range(self.MAX_NAME_ATTEMPTS):
            candidate = base if index == 0 else f"{self.title}_{index}.json"
            full = os.path.join(self.directory, candidate)
            try:
                fd = os.open(full, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
                return full, fd
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
        raise RuntimeError(
            f"could not allocate unique name for {self.title!r} "
            f"in {self.directory} after {self.MAX_NAME_ATTEMPTS} attempts"
        )
##class SaveManager:
##    """
##    Manages the saving of data. This class should provide methods to specify where (e.g., what database or file) and how (e.g., in what format) data should be saved.
##    """
##    def __init__(self, data={},title:str=None,directory:str=None,model:str='default')->None:
##        self.title=title
##        self.model=model
##        self.date = get_date()
##        if isinstance(directory,list):
##            abs_path = directory[0]
##            if not os.path.isabs(directory[0]):
##                abs_path = os.path.join(os.getcwd(), directory[0])
##                mkdirs(abs_path)
##            path = abs_path
##            for child in directory[1:]:
##                path = os.path.join(path, child)
##                mkdirs(path)
##            self.directory=path
##        else:
##            self.directory = mkdirs(directory or os.path.join(os.getcwd(), 'response_data'))
##            self.directory = mkdirs(os.path.join(self.directory, self.date))
##            self.directory = mkdirs(os.path.join(self.directory, self.model))
##        self.file_name = self.create_unique_file_name()
##        self.file_path = os.path.join(self.directory, self.file_name)
##        if data:
##            self.data = safe_json_loads(data)
##            self.data['file_path']=self.file_path
##            self.data['title']=self.title
##            self.data['model']=self.model
##            self.save_to_file(data = data,file_path = self.file_path)
##    def create_unique_file_name(self) -> str:
##        # Sanitize and shorten the title
##        sanitized_title = self.sanitize_title(self.title)
##
##        # Generate base file name
##        base_name = f"{sanitized_title}.json"
##        
##        # Check for uniqueness and append index if needed
##        unique_name = base_name
##        index = 1
##        while os.path.exists(os.path.join(self.directory, unique_name)):
##            unique_name = f"{sanitized_title}_{index}.json"
##            index += 1
##
##        return unique_name
##    @staticmethod
##    def sanitize_title(title: str) -> str:
##        if title:
##            # Replace spaces and special characters
##            title = str(title).replace(" ", "_").replace(":", "_")
##
##            # Limit the length of the title
##            max_length = 30
##            if len(title) > max_length:
##                title = title[:max_length]
##
##            return title
##    def save_to_file(self, data:dict, file_path:str)->None:
##        # Assuming `data` is already a dictionary, we convert it to a JSON string and save.
##        with open(file_path, 'w', encoding='utf-8') as file:
##            json.dump(data, file, ensure_ascii=False, indent=4)
##    
##    @staticmethod
##    def read_saved_json(file_path:str)->dict:
##        # Use 'safe_read_from_json' which is presumed to handle errors and return JSON
##        return safe_read_from_json(file_path)
##    
##    @staticmethod
##    def read_saved_json(file_path:str)->dict:
##        # Use 'safe_read_from_json' which is presumed to handle errors and return JSON
##        return safe_read_from_json(file_path)
