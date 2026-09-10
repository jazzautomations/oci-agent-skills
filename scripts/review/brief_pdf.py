#!/usr/bin/env python3
"""Illustrated Portuguese brief. Optional authoring dependency: reportlab==5.0.0."""
import json
from pathlib import Path
import reportlab
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[2]
W, H = A4
M, CW = 42, W - 84
INK, RED, PAPER = '#202B29', '#B43C2D', '#F7F4EC'
MUTED, LINE, WHITE = '#56655F', '#DADDD2', '#FFFFFF'
PALE, GREEN = '#E7EDE4', '#29664E'
URL = 'https://github.com/jazzautomations/oci-agent-skills'
PAGES = 7


def fonts():
    """Embed Lato when available; use ReportLab's bundled Vera otherwise."""
    system = Path('/usr/share/fonts/truetype/lato')
    bundled = Path(reportlab.__file__).parent / 'fonts'
    for name, lato, vera in [('Body', 'Lato-Regular.ttf', 'Vera.ttf'),
                            ('Bold', 'Lato-Bold.ttf', 'VeraBd.ttf'),
                            ('Italic', 'Lato-Italic.ttf', 'VeraIt.ttf')]:
        path = system / lato if (system / lato).exists() else bundled / vera
        pdfmetrics.registerFont(TTFont(name, str(path)))
    pdfmetrics.registerFontFamily('Body', normal='Body', bold='Bold', italic='Italic', boldItalic='Bold')


class Brief:
    def __init__(self, output, date):
        self.c = Canvas(str(output), pagesize=A4, invariant=1)
        self.c.setTitle('OCI Agent Skills | Do pedido ao fluxo de trabalho')
        self.c.setAuthor('Felipe Salvego / Jazz Automations')
        self.c.setSubject('Apresentação técnica privada — edição 02')
        self.date, self.page = date, 0

    def rect(self, x, y, w, h, color, radius=0):
        self.c.setFillColor(HexColor(color))
        if radius:
            self.c.roundRect(x, H-y-h, w, h, radius, stroke=0, fill=1)
        else:
            self.c.rect(x, H-y-h, w, h, stroke=0, fill=1)

    def line(self, x, y, x2, y2, color=LINE):
        self.c.setStrokeColor(HexColor(color))
        self.c.setLineWidth(1)
        self.c.line(x, H-y, x2, H-y2)

    def text(self, value, x, y, w=CW, size=11.5, color=INK, font='Body', leading=None, max_h=None):
        style = ParagraphStyle('p', fontName=font, fontSize=size,
                               leading=leading or size*1.36, textColor=HexColor(color))
        para = Paragraph(value, style)
        _, height = para.wrap(w, H)
        if y+height > H-57 or (max_h is not None and height > max_h):
            raise ValueError(f'Page {self.page}: text exceeds frame: {value[:70]} ({height:.1f}pt)')
        para.drawOn(self.c, x, H-y-height)
        return y+height

    def start(self, section, dark=False):
        if self.page:
            self.c.showPage()
        self.page += 1
        self.rect(0, 0, W, H, INK if dark else PAPER)
        self.rect(M, 32, 24, 4, '#EF8769' if dark else RED)
        self.text('JAZZ / OCI AGENT SKILLS', M+35, 27, 270, 8.5, WHITE if dark else MUTED, 'Bold')
        self.text(section, W-187, 27, 145, 8.5, '#C8D6CA' if dark else MUTED)
        self.line(M, H-44, W-M, H-44, '#4A5750' if dark else LINE)
        self.c.setFont('Body', 8)
        self.c.setFillColor(HexColor('#C8D6CA' if dark else MUTED))
        self.c.drawString(M, 28, f'REVISÃO PRIVADA  ·  0.2.1 PREVIEW  ·  {self.date}')
        self.c.drawRightString(W-M, 28, f'{self.page:02} / {PAGES:02}')

    def title(self, eyebrow, title, subtitle):
        self.text(eyebrow, M, 78, size=9, color=RED, font='Bold')
        end = self.text(title, M, 100, size=31, font='Bold', leading=35)
        self.text(subtitle, M, end+14, size=12.5, color=MUTED, max_h=52)

    def source(self, paths):
        self.text('NO REPOSITÓRIO  /  '+paths, M, H-80, size=7.7, color=MUTED, max_h=25)

    def number(self, value, x, y):
        self.rect(x, y, 30, 30, PALE, 15)
        self.text(value, x+8, y+6, 22, 11, GREEN, 'Bold')

    def save(self):
        if self.page != PAGES:
            raise ValueError('Unexpected page count')
        self.c.save()


