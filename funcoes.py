import hashlib
import json
import os
import re
import shutil
from datetime import datetime
from getpass import getpass

DATA_DIR = os.path.join(os.path.dirname(__file__), 'dados')
CONTATOS_FILE = os.path.join(DATA_DIR, 'contatos.json')
LOG_FILE = os.path.join(DATA_DIR, 'log.txt')


def _estrutura_padrao():
    return {'usuarios': [], 'contatos': []}


def _ler_senha(mensagem: str) -> str:
    try:
        return getpass(mensagem)
    except Exception:
        # Fallback para ambientes sem suporte ao getpass
        return input(mensagem)


def _garantir_arquivos():
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
    except Exception:
        pass
    if not os.path.exists(CONTATOS_FILE):
        with open(CONTATOS_FILE, 'w', encoding='utf-8') as f:
            json.dump(_estrutura_padrao(), f, ensure_ascii=False, indent=2)
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, 'a', encoding='utf-8').close()


def _criar_backup(arquivo: str, motivo: str):
    base_nome = os.path.basename(arquivo)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    destino = os.path.join(DATA_DIR, f'{base_nome}.{motivo}.{timestamp}.bak')
    try:
        shutil.copy2(arquivo, destino)
        return destino
    except Exception:
        return None


def registrar_log(acao: str):
    _garantir_arquivos()
    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    linha = f'[{timestamp}] {acao}\n'
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(linha)
    except Exception:
        pass


def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()


def _usuario_padrao():
    return {
        'id': 1,
        'nome': 'Administrador',
        'login': 'admin',
        'senha_hash': hash_senha('admin'),
        'criado_em': datetime.now().isoformat(),
    }


def _migrar_dados_legados(contatos_antigos):
    dados = _estrutura_padrao()
    if contatos_antigos:
        usuario = _usuario_padrao()
        dados['usuarios'].append(usuario)
        ids_usados = set()
        proximo_id = 1
        for contato in contatos_antigos:
            contato['usuario_id'] = usuario['id']
            contato_id = contato.get('id')
            try:
                contato_id = int(contato_id)
            except (TypeError, ValueError):
                contato_id = None
            if contato_id is None or contato_id in ids_usados:
                while proximo_id in ids_usados:
                    proximo_id += 1
                contato['id'] = proximo_id
                ids_usados.add(proximo_id)
                proximo_id += 1
            else:
                contato['id'] = contato_id
                ids_usados.add(contato_id)
                if contato_id >= proximo_id:
                    proximo_id = contato_id + 1
        dados['contatos'] = contatos_antigos
        print('Estrutura migrada. Use login "admin" e senha "admin" para ver os contatos existentes.')
        registrar_log('Migra estrutura legada para modelo com usuarios')
    return dados


def carregar_dados():
    _garantir_arquivos()
    dados = _estrutura_padrao()
    try:
        with open(CONTATOS_FILE, 'r', encoding='utf-8') as f:
            dados = json.load(f)
    except json.JSONDecodeError as e:
        backup = _criar_backup(CONTATOS_FILE, 'corrompido')
        aviso = 'Arquivo de contatos corrompido. '
        if backup:
            aviso += f'Backup criado em {os.path.basename(backup)}.'
        else:
            aviso += 'Nao foi possivel criar backup automatico.'
        print(aviso)
        registrar_log(f'Falha ao carregar dados (JSON): {e}')
        dados = _estrutura_padrao()
    except FileNotFoundError:
        registrar_log('Arquivo de dados nao encontrado; sera criado um novo.')
        dados = _estrutura_padrao()
    except Exception as e:
        registrar_log(f'Falha inesperada ao carregar dados: {e}')
        dados = _estrutura_padrao()
    if isinstance(dados, list):
        dados = _migrar_dados_legados(dados)
    elif not isinstance(dados, dict):
        dados = _estrutura_padrao()
    dados.setdefault('usuarios', [])
    dados.setdefault('contatos', [])
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
        raise


def _proximo_id(itens):
    if not itens:
        return 1
    try:
        ids = [int(item.get('id', 0)) for item in itens if item.get('id') is not None]
        return max(ids) + 1
    except Exception:
        return len(itens) + 1


def _obter_usuario_por_login(dados, login: str):
    login = login.lower()
    for usuario in dados.get('usuarios', []):
        if str(usuario.get('login', '')).lower() == login:
            return usuario
    return None


def cadastrar_usuario(dados):
    print('\n--- Cadastro de Usuario ---')
    while True:
        nome = input('Nome completo: ').strip()
        if validar_nome(nome):
            break
    while True:
        login = input('Login desejado: ').strip()
        if len(login) < 3:
            print('Login deve ter pelo menos 3 caracteres.')
            continue
        if not re.match(r'^[\w\.-]+$', login):
            print('Use apenas letras, numeros, ponto, traco ou underline.')
            continue
        if _obter_usuario_por_login(dados, login):
            print('Login indisponivel. Tente outro.')
            continue
        break
    while True:
        senha = _ler_senha('Senha: ').strip()
        if len(senha) < 4:
            print('Senha deve ter pelo menos 4 caracteres.')
            continue
        confirma = _ler_senha('Confirme a senha: ').strip()
        if senha != confirma:
            print('As senhas nao conferem.')
            continue
        break
    usuario = {
        'id': _proximo_id(dados.get('usuarios', [])),
        'nome': nome,
        'login': login,
        'senha_hash': hash_senha(senha),
        'criado_em': datetime.now().isoformat(),
    }
    dados.setdefault('usuarios', []).append(usuario)
    salvar_dados(dados)
    registrar_log(f'Cadastro de usuario: {login}')
    print('Usuario cadastrado com sucesso!')
    return True


