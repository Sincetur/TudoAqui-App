import React from 'react';
import { ArrowLeft, FileText } from 'lucide-react';

export default function TermsOfService({ onBack }) {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white" data-testid="terms-page">
      {/* Header */}
      <nav className="sticky top-0 z-50 bg-[#0a0a0a]/90 backdrop-blur-xl border-b border-[#262626]">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-3 flex items-center gap-3">
          <button onClick={onBack} className="p-2 rounded-lg hover:bg-[#171717] transition" data-testid="terms-back-btn">
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
          <div className="w-10 h-10 rounded-lg bg-[#eab308]/10 flex items-center justify-center">
            <FileText className="w-5 h-5 text-[#eab308]" />
          </div>
          <div>
            <h1 className="text-2xl sm:text-3xl font-black">Termos de Servico</h1>
            <p className="text-[#a3a3a3] text-sm">Ultima actualizacao: Abril 2025</p>
          </div>
        </div>

        <div className="space-y-8 text-[#a3a3a3] text-sm leading-relaxed">
          <section>
            <h2 className="text-white font-bold text-base mb-3">1. Aceitacao dos Termos</h2>
            <p>
              Ao utilizar a aplicacao TUDOaqui ("App"), o utilizador aceita e concorda com estes Termos de Servico.
              A App e operada pela Nhimi Corporate (NIF: 5001193074), com sede em Luanda, Angola, e desenvolvida
              pela Sincesoft - Sinceridade Service (NIF: 2403104787). Se nao concordar com estes termos, nao
              devera utilizar a App.
            </p>
          </section>

          <section>
            <h2 className="text-white font-bold text-base mb-3">2. Descricao do Servico</h2>
            <p className="mb-2">
              O TUDOaqui e uma plataforma digital que integra multiplos servicos numa unica aplicacao:
            </p>
            <ul className="list-disc pl-5 space-y-1">
              <li><strong className="text-white">Eventos:</strong> Descoberta e compra de bilhetes para eventos</li>
              <li><strong className="text-white">Marketplace:</strong> Compra e venda de produtos</li>
              <li><strong className="text-white">Restaurantes:</strong> Encomenda de refeicoes com entrega</li>
              <li><strong className="text-white">Alojamento:</strong> Reserva de propriedades e alojamento</li>
              <li><strong className="text-white">Turismo:</strong> Reserva de experiencias turisticas</li>
              <li><strong className="text-white">Entregas:</strong> Servico de entrega de encomendas</li>
              <li><strong className="text-white">Taxi:</strong> Servico de transporte de passageiros</li>
              <li><strong className="text-white">Imobiliario:</strong> Compra, venda e arrendamento de imoveis</li>
            </ul>
          </section>

          <section>
            <h2 className="text-white font-bold text-base mb-3">3. Registo e Conta</h2>
            <ul className="list-disc pl-5 space-y-1">
              <li>O registo e feito atraves de numero de telefone angolano com verificacao por codigo OTP</li>
              <li>O utilizador deve ter no minimo 18 anos de idade</li>
              <li>E responsavel por manter a confidencialidade do seu numero e codigo de acesso</li>
              <li>Deve fornecer informacoes verdadeiras, actuais e completas</li>
              <li>Uma pessoa so pode ter uma conta activa</li>
            </ul>
          </section>

          <section>
            <h2 className="text-white font-bold text-base mb-3">4. Tipos de Utilizador</h2>
            <p className="mb-2">A App suporta diferentes tipos de utilizador:</p>
            <ul className="list-disc pl-5 space-y-1">
              <li><strong className="text-white">Cliente:</strong> Acede a todos os modulos para compras, reservas e servicos</li>
              <li><strong className="text-white">Parceiro:</strong> Vendedores, proprietarios, organizadores, guias, agentes, motoristas, motoqueiros e staff — mediante aprovacao</li>
              <li><strong className="text-white">Administrador:</strong> Gestao da plataforma</li>
            </ul>
            <p className="mt-2">A mudanca de role requer aprovacao da administracao.</p>
          </section>

          <section>
            <h2 className="text-white font-bold text-base mb-3">5. Pagamentos</h2>
            <ul className="list-disc pl-5 space-y-1">
              <li>Os pagamentos sao efectuados em Kwanzas (AOA)</li>
              <li>Metodos aceites: transferencia bancaria (BAI), Unitel Money e dinheiro (cash)</li>
              <li>Os precos indicados na App incluem o valor do servico conforme apresentado</li>
              <li>Pagamentos por transferencia requerem envio de comprovativo para confirmacao</li>
              <li>A confirmacao do pagamento e feita pela administracao ou pelo parceiro responsavel</li>
              <li>Parceiros recebem pagamento directo via Unitel Money ou transferencia bancaria, com taxa mensal de plataforma</li>
            </ul>
          </section>

          <section>
            <h2 className="text-white font-bold text-base mb-3">6. Cancelamentos e Reembolsos</h2>
            <ul className="list-disc pl-5 space-y-1">
              <li><strong className="text-white">Eventos:</strong> Cancelamento conforme politica do organizador. Bilhetes digitais nao sao reembolsaveis apos uso</li>
              <li><strong className="text-white">Marketplace:</strong> Devolucoes aceites em ate 7 dias apos recepcao, se o produto estiver em condicoes originais</li>
              <li><strong className="text-white">Restaurantes:</strong> Cancelamento gratuito antes da preparacao. Apos preparacao, sem reembolso</li>
              <li><strong className="text-white">Alojamento:</strong> Cancelamento gratuito ate 48 horas antes do check-in</li>
              <li><strong className="text-white">Turismo:</strong> Cancelamento gratuito ate 24 horas antes da experiencia</li>
              <li><strong className="text-white">Taxi/Entregas:</strong> Cancelamento gratuito antes da aceitacao pelo motorista</li>
            </ul>
          </section>

          <section>
            <h2 className="text-white font-bold text-base mb-3">7. Obrigacoes do Utilizador</h2>
            <p className="mb-2">O utilizador compromete-se a:</p>
            <ul className="list-disc pl-5 space-y-1">
              <li>Utilizar a App de forma legal e etica</li>
              <li>Nao publicar conteudo falso, enganoso ou ofensivo</li>
              <li>Nao utilizar a App para actividades ilicitas</li>
              <li>Respeitar outros utilizadores, parceiros e prestadores de servicos</li>
              <li>Manter os seus dados de contacto actualizados</li>
              <li>Nao tentar aceder a contas de outros utilizadores</li>
              <li>Nao interferir com o funcionamento da plataforma</li>
            </ul>
          </section>

          <section>
            <h2 className="text-white font-bold text-base mb-3">8. Obrigacoes dos Parceiros</h2>
            <ul className="list-disc pl-5 space-y-1">
              <li>Fornecer informacoes verdadeiras sobre produtos e servicos</li>
              <li>Cumprir prazos de entrega e prestacao de servicos</li>
              <li>Manter a qualidade dos produtos e servicos conforme anunciado</li>
              <li>Pagar a taxa mensal da plataforma conforme o plano contratado</li>
              <li>Cumprir a legislacao angolana aplicavel ao seu sector de actividade</li>
              <li>Motoristas devem possuir carta de conducao valida e seguro obrigatorio</li>
            </ul>
          </section>

          <section>
            <h2 className="text-white font-bold text-base mb-3">9. Propriedade Intelectual</h2>
            <p>
              A marca TUDOaqui, logotipo, design, codigo-fonte e todo o conteudo produzido pela plataforma
              sao propriedade da Nhimi Corporate. E proibida a reproducao, distribuicao ou uso comercial sem
              autorizacao expressa por escrito.
            </p>
          </section>

          <section>
            <h2 className="text-white font-bold text-base mb-3">10. Limitacao de Responsabilidade</h2>
            <ul className="list-disc pl-5 space-y-1">
              <li>A App actua como intermediario entre utilizadores e parceiros</li>
              <li>Nao somos responsaveis pela qualidade dos produtos ou servicos prestados por parceiros</li>
              <li>Nao garantimos disponibilidade ininterrupta da plataforma</li>
              <li>Disputas entre utilizadores e parceiros devem ser resolvidas entre as partes, podendo a plataforma intervir como mediador</li>
            </ul>
          </section>

          <section>
            <h2 className="text-white font-bold text-base mb-3">11. Suspensao e Cancelamento de Conta</h2>
            <p>
              Reservamo-nos o direito de suspender ou cancelar contas que violem estes termos, incluindo mas
              nao limitado a: fraude, abuso, conteudo ilegal, avaliacoes falsas, ou incumprimento repetido.
              O utilizador pode solicitar o cancelamento da sua conta a qualquer momento.
            </p>
          </section>

          <section>
            <h2 className="text-white font-bold text-base mb-3">12. Alteracoes aos Termos</h2>
            <p>
              Podemos alterar estes termos a qualquer momento. Alteracoes significativas serao comunicadas com
              antecedencia de 15 dias atraves da App. O uso continuado apos alteracoes constitui aceitacao
              dos novos termos.
            </p>
          </section>

          <section>
            <h2 className="text-white font-bold text-base mb-3">13. Lei Aplicavel</h2>
            <p>
              Estes termos sao regidos pela legislacao da Republica de Angola. Qualquer disputa sera submetida
              aos tribunais competentes de Luanda, Angola.
            </p>
          </section>

          <section>
            <h2 className="text-white font-bold text-base mb-3">14. Contacto</h2>
            <div className="p-4 bg-[#171717] border border-[#262626] rounded-xl space-y-1">
              <p><strong className="text-white">Nhimi Corporate</strong></p>
              <p>NIF: 5001193074 | Luanda, Angola</p>
              <p>Email: <a href="mailto:nhimi@nhimi.com" className="text-[#eab308] hover:underline">nhimi@nhimi.com</a></p>
              <p>Telefone: <a href="tel:+244924865667" className="text-[#eab308] hover:underline">+244 924 865 667</a></p>
              <p className="pt-2"><strong className="text-white">Desenvolvido por:</strong> Sincesoft - Sinceridade Service</p>
              <p>NIF: 2403104787 | <a href="https://3s-ao.com" target="_blank" rel="noopener noreferrer" className="text-[#eab308] hover:underline">3s-ao.com</a> | <a href="mailto:apoioaocliente@3s-ao.com" className="text-[#eab308] hover:underline">apoioaocliente@3s-ao.com</a></p>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
