"""
TUDOaqui API - Seed Data
Dados de demonstracao com conteudo real de Angola
"""
import uuid
from datetime import date, time, datetime, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.database import async_session
from src.users.models import User, UserRole, UserStatus
from src.auth.service import AuthService
from src.events.models import Event, EventStatus, TicketType
from src.marketplace.models import Seller, SellerStatus, ProductCategory, Product, ProductStatus
from src.alojamento.models import Property, PropertyType, PropertyStatus
from src.turismo.models import Experience, ExperienceType, ExperienceStatus
from src.realestate.models import RealEstateAgent, AgentStatus, RealEstateProperty, PropertyTypeRE, TransactionType, PropertyStatusRE
from src.tuendi.restaurante.models import Restaurant, RestaurantStatus, MenuCategory, MenuItem, MenuItemStatus


async def seed_exists(session: AsyncSession) -> bool:
    result = await session.execute(select(func.count()).select_from(Event))
    return result.scalar() > 0


async def run_seed():
    async with async_session() as session:
        if await seed_exists(session):
            return {"message": "Seed data ja existe", "seeded": False}

        # === USERS ===
        admin_password_hash = AuthService.hash_password("TUDOaqui@2026")
        users = {}
        user_data = [
            ("seed_admin", "+244912000000", "Admin TUDOaqui", UserRole.ADMIN, admin_password_hash),
            ("seed_org", "+244911000001", "Carlos Mendes", UserRole.GUIA_TURISTA, None),
            ("seed_seller", "+244911000002", "Ana Ferreira", UserRole.PROPRIETARIO, None),
            ("seed_host", "+244911000003", "Manuel Santos", UserRole.PROPRIETARIO, None),
            ("seed_agent", "+244911000004", "Sofia Neto", UserRole.AGENTE_IMOBILIARIO, None),
            ("seed_rest", "+244911000005", "Pedro Gomes", UserRole.PROPRIETARIO, None),
            ("seed_guide", "+244911000006", "Joana Silva", UserRole.AGENTE_VIAGEM, None),
        ]
        for key, tel, nome, role, pw_hash in user_data:
            # Check if user already exists (e.g. admin created at startup)
            result = await session.execute(
                select(User).where(User.telefone == tel)
            )
            existing = result.scalar_one_or_none()
            if existing:
                users[key] = existing
            else:
                u = User(id=uuid.uuid4(), telefone=tel, nome=nome, role=role, status=UserStatus.ATIVO, password_hash=pw_hash)
                session.add(u)
                users[key] = u
        await session.flush()

        # === EVENTS ===
        events_data = [
            {
                "titulo": "Festival Internacional de Musica de Luanda",
                "descricao": "O maior festival de musica da Africa Austral com artistas internacionais e locais. Tres dias de musica, gastronomia e cultura angolana no Complexo Turismo.",
                "local": "Complexo Turistico da Ilha de Luanda",
                "local_latitude": Decimal("-8.80000000"),
                "local_longitude": Decimal("13.23000000"),
                "data_evento": date(2026, 6, 15),
                "hora_evento": time(18, 0),
                "data_fim": date(2026, 6, 17),
                "categoria": "Musica",
                "status": EventStatus.ATIVO,
            },
            {
                "titulo": "Expo Angola Tech 2026",
                "descricao": "Conferencia de tecnologia e inovacao. Startups, IA, fintech e transformacao digital em Angola. Networking com investidores e mentores.",
                "local": "Centro de Convencoes de Talatona",
                "local_latitude": Decimal("-8.92000000"),
                "local_longitude": Decimal("13.19000000"),
                "data_evento": date(2026, 7, 10),
                "hora_evento": time(9, 0),
                "data_fim": date(2026, 7, 12),
                "categoria": "Tecnologia",
                "status": EventStatus.ATIVO,
            },
            {
                "titulo": "Noite de Semba e Kizomba",
                "descricao": "Uma noite especial dedicada a musica e danca angolana com os melhores DJs de Luanda. Open bar e finger food incluidos.",
                "local": "Bar Terraço, Marginal de Luanda",
                "local_latitude": Decimal("-8.81000000"),
                "local_longitude": Decimal("13.23500000"),
                "data_evento": date(2026, 5, 24),
                "hora_evento": time(21, 0),
                "categoria": "Entretenimento",
                "status": EventStatus.ATIVO,
            },
            {
                "titulo": "Maratona de Luanda 2026",
                "descricao": "Corrida de 42km pela marginal de Luanda com vista para o oceano. Categorias: maratona completa, meia maratona e corrida de 10km.",
                "local": "Marginal de Luanda - Fortaleza de Sao Miguel",
                "local_latitude": Decimal("-8.81500000"),
                "local_longitude": Decimal("13.23100000"),
                "data_evento": date(2026, 9, 7),
                "hora_evento": time(6, 0),
                "categoria": "Desporto",
                "status": EventStatus.ATIVO,
            },
            {
                "titulo": "Feira do Livro de Luanda",
                "descricao": "Encontro literario com autores angolanos e lusófonos. Lancamentos, debates e workshops de escrita criativa.",
                "local": "Biblioteca Nacional de Angola",
                "local_latitude": Decimal("-8.83800000"),
                "local_longitude": Decimal("13.23400000"),
                "data_evento": date(2026, 8, 1),
                "hora_evento": time(10, 0),
                "data_fim": date(2026, 8, 5),
                "categoria": "Cultura",
                "status": EventStatus.ATIVO,
            },
        ]
        event_objs = []
        for ed in events_data:
            ev = Event(id=uuid.uuid4(), organizer_id=users["seed_org"].id, **ed)
            session.add(ev)
            event_objs.append(ev)
        await session.flush()

        # Ticket types for events
        for ev in event_objs:
            tt_normal = TicketType(id=uuid.uuid4(), event_id=ev.id, nome="Normal", preco=Decimal("5000.00"), quantidade_total=500, quantidade_vendida=47)
            tt_vip = TicketType(id=uuid.uuid4(), event_id=ev.id, nome="VIP", preco=Decimal("15000.00"), quantidade_total=100, quantidade_vendida=12)
            session.add_all([tt_normal, tt_vip])

        # === MARKETPLACE ===
        seller = Seller(
            id=uuid.uuid4(), user_id=users["seed_seller"].id,
            nome_loja="Kambas Store", descricao="Moda africana contemporanea e acessorios artesanais feitos em Angola",
            cidade="Luanda", provincia="Luanda", taxa_entrega_base=Decimal("1500.00"),
            rating_medio=Decimal("4.70"), total_vendas=234, status=SellerStatus.APROVADO,
        )
        session.add(seller)

        categories_data = [
            ("Moda", "Roupa e acessorios", "shirt"),
            ("Electronica", "Gadgets e tecnologia", "smartphone"),
            ("Casa & Jardim", "Decoracao e mobiliario", "home"),
            ("Alimentacao", "Produtos alimentares", "utensils"),
            ("Desporto", "Equipamento desportivo", "dumbbell"),
        ]
        cat_objs = []
        for nome, desc, icone in categories_data:
            c = ProductCategory(id=uuid.uuid4(), nome=nome, descricao=desc, icone=icone, ordem=len(cat_objs))
            session.add(c)
            cat_objs.append(c)
        await session.flush()

        products_data = [
            {"nome": "Camisa Wax Africana", "descricao": "Camisa em tecido wax 100% algodao, padrao tradicional angolano", "preco": Decimal("8500.00"), "stock": 45, "destaque": True, "category_id": cat_objs[0].id},
            {"nome": "Colar de Missangas Kwanza", "descricao": "Colar artesanal com missangas do rio Kwanza. Peca unica feita por artesaos locais.", "preco": Decimal("3200.00"), "stock": 23, "category_id": cat_objs[0].id},
            {"nome": "Smartphone Xiaomi Redmi 14", "descricao": "Telemovel 6.7 polegadas, 128GB, camera 108MP, bateria 5000mAh", "preco": Decimal("95000.00"), "preco_promocional": Decimal("79990.00"), "stock": 12, "destaque": True, "category_id": cat_objs[1].id},
            {"nome": "Fones Bluetooth TWS Pro", "descricao": "Auriculares sem fio com cancelamento de ruido, 30h de bateria", "preco": Decimal("12500.00"), "stock": 38, "category_id": cat_objs[1].id},
            {"nome": "Conjunto de Panelas Ceramica", "descricao": "Kit 5 pecas com revestimento ceramico anti-aderente", "preco": Decimal("25000.00"), "stock": 15, "category_id": cat_objs[2].id},
            {"nome": "Cafe Sanzala Premium 500g", "descricao": "Cafe 100% robusta angolano, torrado e moido. Origem: Kwanza Sul", "preco": Decimal("4500.00"), "stock": 100, "destaque": True, "category_id": cat_objs[3].id},
            {"nome": "Ginga Picante 250ml", "descricao": "Molho de gindungo artesanal, receita tradicional angolana", "preco": Decimal("1800.00"), "stock": 67, "category_id": cat_objs[3].id},
            {"nome": "Bola de Futebol Pro Match", "descricao": "Bola oficial tamanho 5, material PU, aprovada FIFA", "preco": Decimal("7500.00"), "stock": 20, "category_id": cat_objs[4].id},
        ]
        for pd in products_data:
            p = Product(id=uuid.uuid4(), seller_id=seller.id, status=ProductStatus.ATIVO, visualizacoes=150, vendas=23, **pd)
            session.add(p)

        # === ALOJAMENTO ===
        aloj_data = [
            {
                "titulo": "Apartamento Vista Mar na Ilha",
                "descricao": "Apartamento moderno T2 com vista panoramica para o oceano. Totalmente mobilado com cozinha equipada, varanda e piscina no condominio.",
                "tipo": PropertyType.APARTAMENTO, "endereco": "Rua da Ilha, Ilha de Luanda",
                "cidade": "Luanda", "provincia": "Luanda",
                "latitude": Decimal("-8.79500000"), "longitude": Decimal("13.23200000"),
                "quartos": 2, "camas": 3, "banheiros": 2, "max_hospedes": 5,
                "preco_noite": Decimal("35000.00"), "preco_limpeza": Decimal("5000.00"),
                "comodidades": {"items": ["Wi-Fi", "Piscina", "Ar Condicionado", "Cozinha", "Estacionamento", "Vista Mar"]},
                "rating_medio": Decimal("4.80"), "total_reservas": 45, "status": PropertyStatus.ATIVO,
            },
            {
                "titulo": "Villa Tropical em Talatona",
                "descricao": "Villa espaçosa T4 com jardim tropical, churrasqueira e piscina privativa. Ideal para familias ou grupos.",
                "tipo": PropertyType.VILLA, "endereco": "Condominio Nova Vida, Talatona",
                "cidade": "Luanda", "provincia": "Luanda",
                "latitude": Decimal("-8.92500000"), "longitude": Decimal("13.18500000"),
                "quartos": 4, "camas": 6, "banheiros": 3, "max_hospedes": 10,
                "preco_noite": Decimal("75000.00"), "preco_limpeza": Decimal("10000.00"),
                "comodidades": {"items": ["Wi-Fi", "Piscina Privativa", "Churrasqueira", "Jardim", "Gerador", "Seguranca 24h"]},
                "rating_medio": Decimal("4.90"), "total_reservas": 28, "status": PropertyStatus.ATIVO,
            },
            {
                "titulo": "Quarto Acolhedor no Miramar",
                "descricao": "Quarto privado num apartamento partilhado no coracao do Miramar. Perto de restaurantes, bares e da marginal.",
                "tipo": PropertyType.QUARTO, "endereco": "Rua Rainha Ginga, Miramar",
                "cidade": "Luanda", "provincia": "Luanda",
                "latitude": Decimal("-8.82000000"), "longitude": Decimal("13.22800000"),
                "quartos": 1, "camas": 1, "banheiros": 1, "max_hospedes": 2,
                "preco_noite": Decimal("12000.00"), "preco_limpeza": Decimal("2000.00"),
                "comodidades": {"items": ["Wi-Fi", "Ar Condicionado", "Pequeno Almoco"]},
                "rating_medio": Decimal("4.50"), "total_reservas": 89, "status": PropertyStatus.ATIVO,
            },
            {
                "titulo": "Casa de Praia em Cabo Ledo",
                "descricao": "Casa de ferias a 200m da praia de Cabo Ledo. Perfeita para surfistas e amantes da natureza. Vista incrivel para o oceano.",
                "tipo": PropertyType.CASA, "endereco": "Praia de Cabo Ledo",
                "cidade": "Cabo Ledo", "provincia": "Bengo",
                "latitude": Decimal("-9.62000000"), "longitude": Decimal("13.26500000"),
                "quartos": 3, "camas": 4, "banheiros": 2, "max_hospedes": 8,
                "preco_noite": Decimal("45000.00"), "preco_limpeza": Decimal("7000.00"),
                "comodidades": {"items": ["Wi-Fi", "Churrasqueira", "Praia Proxima", "Cozinha", "Varanda"]},
                "rating_medio": Decimal("4.70"), "total_reservas": 62, "status": PropertyStatus.ATIVO,
            },
        ]
        for ad in aloj_data:
            prop = Property(id=uuid.uuid4(), host_id=users["seed_host"].id, **ad)
            session.add(prop)

        # === TURISMO ===
        turismo_data = [
            {
                "titulo": "Tour pela Cidade de Luanda",
                "descricao": "Descubra a historia e cultura de Luanda num tour guiado de meio dia. Visite a Fortaleza de Sao Miguel, a Igreja da Nazare e o Museu Nacional.",
                "tipo": ExperienceType.TOUR, "local": "Centro Historico de Luanda", "cidade": "Luanda",
                "ponto_encontro": "Frente a Fortaleza de Sao Miguel",
                "latitude": Decimal("-8.81400000"), "longitude": Decimal("13.23200000"),
                "duracao_horas": 4, "max_participantes": 15, "preco": Decimal("15000.00"),
                "preco_crianca": Decimal("7500.00"),
                "inclui": {"items": ["Guia bilingue", "Transporte", "Agua e snacks", "Entrada nos museus"]},
                "nao_inclui": {"items": ["Almoco", "Compras pessoais"]},
                "idiomas": {"items": ["Portugues", "Ingles", "Frances"]},
                "rating_medio": Decimal("4.90"), "total_reservas": 156, "status": ExperienceStatus.ATIVO,
            },
            {
                "titulo": "Safari na Kissama",
                "descricao": "Aventura de dia inteiro no Parque Nacional da Kissama. Avistamento de elefantes, girafas, bufalos e aves exoticas no unico parque nacional acessivel de Luanda.",
                "tipo": ExperienceType.AVENTURA, "local": "Parque Nacional da Kissama", "cidade": "Kissama",
                "ponto_encontro": "Hotel Epic Sana, Luanda (transfer incluido)",
                "latitude": Decimal("-9.38000000"), "longitude": Decimal("13.40000000"),
                "duracao_horas": 10, "max_participantes": 8, "preco": Decimal("45000.00"),
                "preco_crianca": Decimal("25000.00"),
                "inclui": {"items": ["Transfer Luanda-Kissama", "Guia especializado", "Almoco", "Agua", "Binoculos"]},
                "nao_inclui": {"items": ["Gorjetas", "Seguro viagem"]},
                "requisitos": {"items": ["Idade minima: 5 anos", "Usar roupa confortavel"]},
                "idiomas": {"items": ["Portugues", "Ingles"]},
                "rating_medio": Decimal("4.80"), "total_reservas": 89, "status": ExperienceStatus.ATIVO,
            },
            {
                "titulo": "Workshop de Culinaria Angolana",
                "descricao": "Aprenda a preparar pratos tradicionais angolanos com uma chef local. Muamba de galinha, calulu, funge e muito mais. Inclui degustacao.",
                "tipo": ExperienceType.GASTRONOMIA, "local": "Restaurante Dona Ana, Miramar", "cidade": "Luanda",
                "ponto_encontro": "Restaurante Dona Ana, Rua do Miramar",
                "latitude": Decimal("-8.82500000"), "longitude": Decimal("13.22900000"),
                "duracao_horas": 3, "max_participantes": 10, "preco": Decimal("20000.00"),
                "inclui": {"items": ["Ingredientes", "Avental", "Receitas impressas", "Degustacao completa", "Bebidas"]},
                "idiomas": {"items": ["Portugues", "Ingles"]},
                "rating_medio": Decimal("4.95"), "total_reservas": 67, "status": ExperienceStatus.ATIVO,
            },
            {
                "titulo": "Passeio de Barco na Baia de Luanda",
                "descricao": "Passeio de catamara pela baia de Luanda ao por do sol. Vistas espetaculares da marginal e da ilha. Inclui drinks e petiscos a bordo.",
                "tipo": ExperienceType.NATUREZA, "local": "Marina de Luanda", "cidade": "Luanda",
                "ponto_encontro": "Marina de Luanda, Cais 3",
                "latitude": Decimal("-8.80500000"), "longitude": Decimal("13.23800000"),
                "duracao_horas": 2, "max_participantes": 20, "preco": Decimal("25000.00"),
                "inclui": ["Drinks", "Petiscos", "Coletes salva-vidas", "Musica ao vivo"],
                "nao_inclui": ["Transfer para marina"],
                "idiomas": ["Portugues", "Ingles"],
                "rating_medio": Decimal("4.85"), "total_reservas": 234, "status": ExperienceStatus.ATIVO,
            },
        ]
        for td in turismo_data:
            exp = Experience(id=uuid.uuid4(), host_id=users["seed_guide"].id, **td)
            session.add(exp)

        # === REAL ESTATE ===
        agent = RealEstateAgent(
            id=uuid.uuid4(), user_id=users["seed_agent"].id,
            nome_profissional="Sofia Neto", bio="Agente imobiliaria com 8 anos de experiencia no mercado angolano. Especialista em imoveis de luxo em Luanda.",
            numero_licenca="AG-2024-0042", telefone_profissional="+244911000004",
            email_profissional="sofia.neto@imobiliaria.ao",
            provincias={"items": ["Luanda", "Bengo", "Benguela"]},
            especialidades={"items": ["Apartamentos", "Vivendas", "Comercial"]},
            rating_medio=Decimal("4.85"), total_vendas=32, total_arrendamentos=18,
            plano="pro", status=AgentStatus.APROVADO,
        )
        session.add(agent)
        await session.flush()

        re_data = [
            {
                "titulo": "Apartamento T3 Luxo em Talatona",
                "descricao": "Apartamento de alto padrao no condominio Vida Pacifica. 3 quartos (1 suite), sala ampla, cozinha equipada, varanda com vista para jardim. Condominio com piscina, ginasio e seguranca 24h.",
                "tipo": PropertyTypeRE.APARTAMENTO, "tipo_transacao": TransactionType.VENDA,
                "endereco": "Condominio Vida Pacifica, Talatona", "bairro": "Talatona",
                "cidade": "Luanda", "provincia": "Luanda",
                "preco_venda": Decimal("85000000.00"), "condominio": Decimal("150000.00"),
                "area_total": 145, "area_util": 120, "quartos": 3, "suites": 1, "banheiros": 2, "vagas_garagem": 2,
                "ano_construcao": 2022,
                "caracteristicas": {"items": ["Piscina", "Ginasio", "Seguranca 24h", "Elevador", "Ar Condicionado Central"]},
                "destaque": True, "status": PropertyStatusRE.ATIVO, "visualizacoes": 342,
            },
            {
                "titulo": "Vivenda T5 com Piscina no Patriota",
                "descricao": "Vivenda independente com 5 quartos, piscina, jardim e dependencia de empregada. Terreno de 800m2 em zona nobre do Patriota.",
                "tipo": PropertyTypeRE.VIVENDA, "tipo_transacao": TransactionType.VENDA,
                "endereco": "Rua do Patriota, Zona Nobre", "bairro": "Patriota",
                "cidade": "Luanda", "provincia": "Luanda",
                "preco_venda": Decimal("250000000.00"),
                "area_total": 800, "area_util": 350, "quartos": 5, "suites": 2, "banheiros": 4, "vagas_garagem": 4,
                "ano_construcao": 2019,
                "caracteristicas": {"items": ["Piscina", "Jardim", "Gerador", "Cisterna", "Churrasqueira", "Dependencia"]},
                "destaque": True, "status": PropertyStatusRE.ATIVO, "visualizacoes": 567,
            },
            {
                "titulo": "Apartamento T2 para Arrendamento - Maianga",
                "descricao": "Apartamento T2 no 8o andar com vista para a cidade. Mobilado, cozinha equipada, 2 casas de banho. Proximo ao centro comercial.",
                "tipo": PropertyTypeRE.APARTAMENTO, "tipo_transacao": TransactionType.ARRENDAMENTO,
                "endereco": "Av. 4 de Fevereiro, Maianga", "bairro": "Maianga",
                "cidade": "Luanda", "provincia": "Luanda",
                "preco_arrendamento": Decimal("350000.00"), "condominio": Decimal("80000.00"),
                "area_total": 95, "area_util": 80, "quartos": 2, "banheiros": 2, "vagas_garagem": 1,
                "ano_construcao": 2020,
                "caracteristicas": {"items": ["Mobilado", "Ar Condicionado", "Elevador", "Seguranca"]},
                "status": PropertyStatusRE.ATIVO, "visualizacoes": 189,
            },
            {
                "titulo": "Terreno 1000m2 em Viana",
                "descricao": "Terreno plano de 1000m2 com documentacao completa. Zona em desenvolvimento com acesso a estrada principal. Ideal para construcao residencial ou comercial.",
                "tipo": PropertyTypeRE.TERRENO, "tipo_transacao": TransactionType.VENDA,
                "endereco": "Estrada de Viana, Km 12", "bairro": "Viana",
                "cidade": "Luanda", "provincia": "Luanda",
                "preco_venda": Decimal("45000000.00"),
                "area_total": 1000,
                "caracteristicas": {"items": ["Documentacao Completa", "Acesso Asfaltado", "Agua", "Electricidade Proxima"]},
                "status": PropertyStatusRE.ATIVO, "visualizacoes": 98,
            },
            {
                "titulo": "Escritorio Open Space - Alvalade",
                "descricao": "Espaco de escritorio de 200m2 em edificio empresarial. Open space com 3 salas de reuniao, recepcao e copa. Internet fibra optica incluida.",
                "tipo": PropertyTypeRE.ESCRITORIO, "tipo_transacao": TransactionType.ARRENDAMENTO,
                "endereco": "Edificio Business Center, Alvalade", "bairro": "Alvalade",
                "cidade": "Luanda", "provincia": "Luanda",
                "preco_arrendamento": Decimal("800000.00"), "condominio": Decimal("200000.00"),
                "area_total": 200, "area_util": 180, "banheiros": 2, "vagas_garagem": 5,
                "ano_construcao": 2021,
                "caracteristicas": ["Fibra Optica", "Ar Condicionado Central", "Gerador", "Estacionamento", "Seguranca 24h"],
                "status": PropertyStatusRE.ATIVO, "visualizacoes": 145,
            },
        ]
        for rd in re_data:
            rp = RealEstateProperty(id=uuid.uuid4(), agent_id=agent.id, **rd)
            session.add(rp)

        # === RESTAURANTS ===
        restaurants_data = [
            {
                "nome": "Muamba da Mama",
                "descricao": "Restaurante de cozinha tradicional angolana. Especialidade em muamba de galinha, calulu e funge. Ambiente familiar e acolhedor.",
                "endereco": "Rua dos Coqueiros 45, Miramar", "cidade": "Luanda",
                "latitude": Decimal("-8.82200000"), "longitude": Decimal("13.22700000"),
                "hora_abertura": time(11, 0), "hora_fecho": time(23, 0),
                "dias_funcionamento": {"items": [1, 2, 3, 4, 5, 6]},
                "raio_entrega_km": 12, "tempo_preparo_min": 35,
                "pedido_minimo": Decimal("3000.00"), "taxa_entrega": Decimal("1500.00"),
                "categorias": {"items": ["Angolana", "Tradicional", "Familiar"]},
                "telefone": "+244922111222",
                "rating_medio": Decimal("4.80"), "total_pedidos": 1245, "aberto": True,
                "status": RestaurantStatus.APROVADO,
                "menu": [
                    {"cat": "Pratos Principais", "items": [
                        {"nome": "Muamba de Galinha", "descricao": "Frango cozido em oleo de palma com quiabos e especiarias", "preco": Decimal("4500.00"), "popular": True},
                        {"nome": "Calulu de Peixe", "descricao": "Peixe seco com quiabos, tomate e oleo de palma", "preco": Decimal("5000.00"), "popular": True},
                        {"nome": "Funge com Mufete", "descricao": "Funge de milho com peixe grelhado e feijao de oleo de palma", "preco": Decimal("6000.00")},
                        {"nome": "Cabidela de Galinha", "descricao": "Galinha cozida no proprio sangue com arroz", "preco": Decimal("5500.00")},
                    ]},
                    {"cat": "Acompanhamentos", "items": [
                        {"nome": "Funge de Milho", "descricao": "Acompanhamento tradicional de farinha de milho", "preco": Decimal("800.00")},
                        {"nome": "Arroz Branco", "descricao": "Arroz agulha cozido", "preco": Decimal("600.00")},
                        {"nome": "Feijao de Oleo de Palma", "descricao": "Feijao cozido com oleo de palma e cebola", "preco": Decimal("1200.00")},
                    ]},
                    {"cat": "Bebidas", "items": [
                        {"nome": "Cuca (cerveja)", "descricao": "Cerveja angolana gelada 330ml", "preco": Decimal("500.00"), "popular": True},
                        {"nome": "Sumo de Mukunza", "descricao": "Sumo natural de milho fermentado", "preco": Decimal("800.00")},
                        {"nome": "Agua Pura 500ml", "descricao": "Agua mineral", "preco": Decimal("300.00")},
                    ]},
                ],
            },
            {
                "nome": "Sushi Lounge Luanda",
                "descricao": "Restaurante japones com toque angolano. Sushi fresco, sashimi premium e pratos fusion. Ambiente sofisticado na Ilha.",
                "endereco": "Av. Murtala Mohamed, Ilha de Luanda", "cidade": "Luanda",
                "latitude": Decimal("-8.79800000"), "longitude": Decimal("13.23400000"),
                "hora_abertura": time(12, 0), "hora_fecho": time(0, 0),
                "dias_funcionamento": {"items": [0, 1, 2, 3, 4, 5, 6]},
                "raio_entrega_km": 15, "tempo_preparo_min": 40,
                "pedido_minimo": Decimal("5000.00"), "taxa_entrega": Decimal("2000.00"),
                "categorias": {"items": ["Japonesa", "Sushi", "Fusion"]},
                "telefone": "+244922333444",
                "rating_medio": Decimal("4.60"), "total_pedidos": 876, "aberto": True,
                "status": RestaurantStatus.APROVADO,
                "menu": [
                    {"cat": "Sushi & Sashimi", "items": [
                        {"nome": "Combo 30 Pecas", "descricao": "Mix de sushi, sashimi e hot rolls", "preco": Decimal("18000.00"), "popular": True},
                        {"nome": "Sashimi de Salmao", "descricao": "12 fatias de salmao fresco", "preco": Decimal("12000.00")},
                        {"nome": "Hot Roll Luanda", "descricao": "Roll empanado com camarao e manga", "preco": Decimal("8500.00"), "popular": True},
                    ]},
                    {"cat": "Pratos Quentes", "items": [
                        {"nome": "Ramen de Porco", "descricao": "Ramen com caldo de porco, ovo e cebolinha", "preco": Decimal("9500.00")},
                        {"nome": "Yakisoba de Camarao", "descricao": "Massa salteada com camarao e legumes", "preco": Decimal("11000.00")},
                    ]},
                    {"cat": "Bebidas", "items": [
                        {"nome": "Sake Premium", "descricao": "Sake japones servido quente ou frio", "preco": Decimal("5000.00")},
                        {"nome": "Cha Verde", "descricao": "Cha verde japones", "preco": Decimal("1500.00")},
                    ]},
                ],
            },
            {
                "nome": "Burger Republic",
                "descricao": "Os melhores hambúrgueres artesanais de Luanda. Carne angolana de qualidade premium, paes artesanais e molhos caseiros.",
                "endereco": "Shopping Belas, Talatona", "cidade": "Luanda",
                "latitude": Decimal("-8.91500000"), "longitude": Decimal("13.19200000"),
                "hora_abertura": time(11, 0), "hora_fecho": time(22, 0),
                "dias_funcionamento": {"items": [0, 1, 2, 3, 4, 5, 6]},
                "raio_entrega_km": 10, "tempo_preparo_min": 25,
                "pedido_minimo": Decimal("2500.00"), "taxa_entrega": Decimal("1000.00"),
                "categorias": {"items": ["Fast Food", "Hamburgueres", "Americana"]},
                "telefone": "+244922555666",
                "rating_medio": Decimal("4.50"), "total_pedidos": 2103, "aberto": True,
                "status": RestaurantStatus.APROVADO,
                "menu": [
                    {"cat": "Hamburgueres", "items": [
                        {"nome": "Classic Burger", "descricao": "Hamburguer 180g, queijo cheddar, alface, tomate e molho especial", "preco": Decimal("3500.00"), "popular": True},
                        {"nome": "Bacon Deluxe", "descricao": "Hamburguer 200g com bacon crocante, cebola caramelizada e queijo", "preco": Decimal("4800.00"), "popular": True},
                        {"nome": "Veggie Burger", "descricao": "Hamburguer de grao de bico com legumes grelhados", "preco": Decimal("3200.00")},
                        {"nome": "Double Smash", "descricao": "Duplo hamburguer smash 2x120g com cheddar derretido", "preco": Decimal("5500.00")},
                    ]},
                    {"cat": "Acompanhamentos", "items": [
                        {"nome": "Batatas Fritas", "descricao": "Porcao generosa de batatas fritas crocantes", "preco": Decimal("1500.00")},
                        {"nome": "Onion Rings", "descricao": "Aneis de cebola empanados", "preco": Decimal("1800.00")},
                    ]},
                    {"cat": "Bebidas", "items": [
                        {"nome": "Milkshake", "descricao": "Chocolate, baunilha ou morango", "preco": Decimal("2500.00")},
                        {"nome": "Refrigerante", "descricao": "Coca-Cola, Fanta ou Sprite 350ml", "preco": Decimal("500.00")},
                    ]},
                ],
            },
        ]

        for rd in restaurants_data:
            menu_raw = rd.pop("menu")
            rest = Restaurant(id=uuid.uuid4(), owner_id=users["seed_rest"].id, **rd)
            session.add(rest)
            await session.flush()

            for cat_data in menu_raw:
                mc = MenuCategory(id=uuid.uuid4(), restaurant_id=rest.id, nome=cat_data["cat"], ordem=0, ativo=True)
                session.add(mc)
                await session.flush()
                for item in cat_data["items"]:
                    mi = MenuItem(
                        id=uuid.uuid4(), category_id=mc.id, restaurant_id=rest.id,
                        nome=item["nome"], descricao=item.get("descricao"),
                        preco=item["preco"], popular=item.get("popular", False),
                        status=MenuItemStatus.ATIVO,
                    )
                    session.add(mi)

        await session.commit()
        return {"message": "Seed data criado com sucesso", "seeded": True}
