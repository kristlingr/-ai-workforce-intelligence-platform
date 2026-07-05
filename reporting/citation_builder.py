import pathlib
from config.settings import settings

class CitationBuilder:
    """
    Constructs compliant markdown citations and file URL links referencing
    ground-truth database records in the workspace.
    """
    @staticmethod
    def get_dataset_link(dataset_name: str) -> str:
        files = {
            "employees": "employees.csv",
            "worklogs": "worklogs.csv",
            "project_allocations": "project_allocations.csv",
            "attendance": "attendance.csv",
            "capacity": "capacity.csv"
        }
        name_clean = dataset_name.lower().replace(".csv", "").strip()
        filename = files.get(name_clean, f"{name_clean}.csv")
        
        # Use portable path via settings
        clean_path = settings.clean_datasets_dir / filename
            
        # Convert path to forward slashes for file:// scheme
        file_url = f"file:///{clean_path.as_posix()}"
        return f"[{filename}]({file_url})"
