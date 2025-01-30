from pyomo.environ import ConcreteModel
from pyomo.environ import Var
from pyomo.environ import Objective
from pyomo.environ import Constraint
from pyomo.environ import SolverFactory
from pyomo.environ import NonNegativeReals
from ImportFile import ImportFile
import pyomo.environ as pyo

PORC_MIN_SERVICO = 0.4
HORAS_TRABALHADAS_DISPONIVEIS = 176 * 60

class Solver():
    def __init__(self, Arquivo):
        self.modelo = ConcreteModel() #Criar o modelo
        file = ImportFile(Arquivo)
        self.servicos = file.obterServicos()
        self.custos = file.custoServico()

    
    def otimizarLucro(self):
        """ Resolve o problema de maximizacao do lucro com Pyomo + GLPK """
        modelo = ConcreteModel()

        # Definicao do conjunto de servicos
        modelo.SERVICOS = {s.DSC_SERVICO for s in self.servicos}

        # Variaveis de decisao: Quantidade de cada servico a ser feito
        modelo.quantidade = Var(modelo.SERVICOS, within=NonNegativeReals)

        # Funcao objetivo: Maximizar o lucro
        modelo.objetivo = Objective(
            expr=sum(
                modelo.quantidade[s.DSC_SERVICO] * (s.VLR_SERVICO
                - self.custos[s.DSC_SERVICO])
                for s in self.servicos
            ),
            sense=pyo.maximize
        )
        
        #  ----------- Definindo as restricoes no modelo ------------
        
        # Restricao: quantidade minima de cada servico que deve ser realizada
        def restricao_minima(modelo, s):
            return modelo.quantidade[s] >= PORC_MIN_SERVICO * next(serv.AVG_SERVICO for serv in self.servicos if serv.DSC_SERVICO == s)
        modelo.restricao_minima = Constraint(modelo.SERVICOS, rule=restricao_minima)
        
        # Restricao: quantidade maxima de cada servico que pode ser realizada
        def restricao_maxima(modelo, s):
            return modelo.quantidade[s] <= next(serv.AVG_SERVICO for serv in self.servicos if serv.DSC_SERVICO == s)
        modelo.restricao_maxima = Constraint(modelo.SERVICOS, rule=restricao_maxima)

        # Restricao: tempo total de servicos deve ser menor ou igual ao tempo disponivel
        modelo.restricao_tempo = Constraint(
            expr=sum(modelo.quantidade[s.DSC_SERVICO] * s.TMP_SERVICO for s in self.servicos) <= HORAS_TRABALHADAS_DISPONIVEIS
        )

        # Resolver o problema com GLPK
        solver = SolverFactory("glpk")
        resultado = solver.solve(modelo)

        modelo.display()
        # Exibir resultados
        print("Status:", resultado.solver.Status)
        for s in self.servicos:
            print(f"Quantidade de {s.DSC_SERVICO}: {modelo.quantidade[s.DSC_SERVICO].value}")


if __name__ == "__main__":
    solver = Solver("a.xlsx")
    solver.otimizarLucro()
