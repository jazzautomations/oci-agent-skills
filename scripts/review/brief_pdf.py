#!/usr/bin/env python3
"""Build the Portuguese review brief. Optional authoring dependency: reportlab==5.0.0."""
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT = Path(__file__).resolve().parents[2]
INK = colors.HexColor("#222522")
RED = colors.HexColor("#B63D2E")
MUTED = colors.HexColor("#59615A")
PAPER = colors.HexColor("#FAF8F2")
RULE = colors.HexColor("#DEDCD4")
STYLES = {
    "eyebrow": ParagraphStyle("eyebrow", fontName="Helvetica-Bold", fontSize=9,
                              leading=13, textColor=RED, spaceAfter=20),
    "title": ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=37,
                            leading=40, textColor=INK, spaceAfter=18),
    "subtitle": ParagraphStyle("subtitle", fontName="Helvetica", fontSize=16,
                               leading=23, textColor=MUTED, spaceAfter=25),
    "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=15,
                         leading=20, textColor=INK, spaceBefore=17, spaceAfter=9),
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=10.5,
                           leading=16, textColor=INK, spaceAfter=10),
    "small": ParagraphStyle("small", fontName="Helvetica", fontSize=8.5,
                            leading=12, textColor=MUTED, spaceAfter=7),
    "metric": ParagraphStyle("metric", fontName="Helvetica-Bold", fontSize=29,
                             leading=34, textColor=RED, spaceAfter=6),
}


def p(text, style="body"):
    return Paragraph(text, STYLES[style])


def table(rows, widths):
    content = [[p(cell, "small") for cell in row] for row in rows]
    result = Table(content, colWidths=widths, hAlign="LEFT")
    result.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, -1), .5, RULE),
    ]))
    return result


def frame(canvas, doc):
    width, height = A4
    canvas.saveState()
    canvas.setFillColor(PAPER)
    canvas.rect(0, 0, width, height, fill=1, stroke=0)
    canvas.setFillColor(RED)
    canvas.rect(48, height - 40, 38, 4, fill=1, stroke=0)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(48, 30, "OCI AGENT SKILLS  /  REVISÃO TÉCNICA PRIVADA  /  0.2.1")
    canvas.drawRightString(width - 48, 30, f"{doc.page} / 3")
    canvas.restoreState()


