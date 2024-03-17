import shutil
import pathlib
from sys import argv
from threading import Thread

# Можливі формати файлів для пошуку
FORMATS = {
'IMAGES' : ('JPEG', 'PNG', 'JPG', 'SVG', 'GIF', 'ICO'),
'VIDEO' : ('AVI', 'MP4', 'MOV', 'MKV', 'MPEG4'),
'TEXTDOC' : ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX', 'RTF'),
'MUSIC' : ('MP3', 'OGG', 'WAV', 'AMR'),
'ARCHIVES' : ('ZIP', 'GZ', 'TAR')
}

def normalize(data):
    # Строки які потрібні функції normalize для перекладу з кирилеці на латину
    SUMBOLS = '''!"#$%&'()*+№,-/:;<=>?@[\\]^_`{|}~ '''
    CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
    TRANSLATION = (
        "a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
    "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g"
    )
    if len(data.split('.')) > 1:
        name, file_format = data.split('.')[0], data.split('.')[-1]
    else:
        name, file_format = data.split('.')[0], ''
    result = ''
    for sumbol in name:
        if sumbol.lower() in CYRILLIC_SYMBOLS:
            index = CYRILLIC_SYMBOLS.index(sumbol.lower())
            if sumbol in CYRILLIC_SYMBOLS:
                result += TRANSLATION[index]
            else:
                result += TRANSLATION[index].upper()
        elif sumbol in SUMBOLS:
            result += '_'
        else:
            result += sumbol
    result += f".{file_format}"
    return result
    
def folder_creator_for_all_file_tipes(path:str):
    '''Створюємо папки в вказаному місці для сортування файлів'''
    # Також перевіривши чи таких ще не існує
    for key, value in FORMATS.items():
        if not pathlib.Path(f"{path}\\{key.lower()}").exists():
            pathlib.Path(f"{path}\\{key.lower()}").mkdir()
    if not pathlib.Path(str(path) + '\\other').exists():
        pathlib.Path(str(path) + '\\other').mkdir()

def delete_empty_folder(path):
    for file in pathlib.Path(path).iterdir():
        if file.is_dir():
            delete_empty_folder(file)
            if not any(file.iterdir()):
                pathlib.Path(file).rmdir()

def rename(path, name):
    new_name = name
    index = 1
    while True:
        if pathlib.Path(f"{path}\\{new_name}").exists() == False:
            return new_name
        if pathlib.Path(f"{path}\\{name}").exists() and index > 1:
           new_name = str(new_name.split('.')[0])[:-6] + '{:0>6}'.format(str(index)) + '.' + new_name.split('.')[-1]
        elif pathlib.Path(f"{path}\\{name}").exists() and name.split('.')[0].find('__rename__') == -1:
            new_name = new_name.split('.')[0] + f'__rename__{"{:0>6}".format(str(index))}.' + new_name.split('.')[-1]
        index +=1

def sorting(path, global_path = None):
    for item in pathlib.Path(path).iterdir():
        if item.is_dir() and str(item).split('\\')[-1].upper() in FORMATS.keys() or str(item).split('\\')[-1].lower() == 'other':
            continue
        elif item.is_dir():
            if global_path is not None:
                thread = Thread(target=sorting, args=(item, global_path))
                thread.start()
            else:
                thread = Thread(target=sorting, args=(item, path))
                thread.start()
        else:
            file_format = str(item).split("\\")[-1].split('.')[-1]
            for key , value in FORMATS.items():
                if global_path is None:
                    if file_format.upper() in value:
                        new_name = rename(f"{path}\\{key.lower()}",str(item).split("\\")[-1])
                        new_name = normalize(new_name)
                        pathlib.Path(item).replace(f"{path}\\{key.lower()}\\{new_name}")
                else:
                    if file_format.upper() in value:
                        new_name = rename(f"{global_path}\\{key.lower()}",str(item).split("\\")[-1])
                        new_name = normalize(new_name)
                        pathlib.Path(item).replace(f"{global_path}\\{key.lower()}\\{new_name}")
            if pathlib.Path(item).exists():
                if global_path is None:
                    new_name = rename(f"{path}\\other",str(item).split("\\")[-1])
                    new_name = normalize(new_name)
                    pathlib.Path(item).replace(f"{path}\\other\\{new_name}")
                else:
                    new_name = rename(f"{global_path}\\other",str(item).split("\\")[-1])
                    new_name = normalize(new_name)
                    pathlib.Path(item).replace(f"{global_path}\\other\\{new_name}")

def unpacking_archive(file):
    # Відділяє формат файлу від загальної назви щоб в подпльшому назвати папку такою ж назвою як файл але без формату у кінці назви
    format_of_file = str(file).split('\\')[-1].split(".")[-1]
    # Розпаковує архів у папці archives створивши для розпакованих файлів папку з ідентичною назвою до файлу 
    try:
        shutil.unpack_archive(file, f"{'\\'.join(i for i in str(file).split('\\')[:-1])}\\{str(file).split('\\')[-1].split('.')[0]}")
    #Якщо винекне проблема що на архівному файлі було встановнено пароль файл буде пропущено
    except RuntimeError:
        pass
    except shutil.ReadError:
        pass

def main(path):
    if not pathlib.Path(path).exists():
        print(f'Sorry. {path} not exist')
    else:
        folder_creator_for_all_file_tipes(path)
        sorting(path)
        delete_empty_folder(path)
        if pathlib.Path(f"{path}\\archives").exists():
            for file in pathlib.Path(f"{path}\\archives").iterdir():
                thread = Thread(target=unpacking_archive, args=(file,))
                thread.start()
            delete_empty_folder(path)
        print(f"Files in {path} sorted")

def terminal_starter():
    # Обробляємо помилку якщо було передано неправильні значення для запуску програми
    # Та запускаємо саму програму з терміналу
    try:
        path_to_sorting = argv
        if len(path_to_sorting) == 2:
            main(path_to_sorting[1])
    except IndexError:
        print('After name of file sort.py must be path to folder what you want sorting')


# main(r'C:\Users\Administrator\Desktop\sort_folder')


