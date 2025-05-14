# server.py
from flask import Flask, jsonify, request # type: ignore
from flask_cors import CORS # type: ignore
from ProgramModule import ProgramModule

import xml.etree.ElementTree as ET

import os
import tempfile


def convert_nested_lists_to_dict(nested_lists):
    """
    Рекурсивно преобразует вложенные структуры в словари.
    Пустые списки преобразуются в {type: None, word: None, part_of_sentence: None}
    """
    if isinstance(nested_lists, list):
        if not nested_lists:  # Если список пустой
            return [{
                'type': None,
                'word': None,
                'part_of_sentence': None
            }]
        return [convert_nested_lists_to_dict(item) for item in nested_lists]
    elif hasattr(nested_lists, '__dict__'):
        features = getattr(nested_lists, 'features', {})
        
        pos = getattr(nested_lists, 'part_of_sentence', None)
        pos_value = pos.value if hasattr(pos, 'value') else str(pos) if pos else None
        
        return {
            'type': getattr(nested_lists, 'pos', None) or getattr(nested_lists, 'type', None),
            'word': features.get('word'),
            'part_of_sentence': pos_value
        }
    else:
        return {
            'type': None,
            'word': None,
            'part_of_sentence': None
        }
    
# Функция конвертации GraphML в JSON (без xmltodict)
def parse_graphml(file_path):
    """Парсим GraphML с помощью стандартного xml.etree"""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        ns = {'g': 'http://graphml.graphdrawing.org/xmlns'}
        nodes = []
        edges = []

        # Парсим узлы
        for node in root.findall('.//g:node', ns):
            node_id = node.get('id')
            label = node.find('.//g:data[@key="d0"]', ns).text if node.find('.//g:data[@key="d0"]', ns) is not None else ''
            color = node.find('.//g:data[@key="d1"]', ns).text if node.find('.//g:data[@key="d1"]', ns) is not None else '#FFFFFF'
            
            nodes.append({
                'id': node_id,
                'label': label.split('word: ')[-1] if 'word: ' in label else '',
                'color': color,
                'pos': label.split('pos: ')[1].split('\n')[0] if 'pos: ' in label else ''
            })

        # Парсим связи
        for edge in root.findall('.//g:edge', ns):
            edges.append({
                'from': edge.get('source'),
                'to': edge.get('target'),
                'label': edge.find('.//g:data[@key="d2"]', ns).text if edge.find('.//g:data[@key="d2"]', ns) is not None else '',
                'color': edge.find('.//g:data[@key="d3"]', ns).text if edge.find('.//g:data[@key="d3"]', ns) is not None else '#000000'
            })

        return {'nodes': nodes, 'edges': edges}

    except Exception as e:
        print(f"Ошибка парсинга GraphML: {str(e)}")
        return {'nodes': [], 'edges': []}



app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})

@app.route('/api/GraphematicAnalyze', methods=['POST'])
def GraphematicAnalyze():
    data = request.json
    received_text = data.get('text', '')
    #print(f"Получен текст с фронтенда: {received_text}")

    PM = ProgramModule(received_text)
    graph_res = PM.graphem_res()

    # Отправляем ответ обратно
    return jsonify({
        'message': f'Сервер получил: "{received_text}" (длина: {len(received_text)} символов)',
        'graph_res': graph_res
    })


@app.route('/api/Spliter', methods=['POST'])
def Spliter():
    data = request.json
    received_text = data.get('text', '')
    #print(f"Получен текст с фронтенда: {received_text}")

    PM = ProgramModule(received_text)
    graph_res = PM.graphem_res()
    clauses_res, words_res, tokens_res = PM.spliter_res(graph_res)

    # Отправляем ответ обратно
    return jsonify({
        'message': f'Сервер получил: "{received_text}" (длина: {len(received_text)} символов)',
        'clauses_res': clauses_res,
        'words_res': words_res,
        'tokens_res': tokens_res,
    })


