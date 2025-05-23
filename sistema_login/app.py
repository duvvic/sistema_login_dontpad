import customtkinter as ctk
from PIL import Image, ImageTk
import re
from database import Usuario, inicializar_db
import sys
import os
import webbrowser
import random
import string
from fastapi import FastAPI
from database import db
from hashlib import sha256

# --- INICIALIZAÇÃO DO BANCO DE DADOS ---
inicializar_db()
app = FastAPI()

# --- CONFIGURAÇÃO INICIAL ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def resource_path(relative_path):
    """Retorna o caminho absoluto para o arquivo, mesmo no modo .exe"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def gerar_codigo_aleatorio(tamanho=10):
    caracteres = string.ascii_letters + string.digits
    return "".join(random.choices(caracteres, k=tamanho))


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Login e Registro")
        self.geometry("400x550")
        self.resizable(False, False)

        self._setup_background()
        self._create_login_frame()

    def _setup_background(self):
        try:
            img_path = resource_path("foto_ceu.jpg")
            img = Image.open(img_path)
            img = img.resize((400, 550), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(img)
            self.bg_label = ctk.CTkLabel(self, image=self.bg_photo, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.bg_label.lower()
        except Exception:
            self.bg_label = None

    def _create_login_frame(self):
        self.login_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#222222")
        self.login_frame.place(
            relx=0.5, rely=0.5, anchor=ctk.CENTER, relwidth=0.85, relheight=0.75
        )

        ctk.CTkLabel(
            self.login_frame,
            text="BEM-VINDO!",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(pady=(30, 10))

        self.campo_usuario = self._create_labeled_entry(
            self.login_frame, "Usuário:", "Digite seu usuário"
        )
        self.campo_senha = self._create_labeled_entry(
            self.login_frame, "Senha:", "Digite sua senha", show="*"
        )

        self.button_login = ctk.CTkButton(
            self.login_frame,
            text="Entrar",
            command=self._validar_login,
            width=160,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.button_login.pack(pady=(25, 10))

        ctk.CTkLabel(
            self.login_frame, text="Não tem uma conta?", font=ctk.CTkFont(size=14)
        ).pack(pady=(10, 3))
        self.button_registrar = ctk.CTkButton(
            self.login_frame,
            text="Registre-se",
            command=self._abrir_registro,
            width=160,
            height=40,
            fg_color="#555555",
            hover_color="#777777",
            font=ctk.CTkFont(size=14),
        )
        self.button_registrar.pack()

        self.resultado_login = ctk.CTkLabel(
            self.login_frame, text="", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.resultado_login.pack(pady=15)

    def _create_labeled_entry(self, parent, label_text, placeholder, show=None):
        ctk.CTkLabel(parent, text=label_text, font=ctk.CTkFont(size=14)).pack(
            pady=(12, 2)
        )
        entry = ctk.CTkEntry(
            parent, placeholder_text=placeholder, width=230, height=38, show=show
        )
        entry.pack()
        return entry

    def _validar_login(self):
        nome = self.campo_usuario.get().strip()
        senha = sha256(self.campo_senha.get().strip().encode("ascii")).hexdigest()

        if not nome or not senha:
            return self._mostrar_mensagem(
                self.resultado_login, "Preencha todos os campos!", "red"
            )

        try:
            usuario = Usuario.get((Usuario.nome == nome) & (Usuario.senha == senha))
            self._mostrar_mensagem(
                self.resultado_login, f"Bem-vindo(a), {usuario.nome}!", "green"
            )

            if not usuario.codigo_aleatorio:
                usuario.codigo_aleatorio = gerar_codigo_aleatorio()
                usuario.save()

            url = f"https://dontpad.com/{usuario.codigo_aleatorio}"
            webbrowser.open(url)

            self.after(1500, self._abrir_aplicacao_principal)
        except Usuario.DoesNotExist:
            self._mostrar_mensagem(
                self.resultado_login, "Usuário ou senha incorretos.", "red"
            )
        except Exception as e:
            self._mostrar_mensagem(self.resultado_login, f"Erro inesperado: {e}", "red")

    def _mostrar_mensagem(self, label, mensagem, cor):
        label.configure(text=mensagem, text_color=cor)

    def _abrir_registro(self):
        if hasattr(self, "janela_registro") and self.janela_registro.winfo_exists():
            self.janela_registro.lift()
            return

        self.janela_registro = ctk.CTkToplevel(self)
        self.janela_registro.title("Registrar Novo Usuário")
        self.janela_registro.geometry("360x460")
        self.janela_registro.resizable(False, False)
        self.janela_registro.transient(self)
        self.janela_registro.grab_set()

        ctk.CTkLabel(
            self.janela_registro,
            text="Criar nova conta",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack(pady=20)

        self.campo_novo_usuario = self._create_labeled_entry(
            self.janela_registro, "Usuário:", "Escolha um nome de usuário"
        )
        self.campo_email = self._create_labeled_entry(
            self.janela_registro, "Email:", "Digite seu e-mail"
        )
        self.campo_nova_senha = self._create_labeled_entry(
            self.janela_registro,
            "Senha:",
            "Crie sua senha (min. 8 caracteres)",
            show="*",
        )

        self.resultado_registro = ctk.CTkLabel(
            self.janela_registro, text="", font=ctk.CTkFont(size=13)
        )
        self.resultado_registro.pack(pady=12)

        ctk.CTkButton(
            self.janela_registro,
            text="Concluir Registro",
            command=self._concluir_registro,
            width=220,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=15)

        self.janela_registro.protocol("WM_DELETE_WINDOW", self._fechar_janela_registro)

    def _fechar_janela_registro(self):
        self.janela_registro.grab_release()
        self.janela_registro.destroy()

    def _concluir_registro(self):
        nome = self.campo_novo_usuario.get().strip()
        email = self.campo_email.get().strip()
        senha = sha256(self.campo_nova_senha.get().strip().encode("ascii")).hexdigest()

        if not nome or not email or not senha:
            return self._mostrar_mensagem(
                self.resultado_registro, "Preencha todos os campos!", "red"
            )

        if len(senha) < 8:
            return self._mostrar_mensagem(
                self.resultado_registro, "Senha deve ter no mínimo 8 caracteres.", "red"
            )

        regex_email = r"^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        if not re.match(regex_email, email):
            return self._mostrar_mensagem(
                self.resultado_registro, "Email inválido.", "red"
            )

        try:
            if Usuario.select().where(Usuario.nome == nome).exists():
                return self._mostrar_mensagem(
                    self.resultado_registro, "Usuário já existe.", "red"
                )

            if Usuario.select().where(Usuario.email == email).exists():
                return self._mostrar_mensagem(
                    self.resultado_registro, "Email já cadastrado.", "red"
                )

            codigo = gerar_codigo_aleatorio()
            Usuario.create(nome=nome, email=email, senha=senha, codigo_aleatorio=codigo)

            self._mostrar_mensagem(
                self.resultado_registro,
                f"Usuário '{nome}' registrado com sucesso!",
                "green",
            )
            self.after(1500, self.janela_registro.destroy)

        except Exception as e:
            self._mostrar_mensagem(
                self.resultado_registro, f"Erro ao registrar: {e}", "red"
            )

    def _abrir_aplicacao_principal(self):
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()


def fechar_conexao_db():
    if not db.is_closed():
        db.close()
        print("[✓] Conexão com o banco de dados encerrada.")
