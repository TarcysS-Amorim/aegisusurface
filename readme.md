# AegisSurface

> **Local, auditável e orientado a decisão.**
>
> Sistema open‑source de monitoramento e priorização dinâmica de superfície de ataque, com inferência local (GPU‑ready) e foco exclusivo em apoio humano para hardening e pentest ético.

---

## Visão geral
O **AegisSurface** observa continuamente o **estado do host e da rede** (eventos, conexões e serviços), constrói um **baseline de comportamento normal** e destaca **desvios relevantes** por meio de **features interpretáveis** e modelos **não supervisionados**.

O projeto **não executa ataques**, **não coleta dados externos** e **não automatiza ações ofensivas**. Ele **prioriza risco** para apoiar decisões humanas.

---

## Motivação
Ferramentas tradicionais tendem a:
- gerar alertas excessivos;
- misturar coleta, decisão e ação;
- depender de cloud ou dados externos.

O AegisSurface separa responsabilidades:
- **CPU** coleta, normaliza e orquestra;
- **GPU (opcional)** faz inferência contínua;
- **Humano** decide.

Resultado: **menos ruído, mais contexto**.

---

## Princípios
- **Uso ético e autorizado**
- **Execução local (offline)**
- **Projeto auditável e versionado**
- **IA não executa exploits/payloads**
- **Raciocínio técnico explícito**

---

## Arquitetura (alto nível)
```
[ Sensores ] ──► [ Snapshots (Schema v1) ] ──► [ Feature Builder ] ──► [ ML / Scoring ] ──► [ Relatórios ]
     CPU                     JSON (imutável)               CSV                 GPU/CPU               CLI/JSON
```

### Componentes
- **Collectors (CPU)**: observação do host/rede
- **Schema v1**: contrato de dados estável
- **Loop**: coleta contínua (janela fixa)
- **Feature Builder**: engenharia de features temporal
- **ML (opcional)**: autoencoder tabular (baseline)

---

## Fluxo de dados
1. Coleta periódica (ex.: 60s)
2. Snapshot JSON **imutável** (schema v1.0)
3. Agregação temporal → **features numéricas**
4. Análise estatística / ML
5. Score interpretável para decisão humana

---

## Schema v1.0 (resumo)
Cada snapshot representa **uma observação** do estado do sistema.

```json
{
  "schema_version": "1.0",
  "snapshot": { "timestamp_utc": "...", "interval_seconds": 60 },
  "host": { "hostname": "...", "ipv4": "...", "os": "..." },
  "network": {
    "listening": {
      "total_ports": 39,
      "loopback_ports": 19,
      "exposed_ports": 20,
      "sensitive_ports": [135,139,445]
    },
    "connections": {
      "established_external": 24,
      "unique_external_ips": 8
    }
  }
}
```

**Decisões**:
- Sem IPs individuais ou payloads (privacidade)
- Timestamp UTC timezone‑aware
- Versionamento explícito

---

## Estrutura do repositório
```
aegissurface/
├── collectors/            # Sensores (CPU)
├── schema/                # Contratos de dados
├── features/              # Feature builder
├── ml/                    # Modelos (opcional)
├── out/                   # Artefatos gerados (snapshots, CSV)
├── loop.py                # Coleta contínua
└── README.md
```

---

## Como reproduzir
### Requisitos
- Python 3.11+
- Windows 11 (baseline atual) ou Linux
- (Opcional) GPU NVIDIA para ML

### Instalação
```bash
pip install pandas torch
```

### Coleta (schema v1)
```bash
python -m loop
```

### Feature Builder
```bash
python -m features.build_features_v1
```

Saída:
```
out/features/network_features_v1.csv
```

---

## Metodologia
- **Baseline não supervisionado**
- **Deltas temporais** para captar mudanças
- **Separação clara** entre coleta, features e decisão
- **Congelamento de baseline** para evitar drift silencioso

---

## Limitações conhecidas
- Baseline é **específico do host/OS**
- Mudanças estruturais exigem **novo baseline**
- Versão atual foca rede/serviços (sem eventos de processo)

---

## Próximos passos
- Autoencoder tabular (PyTorch, GPU‑ready)
- Scoring interpretável por feature
- Coletores Linux (ss/journalctl)
- Relatórios CLI/PDF

---

## Status do projeto
- [x] Schema v1
- [x] Coleta contínua
- [x] Feature builder
- [ ] ML (em progresso)

---

## Licença
MIT

---

## Aviso ético
Este projeto **não** executa ações ofensivas automáticas. Todo uso deve ser **autorizado** e **documentado**. O objetivo é **apoio à decisão humana** em segurança.