def main():
    evidence = json.loads((ROOT / "docs/evidence/review-demo.json").read_text())
    matrix = json.loads((ROOT / "docs/evidence/validation-matrix.json").read_text())
    if not evidence["ok"] or not all(item["ok"] for item in evidence["checks"]):
        raise ValueError("The brief requires a passing recorded component walkthrough")
    passed = sum(row["result"] == "PASS" for row in matrix["rows"])
    pending = len(matrix["rows"]) - passed
    skills = len(list((ROOT / "skills").glob("*/SKILL.md")))
    mcp = next(item for item in evidence["checks"] if item["name"] == "mcp_stdio")["result"]
    date = evidence["validated_at"][:10]
    width = A4[0] - 96
    story = [
        p("COMMUNITY PREVIEW  /  CONVITE À REVISÃO", "eyebrow"),
        p("OCI Agent<br/>Skills", "title"),
        p("Contexto operacional para agentes<br/>que trabalham com Oracle Cloud.", "subtitle"),
    ]
    metrics = Table([[p(str(skills), "metric"), p(str(mcp["tool_count"]), "metric"), p("5 min", "metric")],
                     [p("skills por domínio", "small"), p("ferramentas MCP fixas", "small"), p("demonstração offline", "small")]],
                    colWidths=[width / 3] * 3)
    metrics.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    story += [metrics, Spacer(1, 20), p("O problema", "h2"),
        p("Encontrar um comando não basta. O agente precisa conhecer o compartment, a região, "
          "os pré-requisitos, o formato da resposta e os limites da operação."),
        p("O projeto reúne instruções específicas por domínio, catálogo da CLI instalada, "
          "helpers com leitura delimitada e um servidor MCP com contratos explícitos."),
        p("Por que mostrar agora", "h2"),
        p("Antes de abrir o repositório, queremos que engenheiros da Oracle revisem tarefas "
          "representativas, apontem pressupostos incorretos e ajudem a priorizar a próxima validação."),
        Spacer(1, 12),
        p("<b>Felipe Salvego · Jazz Automations</b><br/>Projeto independente da comunidade. "
          "Sem vínculo, endosso ou certificação da Oracle. Pacote em preview; revisão técnica privada.", "small"),
        PageBreak(),
        p("01  /  COMO AS PEÇAS FUNCIONAM", "eyebrow"),
        p("Escopo antes<br/>da operação.", "title"),
        p("Cada camada tem um papel que o revisor consegue inspecionar.", "subtitle"),
        table([
            ("<b>Skill + referências</b>", "Selecionam o fluxo e carregam contexto por necessidade."),
            ("<b>Catálogo da CLI</b>", "Expõe comandos e flags da versão instalada; inclui aliases."),
            ("<b>Helpers de leitura</b>", "Usam wrapper comum, escopo explícito e saídas projetadas."),
            ("<b>Guarda consultiva</b>", "Classifica comandos no hook Bash do Claude. Outros adaptadores não recebem esse hook."),
            ("<b>MCP por stdio</b>", "Oferece ferramentas fixas de leitura, sem executor arbitrário de CLI, SQL ou SDK."),
        ], [145, width - 145]),
        p("Demonstração reproduzível", "h2"),
        p("1. Consultar o escopo exigido pelo catálogo.<br/>"
          "2. Classificar uma leitura e uma proposta de escrita como dados inertes.<br/>"
          "3. Inicializar o servidor MCP real, descobrir 15 ferramentas e rejeitar escopo inválido."),
        p(f"<b>Registro: {date} · 4 verificações passaram.</b> A demo não executa operações OCI "
          "e não precisa de credenciais. Código, saída JSON e hashes dos insumos acompanham o pacote.", "small"),
        p("IAM e permissões do host continuam sendo a fronteira de acesso. A demo de componentes "
          "não mede sucesso de uma tarefa de agente nem aplicação de permissões pelo host.", "small"),
        PageBreak(),
        p("02  /  EVIDÊNCIA E PRÓXIMA VALIDAÇÃO", "eyebrow"),
        p("Revisão com<br/>limites claros.", "title"),
        p(f"{passed} gates passaram. {pending} permanecem abertos.", "subtitle"),
        table([
            ("<b>Já registrado</b>", "362 testes de regressão; 277 blocos OCI aceitos pelo lint de sintaxe. "
             "A varredura de helpers registra 27 entradas aprovadas, sendo 6 offline."),
            ("<b>Roteamento / agente</b>", "Proxy estático de descrição: 37,5%, abaixo de 90%. "
             "Avaliação no host e comparação comportamental ainda incompletas."),
            ("<b>Leituras / ambientes</b>", "Cloud Guard 404 e Support 403 na triagem delimitada; faltam fixtures e dados de métricas. "
             "Outros principals, regiões e plataformas exigem validação."),
            ("<b>Distribuição / publicação</b>", "Drift local validado; fluxo agendado e abertura de issue ainda não medidos. "
             "Histórico contém ocorrências de e-mail em patches e precisa de revisão antes da publicação."),
        ], [145, width - 145]),
        p("O feedback que mais ajuda", "h2"),
        p("Escolha um domínio. Aponte um pré-requisito ausente, uma hipótese incorreta sobre a API "
          "ou uma tarefa importante que o agente deveria resolver. Inclua o arquivo, o comportamento "
          "esperado e a menor forma de reproduzir com dados sanitizados."),
        p("Abra o pacote", "h2"),
        p('<link href="https://github.com/jazzautomations/oci-agent-skills" color="#B63D2E">'
          'github.com/jazzautomations/oci-agent-skills</link><br/>'
          'Acesso ao repositório privado deve ser concedido pelo proprietário. Alternativa: ZIP da árvore atual, sem histórico Git.', "small"),
        p("No código: docs/review/README.md · docs/review/demo.md · docs/validation-matrix.md. "
          "Evidências datadas não substituem uma nova execução no ambiente do revisor.", "small"),
    ]
    output = ROOT / "docs/review/brief-pt.pdf"
    SimpleDocTemplate(str(output), pagesize=A4, rightMargin=48, leftMargin=48,
                      topMargin=65, bottomMargin=58, title="OCI Agent Skills — Revisão técnica",
                      author="Felipe Salvego / Jazz Automations", invariant=1).build(
                          story, onFirstPage=frame, onLaterPages=frame)
    print(output.relative_to(ROOT))


if __name__ == "__main__":
    main()
