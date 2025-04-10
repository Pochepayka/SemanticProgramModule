# server.py
from flask import Flask, jsonify, request # type: ignore
from flask_cors import CORS # type: ignore

from ProgramModule import ProgramModule

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для React

@app.route('/api/GraphematicAnalyze', methods=['POST'])
def GraphematicAnalyze():
    data = request.json
    received_text = data.get('text', '')
    
    # Здесь можно обработать полученный текст
    print(f"Получен текст с фронтенда: {received_text}")
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
    
    # Здесь можно обработать полученный текст
    print(f"Получен текст с фронтенда: {received_text}")
    PM = ProgramModule(received_text)

    graph_res = PM.graphem_res()
    clauses_res, words_res, tokens_res = PM.spliter_res(graph_res)
    #print(clauses_res)

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
    
    # Здесь можно обработать полученный текст
    print(f"Получен текст с фронтенда: {received_text}")
    PM = ProgramModule(received_text)

    graph_res = PM.graphem_res()
    clauses_res, words_res, tokens_res = PM.spliter_res(graph_res)
    morph_res_for_clauses, morph_res = PM.morph_res(clauses_res)
    print (morph_res)

    # Отправляем ответ обратно
    return jsonify({
        'message': f'Сервер получил: "{received_text}" (длина: {len(received_text)} символов)',
        'morph_res_for_clauses': morph_res_for_clauses,
        'morph_res': morph_res,
        
    })


def syntax_node_to_dict(node, include_parent=False):
    if node is None:
        return None
    
    result = {
        'type': node.type,
        'lemma': node.lemma,
        'features': node.features,
        'part_of_sentence': str(node.part_of_sentence),  # Convert enum to string
        'children': [syntax_node_to_dict(child, include_parent) for child in node.children],
        'connections': [
            {
                'type': conn.type if hasattr(conn, 'type') else str(conn),
                'target': syntax_node_to_dict(conn.target, include_parent) if hasattr(conn, 'target') else None
            } 
            for conn in node.connections
        ]
    }
    
    # Optional: include parent reference if needed (but beware of circular references)
    if include_parent and node.parent:
        result['parent'] = {
            'type': node.parent.type,
            'lemma': node.parent.lemma
        }
    
    return result

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


@app.route('/api/SintaxisAnalyze', methods=['POST'])
def SintaxisAnalyze():
    data = request.json
    received_text = data.get('text', '')
    
    # Здесь можно обработать полученный текст
    print(f"Получен текст с фронтенда: {received_text}")
    PM = ProgramModule(received_text)

    graph_res = PM.graphem_res()
    clauses_res, words_res, tokens_res = PM.spliter_res(graph_res)
    morph_res_for_clauses, morph_res = PM.morph_res(clauses_res)
    sintaxis_root, sintaxis_nodes, sintaxis_text_info, sintaxis_tree_in_txt = PM.sintaxis_res(clauses_res, morph_res_for_clauses, tokens_res)

    # Отправляем ответ обратно
    return jsonify({
        'message': f'Сервер получил: "{received_text}" (длина: {len(received_text)} символов)',
        'sintaxis_root': sintaxis_root,
        'sintaxis_nodes': sintaxis_nodes,
        'sintaxis_text_info': sintaxis_text_info,
        'sintaxis_tree_in_txt': sintaxis_tree_in_txt
    })

@app.route('/api/BuildSintaxisTree', methods=['POST'])
def BuildSintaxisTree():
    data = request.json
    received_text = data.get('text', '')
    
    # Здесь можно обработать полученный текст
    print(f"Получен текст с фронтенда: {received_text}")
    PM = ProgramModule(received_text)

    graph_res = PM.graphem_res()
    clauses_res, words_res, tokens_res = PM.spliter_res(graph_res)
    morph_res_for_clauses, morph_res = PM.morph_res(clauses_res)
    sintaxis_root, sintaxis_nodes, sintaxis_text_info, sintaxis_tree_in_txt = PM.sintaxis_res(clauses_res, morph_res_for_clauses, tokens_res)

    # Отправляем ответ обратно
    return jsonify({
        'message': f'Сервер получил: "{received_text}" (длина: {len(received_text)} символов)',
        'sintaxis_root': sintaxis_root,
        'sintaxis_nodes': sintaxis_nodes,
        'sintaxis_text_info': sintaxis_text_info,
        'sintaxis_tree_in_txt': sintaxis_tree_in_txt
    })

@app.route('/api/SemanticAnalize', methods=['POST'])
def SemanticAnalize():
    data = request.json
    received_text = data.get('text', '')
    
    # Здесь можно обработать полученный текст
    print(f"Получен текст с фронтенда: {received_text}")
    PM = ProgramModule(received_text)

    graph_res = PM.graphem_res()
    clauses_res, words_res, tokens_res = PM.spliter_res(graph_res)
    morph_res_for_clauses, morph_res = PM.morph_res(clauses_res)
    sintaxis_root, sintaxis_nodes, sintaxis_text_info, sintaxis_tree_in_txt = PM.sintaxis_res(clauses_res, morph_res_for_clauses, tokens_res)
    subjects, actions, objects, datas = PM.semantic_res(sintaxis_root)

    #print(datas)

    serializable_result = convert_nested_lists_to_dict(datas)
    print(serializable_result)

    # Отправляем ответ обратно
    return jsonify({
        'message': f'Сервер получил: "{received_text}" (длина: {len(received_text)} символов)',
        'data': serializable_result,
    })


@app.route('/api/connect', methods=['GET', 'POST'])
def handle_data():
    if request.method == 'POST':
        data = request.json
        return jsonify({"response": f"Received: {data['message']}"})
    else:
        return jsonify({"message": "Hello from Flask!"})



if __name__ == '__main__':
    app.run(port=5000, debug=True)