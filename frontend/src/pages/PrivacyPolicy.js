import React from 'react';
import { ArrowLeft, Shield } from 'lucide-react';

export default function PrivacyPolicy({ onBack }) {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white" data-testid="privacy-page">
      {/* Header */}
      <nav className="sticky top-0 z-50 bg-[#0a0a0a]/90 backdrop-blur-xl border-b border-[#262626]">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-3 flex items-center gap-3">
          <button onClick={onBack} className="p-2 rounded-lg hover:bg-[#171717] transition" data-testid="privacy-back-btn">
            <ArrowLeft className="w-5 h-5 text-[#a3a3a3]" />
          </button>
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-md bg-[#dc2626] flex items-center justify-center">
              <span className="text-white text-[10px] font-black">T</span>
            </div>
            <span className="text-white font-black text-sm">TUDO<span className="text-[#eab308]">Aqui</span></span>
          </div>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-12">
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 rounded-lg bg-[#dc2626]/10 flex items-center justify-center">
            <Shield className="w-5 h-5 text-[#dc2626]" />
          </div>
          <div>
            <h1 className="text-2xl sm:text-3xl font-black">Politica de Privacidade</h1>
            <p className="text-[#a3a3a3] text-sm">Ultima actualizacao: Abril 2025</p>
          </div>
        </div>

        <div className="space-y-8 text-[#a3a3a3] text-sm leading-relaxed">
          <section>
            <h2 className="text-white font-bold text-base mb-3">1. Introducao</h2>
            <p>
              A Nhimi Corporate (NIF: 5001193074), com sede em Luanda, Angola, e a entidade responsavel pelo
              tratamento dos dados pessoais recolhidos atraves da aplicacao TUDOaqui ("App"). Esta Politica de
              Privacidade descreve como recolhemos, utilizamos, armazenamos e protegemos os seus dados pessoais
              em conformidade com a legislacao angolana aplicavel.
            </p>
          </section>

          <section>
            <h2 className="text-white font-bold text-base mb-3">2. Dados que Recolhemos</h2>
            <p className="mb-2">Recolhemos os seguintes tipos de dados:</p>
            <ul className="list-disc pl-5 space-y-1">
              <li><strong className="text-white">Dados de identificacao:</strong> nome, numero de telefone, endereco de email</li>
              <li><strong className="text-white">Dados de localizacao:</strong> coordenadas GPS (quando autorizado) para servicos de taxi, entregas e turismo</li>
              <li><strong className="text-white">Dados de transaccao:</strong> historico de compras, reservas, pagamentos e avaliacoes</li>
              <li><strong className="text-white">Dados do dispositivo:</strong> modelo, sistema operativo, identificador unico para notificacoes</li>
              <li><strong className="text-white">Dados de utilizacao:</strong> paginas visitadas, funcionalidades utilizadas, tempo de sessao</li>
            </ul>
          </section>

          <section>
            <h2 className="text-white font-bold text-base mb-3">3. Como Utilizamos os Dados</h2>
            <ul className="list-disc pl-5 space-y-1">
              <li>Fornecer e melhorar os servicos da App (eventos, marketplace, restaurantes, alojamento, turismo, entregas, taxi, imobiliario)</li>
              <li>Processar pagamentos e transaccoes (transferencia bancaria BAI, Unitel Money, dinheiro)</li>
              <li>Enviar notificacoes sobre estado de encomendas, reservas e eventos</li>
              <li>Conectar utilizadores com motoristas, entregadores e prestadores de servicos</li>
              <li>Garantir a seguranca da plataforma e prevenir fraudes</li>
              <li>Cumprir obrigacoes legais e regulatorias</li>
            </ul>
          </section>

          <section>
            <h2 className="text-white font-bold text-base mb-3">4. Partilha de Dados</h2>
            <p className="mb-2">Os seus dados podem ser partilhados com:</p>
            <ul className="list-disc pl-5 space-y-1">
              <li><strong className="text-white">Parceiros e prestadores de servicos:</strong> restaurantes, motoristas, entregadores, proprietarios de alojamento, organizadores de eventos e agentes imobiliarios — apenas os dados necessarios para cumprir o servico solicitado</li>
              <li><strong className="text-white">Processadores de pagamento:</strong> Multicaixa Express, instituicoes bancarias angolanas — para processar transaccoes</li>
              <li><strong className="text-white">Autoridades:</strong> quando exigido por lei ou ordem judicial</li>
            </ul>
            <p className="mt-2">Nao vendemos os seus dados pessoais a terceiros.</p>
          </section>

          <section>
            <h2 className="text-white font-bold text-base mb-3">5. Seguranca dos Dados</h2>
            <p>
              Implementamos medidas tecnicas e organizacionais para proteger os seus dados, incluindo:
              encriptacao de dados em transito (HTTPS/TLS), autenticacao por codigo OTP, controlo de acesso
              baseado em funcoes (RBAC), e monitorizacao continua de seguranca. Os dados sao armazenados em
              servidores seguros com backups regulares.
            </p>
          </section>

          <section>
            <h2 className="text-white font-bold text-base mb-3">6. Retencao de Dados</h2>
            <p>
              Os dados pessoais sao retidos enquanto a sua conta estiver activa e durante o periodo necessario
              para cumprir as finalidades descritas nesta politica. Dados de transaccoes sao mantidos por um
              minimo de 5 anos para fins fiscais e legais, conforme a legislacao angolana.
            </p>
          </section>

          <section>
            <h2 className="text-white font-bold text-base mb-3">7. Os Seus Direitos</h2>
            <p className="mb-2">Tem o direito de:</p>
            <ul className="list-disc pl-5 space-y-1">
              <li>Aceder aos seus dados pessoais</li>
              <li>Rectificar dados incorrectos ou incompletos</li>
              <li>Solicitar a eliminacao dos seus dados (sujeito a obrigacoes legais)</li>
              <li>Retirar o consentimento para a localizacao GPS a qualquer momento</li>
              <li>Solicitar a portabilidade dos seus dados</li>
            </ul>
            <p className="mt-2">
              Para exercer estes direitos, contacte-nos atraves de <a href="mailto:nhimi@nhimi.com" className="text-[#eab308] hover:underline">nhimi@nhimi.com</a>.
            </p>
          </section>

          <section>
            <h2 className="text-white font-bold text-base mb-3">8. Cookies e Tecnologias Similares</h2>
            <p>
              A App utiliza tokens de sessao (localStorage) para manter a sua autenticacao. Nao utilizamos
              cookies de rastreamento de terceiros. A versao web pode utilizar service workers para
              funcionalidades offline (PWA).
            </p>
          </section>

          <section>
            <h2 className="text-white font-bold text-base mb-3">9. Menores</h2>
            <p>
              A App nao se destina a menores de 18 anos. Nao recolhemos intencionalmente dados de menores.
              Se tomarmos conhecimento de que recolhemos dados de um menor, procederemos a sua eliminacao.
            </p>
          </section>

          <section>
            <h2 className="text-white font-bold text-base mb-3">10. Alteracoes a esta Politica</h2>
            <p>
              Reservamo-nos o direito de actualizar esta politica. Alteracoes significativas serao comunicadas
              atraves da App. A data de ultima actualizacao e indicada no topo deste documento.
            </p>
          </section>

          <section>
            <h2 className="text-white font-bold text-base mb-3">11. Contacto</h2>
            <div className="p-4 bg-[#171717] border border-[#262626] rounded-xl space-y-1">
              <p><strong className="text-white">Nhimi Corporate</strong> — Responsavel pelo Tratamento de Dados</p>
              <p>NIF: 5001193074 | Luanda, Angola</p>
              <p>Email: <a href="mailto:nhimi@nhimi.com" className="text-[#eab308] hover:underline">nhimi@nhimi.com</a></p>
              <p>Telefone: <a href="tel:+244924865667" className="text-[#eab308] hover:underline">+244 924 865 667</a></p>
              <p className="pt-2"><strong className="text-white">Suporte Tecnico:</strong> <a href="mailto:apoioaocliente@3s-ao.com" className="text-[#eab308] hover:underline">apoioaocliente@3s-ao.com</a> | +244 951 064 945</p>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
