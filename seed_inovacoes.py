from app import app, db
from models.inovacao import Inovacao

ferramentas_lean = [
    {
        'nome': '5S',
        'categoria': 'Organização',
        'descricao': 'Metodologia japonesa de organização do ambiente de trabalho em 5 etapas: Seiri (Utilização), Seiton (Ordenação), Seiso (Limpeza), Seiketsu (Padronização) e Shitsuke (Disciplina).',
        'beneficios': 'Melhoria da produtividade, redução de desperdícios, ambiente mais seguro e organizado, facilita identificação de problemas.',
        'requisitos': 'Comprometimento da equipe, treinamento básico, tempo para implementação inicial.',
        'tempo_implementacao': '1-3 meses',
        'nivel_complexidade': 'Baixa'
    },
    {
        'nome': 'Kaizen',
        'categoria': 'Melhoria Contínua',
        'descricao': 'Filosofia de melhoria contínua que envolve todos os colaboradores na identificação e implementação de pequenas melhorias incrementais.',
        'beneficios': 'Cultura de melhoria contínua, engajamento dos colaboradores, redução de custos, aumento de qualidade.',
        'requisitos': 'Cultura organizacional aberta, sistema de sugestões, reconhecimento de contribuições.',
        'tempo_implementacao': 'Contínuo',
        'nivel_complexidade': 'Média'
    },
    {
        'nome': 'Kanban',
        'categoria': 'Gestão Visual',
        'descricao': 'Sistema de gestão visual que usa cartões para controlar o fluxo de produção e estoque, baseado na demanda real.',
        'beneficios': 'Redução de inventário, melhor controle de produção, identificação de gargalos, just-in-time.',
        'requisitos': 'Mapeamento de processos, definição de limites de estoque, treinamento da equipe.',
        'tempo_implementacao': '2-4 meses',
        'nivel_complexidade': 'Média'
    },
    {
        'nome': 'Poka-Yoke',
        'categoria': 'Qualidade',
        'descricao': 'Dispositivos à prova de erros que impedem que defeitos sejam produzidos ou passem despercebidos no processo.',
        'beneficios': 'Redução drástica de defeitos, menor retrabalho, maior confiabilidade do processo.',
        'requisitos': 'Análise de falhas, criatividade para soluções, investimento em dispositivos.',
        'tempo_implementacao': '1-6 meses',
        'nivel_complexidade': 'Média'
    },
    {
        'nome': 'TPM (Manutenção Produtiva Total)',
        'categoria': 'Manutenção',
        'descricao': 'Abordagem que visa maximizar a eficiência dos equipamentos através de manutenção preventiva, autônoma e preditiva.',
        'beneficios': 'Redução de paradas não planejadas, maior OEE, vida útil estendida dos equipamentos.',
        'requisitos': 'Treinamento de operadores, programa de manutenção, medição de indicadores.',
        'tempo_implementacao': '6-12 meses',
        'nivel_complexidade': 'Alta'
    },
    {
        'nome': 'VSM (Mapeamento do Fluxo de Valor)',
        'categoria': 'Análise de Processos',
        'descricao': 'Ferramenta visual para mapear o fluxo de materiais e informações necessários para levar um produto ao cliente.',
        'beneficios': 'Identificação de desperdícios, visualização do fluxo completo, base para melhorias.',
        'requisitos': 'Conhecimento do processo completo, tempo para mapeamento, equipe multidisciplinar.',
        'tempo_implementacao': '1-2 meses',
        'nivel_complexidade': 'Alta'
    },
    {
        'nome': 'SMED (Troca Rápida de Ferramentas)',
        'categoria': 'Setup',
        'descricao': 'Metodologia para reduzir o tempo de setup/changeover de máquinas e equipamentos.',
        'beneficios': 'Aumento de capacidade produtiva, maior flexibilidade, redução de lotes.',
        'requisitos': 'Análise de tempos, modificações em equipamentos, padronização.',
        'tempo_implementacao': '3-6 meses',
        'nivel_complexidade': 'Alta'
    },
    {
        'nome': 'Trabalho Padronizado',
        'categoria': 'Padronização',
        'descricao': 'Documentação e padronização da melhor forma conhecida de realizar uma tarefa.',
        'beneficios': 'Consistência de qualidade, facilita treinamento, base para melhorias.',
        'requisitos': 'Definição de melhores práticas, documentação clara, treinamento.',
        'tempo_implementacao': '2-4 meses',
        'nivel_complexidade': 'Baixa'
    },
    {
        'nome': 'Gestão Visual',
        'categoria': 'Comunicação',
        'descricao': 'Uso de sinais visuais (quadros, cores, sinais) para comunicar informações importantes rapidamente.',
        'beneficios': 'Comunicação rápida e eficaz, identificação rápida de problemas, transparência.',
        'requisitos': 'Definição de indicadores, design de quadros visuais, atualização regular.',
        'tempo_implementacao': '1-2 meses',
        'nivel_complexidade': 'Baixa'
    },
    {
        'nome': 'Células de Manufatura',
        'categoria': 'Layout',
        'descricao': 'Reorganização do layout em células de trabalho para minimizar movimentação e aumentar fluxo.',
        'beneficios': 'Redução de lead time, menor movimentação, melhor comunicação da equipe.',
        'requisitos': 'Análise de fluxo, reorganização física, treinamento multifuncional.',
        'tempo_implementacao': '3-6 meses',
        'nivel_complexidade': 'Alta'
    },
    {
        'nome': 'Six Sigma',
        'categoria': 'Qualidade',
        'descricao': 'Metodologia estruturada (DMAIC) para redução de variabilidade e defeitos nos processos.',
        'beneficios': 'Qualidade excepcional (3,4 defeitos por milhão), redução de custos da não-qualidade.',
        'requisitos': 'Treinamento de Black/Green Belts, ferramentas estatísticas, projetos estruturados.',
        'tempo_implementacao': '6-12 meses por projeto',
        'nivel_complexidade': 'Alta'
    },
    {
        'nome': 'Jidoka (Autonomação)',
        'categoria': 'Automação',
        'descricao': 'Automação com toque humano - máquinas param automaticamente quando detectam problemas.',
        'beneficios': 'Prevenção de defeitos, liberação de mão de obra, qualidade assegurada.',
        'requisitos': 'Investimento em sensores/automação, análise de modos de falha.',
        'tempo_implementacao': '6-12 meses',
        'nivel_complexidade': 'Alta'
    },
    {
        'nome': 'Heijunka (Nivelamento de Produção)',
        'categoria': 'Planejamento',
        'descricao': 'Nivelamento do mix e volume de produção para criar um fluxo mais estável.',
        'beneficios': 'Redução de variabilidade, melhor uso de recursos, inventário mais baixo.',
        'requisitos': 'Flexibilidade de produção, análise de demanda, setup rápido.',
        'tempo_implementacao': '4-8 meses',
        'nivel_complexidade': 'Alta'
    },
    {
        'nome': 'Andon',
        'categoria': 'Controle de Qualidade',
        'descricao': 'Sistema de sinalização visual e sonora que alerta sobre problemas na linha de produção.',
        'beneficios': 'Resposta rápida a problemas, empoderamento dos operadores, contenção de defeitos.',
        'requisitos': 'Sistema de sinalização, processo de resposta, cultura de parada para qualidade.',
        'tempo_implementacao': '2-4 meses',
        'nivel_complexidade': 'Média'
    },
    {
        'nome': 'Gemba Walk',
        'categoria': 'Gestão',
        'descricao': 'Prática de líderes irem regularmente ao "gemba" (local real onde o trabalho acontece) para observar e aprender.',
        'beneficios': 'Líderes mais conectados com realidade, identificação de problemas reais, respeito pelos colaboradores.',
        'requisitos': 'Comprometimento da liderança, checklist de observação, ação sobre achados.',
        'tempo_implementacao': 'Contínuo',
        'nivel_complexidade': 'Baixa'
    }
]

if __name__ == '__main__':
    with app.app_context():
        print("Populando ferramentas Lean Manufacturing...")
        
        for ferramenta in ferramentas_lean:
            existente = Inovacao.query.filter_by(nome=ferramenta['nome']).first()
            if not existente:
                inovacao = Inovacao(**ferramenta)
                db.session.add(inovacao)
                print(f"✓ {ferramenta['nome']} adicionada")
            else:
                print(f"- {ferramenta['nome']} já existe")
        
        db.session.commit()
        print("\n✅ Ferramentas Lean Manufacturing populadas com sucesso!")
        print(f"Total: {Inovacao.query.count()} ferramentas disponíveis")
