""" Exportation to Various Formats (XSLX, PDF, PPTX, JSON) """
from libs.ui_generation import create_slides
from libs.ui_generation import output_to_json
from libs.ui_generation import create_pdf

from libs.metrics import metadata_to_dataset
from libs.utils import remove_temp_dir


def run_exports(analysis: dict, script: list):
    """Run Exports

    Exporter for UI items (PPTX, PDF, metadata.json, etc.)

    Arguments:
        analysis {dict} -- funds data object
        script {list} -- controlling list: dataset, funds, periods, config
    """
    config = script[3]

    create_slides(analysis, config=config)
    output_to_json(analysis, config)
    create_pdf(analysis, config=config)
    metadata_to_dataset(config=config)
    remove_temp_dir()
