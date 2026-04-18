# Trata-se de um sistema de gestão para estéticas automotivas

## Funcionalidades

### Configurações iniciais
-> Criação do tenant (nome da estética, telefone, endereço, cnpj, etc)
-> Criação dos Métodos de Pagamento (PIX, DINHEIRO, CARTÃO) vinculados ao tenant
-> Criação dos status de ordem de serviço (AGENDADO, EM_ANDAMENTO, CONCLUÍDO, ENTREGUE, CANCELADO) vinculados ao tenant

### Cadastros
-> Cadastro de clientes (nome, telefone) por tenant
-> Cadastro de funcionários (nome, telefone, comissão) por tenant

### Operações
-> Criar ordem de serviço (veículo, preço total, data fim)
-> Adicionar serviços à ordem de serviço (lavagem, polimento, etc)
-> Atualizar status da ordem de serviço (AGENDADO, EM_ANDAMENTO, CONCLUÍDO, ENTREGUE, CANCELADO)
-> Adicionar Pagamentos para a ordem de serviço vinculando ao caixa do dia do recebimento
-> Fazer operações de caixa (abrir, fechar, registrar entradas genéricas e saídas)

## Modelagem

-> Tenant: nome, telefone, endereço, cnpj
-> Cliente: nome, telefone, tenant
-> Funcionário: nome, telefone, comissão (porcentagem), tenant
-> Veículo: modelo (model_name), placa (license_plate), cliente, tenant (unicidade de placa por tenant)
-> Ordem de Serviço: veículo, descrição, preço total (total_price), data de início (start_date), data de fim (end_date), status, caixa inicial (cash_register), tenant
-> Serviço: ordem de serviço, nome do serviço, preço do serviço
-> FuncionárioServiço: funcionário, serviço (vinculação para comissão)
-> Pagamento: ordem de serviço, caixa (cash_register), valor (amount), método de pagamento, data de criação
-> Método de Pagamento: nome, tenant
-> Status de Ordem de Serviço: nome, tenant
-> Caixa: data do caixa (register_date), valor total (total_amount), status (is_open), tenant (único por data por tenant)
-> Entrada (Inflow): caixa, descrição, valor, data de criação
-> Saída (Outflow): caixa, descrição, valor, data de criação

## Regras de Negócio

-> O sistema deve ser capaz de calcular a comissão de funcionários baseado na soma de todos os serviços atrelados a ele no caixa do dia (através do vínculo EmployeeService).
-> O sistema deve ser capaz de calcular o valor total do caixa: Soma(Pagamentos) + Soma(Entradas) - Soma(Saídas).
-> Ao criar uma ordem de serviço, o sistema deve buscar um caixa aberto na data de hoje ou criar um automaticamente, atrelando a OS a ele.
-> Ao criar um Service para um ServiceOrder, um (ou mais) EmployeeService deve ser criado automaticamente para rastrear a comissão.
-> Travas de Segurança: O banco de dados impede que um objeto de um Tenant seja vinculado a objetos de outro Tenant (ex: OS do Tenant A usando veículo do Tenant B).
-> Integridade: O sistema impede a exclusão de registros que possuam vínculos históricos (ex: não é possível deletar um veículo que possua ordens de serviço).