def autenticar_usuario(dados):
    print('\n--- Login ---')
    login = input('Login: ').strip()
    if not login:
        print('Informe o login.')
        return None
    senha = _ler_senha('Senha: ').strip()
    usuario = _obter_usuario_por_login(dados, login)
    if not usuario:
        print('Usuario nao encontrado.')
        registrar_log(f'Tentativa de login invalida: {login}')
        return None
    if usuario.get('senha_hash') != hash_senha(senha):
        print('Senha incorreta.')
        registrar_log(f'Senha incorreta para usuario: {login}')
        return None
    print(f'Bem-vindo, {usuario.get("nome")}')
    registrar_log(f'Login efetuado por: {login}')
    return usuario


def validar_nome(nome: str) -> bool:
    nome = nome.strip()
    if len(nome) < 3:
        print('Nome deve ter pelo menos 3 caracteres.')
        return False
    if any(ch.isdigit() for ch in nome):
        print('Nome nao deve conter numeros.')
        return False
    return True


def validar_email(email: str) -> bool:
    email = email.strip()
    if not email:
        print('E-mail nao pode ser vazio.')
        return False
    padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(padrao, email):
        print('E-mail em formato invalido.')
        return False
    return True


def validar_telefone(telefone: str) -> bool:
    telefone = telefone.strip()
    if not telefone:
        print('Telefone nao pode ser vazio.')
        return False
    digitos = re.sub(r'\D', '', telefone)
    if len(digitos) < 8 or len(digitos) > 11:
        print('Telefone deve ter entre 8 e 11 digitos.')
        return False
    return True


def _contatos_do_usuario(dados, usuario_id):
    return [
        contato
        for contato in dados.get('contatos', [])
        if contato.get('usuario_id') == usuario_id
    ]


def cadastrar_contato(dados, usuario):
    print('\n--- Cadastro de Novo Contato ---')
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
        'id': _proximo_id(dados.get('contatos', [])),
        'usuario_id': usuario.get('id'),
        'nome': nome,
        'telefone': telefone,
        'email': email,
    }
    dados.setdefault('contatos', []).append(novo)
    salvar_dados(dados)
    registrar_log(f'Cadastro de contato por {usuario.get("login")}: {nome}')
    print('Cadastro realizado com sucesso!')


def listar_contatos(dados, usuario):
    print('\n--- Lista de Contatos ---')
    contatos = _contatos_do_usuario(dados, usuario.get('id'))
    if not contatos:
        print('Nenhum contato cadastrado para este usuario.')
        return
    for c in contatos:
        print(f"ID: {c.get('id')} | Nome: {c.get('nome')} | Telefone: {c.get('telefone')} | E-mail: {c.get('email')}")
    print(f"\nTotal de contatos: {len(contatos)}")
    registrar_log(f'Listou contatos ({usuario.get("login")})')


def _encontrar_por_id(contatos, id_busca, usuario_id):
    for item in contatos:
        try:
            if int(item.get('id')) == int(id_busca) and item.get('usuario_id') == usuario_id:
                return item
        except Exception:
            continue
    return None


def editar_contato(dados, usuario):
    print('\n--- Editar Contato ---')
    contatos = _contatos_do_usuario(dados, usuario.get('id'))
    if not contatos:
        print('Nenhum contato para editar.')
        return
    id_str = input('Informe o ID do contato a editar: ').strip()
    contato = _encontrar_por_id(dados.get('contatos', []), id_str, usuario.get('id'))
    if not contato:
        print('Contato nao encontrado.')
        return
    print(f"Editando contato: {contato.get('nome')}")
    while True:
        entrada = input(f"Novo nome [{contato.get('nome')}]: ").strip()
        if not entrada:
            novo_nome = contato.get('nome')
            break
        if validar_nome(entrada):
            novo_nome = entrada
            break
    while True:
        entrada = input(f"Novo telefone [{contato.get('telefone')}]: ").strip()
        if not entrada:
            novo_tel = contato.get('telefone')
            break
        if validar_telefone(entrada):
            novo_tel = entrada
            break
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
    salvar_dados(dados)
    registrar_log(f'Edita contato ID {contato.get("id")} - {usuario.get("login")}')
    print('Contato atualizado com sucesso!')


def excluir_contato(dados, usuario):
    print('\n--- Excluir Contato ---')
    contatos = _contatos_do_usuario(dados, usuario.get('id'))
    if not contatos:
        print('Nenhum contato para excluir.')
        return
    id_str = input('Informe o ID do contato a excluir: ').strip()
    contato = _encontrar_por_id(dados.get('contatos', []), id_str, usuario.get('id'))
    if not contato:
        print('Contato nao encontrado.')
        return
    confirma = input(f"Confirma exclusao de '{contato.get('nome')}'? (s/N): ").strip().lower()
    if confirma == 's':
        dados.get('contatos', []).remove(contato)
        salvar_dados(dados)
        registrar_log(f'Exclui contato ID {contato.get("id")} - {usuario.get("login")}')
        print('Contato excluido com sucesso!')
    else:
        print('Exclusao cancelada.')
