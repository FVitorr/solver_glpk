# NOME_SERVICO	VALOR_SERVICO	TEMPO_SERVICO     AVG_SERVICOS           MAQ        TMP_MAQ        j1           j2          j3
#      x1            15	             15                200              j1, j2        5, 5         15           20          10
#      x2	         20         	 20                300              j2, j3        2, 3

import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class Servico:
    DSC_SERVICO: str
    VLR_SERVICO: float
    TMP_SERVICO: float
    AVG_SERVICO: int
    TMP_MAQUINAS: Dict[str, int] = field(default_factory=dict)
    
@dataclass
class Maquina:
    DSC_MAQUINA: str
    CUSTO: float

class ImportFile:
    def __init__(self, arquivo: str):
        self.maquinas = []
        self.df = None
        #try:
        df = pd.read_excel(arquivo, engine="openpyxl")
        self.df = df
        
        # Processa os tempos das maquinas
        # Processa os tempos das maquinas
        for i, row in df.iterrows():
            maquinas = row["MAQ"].split(", ")
            for maquina in maquinas:
                if maquina not in self.maquinas:
                    self.maquinas.append(maquina)
            
            try:
                tempos = list(map(int, row["TMP_MAQ"].split(", ")))
            except:
                tempos = [int(row["TMP_MAQ"])]
            
            # Verifica se o número de máquinas e tempos são iguais
            if len(maquinas) == len(tempos):
                # Cria um dicionário de tempos por máquina
                tempos_maquinas = {maquinas[j]: tempos[j] for j in range(len(maquinas))}
            else:
                # Caso contrário, trate o erro (talvez com uma mensagem ou valor padrão)
                print(f"Erro na linha {i}: número de máquinas e tempos não correspondem.")
                tempos_maquinas = {}

            df.at[i, "TMP_MAQ"] = tempos_maquinas

        self.dados = df.to_dict(orient="records")

        
        #except Exception as e:
            #print(f"Erro ao ler o arquivo: {e}")
            #self.dados = []
    
    def obterCustoMaquinas(self):
        maqCust = {}
        for maq in self.maquinas:
            if maq not in maqCust.keys():
                maqCust[maq] = self.df[maq].values[0]
        return maqCust
    
    def custoServico(self) -> float:
        custoUnitario = self.obterCustoMaquinas()
        custoR = {}
        for i in self.dados:
            custo = 0
            for maq in i["TMP_MAQ"]:
                try:
                    custo += i["TMP_MAQ"][maq] * custoUnitario[maq]
                except:
                    pass
            key = str(i["DSC_SERVICO"]).replace(" ", "_")
            custoR[key] = custo
        return custoR

    def obterServicos(self) -> List[Servico]:
        """ Retorna a lista de objetos do tipo Servico """
        return [
            Servico(
                DSC_SERVICO=i["DSC_SERVICO"].replace(" ", "_"),
                VLR_SERVICO=i["VLR_SERVICO"],
                TMP_SERVICO=i["TMP_SERVICO"],
                AVG_SERVICO=i["AVG_SERVICO"],
                TMP_MAQUINAS=i["TMP_MAQ"]
            )
            for i in self.dados
        ]
    

if __name__ == "__main__":
    file = ImportFile("a.xlsx")
    
    # Lista de servicos como objetos
    servicos = file.obterServicos()
    print(servicos)
    print(file.custoServico())
    print(file.obterCustoMaquinas())
    

