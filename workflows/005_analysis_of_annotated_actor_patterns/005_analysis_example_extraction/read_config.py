import configparser
import os
import pathlib

def read_config(file: str, absolute_file_location: str = ""):
    """
    Read configuration ini file from the configuration folder.
    The file must have Microsoft Windows INI structure.
    :param file: str
        name of the file

    :param absolute_file_location
        quick hack to get  read config work in a reasonable way
        Currently it reads from cda-data-cleaning/configurations which is not a good place if you want to use
        it as a tool in another workflow.

        If set read_config uses this location instead of the other location

    :return: ConfigParser

    Example:
    If the config file 'egcut_epi_microrun.example.ini' in the configurations folder contains lines:

        [luigi]
        folder = luigi_targets

    Then

        parser = read_config('egcut_epi_microrun.example.ini')
        parser['luigi']['folder']

    returns 'luigi_targets'
    """
    config = configparser.ConfigParser()

    if len(absolute_file_location) == 0:
        # We navigate from <checkout>/cda_data_cleaning/common to <checkout>/configurations, then add given file name
        config_file_full_name = os.path.join(
            pathlib.Path(__file__).parent.parent.parent.as_posix(), "configurations", file
        )
        config.read(config_file_full_name)
    else:
        config.read(absolute_file_location)

    # For production support we keep credentials in env. variables -- use those when available
    # DEBUG:
    #   ex = read_config('egcut_epi_microrun.example.ini')
    #   print(ex['database-configuration']['username'], ex['database-configuration']['password'])
    # OR: python -c "import cda_data_cleaning.common as c; ex = c.read_config('egcut_epi_microrun.example.ini');
    #     print(ex['database-configuration']['username'], ex['database-configuration']['password'])"
    #enriched_config = use_credentials_from_env_when_available(config)

    #return enriched_config
    return config



# NOTE: read_config() returns initialised ConfigParser that is fed into
#         cda_data_cleaning/common/db_operations.py -> create_connection()
#       to create connection into DB declared in 'database-configuration' section
# Following is mindlessly duplicated across many-many places (luigi tasks):
#         config = read_config(str(self.config_file))
#         schema = config['database-configuration']['work_schema']
#         role = config['database-configuration']['role']
