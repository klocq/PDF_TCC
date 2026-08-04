'''-- 1. Criação da tabela de matriz curricular
CREATE TABLE IF NOT EXISTS matriz_curricular (
    id SERIAL PRIMARY KEY,
    codigo_disciplina VARCHAR(10) NOT NULL,
    nome_disciplina VARCHAR(150) NOT NULL,
    fase VARCHAR(20) NOT NULL,              -- '1ª Fase', '2ª Fase', ..., '6ª Fase', 'Optativa'
    tipo VARCHAR(20) NOT NULL,              -- 'Obrigatória' ou 'Optativa'
    curriculo VARCHAR(10) NOT NULL,         -- '2016.1' ou '2026.1'
    CONSTRAINT unq_disciplina_curriculo UNIQUE (codigo_disciplina, curriculo)
);

-- Índice para acelerar a busca no Streamlit por versão do currículo
CREATE INDEX IF NOT EXISTS idx_matriz_curriculo ON matriz_curricular(curriculo);

INSERT INTO matriz_curricular (codigo_disciplina, nome_disciplina, fase, tipo, curriculo) VALUES

-- ==========================================================
-- CURRÍCULO 20161
-- ==========================================================
-- 1ª Fase
('CIN7139', 'Introdução às Tecnologias da Informação e Comunicação', '1ª Fase', 'Ob', '20161'),
('CIN7140', 'Pesquisa Bibliográfica', '1ª Fase', 'Ob', '20161'),
('CIN7141', 'Lógica Instrumental I', '1ª Fase', 'Ob', '20161'),
('CIN7142', 'Evolução do Pensamento Filosófico e Científico', '1ª Fase', 'Ob', '20161'),
('CIN7143', 'Empreendedorismo I', '1ª Fase', 'Ob', '20161'),
('CIN7144', 'Tutoria Acadêmica I', '1ª Fase', 'Ob', '20161'),
('CIN7145', 'Gestão da Informação', '1ª Fase', 'Ob', '20161'),
('CIN7925', 'Introdução a Algoritmos', '1ª Fase', 'Ob', '20161'),
('LLV7802', 'Leitura e Produção do Texto', '1ª Fase', 'Ob', '20161'),

-- 2ª Fase
('CAD5103', 'Administração I', '2ª Fase', 'Ob', '20161'),
('CIN7201', 'Sistemas de Organização do Conhecimento', '2ª Fase', 'Ob', '20161'),
('CIN7202', 'Sociedade da Informação', '2ª Fase', 'Ob', '20161'),
('CIN7203', 'Ética Profissional', '2ª Fase', 'Ob', '20161'),
('CIN7204', 'Tutoria Acadêmica II', '2ª Fase', 'Ob', '20161'),
('CIN7205', 'Recuperação da Informação', '2ª Fase', 'Ob', '20161'),
('CIN7206', 'Fontes Gerais de Informação', '2ª Fase', 'Ob', '20161'),

-- 3ª Fase
('CIN7301', 'Introdução à Representação Temática', '3ª Fase', 'Ob', '20161'),
('CIN7302', 'Introdução à Representação Descritiva', '3ª Fase', 'Ob', '20161'),
('CIN7303', 'Metodologia da Pesquisa', '3ª Fase', 'Ob', '20161'),
('CIN7304', 'Introdução à Bancos de Dados', '3ª Fase', 'Ob', '20161'),
('CIN7305', 'Gestão da Qualidade', '3ª Fase', 'Ob', '20161'),
('CIN7306', 'Competência Informacional', '3ª Fase', 'Ob', '20161'),
('CIN7307', 'Interação Comunitária I', '3ª Fase', 'Ob', '20161'),
('CIN7309', 'Gestão de Processos Organizacionais', '3ª Fase', 'Ob', '20161'),
('HST7921', 'História do Brasil Contemporâneo', '3ª Fase', 'Ob', '20161'),

-- 4ª Fase
('CIN7401', 'Estudos Métricos da Informação', '4ª Fase', 'Ob', '20161'),
('CIN7402', 'Editoração Científica', '4ª Fase', 'Ob', '20161'),
('CIN7403', 'Acessibilidade e Inclusão Digital', '4ª Fase', 'Ob', '20161'),
('CIN7404', 'Planejamento Estratégico', '4ª Fase', 'Ob', '20161'),
('CIN7405', 'Projeto de Informatização', '4ª Fase', 'Ob', '20161'),
('CIN7406', 'Preservação Digital', '4ª Fase', 'Ob', '20161'),
('CIN7408', 'Interação Comunitária II', '4ª Fase', 'Ob', '20161'),
('CIN7412', 'Marketing da Informação', '4ª Fase', 'Ob', '20161'),
('INE5111', 'Estatística Aplicada I', '4ª Fase', 'Ob', '20161'),

-- 5ª Fase
('CIN7501', 'Arquitetura da Informação e Usabilidade', '5ª Fase', 'Ob', '20161'),
('CIN7502', 'Mineração de Texto', '5ª Fase', 'Ob', '20161'),
('CIN7503', 'Bancos de Dados', '5ª Fase', 'Ob', '20161'),
('CIN7504', 'Gerenciamento de Projetos', '5ª Fase', 'Ob', '20161'),
('CIN7505', 'Estágio em Ciência da Informação', '5ª Fase', 'Ob', '20161'),

-- 6ª Fase
('CIN7601', 'Linked Data', '6ª Fase', 'Ob', '20161'),
('CIN7602', 'Mídias Sociais', '6ª Fase', 'Ob', '20161'),
('CIN7603', 'Empreendedorismo II', '6ª Fase', 'Ob', '20161'),
('CIN7604', 'TCC', '6ª Fase', 'Ob', '20161'),

-- Disciplinas Optativas
('CIN7950', 'Programa de Intercâmbio I', 'Optativas', 'Op', '20161'),
('CIN7138', 'Introdução à Ciência da Informação', 'Optativas', 'Op', '20161'),
('CIN7308', 'Gestão dos Processos Organizacionais', 'Optativas', 'Op', '20161'),
('CIN7901', 'Análise de Risco e Negociação', 'Optativas', 'Op', '20161'),
('CIN7902', 'Marketing da Informação', 'Optativas', 'Op', '20161'),
('CIN7903', 'Inteligência Competitiva', 'Optativas', 'Op', '20161'),
('CIN7904', 'Avaliação de Desempenho', 'Optativas', 'Op', '20161'),
('CIN7905', 'Teoria da Decisão', 'Optativas', 'Op', '20161'),
('CIN7906', 'Inovação e Informação', 'Optativas', 'Op', '20161'),
('CIN7907', 'Lógica Aplicada I', 'Optativas', 'Op', '20161'),
('CIN7908', 'Lógica Aplicada II', 'Optativas', 'Op', '20161'),
('CIN7909', 'Prototipagem de Cenários Informacionais', 'Optativas', 'Op', '20161'),
('CIN7910', 'Projeto de Implemetação de Cenários Web', 'Optativas', 'Op', '20161'),
('CIN7911', 'Informação na Web', 'Optativas', 'Op', '20161'),
('CIN7912', 'Linguagens de Marcação', 'Optativas', 'Op', '20161'),
('CIN7913', 'Lógica Instrumental II', 'Optativas', 'Op', '20161'),
('CIN7914', 'Análise de Redes Sociais', 'Optativas', 'Op', '20161'),
('CIN7915', 'Data Science', 'Optativas', 'Op', '20161'),
('CIN7916', 'Teoria e Análise de Sistemas', 'Optativas', 'Op', '20161'),
('CIN7917', 'Visualização da Informação', 'Optativas', 'Op', '20161'),
('CIN7918', 'Sistemas de Suporte à Informação Digital', 'Optativas', 'Op', '20161'),
('CIN7919', 'Informação, Direito e Cidadania', 'Optativas', 'Op', '20161'),
('CIN7920', 'Informação Tecnológica e Inovação', 'Optativas', 'Op', '20161'),
('CIN7921', 'Marketing em Arquivo', 'Optativas', 'Op', '20161'),
('CIN7922', 'Direito na Gestão da Inovação', 'Optativas', 'Op', '20161'),
('CIN7923', 'Atividades Complementares', 'Optativas', 'Op', '20161'),
('CIN7924', 'Tipologia de Bibliotecas', 'Optativas', 'Op', '20161'),
('CIN7926', 'Informação e Cultura Popular', 'Optativas', 'Op', '20161'),
('CIN7927', 'Gestão da Informação Pública', 'Optativas', 'Op', '20161'),
('CIN7928', 'Tópicos Especiais em Informação e Tecnologia', 'Optativas', 'Op', '20161'),
('CIN7929', 'Engenharia de Dados', 'Optativas', 'Op', '20161'),
('CIN7930', 'Arquivos Pessoais', 'Optativas', 'Op', '20161'),
('CIN7931', 'Informação em Arte', 'Optativas', 'Op', '20161'),
('CIN7932', 'Ciência da Informação e Museologia', 'Optativas', 'Op', '20161'),
('CIN7933', 'Gestão da Inovação', 'Optativas', 'Op', '20161'),
('CIN7934', 'Práticas de Inteligência Competitiva', 'Optativas', 'Op', '20161'),
('CIN7935', 'Liderança e Gerência', 'Optativas', 'Op', '20161'),
('CIN7936', 'Proteção de Dados Pessoais', 'Optativas', 'Op', '20161'),
('CIN7937', 'Engenharia de Dados II', 'Optativas', 'Op', '20161'),
('CIN7938', 'Segurança da Informação', 'Optativas', 'Op', '20161'),
('CIN7939', 'Tópicos Especiais em Informação e Tecnologia II', 'Optativas', 'Op', '20161'),
('CIN7940', 'Tópicos Especiais em Informação e Tecnologia III', 'Optativas', 'Op', '20161'),
('CIN7941', 'Algoritmos II', 'Optativas', 'Op', '20161'),
('CIN7942', 'Introdução à aprendizagem de Máquina', 'Optativas', 'Op', '20161'),
('CIN7943', 'Experiência do Usuário (UX) User Experience', 'Optativas', 'Op', '20161'),
('CIN7944', 'Curadoria Digital', 'Optativas', 'Op', '20161'),
('CIN7945', 'Fontes de Informação Tecnológica', 'Optativas', 'Op', '20161'),
('CIN7946', 'Pitch de Carreira', 'Optativas', 'Op', '20161'),
('CIN7951', 'O Marco Legal das Startups e o Marco Legal da Ciência, Tecnologia e Inovação: interfaces entre direito', 'Optativas', 'Op', '20161'),
('EGC5028', 'Habitats de Inovação', 'Optativas', 'Op', '20161'),

-- ==========================================================
-- CURRÍCULO 20261
-- ==========================================================
-- 1ª Fase
('CAD5103', 'Administração I', '1ª Fase', 'Ob', '20261'),
('CIN7141', 'Lógica Instrumental I', '1ª Fase', 'Ob', '20261'),
('CIN7143', 'Empreendedorismo I', '1ª Fase', 'Ob', '20261'),
('CIN7144', 'Tutoria Acadêmica I', '1ª Fase', 'Ob', '20261'),
('CIN7145', 'Gestão da Informação', '1ª Fase', 'Ob', '20261'),
('CIN7925', 'Introdução a Algoritmos', '1ª Fase', 'Ob', '20261'),
('CIN7943', 'Experiência do Usuário (UX) User Experience', '1ª Fase', 'Ob', '20261'),
('LLV7802', 'Leitura e Produção do Texto', '1ª Fase', 'Ob', '20261'),
('MTM3110', 'Cálculo 1', '1ª Fase', 'Ob', '20261'),

-- 2ª Fase
('CIN7201', 'Sistemas de Organização do Conhecimento', '2ª Fase', 'Ob', '20261'),
('CIN7204', 'Tutoria Acadêmica II', '2ª Fase', 'Ob', '20261'),
('CIN7309', 'Gestão de Processos Organizacionais', '2ª Fase', 'Ob', '20261'),
('CIN7412', 'Marketing da Informação', '2ª Fase', 'Ob', '20261'),
('CIN7907', 'Lógica Aplicada I', '2ª Fase', 'Ob', '20261'),
('INE5111', 'Estatística Aplicada I', '2ª Fase', 'Ob', '20261'),

-- 3ª Fase
('CIN7000', 'Laboratório de Empreendimentos Sociais (EXT 36h-a)', '3ª Fase', 'Ob', '20261'),
('CIN7301', 'Introdução à Representação Temática', '3ª Fase', 'Ob', '20261'),
('CIN7302', 'Introdução à Representação Descritiva', '3ª Fase', 'Ob', '20261'),
('CIN7304', 'Introdução à Bancos de Dados', '3ª Fase', 'Ob', '20261'),
('CIN7501', 'Arquitetura da Informação e Usabilidade', '3ª Fase', 'Ob', '20261'),
('CIN7602', 'Mídias Sociais', '3ª Fase', 'Ob', '20261'),
('CIN7936', 'Proteção de Dados Pessoais', '3ª Fase', 'Ob', '20261'),
('MTM3687', 'Aprendizado de Máquina Aplicado', '3ª Fase', 'Ob', '20261'),

-- 4ª Fase
('CIN1111', 'Fontes de Informação Tecnológica (EXT 36h-a)', '4ª Fase', 'Ob', '20261'),
('CIN7401', 'Estudos Métricos da Informação', '4ª Fase', 'Ob', '20261'),
('CIN7403', 'Acessibilidade e Inclusão Digital', '4ª Fase', 'Ob', '20261'),
('CIN7404', 'Planejamento Estratégico', '4ª Fase', 'Ob', '20261'),
('CIN7411', 'Análise Exploratória de Dados', '4ª Fase', 'Ob', '20261'),
('CIN7503', 'Bancos de Dados', '4ª Fase', 'Ob', '20261'),
('CIN7903', 'Inteligência Competitiva', '4ª Fase', 'Ob', '20261'),
('CIN7938', 'Segurança da Informação', '4ª Fase', 'Ob', '20261'),
('HST7921', 'História do Brasil Contemporâneo', '4ª Fase', 'Ob', '20261'),

-- 5ª Fase
('CIN7502', 'Mineração de Texto', '5ª Fase', 'Ob', '20261'),
('CIN7504', 'Gerenciamento de Projetos', '5ª Fase', 'Ob', '20261'),
('CIN7505', 'Estágio em Ciência da Informação', '5ª Fase', 'Ob', '20261'),
('CIN7933', 'Gestão da Inovação', '5ª Fase', 'Ob', '20261'),

-- 6ª Fase
('CIN1112', 'Empreendedorismo II (EXT 72h-a)', '6ª Fase', 'Ob', '20261'),
('CIN7601', 'Linked Data', '6ª Fase', 'Ob', '20261'),
('CIN7604', 'TCC', '6ª Fase', 'Ob', '20261'),

-- Rol de Disciplinas Optativas
('CIN1114', 'Direito na Gestão da Inovação (EXT 36h-a)', 'Optativas', 'Op', '20261'),
('CIN7901', 'Análise de Risco e Negociação', 'Optativas', 'Op', '20261'),
('CIN7904', 'Avaliação de Desempenho', 'Optativas', 'Op', '20261'),
('CIN7905', 'Teoria da Decisão', 'Optativas', 'Op', '20261'),
('CIN7906', 'Inovação e Informação', 'Optativas', 'Op', '20261'),
('CIN7908', 'Lógica Aplicada II', 'Optativas', 'Op', '20261'),
('CIN7909', 'Prototipagem de Cenários Informacionais', 'Optativas', 'Op', '20261'),
('CIN7910', 'Projeto de Implemetação de Cenários Web', 'Optativas', 'Op', '20261'),
('CIN7911', 'Informação na Web', 'Optativas', 'Op', '20261'),
('CIN7912', 'Linguagens de Marcação', 'Optativas', 'Op', '20261'),
('CIN7913', 'Lógica Instrumental II', 'Optativas', 'Op', '20261'),
('CIN7914', 'Análise de Redes Sociais', 'Optativas', 'Op', '20261'),
('CIN7915', 'Data Science', 'Optativas', 'Op', '20261'),
('CIN7916', 'Teoria e Análise de Sistemas', 'Optativas', 'Op', '20261'),
('CIN7917', 'Visualização da Informação', 'Optativas', 'Op', '20261'),
('CIN7918', 'Sistemas de Suporte à Informação Digital', 'Optativas', 'Op', '20261'),
('CIN7919', 'Informação, Direito e Cidadania', 'Optativas', 'Op', '20261'),
('CIN7920', 'Informação Tecnológica e Inovação', 'Optativas', 'Op', '20261'),
('CIN7927', 'Gestão da Informação Pública', 'Optativas', 'Op', '20261'),
('CIN7928', 'Tópicos Especiais em Informação e Tecnologia', 'Optativas', 'Op', '20261'),
('CIN7929', 'Engenharia de Dados', 'Optativas', 'Op', '20261'),
('CIN7934', 'Práticas de Inteligência Competitiva', 'Optativas', 'Op', '20261'),
('CIN7935', 'Liderança e Gerência', 'Optativas', 'Op', '20261'),
('CIN7937', 'Engenharia de Dados II', 'Optativas', 'Op', '20261'),
('CIN7939', 'Tópicos Especiais em Informação e Tecnologia II', 'Optativas', 'Op', '20261'),
('CIN7940', 'Tópicos Especiais em Informação e Tecnologia III', 'Optativas', 'Op', '20261'),
('CIN7941', 'Algoritmos II', 'Optativas', 'Op', '20261'),
('CIN7944', 'Curadoria Digital', 'Optativas', 'Op', '20261'),
('CIN7946', 'Pitch de Carreira', 'Optativas', 'Op', '20261'),
('LSB7244', 'Língua Brasileira de Sinais - Libras I (PCC 18h-a)', 'Optativas', 'Op', '20261'),

-- Rol de Atividades Complementares
('CIN7923', 'Atividades Complementares', 'Atividades Complementares', 'Op', '20261'),

-- Rol de Atividades de Extensão
('CIN1113', 'Atividades de Extensão (ações em projetos, cursos e eventos)', 'Atividades de Extensão', 'Op', '20261');'''