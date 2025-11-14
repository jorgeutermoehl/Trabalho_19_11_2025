import json
import os
import re
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


def validar_nome(nome: str) -> bool:
    nome = nome.strip()
    if len(nome) < 3:
        print('Nome deve ter pelo menos 3 caracteres.')
        return False
    if any(ch.isdigit() for ch in nome):
        print('Nome não deve conter números.')
        return False
    return True


def validar_email(email: str) -> bool:
    email = email.strip()
    if not email:
        print('E-mail não pode ser vazio.')
        return False
    padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(padrao, email):
        print('E-mail em formato inválido.')
        return False
    return True


def validar_telefone(telefone: str) -> bool:
    telefone = telefone.strip()
    if not telefone:
        print('Telefone não pode ser vazio.')
        return False
    digitos = re.sub(r'\D', '', telefone)
    if len(digitos) < 8 or len(digitos) > 11:
        print('Telefone deve ter entre 8 e 11 dígitos.')
        return False
    return True


def cadastrar_contato(dados):
    print('\n--- Cadastro de Novo Contato ---')
    try:
        while True:
            nome = input('Nome: ').strip()
            if validar_nome(nome):
                break
        while True:
            telefone = input('Telefone: ').strip()
            if validar_telefone(telefone):
                break
        while True:
            email = input('E-mail: ').strip()
            if validar_email(email):
                break
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
        # Nome
        while True:
            entrada = input(f"Novo nome [{contato.get('nome')}]: ").strip()
            if not entrada:
                novo_nome = contato.get('nome')
                break
            if validar_nome(entrada):
                novo_nome = entrada
                break
        # Telefone
        while True:
            entrada = input(f"Novo telefone [{contato.get('telefone')}]: ").strip()
            if not entrada:
                novo_tel = contato.get('telefone')
                break
            if validar_telefone(entrada):
                novo_tel = entrada
                break
        # E-mail
        while True:
            entrada = input(f"Novo e-mail [{contato.get('email')}]: ").strip()
            if not entrada:
                novo_email = contato.get('email')
                break
            if validar_email(entrada):
                novo_email = entrada
                break

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