def main():
    fonts()
    evidence = json.loads((ROOT/'docs/evidence/review-demo.json').read_text())
    matrix = json.loads((ROOT/'docs/evidence/validation-matrix.json').read_text())
    if not evidence['ok'] or not all(item['ok'] for item in evidence['checks']):
        raise ValueError('A passing recorded walkthrough is required')
    tools = next(item['result']['tool_count'] for item in evidence['checks'] if item['name']=='mcp_stdio')
    skills = len(list((ROOT/'skills').glob('*/SKILL.md')))
    passed = sum(row['result']=='PASS' for row in matrix['rows'])
    output = ROOT/'docs/review/brief-pt.pdf'
    b = Brief(output, evidence['validated_at'][:10])

    b.start('APRESENTAÇÃO / EDIÇÃO 03', dark=True)
    b.text('OCI Agent<br/>Skills', M, 86, size=54, color=WHITE, font='Bold', leading=55)
    b.text('Da pergunta sobre a nuvem<br/>a um fluxo de trabalho verificável.', M, 224,
           size=23, color='#E5EEDC', leading=29)
    b.text('Um pacote aberto à inspeção que dá ao agente instruções por domínio, referências sob demanda e ferramentas de leitura com escopo explícito.',
           M, 305, 470, 13, '#C8D6CA', max_h=70)
    b.rect(M, 412, CW, 152, '#2D3B35', 12)
    for index, (title, body) in enumerate([
        ('ENTENDER', 'Selecionar o domínio<br/>e delimitar a tarefa.'),
        ('INVESTIGAR', 'Consultar comandos<br/>e leituras permitidas.'),
        ('EXPLICAR', 'Organizar evidências<br/>e próximos passos.')]):
        x=M+20+index*164
        b.text(f'0{index+1}', x, 434, 100, 10, '#EF8769', 'Bold')
        b.text(title, x, 463, 145, 12, WHITE, 'Bold')
        b.text(body, x, 489, 145, 10.5, '#C8D6CA')
        if index < 2:
            b.line(x+137, 468, x+151, 468, '#EF8769')
    b.text(f'<b>{skills} skills</b> por domínio   /   <b>{tools} ferramentas MCP</b> de leitura', M, 591, size=12, color=WHITE)
    b.text('PARA QUEM', M, 641, size=9, color='#EF8769', font='Bold')
    b.text('Engenharia de cloud, plataforma, operações e dados que trabalha com agentes de programação e quer revisar como eles usam OCI.', M, 660, 480, 12, '#C8D6CA')
    b.text('Felipe Salvego · Jazz Automations<br/>Projeto independente da comunidade. Sem vínculo ou endosso da Oracle.', M, 723, size=9, color='#C8D6CA')

    b.start('01 / UM CASO CONCRETO')
    b.title('O QUE MUDA NO TRABALHO DO AGENTE', '“A porta está aberta.<br/>Por que o site não responde?”',
            'Um exemplo de diagnóstico de rede ajuda a entender a proposta.')
    b.rect(M, 246, CW, 64, '#EFE4D6', 8)
    b.text('PEDIDO DO USUÁRIO', M+16, 258, size=8.5, color=RED, font='Bold')
    b.text('“Liberei a porta 80 na security list, mas o acesso externo continua em timeout.”', M+16, 277, CW-32, 12, max_h=33)
    steps = [
        ('Definir onde investigar', 'Confirmar perfil, região, compartment e recurso afetado. A investigação precisa ter um alvo e um limite.'),
        ('Carregar a skill de rede', 'A oci-networking orienta o diagnóstico de alcance: VCN, subnet, rotas, gateway e regras de acesso.'),
        ('Escolher as leituras necessárias', 'O catálogo ajuda a verificar comandos e flags. Os helpers fazem leituras delimitadas; o MCP de rede oferece apenas resumos de VCN/subnet.'),
        ('Organizar uma conclusão revisável', 'A saída esperada distingue o que foi observado, o que falta confirmar e qual mudança poderia ser proposta, com escopo e recuperação.'),
    ]
    for i,(title,body) in enumerate(steps):
        y=334+i*87
        if i<3:b.line(M+15,y+30,M+15,y+87)
        b.number(str(i+1),M,y)
        b.text(title,M+46,y,CW-46,13,font='Bold')
        b.text(body,M+46,y+25,CW-46,10.8,max_h=48)
    b.text('<b>Como ler este exemplo:</b> é o fluxo previsto nas instruções do pacote. Não é um incidente executado nem uma promessa de diagnóstico automático. O MCP de rede não retorna regras, rotas ou tráfego.', M, 697, size=9.5, color=MUTED,max_h=48)
    b.source('skills/oci-networking/SKILL.md · docs/mcp-tools.md')

    b.start('02 / COMO FUNCIONA')
    b.title('INSTRUÇÕES, DESCOBERTA E EXECUÇÃO', 'Três peças que se<br/>complementam.',
            'O pacote é usado dentro do agente. Cada peça resolve uma parte diferente da tarefa.')
    for x,title,body in [
        (M,'SKILL','Um guia de trabalho: quando usar, perguntas de escopo, rotas por sintoma, exemplos, referências e cuidados operacionais.'),
        (M+264,'CATÁLOGO CLI','Um índice consultável da CLI instalada. Ajuda a descobrir comandos e flags obrigatórias sem carregar o inventário inteiro no prompt.')]:
        b.rect(x,241,247,147,WHITE,8)
        b.rect(x,241,247,4,RED)
        b.text(title,x+16,259,215,10,color=RED,font='Bold')
        b.text(body,x+16,284,215,11.4,max_h=88)
    b.text('O agente usa esse contexto e escolhe um caminho de leitura:',M,414,size=12,font='Bold')
    for x,title,body,bottom in [
        (M,'HELPERS / SHELL','Scripts do pacote → wrapper comum → operações OCI permitidas.', 'No Claude, o hook Bash classifica propostas como permitir, pedir revisão ou negar.'),
        (M+264,'MCP / STDIO','Cliente MCP → servidor do pacote → uma das 15 ferramentas fixas.', 'MCP é o protocolo que permite ao agente descobrir e chamar essas ferramentas.')]:
        b.rect(x,450,247,173,PALE,8)
        b.text(title,x+16,467,215,10,color=GREEN,font='Bold')
        b.text(body,x+16,493,215,12,max_h=52)
        b.text(bottom,x+16,554,215,10.2,color=MUTED,max_h=53)
    b.rect(M,648,CW,75,INK,8)
    b.text('A fronteira de acesso continua sendo IAM + permissões do host.',M+16,662,CW-32,12,WHITE,'Bold')
    b.text('A guarda é consultiva e específica do hook fornecido ao Claude. O MCP não oferece executor genérico de CLI, SQL ou SDK.',M+16,689,CW-32,10,'#C8D6CA',max_h=29)
    b.source('docs/foundation.md · runtime/README.md · scripts/lib/oci_ro.py')

    b.start('03 / ONDE APLICAR')
    b.title('COBERTURA DO PACOTE', f'{skills} skills. Nove frentes<br/>de trabalho.',
            'Da identidade ao banco de dados: cada domínio tem instruções e referências próprias.')
    domains = [
        ('05','Identidade e governança','Navegação, autenticação, tenancy, políticas IAM e limites.'),
        ('05','Infraestrutura','Compute, rede, object storage, block/file storage e bastion.'),
        ('04','Entrega e IaC','OKE, pipelines, serverless e Terraform.'),
        ('05','Operação e segurança','Métricas, logs, incidentes, postura de segurança e certificados.'),
        ('03','Custos e Free Tier','Custos, desperdício potencial e planejamento dentro dos limites da oferta.'),
        ('05','Database e APEX','Autonomous, frotas, vetores/IA, acesso SQL e APEX.'),
        ('03','IA e dados','Generative AI, serviços de IA e plataformas de dados.'),
        ('05','Continuidade e migração','Backup, avaliação de inventário, mapeamento, landing zone e atualização.'),
        ('02','SDKs e aplicações','Padrões de SDK e navegação em aplicações empresariais Oracle.'),
    ]
    if sum(int(n) for n,_,_ in domains) != skills:raise ValueError('Coverage counts need review')
    for i,(count,title,body) in enumerate(domains):
        y=237+i*51
        b.text(count,M,y,38,20,color=RED,font='Bold')
        b.text(title,M+53,y,CW-53,12,font='Bold')
        b.text(body,M+53,y+20,CW-53,10.4,color=MUTED,max_h=29)
        b.line(M,y+44,W-M,y+44)
    b.text('A amplitude das skills é maior que a superfície das 15 ferramentas MCP. Uma skill também pode orientar CLI, SQL, revisão de código ou um plano de mudança. Cobertura de instruções não significa validação completa de todos os serviços.',M,710,size=10,color=MUTED,max_h=42)
    b.source('docs/skills.md · docs/audit.md · docs/oracle-product-map.md')

    b.start('04 / VEJA FUNCIONAR')
    b.title('DEMONSTRAÇÃO OFFLINE', 'Uma demo de cinco minutos.<br/>Sem credenciais OCI.',
            'Ela executa componentes reais do pacote e grava um relatório JSON com hashes dos insumos.')
    b.rect(M,242,CW,133,INK,10)
    b.text('TERMINAL / NA RAIZ DO REPOSITÓRIO',M+18,257,CW-36,8.5,'#EF8769','Bold')
    b.text('uv sync --frozen --project runtime',M+18,284,CW-36,11,WHITE)
    b.text('uv run --frozen --project runtime python scripts/review/demo.py<br/>--report /tmp/oci-review.json',M+18,316,CW-36,10.5,'#C8D6CA')
    b.text('Una as duas linhas do segundo comando. Python 3.13+ e uv; a instalação inicial pode baixar dependências.',M,386,size=9.3,color=MUTED,max_h=29)
    rows=[
        ('CATÁLOGO','Escopo identificado','A consulta de requisitos para compute instance list retorna --compartment-id.'),
        ('GUARDA','Leitura: allow','A proposta de listar instâncias é classificada como leitura permitida.'),
        ('GUARDA','Escrita: ask','A proposta de criar uma instância pede revisão. Ela é tratada como texto; não é executada.'),
        ('MCP','15 ferramentas + escopo inválido rejeitado','O servidor real inicializa por stdio e rejeita a entrada inválida sem config OCI válida.'),
    ]
    for i,(tag,title,body) in enumerate(rows):
        y=432+i*63
        b.text(tag,M,y,82,8.8,color=GREEN,font='Bold')
        b.text(title,M+87,y,CW-87,11.5,font='Bold')
        b.text(body,M+87,y+21,CW-87,10.2,max_h=29)
        b.line(M,y+55,W-M,y+55)
    b.text('<b>Resultado registrado:</b> 4 verificações passaram. A demo não mede execução de tarefas pelo modelo, aplicação do hook pelo host ou operações na tenancy. A saída completa está em docs/evidence/review-demo.json.',M,707,size=10,color=MUTED,max_h=42)
    b.source('docs/review/demo.md · scripts/review/demo.py · docs/evidence/review-demo.json')

    b.start('05 / O QUE ESTÁ COMPROVADO')
    b.title('VALIDAÇÃO COM ESCOPO DECLARADO', 'Evidência para inspecionar.<br/>Critérios para evoluir.',
            f'{passed} de {len(matrix["rows"])} critérios de liberação passaram. O pacote continua em preview.')
    for i,(number,label,detail) in enumerate([
        ('450','testes passaram','Regressão de código'),
        ('285','blocos OCI válidos','Sintaxe dos exemplos'),
        ('28','helpers aprovados','22 live_read + 6 offline')]):
        x=M+i*174
        b.rect(x,241,163,111,WHITE,8)
        b.text(number,x+14,252,137,30,color=RED,font='Bold')
        b.text(label,x+14,296,137,10.5,font='Bold')
        b.text(detail,x+14,318,137,8.7,color=MUTED)
    b.text('Essas medições verificam componentes e leituras selecionadas. Não comprovam deployments completos nem superioridade sobre outros agentes.',M,371,size=11,color=MUTED,max_h=33)
    b.text('O que ainda precisa ser fechado',M,423,size=16,font='Bold')
    pending_rows=[
        ('V22','Histórico Git','Ocorrências de e-mail em patches antigos; preparar a limpeza antes de publicar.'),
        ('V24','Manutenção hospedada','Verificar a execução agendada e a criação de issue do monitor de drift.'),
        ('V25','Leituras restantes','Resolver pré-requisitos e dados ausentes; triagem com Cloud Guard 404 / Support 403.'),
        ('V27','Avaliação no host','Acesso ao avaliador de tarefas do Claude indisponível no registro atual.'),
        ('V28','Comparação comportamental','Executar tarefas com modelo sob os mesmos prompts e limites nas quatro variantes.'),
    ]
    for i,(gate,title,body) in enumerate(pending_rows):
        y=461+i*43
        b.text(gate,M,y,42,10,color=RED,font='Bold')
        b.text(f'<b>{title}</b> · {body}',M+48,y,CW-48,10.3,max_h=32)
        b.line(M,y+36,W-M,y+36)
    b.text('<b>Seleção semântica:</b> 77/80 e 77/80; zero ativações indevidas em 40 negativos por rodada. Evidência datada, sem medir tarefas completas no host.',M,699,size=10,color=GREEN,max_h=42)
    b.source('docs/validation-matrix.md · docs/evals.md · docs/evidence/README.md')

    b.start('06 / PRÓXIMO PASSO')
    b.title('CONVITE À REVISÃO TÉCNICA', 'Escolha um domínio.<br/>Vamos validar um caso útil.',
            'O objetivo desta apresentação é colher feedback de engenharia antes da abertura pública.')
    for i,(title,body) in enumerate([
        ('Revise uma skill que você conhece','A descrição seleciona a tarefa certa? As perguntas de escopo, os pré-requisitos e as referências correspondem à prática do serviço?'),
        ('Inspecione uma ferramenta de leitura','O escopo é suficiente? Uma resposta parcial fica visível? O tratamento de paginação e erro evita conclusões indevidas?'),
        ('Sugira uma tarefa representativa','Indique o resultado esperado e um ambiente mínimo. Isso ajuda a transformar a revisão em uma validação de ponta a ponta.')]):
        y=245+i*105
        b.number(str(i+1),M,y)
        b.text(title,M+47,y,CW-47,13,font='Bold')
        b.text(body,M+47,y+27,CW-47,11.2,max_h=49)
    b.rect(M,579,CW,131,INK,10)
    b.text('COMECE PELO REPOSITÓRIO',M+18,595,CW-36,9,'#EF8769','Bold')
    b.text(f'<link href="{URL}" color="#FFFFFF">github.com/jazzautomations/oci-agent-skills</link>',M+18,623,CW-36,13,WHITE,'Bold')
    b.text('docs/review/README.md: apresentação, roteiro e feedback.<br/>Acesso privado concedido pelo proprietário; o ZIP permite revisar a árvore sem histórico Git.',M+18,655,CW-36,10.5,'#C8D6CA',max_h=44)
    b.text('<b>Felipe Salvego · Jazz Automations</b><br/>Projeto independente. Esta revisão não representa certificação ou endosso da Oracle.',M,730,size=10,color=MUTED,max_h=32)
    b.save()
    print(f'{output.relative_to(ROOT)} — {PAGES} pages')


if __name__=='__main__':
    main()