@app.route('/api/MorphAnalyze', methods=['POST'])
def MorphAnalyze():
    data = request.json
    received_text = data.get('text', '')
    #print(f"Получен текст с фронтенда: {received_text}")

    PM = ProgramModule(received_text)
    graph_res = PM.graphem_res()
    clauses_res, words_res, tokens_res = PM.spliter_res(graph_res)
    morph_res_for_clauses, morph_res = PM.morph_res(clauses_res)

    # Отправляем ответ обратно
    return jsonify({
        'message': f'Сервер получил: "{received_text}" (длина: {len(received_text)} символов)',
        'morph_res_for_clauses': morph_res_for_clauses,
        'morph_res': morph_res,
        
    })


@app.route('/api/SintaxisAnalyze', methods=['POST'])
def SintaxisAnalyze():
    data = request.json
    received_text = data.get('text', '')
    #print(f"Получен текст с фронтенда: {received_text}")

    PM = ProgramModule(received_text)
    graph_res = PM.graphem_res()
    clauses_res, words_res, tokens_res = PM.spliter_res(graph_res)
    morph_res_for_clauses, morph_res = PM.morph_res(clauses_res)
    sintaxis_root, sintaxis_nodes, sintaxis_text_info, sintaxis_tree_in_txt, path_to_graphml, graph, sintaxis_text_info_txt = PM.sintaxis_res(morph_res_for_clauses)

    tokens, links = PM.collect_links_and_node(sintaxis_nodes, tokens_res)

    graphData = parse_graphml(path_to_graphml)


    # Отправляем ответ обратно
    return jsonify({
        'message': f'Сервер получил: "{received_text}" (длина: {len(received_text)} символов)',
        'sintaxis_text_info': sintaxis_text_info,
        "sintaxis_text_info_txt" : sintaxis_text_info_txt,
        "sintaxis_tree_in_txt": sintaxis_tree_in_txt,
        'tokens': tokens,
        "links" : links,
        'graphData': graphData,
    })

# @app.route('/api/BuildSintaxisTree', methods=['POST'])
# def BuildSintaxisTree():
#     data = request.json
#     received_text = data.get('text', '')
    
#     # Здесь можно обработать полученный текст
#     print(f"Получен текст с фронтенда: {received_text}")
#     PM = ProgramModule(received_text)

#     graph_res = PM.graphem_res()
#     clauses_res, words_res, tokens_res = PM.spliter_res(graph_res)
#     morph_res_for_clauses, morph_res = PM.morph_res(clauses_res)
#     sintaxis_root, sintaxis_nodes, sintaxis_text_info, sintaxis_tree_in_txt, path_to_graphml, graph = PM.sintaxis_res(clauses_res, morph_res_for_clauses, tokens_res)



#     # Получаем данные графа
#     graphData = parse_graphml(path_to_graphml)

#     # print(f"\n\n\n {graphData} \n\n\n")

#     # Отправляем ответ обратно
#     return jsonify({
#         'message': f'Сервер получил: "{received_text}" (длина: {len(received_text)} символов)',
#         # 'sintaxis_root': sintaxis_root,
#         # 'sintaxis_nodes': sintaxis_nodes,
#         # 'sintaxis_text_info': sintaxis_text_info,
#         # 'sintaxis_tree_in_txt': sintaxis_tree_in_txt,
#         'graphData': graphData,
#     })

@app.route('/api/SemanticAnalize', methods=['POST'])
def SemanticAnalize():
    data = request.json
    received_text = data.get('text', '')
    #print(f"Получен текст с фронтенда: {received_text}")

    PM = ProgramModule(received_text)
    graph_res = PM.graphem_res()
    clauses_res, words_res, tokens_res = PM.spliter_res(graph_res)
    morph_res_for_clauses, morph_res = PM.morph_res(clauses_res)
    sintaxis_root, _, _, _, _, _, _ \
        = PM.sintaxis_res(morph_res_for_clauses)
    semantic_table = PM.semantic_res(sintaxis_root)
    serializable_result = convert_nested_lists_to_dict(semantic_table)

    # Отправляем ответ обратно
    return jsonify({
        'message': f'Сервер получил: "{received_text}" (длина: {len(received_text)} символов)',
        'semantic_table': serializable_result,
    })


@app.route('/api/connect', methods=['GET', 'POST'])
def handle_data():
    if request.method == 'POST':
        data = request.json
        return jsonify({"response": f"Received: {data['message']}"})
    else:
        return jsonify({"message": "Hello from Flask!"})



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)