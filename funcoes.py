import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), 'dados')
CONTATOS_FILE = os.path.join(DATA_DIR, 'contatos.json')
LOG_FILE = os.path.join(DATA_DIR, 'log.txt')


def _garantir_arquivos():
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
    except Exception:
        pass
    if not os.path.exists(CONTATOS_FILE):
        with open(CONTATOS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, 'a', encoding='utf-8').close()


def registrar_log(acao: str):
    _garantir_arquivos()
    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    linha = f'[{timestamp}] {acao}\n'
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(linha)
    except Exception:
        pass


def carregar_dados():
    _garantir_arquivos()
    try:
        with open(CONTATOS_FILE, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            if not isinstance(dados, list):
                dados = []
    except Exception:
        dados = []
    registrar_log('Inicializa sistema e carrega dados')
    return dados


def salvar_dados(dados):
    _garantir_arquivos()
    try:
        with open(CONTATOS_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        registrar_log('Salva dados no arquivo')
    except Exception as e:
        registrar_log(f'Erro ao salvar dados: {e}')


def _proximo_id(dados):
    if not dados:
        return 1
    try:
        ids = [int(item.get('id', 0)) for item in dados]
        return max(ids) + 1
    except Exception:
        return len(dados) + 1


def cadastrar_contato(dados):
    print('\n--- Cadastro de Novo Contato ---')
    try:
        nome = input('Nome: ').strip()
        telefone = input('Telefone: ').strip()
        email = input('E-mail: ').strip()
        if not nome:
            print('Nome não pode ser vazio. Cadastro cancelado.')
            return
        novo = {
            'id': _proximo_id(dados),
            'nome': nome,
            'telefone': telefone,
            'email': email,
        }
        dados.append(novo)
        registrar_log(f'Cadastro de novo contato: {nome}')
        print('Cadastro realizado com sucesso!')
    except Exception as e:
        print('Ocorreu um erro ao cadastrar:', e)
        registrar_log(f'Erro no cadastro: {e}')


def listar_contatos(dados):
    print('\n--- Lista de Contatos ---')
    if not dados:
        print('Nenhum contato cadastrado.')
        return
    for c in dados:
        print(f"ID: {c.get('id')} | Nome: {c.get('nome')} | Telefone: {c.get('telefone')} | E-mail: {c.get('email')}")
    print(f"\nTotal de contatos: {len(dados)}")
    registrar_log('Listou contatos')


def _encontrar_por_id(dados, id_busca):
    for item in dados:
        try:
            if int(item.get('id')) == int(id_busca):
                return item
        except Exception:
            continue
    return None


def editar_contato(dados):
    print('\n--- Editar Contato ---')
    if not dados:
        print('Nenhum contato para editar.')
        return
    try:
        id_str = input('Informe o ID do contato a editar: ').strip()
        contato = _encontrar_por_id(dados, id_str)
        if not contato:
            print('Contato não encontrado.')
            return
        print(f"Editando contato: {contato.get('nome')}")
        novo_nome = input(f"Novo nome [{contato.get('nome')}]: ").strip() or contato.get('nome')
        novo_tel = input(f"Novo telefone [{contato.get('telefone')}]: ").strip() or contato.get('telefone')
        novo_email = input(f"Novo e-mail [{contato.get('email')}]: ").strip() or contato.get('email')
        contato['nome'] = novo_nome
        contato['telefone'] = novo_tel
        contato['email'] = novo_email
        registrar_log(f'Edita contato ID {contato.get("id")} - {contato.get("nome")}')
        print('Contato atualizado com sucesso!')
    except Exception as e:
        print('Erro ao editar contato:', e)
        registrar_log(f'Erro ao editar contato: {e}')


def excluir_contato(dados):
    print('\n--- Excluir Contato ---')
    if not dados:
        print('Nenhum contato para excluir.')
        return
    try:
        id_str = input('Informe o ID do contato a excluir: ').strip()
        contato = _encontrar_por_id(dados, id_str)
        if not contato:
            print('Contato não encontrado.')
            return
        confirma = input(f"Confirma exclusão de '{contato.get('nome')}'? (s/N): ").strip().lower()
        if confirma == 's':
            dados.remove(contato)
            registrar_log(f'Exclui contato ID {contato.get("id")} - {contato.get("nome")}')
            print('Contato excluído com sucesso!')
        else:
            print('Exclusão cancelada.')
    except Exception as e:
        print('Erro ao excluir contato:', e)
        registrar_log(f'Erro ao excluir contato: {e}')
