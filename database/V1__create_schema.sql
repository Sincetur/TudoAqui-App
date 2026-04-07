-- ============================================
-- TUDOaqui SuperApp - Schema SQL (Fase 1 MVP)
-- Tuendi Taxi + Core + Pagamentos
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. USERS (Core)
-- ============================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    telefone VARCHAR(20) UNIQUE NOT NULL,
    nome VARCHAR(120),
    email VARCHAR(150),
    role VARCHAR(30) NOT NULL CHECK (role IN (
        'cliente', 'motorista', 'entregador', 'organizador',
        'vendedor', 'anfitriao', 'agente', 'staff', 'admin'
    )),
    status VARCHAR(20) NOT NULL DEFAULT 'ativo' CHECK (status IN (
        'ativo', 'inativo', 'suspenso', 'pendente'
    )),
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 2. OTP (Autenticação)
-- ============================================
CREATE TABLE otp_codes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    telefone VARCHAR(20) NOT NULL,
    codigo VARCHAR(6) NOT NULL,
    tentativas INT DEFAULT 0,
    verificado BOOLEAN DEFAULT FALSE,
    expira_em TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 3. REFRESH TOKENS
-- ============================================
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(500) NOT NULL UNIQUE,
    device_info TEXT,
    expira_em TIMESTAMP WITH TIME ZONE NOT NULL,
    revogado BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 4. DRIVERS (Motoristas)
-- ============================================
CREATE TABLE drivers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    veiculo VARCHAR(100) NOT NULL,
    matricula VARCHAR(30) NOT NULL,
    cor_veiculo VARCHAR(50),
    marca VARCHAR(50),
    modelo VARCHAR(50),
    ano INT,
    carta_conducao VARCHAR(50),
    documento_veiculo VARCHAR(100),
    online BOOLEAN DEFAULT FALSE,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    ultima_localizacao_at TIMESTAMP WITH TIME ZONE,
    rating_medio DECIMAL(3, 2) DEFAULT 5.00,
    total_corridas INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pendente' CHECK (status IN (
        'pendente', 'aprovado', 'rejeitado', 'suspenso'
    )),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 5. RIDES (Corridas)
-- ============================================
CREATE TABLE rides (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cliente_id UUID NOT NULL REFERENCES users(id),
    motorista_id UUID REFERENCES drivers(id),
    
    -- Origem
    origem_endereco TEXT NOT NULL,
    origem_latitude DECIMAL(10, 8) NOT NULL,
    origem_longitude DECIMAL(11, 8) NOT NULL,
    
    -- Destino
    destino_endereco TEXT NOT NULL,
    destino_latitude DECIMAL(10, 8) NOT NULL,
    destino_longitude DECIMAL(11, 8) NOT NULL,
    
    -- Valores
    distancia_km DECIMAL(10, 2),
    duracao_estimada_min INT,
    valor_estimado NUMERIC(12, 2),
    valor_final NUMERIC(12, 2),
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'solicitada' CHECK (status IN (
        'solicitada', 'aceite', 'motorista_a_caminho', 'em_curso', 
        'finalizada', 'cancelada_cliente', 'cancelada_motorista'
    )),
    
    -- Timestamps
    solicitada_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    aceite_at TIMESTAMP WITH TIME ZONE,
    iniciada_at TIMESTAMP WITH TIME ZONE,
    finalizada_at TIMESTAMP WITH TIME ZONE,
    cancelada_at TIMESTAMP WITH TIME ZONE,
    motivo_cancelamento TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 6. RIDE TRACKING (Histórico de localização)
-- ============================================
CREATE TABLE ride_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ride_id UUID NOT NULL REFERENCES rides(id) ON DELETE CASCADE,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    velocidade DECIMAL(5, 2),
    bearing DECIMAL(5, 2),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 7. RATINGS (Avaliações)
-- ============================================
CREATE TABLE ratings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ride_id UUID NOT NULL REFERENCES rides(id) ON DELETE CASCADE,
    avaliador_id UUID NOT NULL REFERENCES users(id),
    avaliado_id UUID NOT NULL REFERENCES users(id),
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('cliente_para_motorista', 'motorista_para_cliente')),
    nota INT NOT NULL CHECK (nota >= 1 AND nota <= 5),
    comentario TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(ride_id, tipo)
);

