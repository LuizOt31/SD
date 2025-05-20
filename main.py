from sala import nova_sala


def entrar_sala():
    print("Em construção...")
    ...

def criar_sala():
    print("Sua sala será em que formato? (digite o número por favor)")
    print("1. Texto\n2. Audio\n3. Video")

    tipo_sala = input()
    if tipo_sala == 1:
        nova_sala()
    else: # Corrijir futuramente
        return

def main():
    '''
    Função principal que roda nosso "Skype"

    Há duas opções:
        * Entrar em uma sala
        * Criar uma sala, que consequentemente, entra nela também
    
    As salas podem ser de texto, voz e video. Será definido na hora que criar a sala.
    '''

    print("Digite o numero que deseja fazer")
    print("1. Entrar em uma sala\n2. Criar uma sala")
    aux = input()

    if aux == 1:
        entrar_sala()
    elif aux == 2:
        criar_sala()
    else:
        print("Vai toma no CU, faz essa porra direito")
        return


if __name__ == "__main__":
    main()