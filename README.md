Sistema para agendar, consultar e cancelar consultas médicas. Esta versão é um programa de desktop feito em Python (Tkinter), que guarda os dados em um arquivo JSON.

Documentação completa do projeto (visão geral, usuários, fluxograma e algoritmo): [agendamento.html](agendamento.html)

## O que o programa faz

**Aba "Agendar Consulta"**
- Pede nome completo, CPF e data de nascimento
- Mostra os próximos 10 dias úteis (domingos ficam de fora)
- Mostra os horários livres, das 08:00 às 22:00, de 30 em 30 minutos
- Não mostra horários já ocupados nem horários que já passaram no dia de hoje
- Gera um protocolo de 9 dígitos para cada agendamento

**Aba "Consultar / Cancelar"**
- Pesquisa por nome, CPF ou protocolo
- Cancela um agendamento pelo protocolo, com confirmação antes de apagar

**Validações**
- O nome precisa ter nome e sobrenome
- O CPF precisa ter 11 números (o programa formata como `000.000.000-00`)
- A data de nascimento precisa existir e não pode estar no futuro

## Como executar

Requisitos: Python 3 com Tkinter. O Tkinter já vem junto com o Python no Windows e no macOS. No Linux, pode ser preciso instalar (`sudo apt install python3-tk`).

```
python SCG_3_0.py
```

Não é preciso instalar nenhuma biblioteca extra. Na primeira execução, o arquivo `agendamentos.json` é criado na mesma pasta do programa.

## Arquivo de dados: agendamentos.json

Lista de agendamentos. Cada item tem estes campos:

| Campo | Descrição | Exemplo |
|---|---|---|
| `protocolo` | Número único do agendamento | `"775381585"` |
| `nome` | Nome completo da pessoa | `"Maria da Silva"` |
| `cpf` | CPF da pessoa | `"000.000.000-00"` |
| `nascimento` | Data de nascimento (dd/mm/aaaa) | `"01/01/2000"` |
| `data` | Data do agendamento (dd/mm/aaaa) | `"06/05/2026"` |
| `horario` | Horário do agendamento (hh:mm) | `"21:00"` |

Exemplo:

```json
[
    {
        "protocolo": "123456789",
        "nome": "Maria da Silva",
        "cpf": "000.000.000-00",
        "nascimento": "01/01/2000",
        "data": "06/05/2026",
        "horario": "21:00"
    }
]
```

Para ler o arquivo em Python:

```python
import json

with open("agendamentos.json", "r", encoding="utf-8") as arquivo:
    agendamentos = json.load(arquivo)

for ag in agendamentos:
    print(ag["protocolo"], ag["nome"], ag["data"], ag["horario"])
```

## Aviso sobre dados pessoais

O `agendamentos.json` guarda CPF, nome e data de nascimento. Se os dados forem reais, **não publique no GitHub**, porque o repositório fica visível para qualquer pessoa. Antes de subir, use só dados fictícios ou adicione o arquivo ao `.gitignore`:

```
agendamentos.json
```

## Objetivos do projeto

- Facilitar o agendamento de consultas
- Reduzir filas e tempo de espera
- Organizar a agenda médica
- Evitar conflitos de horários
- Melhorar a comunicação entre clínica e paciente
- Armazenar o histórico de atendimentos
- Aumentar a eficiência da clínica

## Ainda não implementado

Estes itens estão na documentação do projeto, mas o programa atual não os tem:

- Login e perfis de usuário (paciente, médico, recepcionista, administrador)
- Escolha de médico e de especialidade
- Remarcação de consultas
- Envio de comprovante por SMS, e-mail ou WhatsApp
- Prontuário, controle de presença e relatórios

## Arquivos

- `SCG_3_0.py`: o programa
- `agendamentos.json`: os dados (criado pelo programa)
- `agendamento.html`: documentação completa do projeto
- `README.md`: este arquivo
md…]()
