"""
Code to rename images from DamCams
For questions: Ignacio Aguirre (ignacio.aguirre@usask.ca)
Date: November, 11, 2022
Version: 3.0
Python version >3.7
"""
import numpy as np
import pandas as pd
import os
import glob
import datetime
import shutil
from pathlib import Path
from tqdm import tqdm


def get_list_all_images(dir):
    images = glob.glob(dir + '\**\*.JPG', recursive=True)
    total_images = len(images)
    return images, total_images


def get_list_all_directories(path):
    return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]


def new_date_name(mod_time, time_delta=0, print_seconds=False):
    mod_time = mod_time - datetime.timedelta(hours=time_delta, minutes=0)
    hour, minute, second = mod_time.hour, mod_time.minute, mod_time.second
    year, month, day = mod_time.year, mod_time.month, mod_time.day
    if print_seconds:
        new_name = '{}_{}_{}__{}_{}_{}'.format(year, month, day, hour, minute, second)
    else:
        new_name = '{}_{}_{}__{}_{}'.format(year, month, day, hour, minute)
    return new_name


def get_image_reason(image_path):
    mh = get_modified_time(image_path)
    hour, minute, second = mh.hour, mh.minute, mh.second
    if (minute == 0) and (second == 0) and hour in [8, 16, 0]:
        return 'Time'
    else:
        return 'Motion'


def get_image_reason_valid(image_path):
    mh = get_modified_time(image_path)
    hour, minute, second = mh.hour, mh.minute, mh.second
    if (minute == 0) and (second == 0):
        return 'Time'
    else:
        return 'Motion'


def get_modified_time(image_path):
    m_time = os.path.getmtime(image_path)
    dt_m = datetime.datetime.fromtimestamp(m_time)
    return dt_m


def get_created_time(image_path):
    c_time = os.path.getctime(image_path)
    dt_c = datetime.datetime.fromtimestamp(c_time)
    return dt_c


def collector_archivos_out(path_in):
    lista_salida = []
    os.chdir(path_in)
    for file in glob.iglob("*.JPG", recursive=True):
        lista_salida.append(file)
    return lista_salida


def collector_archivos_out2(path_in):
    files = []
    for dir, _, _ in os.walk(path_in):
        files.extend(glob(os.path.join(dir, '*.JPG')))
    return files


def create_full_name(date_part, old_info):
    full = '{}_{}_{}_{}__{}__{}.JPG'.format(study_area, place, download, folder, date_part, old_info)
    return full


def folder_name(folder, down_name):
    vals = dict(zip(range(100, 126), "abcdefghijklmnopqrstuvwxyz".upper()))
    num_folder = int(folder.split('R')[0])
    letter_folder = vals.get(num_folder)
    return down_name + letter_folder


def rename_and_report(input_folder, new_folder):
    list_files = collector_archivos_out(input_folder)

    df = pd.DataFrame(
        columns=['OldPath', 'NewName', 'NewPath', 'ModTime', 'CreatedTime', 'StudyArea', 'Place', 'Download',
                 'AuxFolder'], index=range(len(list_files)))

    for file in tqdm(range(0, len(list_files))):
        old_path = os.path.join(input_folder, list_files[file])

        just_name = list_files[file]
        just_name = just_name[:-4].replace('RCNX', '')
        current_file_name = list_files[file]
        mod_time = get_modified_time(list_files[file])
        created_time = get_created_time(list_files[file])
        date_part = new_date_name(mod_time)
        full_name = create_full_name(date_part, just_name)

        new_path = os.path.join(new_folder, full_name)
        shutil.copy2(old_path, new_path)

        df.loc[file].OldPath = old_path
        df.loc[file].NewName = full_name
        df.loc[file].NewPath = new_path
        df.loc[file].ModTime = mod_time
        df.loc[file].CreatedTime = created_time
        df.loc[file].StudyArea = study_area
        df.loc[file].Place = place
        df.loc[file].Download = download
        df.loc[file].AuxFolder = folder

    full = '{}_{}_{}_{}.csv'.format(study_area, place, download, folder)
    full_out = os.path.join(report_folder, full)
    df.to_csv(full_out)
    return df


# Basic data
input_g = r'd:\DamsCams_Renaming\Example_Data\Example_Place\Download_1\Place_1\DCIM'  # Input folder
study_area = 'ED'  # {Sibbald Fen: SF, Example Data: ED} #Code name of the study area
place = 'Dam0'  # Place
report_folder = r'd:\DamsCams_Renaming\Example_Data\Reports'  # Folder to save reports
output_folder = r'd:\DamsCams_Renaming\Example_Data\Renamed\Example_Place'  # Folder to save new renamed data
down_name = 'D1'

l_dir = get_list_all_directories(input_g)
for dir in l_dir:
    print('Folder: ', dir)

    download = folder_name(dir, down_name)
    new_path = os.path.join(output_folder, download)
    Path(new_path).mkdir(parents=True, exist_ok=True)

    old_folder = os.path.join(input_g, dir)
    folder = os.path.split(old_folder)[1].replace('RECNX', '')

    df = rename_and_report(old_folder, new_path)
