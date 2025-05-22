import zmq
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox

class ChatClient(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mini Chat ZeroMQ")
        self.geometry("400x500")

        # Perguntar nome e sala
        self.nome = simpledialog.askstring("Nome", "Digite seu nome:", parent=self)
        if not self.nome:
            messagebox.showerror("Erro", "Nome obrigatório!")
            self.destroy()
            return

        self.sala = simpledialog.askstring("Sala", "Digite a sala:", parent=self)
        if not self.sala:
            messagebox.showerror("Erro", "Sala obrigatória!")
            self.destroy()
            return

        # Config ZeroMQ
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.identity = self.nome.encode()
        self.socket.connect("tcp://localhost:5555")  # ajuste a porta se precisar

        self.socket.send_multipart([b"", f"ENTRAR||{self.sala}||{self.nome}".encode()])

        # Widgets
        self.text_area = scrolledtext.ScrolledText(self, state='disabled', wrap=tk.WORD)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.entry_message = tk.Entry(self)
        self.entry_message.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        self.entry_message.bind("<Return>", self.enviar_mensagem)

        self.btn_enviar = tk.Button(self, text="Enviar", command=self.enviar_mensagem)
        self.btn_enviar.pack(side=tk.RIGHT, padx=10, pady=10)

        # Thread para escutar mensagens
        self.thread = threading.Thread(target=self.escutar, daemon=True)
        self.thread.start()

    def escutar(self):
        while True:
            try:
                _, msg = self.socket.recv_multipart()
                texto = msg.decode()
                self.mostrar_mensagem(texto)
            except Exception as e:
                print(f"Erro ao receber mensagem: {e}")
                break

    def mostrar_mensagem(self, texto):
        # Atualiza a text_area no thread principal
        def atualizar():
            self.text_area.configure(state='normal')
            self.text_area.insert(tk.END, texto + "\n")
            self.text_area.configure(state='disabled')
            self.text_area.see(tk.END)
        self.after(0, atualizar)

    def enviar_mensagem(self, event=None):
        texto = self.entry_message.get().strip()
        if texto:
            self.socket.send_multipart([b"", f"MSG||{texto}".encode()])
            self.entry_message.delete(0, tk.END)

if __name__ == "__main__":
    app = ChatClient()
    app.mainloop()
