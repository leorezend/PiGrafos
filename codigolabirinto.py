import requests
import websockets
import asyncio
import json

BASE_URL = "http://localhost:8000"

def cadastrar_grupo():
    url = f"{BASE_URL}/grupo"
    data = {"nome": "SÓ CANALHAS"}
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        grupo_id = response.json().get("GrupoId").replace("-","")
        return grupo_id
    else:
        print(f"Erro na requisição: {response.status_code}")
        print(f"Detalhes: {response.text}")
        return None

def iniciar_desafio(id_grupo, id_labirinto):
    url = f"{BASE_URL}/generate-websocket/"
    data = {"grupo_id": id_grupo, "labirinto_id": id_labirinto}
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        return response.json()["Conexao"]
    else:
        print(f"Erro ao iniciar o desafio: {response.status_code}")
        print(f"Detalhes: {response.text}")
        return None

def obter_labirintos(id_grupo):
    url = f"{BASE_URL}/labirintos/{id_grupo}"
    response = requests.get(url)
    print(f"{id_grupo}")
    print(response.text)
    if response.status_code == 200:
        dados = response.json()
        return dados.get("Labirintos", []) 
    else:
        print(f"Erro ao obter labirintos: {response.status_code}")
        print(f"Detalhes: {response.text}")
        return [] 

async def resolver_labirinto(ws_url, id_labirinto):
    async with websockets.connect(ws_url) as websocket:
        dados_iniciais = await websocket.recv()
        dados_iniciais = json.loads(dados_iniciais)
        print(f"Dados Iniciais: {dados_iniciais}")

        entrada = dados_iniciais["Entrada"]

        visitados = set()
        caminho = []
        await dfs(websocket, entrada, visitados, caminho)

        print("Caminho:", caminho)
        await websocket.send(json.dumps({"Desconectar": True}))

async def dfs(websocket, vertice_atual, visitados, caminho):
    if vertice_atual in visitados:
        return

    visitados.add(vertice_atual)
    caminho.append(vertice_atual)

    await websocket.send(f"Ir:{vertice_atual}")

    response = await websocket.recv()
    dados = json.loads(response)

    adjacencias = dados["Adjacencia"]
    print(f"Visitando vértice: {vertice_atual}, adjacentes: {adjacencias}")

    for vizinho in adjacencias:
        await dfs(websocket, vizinho[0], visitados, caminho)

async def main():
    grupo_id = cadastrar_grupo()
    if not grupo_id:
        print("Erro ao cadastrar o grupo.")
        return

    print(f"Grupo cadastrado com Id: {grupo_id}")

    labirintos = obter_labirintos(grupo_id)
    if not labirintos:
        print("Nenhum labirinto disponível.")
        return

    print(f"Labirintos disponíveis: {labirintos}")
    
    id_labirinto = labirintos[0]["IdLabirinto"]

    ws_url = iniciar_desafio(grupo_id, id_labirinto)
    if not ws_url:
        print("Erro ao obter o link do WebSocket.")
        return

    print(f"Conexão WebSocket iniciada: {ws_url}")

    await resolver_labirinto(ws_url, id_labirinto)

asyncio.run(main())