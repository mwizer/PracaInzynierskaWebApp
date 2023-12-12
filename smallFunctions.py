import os
import time
import pickle
import string
import secrets
import asyncio
import pandas as pd
import numpy as np

# global variable
TIME_TO_DELETE = 10  # time in minutes


async def delete_files(folder_path: str) -> None:
    """
    Background task that deletes old model files
    :param folder_path: Path to file \
    """
    global TIME_TO_DELETE
    print('tak')
    while True:
        now = time.time()
        print(now)
        for f in os.listdir(folder_path):
            path = os.path.join('.', folder_path, f)
            if os.stat(path).st_mtime < now - TIME_TO_DELETE * 60:
                os.remove(path)
        await asyncio.sleep(10)


def allowed_file(filename: str, allowed_extension: set) -> bool:
    """
    Check if file has correct extension

    :param filename: name of file
    :param allowed_extension: list of allowed extensions
    :return: True if file has correct extension, else return False
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extension


def allowed_model(filepath: str, allowed_models: list) -> bool:
    """
    Check if model in file is acceptable

    :param filepath: path to saved file
    :param allowed_models:
    :return: True if file has correct model, else return False
    """
    model = pickle.load(open(filepath, "rb"))
    return type(model) in allowed_models


def return_model(model: object, allowed_models: list) -> str:
    """
    Return model type
    :param model: sklearn GMM or CtGAN model
    :param allowed_models: list of allowed models
    :return: string representation of model
    """
    model_types = {0: 'GMM', 1: "CTGAN"}
    return model_types[allowed_models.index(type(model[0]))]


def generate_samples(mtype: str, nsamples: int, model_name=None) -> str:
    """
    Generate n samples using model
    :param mtype: type of used model
    :param nsamples: number of samples to generate
    :param model_name: name of model in use to generate. if None use original models
    :return: string representation of csv file with generated data
    """
    if int(nsamples) > 10000:
        nsamples = 10000

    if mtype == "GMM":
        default_columns = False
        if model_name is None:
            model_name = 'gmm.pickle'
            default_columns = True
        model = pickle.load(open(model_name, "rb"))
        samples = convert_to_df(model[0].sample(n_samples=int(nsamples))[0], column_names=default_columns)
    else:  # ctgan
        if model_name is None:
            model_name = 'ctgan.pickle'
        model = pickle.load(open(model_name, "rb"))
        samples = model[0].sample(int(nsamples))

    return samples.to_csv(index=False)


def generate_name() -> str:
    """
    Generate uniqe filename for model
    :return: Name for new file
    """
    filenames = [f for f in os.listdir('./uploads') if os.path.isfile(os.path.join('./uploads', f))]
    name = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(secrets.randbelow(10) + 10)) + '.pickle'
    if name in filenames:
        name = generate_name()

    return name


def convert_to_df(ar: np.array, column_names: bool) -> pd.DataFrame:
    """
    Convert numpy array to pandas dataframa for default models
    :param ar: samples generated from GMM method
    :param column_names: bool - True if we want to overwrite column names and types (default True for default models)
    :return: samples generated from GMM method as pd.DataFrame
    """
    ndf = pd.DataFrame(ar)
    if column_names:
        ndf.columns = ['Height (cm)', 'Body weight (kg)', 'SEX', 'Age',
                       'LDL cholesterol mg/dl', 'Cholesterol HDL mg/dl', 'Hypertension',
                       'Diabetes mellitus', 'CRP ultraczułe mg/l', 'Main ICD10']
        types = {'Height (cm)': 'int64',
                 'Body weight (kg)': 'float64',
                 'SEX': 'int64',
                 'Age': 'int64',
                 'LDL cholesterol mg/dl': 'int64',
                 'Cholesterol HDL mg/dl': 'int64',
                 'Hypertension': 'int64',
                 'Diabetes mellitus': 'int64',
                 'CRP ultraczułe mg/l': 'float64',
                 'Main ICD10': 'int64'}
        ndf = ndf.astype(types)
    return ndf