-- ============================================
-- 8. PAYMENTS (Pagamentos)
-- ============================================
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    referencia VARCHAR(100) UNIQUE NOT NULL,
    origem_tipo VARCHAR(20) NOT NULL CHECK (origem_tipo IN (
        'ride', 'ticket', 'marketplace', 'booking', 'experience'
    )),
    origem_id UUID NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id),
    
    metodo VARCHAR(30) NOT NULL CHECK (metodo IN (
        'multicaixa', 'mobilemoney', 'wallet', 'dinheiro'
    )),
    valor NUMERIC(12, 2) NOT NULL,
    taxa_servico NUMERIC(12, 2) DEFAULT 0,
    valor_total NUMERIC(12, 2) NOT NULL,
    
    status VARCHAR(20) NOT NULL DEFAULT 'iniciado' CHECK (status IN (
        'iniciado', 'pendente', 'processando', 'confirmado', 'falhado', 'reembolsado'
    )),
    
    -- Dados externos
    external_ref VARCHAR(200),
    external_status VARCHAR(50),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    confirmado_at TIMESTAMP WITH TIME ZONE
);

-- ============================================
-- 9. LEDGER ENTRIES (Livro razão)
-- ============================================
CREATE TABLE ledger_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    payment_id UUID REFERENCES payments(id),
    origem_tipo VARCHAR(20) NOT NULL,
    origem_id UUID NOT NULL,
    beneficiario_id UUID REFERENCES users(id), -- NULL = plataforma
    tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('credito', 'debito')),
    valor NUMERIC(12, 2) NOT NULL,
    descricao TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 10. WALLETS (Carteiras - preparado para Fase 2)
-- ============================================
CREATE TABLE wallets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    saldo NUMERIC(14, 2) DEFAULT 0,
    saldo_bloqueado NUMERIC(14, 2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 11. NOTIFICATIONS
-- ============================================
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    titulo VARCHAR(200) NOT NULL,
    mensagem TEXT NOT NULL,
    tipo VARCHAR(30) NOT NULL CHECK (tipo IN (
        'ride_status', 'payment', 'promo', 'system', 'rating'
    )),
    dados JSONB,
    lida BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 12. CONFIGURAÇÕES DO SISTEMA
-- ============================================
CREATE TABLE config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chave VARCHAR(100) UNIQUE NOT NULL,
    valor TEXT NOT NULL,
    descricao TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Inserir configurações padrão
INSERT INTO config (chave, valor, descricao) VALUES
('TAXA_PLATAFORMA_TUENDI', '0.20', 'Taxa da plataforma para corridas Tuendi (20%)'),
('PRECO_BASE_KM', '150', 'Preço base por km em Kz'),
('PRECO_BASE_MINUTO', '50', 'Preço base por minuto em Kz'),
('TAXA_MINIMA', '500', 'Taxa mínima por corrida em Kz'),
('RAIO_BUSCA_MOTORISTAS', '5000', 'Raio de busca de motoristas em metros'),
('TEMPO_EXPIRACAO_OTP', '5', 'Tempo de expiração do OTP em minutos'),
('MAX_TENTATIVAS_OTP', '3', 'Máximo de tentativas de OTP');

-- ============================================
-- ÍNDICES
-- ============================================
CREATE INDEX idx_users_telefone ON users(telefone);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);

CREATE INDEX idx_otp_telefone ON otp_codes(telefone);
CREATE INDEX idx_otp_expira ON otp_codes(expira_em);

CREATE INDEX idx_drivers_user ON drivers(user_id);
CREATE INDEX idx_drivers_online ON drivers(online);
CREATE INDEX idx_drivers_status ON drivers(status);
CREATE INDEX idx_drivers_location ON drivers(latitude, longitude);

CREATE INDEX idx_rides_cliente ON rides(cliente_id);
CREATE INDEX idx_rides_motorista ON rides(motorista_id);
CREATE INDEX idx_rides_status ON rides(status);
CREATE INDEX idx_rides_created ON rides(created_at);

