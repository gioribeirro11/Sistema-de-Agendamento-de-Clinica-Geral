# =========================================================
# 1. IMPORTANDO AS FERRAMENTAS (BIBLIOTECAS)
# =========================================================
import tkinter as tk               # Biblioteca nativa para criação de janelas e interfaces
from tkinter import ttk            # Extensão do tkinter para widgets com visual moderno e abas
from tkinter import messagebox     # Módulo para exibição de janelas de alerta e confirmação
import json                        # Utilizado para converter listas/dicionários em texto para o banco de dados
import os                          # Gerencia caminhos de arquivos e verifica existência de pastas
import re                          # Expressões regulares para filtrar e validar CPFs e datas
import datetime                    # Essencial para cálculos de datas úteis e validação de horários
import random                      # Gera números aleatórios para criar os protocolos de atendimento

# =========================================================
# 2. GERENCIADOR DE DADOS 
# =========================================================
class GerenciadorDados:
    """
    Esta classe abstrai a manipulação do arquivo JSON. 
    Serve para garantir que o código da interface não precise lidar com leitura/escrita de arquivos.
    """
    def __init__(self, nome_arquivo="agendamentos.json"):
        # Localiza o diretório onde o script está rodando para salvar o banco no mesmo local
        self.diretorio_base = os.path.dirname(os.path.abspath(__file__))
        self.caminho_completo = os.path.join(self.diretorio_base, nome_arquivo)

    def carregar(self):
        """
        Tenta abrir o arquivo JSON. Se o arquivo não existir ou estiver corrompido, 
        retorna uma lista vazia para evitar que o programa trave.
        """
        if not os.path.exists(self.caminho_completo):
            return []
        try:
            with open(self.caminho_completo, "r", encoding="utf-8") as arquivo:
                return json.load(arquivo)
        except Exception as erro:
            print(f"Erro ao ler banco de dados: {erro}")
            return []

    def salvar(self, dados):
        """
        Converte a lista de agendamentos em formato JSON e grava no disco. 
        Usa ensure_ascii=False para preservar acentos em nomes brasileiros.
        """
        try:
            with open(self.caminho_completo, "w", encoding="utf-8") as arquivo:
                json.dump(dados, arquivo, indent=4, ensure_ascii=False)
            return True
        except Exception as erro:
            messagebox.showerror("Erro Crítico", f"Falha ao salvar no disco: {erro}")
            return False


