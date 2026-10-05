# agendamentos.json

Arquivo de dados em formato JSON com uma lista de agendamentos. Ele serve como "banco de dados" simples para guardar os horários marcados.

## Estrutura

O arquivo é uma lista de objetos, e cada objeto representa um agendamento:

| Campo | Descrição | Exemplo |
|---|---|---|
| `protocolo` | Número único do agendamento | `"775381585"` |
| `nome` | Nome completo da pessoa | `"Maria da Silva"` |
| `cpf` | CPF da pessoa | `"000.000.000-00"` |
| `nascimento` | Data de nascimento (dd/mm/aaaa) | `"01/01/2000"` |
| `data` | Data do agendamento (dd/mm/aaaa) | `"06/05/2026"` |
| `horario` | Horário do agendamento (hh:mm) | `"21:00"` |

## Exemplo

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

## Como ler o arquivo em Python

```python
import json

with open("agendamentos.json", "r", encoding="utf-8") as arquivo:
    agendamentos = json.load(arquivo)

for ag in agendamentos:
    print(ag["protocolo"], ag["nome"], ag["data"], ag["horario"])
```

## Aviso sobre dados pessoais

Este arquivo contém **CPF, nome e data de nascimento**. Se os dados forem reais, **não publique no GitHub**: o repositório fica visível para qualquer pessoa. Antes de subir, troque tudo por dados fictícios (como no exemplo acima) ou adicione `agendamentos.json` ao `.gitignore`.
