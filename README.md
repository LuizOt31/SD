# Aplicação canal de texto P2P

Esse projeto visa fazer um "whatsapp/Messager" simplificado usando ZeroMQ e sendo totalmente descentralizado (sem servidor envolvido no caso).

## Como funciona?

Usa o modelo do ZMQ Publisher-Subscriber (Pub-Sub), onde todo mundo é "cliente" (Subscriber) e "servidor" (Publisher) ao mesmo tempo.

Quando você inicializa este código, ele irá perguntar o identificador númerico da sala que deseja entrar... Na verdade não é bem entrar. Toda mensagem que você a mandar, terá no começo o identificador da sala. Assim, podemos ter o seguinte cenário:

- fulano A e fulana B se conectam na sala 1010
- fulana C e fulano D se conectam na sala 1000

No caso acima, A não enxerga C nem D, apena B.

Para A encontrar B para se comunicar, é lançado uma mensagem em broadcast na rede pelo protocolo UDP perguntando "Quem está na sala *num*? este é meu ip!". Se houver alguém nesta sala, irá mandar uma mensagem "Eu estou na sala *num*! Este é meu ip!", e um handshake é feito, onde o subscriber de cada peer se conectara no publisher do outro (se conectam pela porta "tcp://{ip}6000")

**Atenção:** A comunicação só funciona com pessoas que estao na mesma rede. Redes diferentes esse código não consegue lidar. A ideia do projeto era entender uma solução descentralizada de sistemas distribuidos.

## Como rodar?

É necessário rodar o ambiente virtual python

```sh
source bin/activate
```

Após isso, é necessário apenas rodar

```sh
python3 main.py
```