# =========================================================
# 3. APLICATIVO PRINCIPAL 
# =========================================================
class SistemaAgendamento(tk.Tk):
    """
    Classe principal que herda de tk.Tk. Ela gerencia tanto a interface visual 
    quanto a lógica de validação dos agendamentos.
    """
    def __init__(self):
        super().__init__()

        # Configura o título e o tamanho fixo da janela principal
        self.title("Sistema de Agendamento Clínico")
        self.geometry("700x650")
        
        # Inicializa o arquivista e carrega os dados existentes para a memória
        self.banco_dados = GerenciadorDados()
        self.agendamentos = self.banco_dados.carregar()
        
        # Monta os componentes visuais
        self.construir_interface()
        # Popula a lista de horários pela primeira vez
        self.atualizar_horarios()

    # ---------------------------------------------------------
    # REGRAS DE TEMPO 
    # ---------------------------------------------------------
    def listar_datas_uteis(self):
        """
        Lógica para gerar as opções do menu suspenso. 
        Calcula os próximos 10 dias a partir de hoje, ignorando domingos.
        """
        datas = []
        hoje = datetime.date.today()
        while len(datas) < 10:
            if hoje.weekday() != 6:
                datas.append(hoje.strftime('%d/%m/%Y'))
            hoje += datetime.timedelta(days=1)
        return datas

    def atualizar_horarios(self, event=None):
        """
        Função reativa: sempre que o usuário muda a data, esta função recalcula 
        os horários disponíveis, filtrando os já ocupados no JSON e horários que já passaram.
        """
        data_selecionada = self.combo_data.get()
        horarios_livres = []
        agora = datetime.datetime.now()
        
        # Define o início e fim do expediente para o laço de repetição
        hora_atual_loop = datetime.datetime.strptime("08:00", "%H:%M")
        hora_fim_loop = datetime.datetime.strptime("22:00", "%H:%M")
        
        while hora_atual_loop <= hora_fim_loop:
            horario_texto = hora_atual_loop.strftime("%H:%M")
            
            # Verifica se já existe um agendamento para este par Data/Hora no banco
            ocupado = any(f['data'] == data_selecionada and f['horario'] == horario_texto for f in self.agendamentos)
            
            # Se a data for hoje, impede agendamentos em horários que já passaram do relógio atual
            passado = False
            if data_selecionada == agora.strftime('%d/%m/%Y'):
                if hora_atual_loop.time() <= agora.time():
                    passado = True
            
            if not ocupado and not passado:
                horarios_livres.append(horario_texto)
                
            hora_atual_loop += datetime.timedelta(minutes=30) # Incremento de 30 em 30 min
        
        # Atualiza visualmente o widget Combobox com as novas opções filtradas
        if horarios_livres:
            self.combo_horario['values'] = horarios_livres
            self.combo_horario.set(horarios_livres[0])
        else:
            self.combo_horario['values'] = ["Sem horários"]
            self.combo_horario.set("Sem horários")

    # ---------------------------------------------------------
    # AÇÕES DOS BOTÕES
    # ---------------------------------------------------------
    def registrar_agendamento(self):
        """
        Coleta os dados dos campos de entrada, aplica Regex para limpar CPF e data, 
        valida a existência de sobrenome e gera um protocolo único de 9 dígitos.
        """
        nome_puro = self.ent_nome.get()
        cpf_puro = self.ent_cpf.get()
        nasc_puro = self.ent_nasc.get()
        
        # Validação: impede nomes sem sobrenome para evitar duplicidade de homônimos
        nome_limpo = nome_puro.strip()
        if len(nome_limpo.split()) < 2:
            messagebox.showwarning("Aviso", "Por favor, digite o NOME e o SOBRENOME.")
            return

        # Regex: remove qualquer caractere que não seja número do CPF
        numeros_cpf = re.sub(r'\D', '', cpf_puro)
        if len(numeros_cpf) != 11:
            messagebox.showerror("Erro", "CPF inválido (deve ter 11 números).")
            return
        cpf_pronto = f"{numeros_cpf[:3]}.{numeros_cpf[3:6]}.{numeros_cpf[6:9]}-{numeros_cpf[9:]}"

        # Validação de Data de Nascimento: converte texto em objeto date para checar se é real
        numeros_nasc = re.sub(r'\D', '', nasc_puro)
        if len(numeros_nasc) != 8:
            messagebox.showerror("Erro", "Data de nascimento deve ter 8 números.")
            return
            
        try:
            dia, mes, ano = int(numeros_nasc[:2]), int(numeros_nasc[2:4]), int(numeros_nasc[4:])
            data_nasc_real = datetime.date(ano, mes, dia)
            if data_nasc_real > datetime.date.today():
                messagebox.showerror("Erro", "Data não pode ser no futuro.")
                return
            nasc_pronto = data_nasc_real.strftime("%d/%m/%Y")
        except ValueError:
            messagebox.showerror("Erro", "Data de nascimento inexistente.")
            return
            
        # Loop para garantir que o protocolo gerado não coincida com um existente
        while True:
            protocolo_novo = str(random.randint(100000000, 999999999))
            if not any(ag['protocolo'] == protocolo_novo for ag in self.agendamentos):
                break
                
        # Montagem do dicionário (objeto) que será salvo no JSON
        novo_agendamento = {
            "protocolo": protocolo_novo,
            "nome": nome_puro.title(),
            "cpf": cpf_pronto,
            "nascimento": nasc_pronto,
            "data": self.combo_data.get(),
            "horario": self.combo_horario.get()
        }
        
        # Atualiza a memória e persiste os dados no arquivo físico
        self.agendamentos.append(novo_agendamento)
        self.banco_dados.salvar(self.agendamentos)
        
        messagebox.showinfo("Sucesso", f"Agendamento Finalizado ✅\nProtocolo: {protocolo_novo}")
        
        # Limpa os campos da tela e reseta os horários para o próximo uso
        self.ent_nome.delete(0, 'end')
        self.ent_cpf.delete(0, 'end')
        self.ent_nasc.delete(0, 'end')
        self.atualizar_horarios()

    def pesquisar_agendamento(self):
        """
        Filtra a lista de agendamentos em memória com base no termo digitado. 
        A busca é 'case-insensitive' e funciona por Nome, CPF ou Protocolo.
        """
        termo = self.ent_busca.get().lower()
        termo_numero = re.sub(r'\D', '', termo)
        
        resultados = [ag for ag in self.agendamentos if 
                     termo in ag['nome'].lower() or 
                     termo == ag['protocolo'] or 
                     termo_numero == re.sub(r'\D', '', ag['cpf'])]
                
        # Gerencia o estado do widget de texto (deve estar normal para editar e disabled para o usuário não digitar nele)
        self.txt_lista.config(state="normal")
        self.txt_lista.delete("1.0", "end")
        
        if resultados:
            for ag in resultados:
                self.txt_lista.insert("end", f"[{ag['protocolo']}] - {ag['data']} às {ag['horario']} | {ag['nome']}\n")
        else:
            self.txt_lista.insert("end", "Nenhum paciente encontrado.")
            
        self.txt_lista.config(state="disabled")

    def cancelar_agendamento(self):
        """
        Remove um registro do banco de dados baseado no protocolo exato. 
        Exige confirmação do usuário antes de deletar permanentemente.
        """
        protocolo_alvo = self.ent_cancela.get()
        ficha_encontrada = next((ag for ag in self.agendamentos if ag['protocolo'] == protocolo_alvo), None)
        
        if ficha_encontrada:
            if messagebox.askyesno("Atenção", f"Cancelar consulta de {ficha_encontrada['nome']}?"):
                self.agendamentos.remove(ficha_encontrada) # Remove da lista em memória
                self.banco_dados.salvar(self.agendamentos) # Atualiza o arquivo JSON
                messagebox.showinfo("Cancelado", "Consulta cancelada.")
                self.ent_cancela.delete(0, 'end')
                self.pesquisar_agendamento() # Atualiza a lista de busca
                self.atualizar_horarios()    # Libera o horário na primeira aba
        else:
            messagebox.showerror("Erro", "Protocolo não encontrado.")

    # ---------------------------------------------------------
    # CONSTRUÇÃO DA TELA 
    # ---------------------------------------------------------
    def construir_interface(self):
        """
        Define toda a estrutura hierárquica da interface:
        Notebook (Abas) -> Frame (Aba) -> Widgets (Labels, Buttons, Entries).
        """
        self.abas = ttk.Notebook(self)
        self.abas.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Criação das superfícies das abas
        aba1 = ttk.Frame(self.abas)
        aba2 = ttk.Frame(self.abas)
        self.abas.add(aba1, text="Agendar Consulta")
        self.abas.add(aba2, text="Consultar / Cancelar")

        # --- Elementos da Aba de Cadastro ---
        ttk.Label(aba1, text="Nome Completo do Paciente:", font=("Arial", 11, "bold")).pack(pady=(15,0))
        self.ent_nome = ttk.Entry(aba1, width=50)
        self.ent_nome.pack(pady=5)
        
        ttk.Label(aba1, text="CPF (apenas números):", font=("Arial", 11, "bold")).pack(pady=(10,0))
        self.ent_cpf = ttk.Entry(aba1, width=50)
        self.ent_cpf.pack(pady=5)

        ttk.Label(aba1, text="Data de Nascimento (DDMMAAAA):", font=("Arial", 11, "bold")).pack(pady=(10,0))
        self.ent_nasc = ttk.Entry(aba1, width=50)
        self.ent_nasc.pack(pady=5)
        
        ttk.Label(aba1, text="Data da Consulta:", font=("Arial", 11, "bold")).pack(pady=(10,0))
        self.combo_data = ttk.Combobox(aba1, values=self.listar_datas_uteis(), state="readonly")
        self.combo_data.current(0)
        # Evento: ao mudar a data no combo, chama atualizar_horarios
        self.combo_data.bind("<<ComboboxSelected>>", self.atualizar_horarios)
        self.combo_data.pack(pady=5)
        
        ttk.Label(aba1, text="Horários Disponíveis:", font=("Arial", 11, "bold")).pack(pady=(10,0))
        self.combo_horario = ttk.Combobox(aba1, state="readonly")
        self.combo_horario.pack(pady=5)
        
        btn_salvar = ttk.Button(aba1, text="FINALIZAR AGENDAMENTO", command=self.registrar_agendamento)
        btn_salvar.pack(pady=30)

        # --- Elementos da Aba de Pesquisa e Cancelamento ---
        ttk.Label(aba2, text="Pesquisar Paciente (Nome, CPF ou Protocolo):", font=("Arial", 11, "bold")).pack(pady=(15,0))
        self.ent_busca = ttk.Entry(aba2, width=50)
        self.ent_busca.pack(pady=5)
        
        ttk.Button(aba2, text="Pesquisar", command=self.pesquisar_agendamento).pack(pady=5)
        
        # Área de exibição de resultados com barra de rolagem automática se necessário
        self.txt_lista = tk.Text(aba2, width=70, height=10, state="disabled", bg="#f0f0f0")
        self.txt_lista.pack(pady=15, padx=10)
        
        ttk.Label(aba2, text="Protocolo para Cancelar:", font=("Arial", 11, "bold"), foreground="red").pack()
        self.ent_cancela = ttk.Entry(aba2, width=30)
        self.ent_cancela.pack(pady=5)
        ttk.Button(aba2, text="Cancelar Agendamento", command=self.cancelar_agendamento).pack(pady=5)

# =========================================================
# 4. INICIALIZAÇÃO
# =========================================================
if __name__ == "__main__":
    # Instancia a classe e inicia o loop principal de eventos do Windows
    app = SistemaAgendamento()
    app.mainloop()
