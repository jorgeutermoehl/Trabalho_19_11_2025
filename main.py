from funcoes import (
    autenticar_usuario,
    cadastrar_contato,
    cadastrar_usuario,
    carregar_dados,
    editar_contato,
    excluir_contato,
    listar_contatos,
    salvar_dados,
)


def painel_contatos(dados, usuario):
    while True:
        print('\n' + '=' * 40)
        print(f'Agenda de Contatos - Usuario: {usuario.get("login")}')
        print('=' * 40)
        print('1) Cadastrar contato')
        print('2) Listar contatos')
        print('3) Editar contato')
        print('4) Excluir contato')
        print('5) Sair da conta')

        escolha = input('Escolha uma opcao (1-5): ').strip()
        if escolha == '1':
            cadastrar_contato(dados, usuario)
            salvar_dados(dados)
        elif escolha == '2':
            listar_contatos(dados, usuario)
        elif escolha == '3':
            editar_contato(dados, usuario)
            salvar_dados(dados)
        elif escolha == '4':
            excluir_contato(dados, usuario)
            salvar_dados(dados)
        elif escolha == '5':
            print('Saindo da conta atual.')
            break
        else:
            print('Opcao invalida. Digite um numero de 1 a 5.')


def menu():
    dados = carregar_dados()
    while True:
        print('\n' + '=' * 40)
        print('Controle de Acesso')
        print('=' * 40)
        print('1) Fazer login')
        print('2) Cadastrar novo usuario')
        print('3) Sair do sistema')

        escolha = input('Escolha uma opcao (1-3): ').strip()
        if escolha == '1':
            usuario = autenticar_usuario(dados)
            if usuario:
                painel_contatos(dados, usuario)
        elif escolha == '2':
            if cadastrar_usuario(dados):
                salvar_dados(dados)
        elif escolha == '3':
            print('Saindo. Obrigado por usar a agenda!')
            break
        else:
            print('Opcao invalida. Digite 1, 2 ou 3.')


if __name__ == '__main__':
    try:
        menu()
    except KeyboardInterrupt:
        print('\nPrograma interrompido pelo usuario. Saindo...')
