import json, sys, tempfile, unittest
from decimal import Decimal
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from calcular_pontos import processar, cpf_valido

CFG = {"pontos_por_real": 2, "periodo_inicio": "2026-11-26", "periodo_fim": "2026-12-02"}

def rodar(linhas):
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
        f.write("cpf;nome;data_compra;valor;id_comprovante\n" + "\n".join(linhas) + "\n")
    return processar(f.name, CFG)

class T(unittest.TestCase):
    def test_cpf(self):
        self.assertTrue(cpf_valido("52998224725"))
        self.assertFalse(cpf_valido("11111111111"))
        self.assertFalse(cpf_valido("52998224726"))

    def test_dobro_soma_por_cpf(self):
        resumo, _, rej = rodar(["529.982.247-25;A;2026-11-27;18,50;N1", "52998224725;A;27/11/2026;12,00;N2"])
        self.assertEqual(resumo[0]["pontos"], 61)  # 30,50 * 2
        self.assertEqual(resumo[0]["total"], Decimal("30.50"))
        self.assertEqual(rej, [])

    def test_rejeicoes(self):
        _, ac, rej = rodar([
            "529.982.247-25;A;2026-11-27;10,00;N1",
            "529.982.247-25;A;2026-11-27;10,00;N1",   # duplicado
            "123.456.789-00;B;2026-11-27;10,00;N3",   # cpf invalido
            "529.982.247-25;A;2026-12-03;10,00;N4",   # fora do periodo
            "529.982.247-25;A;2026-11-27;0;N5",       # valor zero
        ])
        self.assertEqual(len(ac), 1)
        self.assertEqual(len(rej), 4)

    def test_exportacao_supabase(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write("id,nome,cpf,data_compra,valor,nsu,status\n"
                    "1,A,52998224725,2026-11-27,10.50,N1,aprovado\n"
                    "2,A,52998224725,2026-11-27,5.00,N2,pendente\n"
                    "3,A,52998224725,2026-11-27,5.00,N3,rejeitado\n")
        resumo, ac, rej = processar(f.name, CFG)
        self.assertEqual(resumo[0]["pontos"], 21)
        self.assertEqual(len(rej), 1)

if __name__ == "__main__":
    unittest.main()
