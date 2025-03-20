import json


def FromJSON(name_dict):
    """Импортирование словаря из JSON-файла."""
    with open(name_dict, 'r', encoding='utf-8') as f:
        loaded_dict = json.load(f)
    return loaded_dict

def ToJSON(my_dict, name_dict="new_dict"):
    """Сохранение словаря в JSON-файл."""

    # Преобразуем множества в списки
    def convert_sets_to_lists(obj):
        if isinstance(obj, dict):
            return {key: convert_sets_to_lists(value) for key, value in obj.items()}
        elif isinstance(obj, set):
            return list(obj)  # Преобразуем множество в список
        elif isinstance(obj, list):
            return [convert_sets_to_lists(item) for item in obj]
        else:
            return obj

    # Преобразуем входной словарь
    my_dict = convert_sets_to_lists(my_dict)

    # Сохраняем преобразованный словарь в JSON
    with open(name_dict + '.json', 'w', encoding='utf-8') as f:
        json.dump(my_dict, f, ensure_ascii=False)

    return name_dict + '.json'
