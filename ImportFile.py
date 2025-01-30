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
        self.maquinas = None
        self.df = None
        try:
            df = pd.read_excel(arquivo, engine="openpyxl")
            self.df = df
            
            # Processa os tempos das maquinas
            for i, row in df.iterrows():
                self.maquinas = row["MAQ"].split(", ")
                
                try:
                    tempos = list(map(int, row["TMP_MAQ"].split(", ")))
                except:
                    tempos = [int(row["TMP_MAQ"])]
                
                # Cria um dicionario de tempos por maquina
                tempos_maquinas = {self.maquinas[j]: tempos[j] for j in range(len(self.maquinas))}
                
                df.at[i, "TMP_MAQ"] = tempos_maquinas

            self.dados = df.to_dict(orient="records")
        
        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")
            self.dados = []
    
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
                custo += i["TMP_MAQ"][maq] * custoUnitario[maq]
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
    print(file.custoServico())
    #print(file.obterCustoMaquinas())
    

