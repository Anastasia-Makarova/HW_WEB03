from abc import ABC, abstractmethod
import re
import shutil
import sys
from pathlib import Path


class Report(ABC):
    @abstractmethod
    def create_report(self, path: str):
        pass


class Console_report:
    def __init__(self, path: str) -> None:
        self._path = path


    def console_output(self, path: str) -> str:
        for element in Path(path).iterdir():
            if element.is_dir():
                print("\n", element.stem,":")
                self.console_output(Path(path).joinpath(element))
            else:
                print("    ", element.name)


class Create_txt_report:
    def __init__(self, path: str) -> None:
        self._path = path


    def create_report(self, path: str) -> str:
        path = Path(path)
        result = ""
        for k, v in dict_of_categories_files.items():
            result += f'{k.upper():^100}\n{v}\n'

        result += f'known_formats={known_formats}\nother_formats={other_formats}\n'

        
        report_filename = path.joinpath("sorting_report.txt")
        with open(str(report_filename), "w", encoding="utf-8") as report_file:
            report_file.write(result)



        return f"Folder '{path}' sorted successfully. See report file: '{report_filename.absolute()}'."



CATEGORIES = {'images':['.jpeg', '.png', '.jpg', '.svg'],
             'video':['.avi', '.mp4', '.mov', '.mkv'],
             'documents':['.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx'],
             'audio':['.mp3', '.ogg', '.wav', '.amr'],
             'archives':['.zip', '.gz', '.tar']}

dict_of_categories_files = {}

known_formats, other_formats = set(), set()

dict_of_files_for_duplicates = {}

root_path: Path = None

CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")
TRANSLATION_DICT = {}


def create_translation_dict() -> dict:  
    for cyr, lat in zip(CYRILLIC_SYMBOLS, TRANSLATION):
        TRANSLATION_DICT[ord(cyr)] = lat
        TRANSLATION_DICT[ord(cyr.upper())] = lat.upper()
    
    return TRANSLATION_DICT


def normalize(name_of_path:str) -> str:         
    return re.sub('\W', '_', name_of_path.translate(TRANSLATION_DICT))


def define_category(file_format:str) -> str:
    file_format = file_format.lower()
    if [k for k in CATEGORIES if file_format in CATEGORIES[k]]:
        return [d for d in CATEGORIES if file_format in CATEGORIES[d]][0]
    else:
        return 'other'
    

def sort_files_for_lists(category:str, file_name:str, file_format:str) -> None:  
    if category not in (dict_of_categories_files):
        dict_of_categories_files.update({category:[file_name]})
    else:
        dict_of_categories_files[category].append(file_name) 

    other_formats.add(file_format) if category == 'other' else known_formats.add(file_format)


def check_duplicates(file_name:str) -> int:
    if file_name not in dict_of_files_for_duplicates:
        dict_of_files_for_duplicates.update({file_name:1})
    else:
        dict_of_files_for_duplicates[file_name] = dict_of_files_for_duplicates[file_name] + 1

    return dict_of_files_for_duplicates[file_name]


def unpack_archive(archive:Path) -> None:
    path_for_unpacking_archives = str(archive)[:-(len(archive.suffix))]
    shutil.unpack_archive(archive, path_for_unpacking_archives)      


def removing_folders(current_folder:Path) -> None:
    if len([f for f in current_folder.iterdir()]) == 0:
        current_folder.rmdir()
        removing_folders(current_folder.parent)


def sort_folders(path:Path) -> None:    
    for i in path.iterdir():
        new_name = normalize(i.name.replace(i.suffix,'')) 
        
        if i.is_dir() and i.name not in (CATEGORIES):
            if len([f for f in i.iterdir()]) == 0:
                i.rmdir()       
            else:          
                i = i.rename(Path(i.parent).joinpath(new_name))
                path = (path).joinpath(i)                
                sort_folders (path)
                
        if i.is_file():
            category = define_category(i.suffix)
            target_path_to_create = Path(root_path).joinpath(category)
            
            if not target_path_to_create.exists():
                target_path_to_create.mkdir()

            sort_files_for_lists(category, i.name, i.suffix)
            count_of_duplicates = check_duplicates (i.name)
                
            new_name = new_name + '_' + str(count_of_duplicates) + i.suffix if count_of_duplicates > 1 else new_name + i.suffix
            
            destination_folder = Path(root_path).joinpath(category, new_name)  
            i.replace(destination_folder)
            
            if category == 'archives':
                unpack_archive(destination_folder)

            removing_folders(i.parent)


def sort_folder(path: str) -> str:
    global root_path
    root_path = Path(path)
    if not root_path.exists():
        return f"The specified folder {path} does not exist."
    create_translation_dict()
    sort_folders(Path(path))


def main():
    try:
        folder_path = Path(sys.argv[1])
    except IndexError:
        return "No path to folder"

    if not folder_path.exists():
        return "Folder does not exist. Try another path."
    

    sort_folder(folder_path)

    output = Console_report(folder_path)
    print(output.console_output(folder_path))
    result = Create_txt_report(folder_path)
    return result.create_report(folder_path)

if __name__  == "__main__":
    # main()
    print(main())