CREATE INDEX idx_payments_user ON payments(user_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_origem ON payments(origem_tipo, origem_id);

CREATE INDEX idx_ledger_beneficiario ON ledger_entries(beneficiario_id);
CREATE INDEX idx_ledger_origem ON ledger_entries(origem_tipo, origem_id);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_lida ON notifications(lida);

-- ============================================
-- TRIGGERS
-- ============================================

-- Trigger para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_drivers_updated_at
    BEFORE UPDATE ON drivers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_rides_updated_at
    BEFORE UPDATE ON rides
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_payments_updated_at
    BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Trigger para atualizar total de corridas do motorista
CREATE OR REPLACE FUNCTION update_driver_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'finalizada' AND OLD.status != 'finalizada' THEN
        UPDATE drivers 
        SET total_corridas = total_corridas + 1
        WHERE id = NEW.motorista_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_ride_completed
    AFTER UPDATE ON rides
    FOR EACH ROW EXECUTE FUNCTION update_driver_stats();

-- Trigger para atualizar rating médio do motorista
CREATE OR REPLACE FUNCTION update_driver_rating()
RETURNS TRIGGER AS $$
DECLARE
    avg_rating DECIMAL(3, 2);
    driver_user_id UUID;
BEGIN
    IF NEW.tipo = 'cliente_para_motorista' THEN
        -- Buscar o driver_id através do ride
        SELECT d.id INTO driver_user_id
        FROM rides r
        JOIN drivers d ON d.id = r.motorista_id
        WHERE r.id = NEW.ride_id;
        
        IF driver_user_id IS NOT NULL THEN
            SELECT AVG(rt.nota)::DECIMAL(3, 2) INTO avg_rating
            FROM ratings rt
            JOIN rides r ON r.id = rt.ride_id
            WHERE r.motorista_id = driver_user_id
            AND rt.tipo = 'cliente_para_motorista';
            
            UPDATE drivers SET rating_medio = COALESCE(avg_rating, 5.00)
            WHERE id = driver_user_id;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_rating_created
    AFTER INSERT ON ratings
    FOR EACH ROW EXECUTE FUNCTION update_driver_rating();

-- ============================================
-- VIEWS
-- ============================================

-- View de corridas ativas
CREATE VIEW vw_corridas_ativas AS
SELECT 
    r.*,
    c.nome as cliente_nome,
    c.telefone as cliente_telefone,
    d.veiculo,
    d.matricula,
    d.cor_veiculo,
    u.nome as motorista_nome,
    u.telefone as motorista_telefone
FROM rides r
JOIN users c ON c.id = r.cliente_id
LEFT JOIN drivers d ON d.id = r.motorista_id
LEFT JOIN users u ON u.id = d.user_id
WHERE r.status NOT IN ('finalizada', 'cancelada_cliente', 'cancelada_motorista');

-- View de motoristas online
CREATE VIEW vw_motoristas_online AS
SELECT 
    d.*,
    u.nome,
    u.telefone,
    u.avatar_url
FROM drivers d
JOIN users u ON u.id = d.user_id
WHERE d.online = TRUE 
AND d.status = 'aprovado'
AND u.status = 'ativo';

-- View de ganhos do motorista
CREATE VIEW vw_ganhos_motorista AS
SELECT
    d.id as driver_id,
    u.nome as motorista,
    COUNT(r.id) as total_corridas,
    COALESCE(SUM(l.valor), 0) as total_ganho,
    d.rating_medio
FROM drivers d
JOIN users u ON u.id = d.user_id
LEFT JOIN rides r ON r.motorista_id = d.id AND r.status = 'finalizada'
LEFT JOIN ledger_entries l ON l.beneficiario_id = u.id AND l.tipo = 'credito'
GROUP BY d.id, u.nome, d.rating_medio;

-- View de comissões da plataforma
CREATE VIEW vw_comissoes_plataforma AS
SELECT
    DATE(created_at) as data,
    COUNT(*) as total_transacoes,
    SUM(valor) as total_comissoes
FROM ledger_entries
WHERE tipo = 'credito' AND beneficiario_id IS NULL
GROUP BY DATE(created_at)
ORDER BY data DESC;

-- ============================================
-- SEED DATA (Dados iniciais)
-- ============================================

-- Admin do sistema
INSERT INTO users (id, telefone, nome, role, status) VALUES
(uuid_generate_v4(), '+244900000001', 'Admin TUDOaqui', 'admin', 'ativo');

-- Clientes de teste
INSERT INTO users (id, telefone, nome, role, status) VALUES
(uuid_generate_v4(), '+244923456789', 'João Silva', 'cliente', 'ativo'),
(uuid_generate_v4(), '+244912345678', 'Maria Santos', 'cliente', 'ativo');

-- Motoristas de teste
INSERT INTO users (id, telefone, nome, role, status) 
VALUES (uuid_generate_v4(), '+244934567890', 'Pedro Neto', 'motorista', 'ativo')
RETURNING id;

-- Nota: O driver será criado depois de ter o user_id
