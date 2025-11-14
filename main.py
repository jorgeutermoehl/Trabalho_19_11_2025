from funcoes import (
    carregar_dados,
    salvar_dados,
    cadastrar_contato,
    listar_contatos,
    editar_contato,
    excluir_contato,
)


def menu():
    dados = carregar_dados()
    while True:
        print('\n' + '=' * 40)
        print('Agenda de Contatos - Menu Principal')
        print('=' * 40)
        print('1) Cadastrar contato')
        print('2) Listar contatos')
        print('3) Editar contato')
        print('4) Excluir contato')
        print('5) Sair')

        escolha = input('Escolha uma opção (1-5): ').strip()
        if escolha == '1':
            cadastrar_contato(dados)
            salvar_dados(dados)
        elif escolha == '2':
            listar_contatos(dados)
        elif escolha == '3':
            editar_contato(dados)
            salvar_dados(dados)
        elif escolha == '4':
            excluir_contato(dados)
            salvar_dados(dados)
        elif escolha == '5':
            print('Saindo. Obrigado por usar a Agenda de Contatos!')
            break
        else:
            print('Opção inválida. Digite um número de 1 a 5.')


if __name__ == '__main__':
    try:
        menu()
    except KeyboardInterrupt:
        print('\nPrograma interrompido pelo usuário. Saindo...')
