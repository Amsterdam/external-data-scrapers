from data_sources.importer_class import Importer


def get_latest_query(session, raw_model, model):
    """
    Deprecated and replaced by Importer class which contains
    the same method
    """

    importer = Importer()
    importer.clean_model = model
    importer.raw_model = raw_model
    return importer.get_latest_query()
