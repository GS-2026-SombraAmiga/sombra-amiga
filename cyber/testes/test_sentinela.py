"""Testes da Sentinela Cidadã. Rodar na pasta cyber/: python -m unittest discover -s testes -v"""

import os
import tempfile
import textwrap
import unittest
from pathlib import Path

os.environ["SENTINELA_SEM_LLM"] = "1"

from sentinela import analisador, llm, regras, risco  # noqa: E402

REGRAS = regras.carregar()
EXEMPLOS = Path(__file__).resolve().parent.parent / "exemplos"


def analisar_codigo(codigo: str, nome: str = "Servico.cs"):
    with tempfile.TemporaryDirectory() as pasta:
        arquivo = Path(pasta) / nome
        arquivo.write_text(textwrap.dedent(codigo), encoding="utf-8")
        return analisador.analisar([arquivo], REGRAS, raiz=Path(pasta))


def vazamentos(resultado):
    return [a for a in resultado.achados if a.tipo == "vazamento"]


class RegrasPii(unittest.TestCase):
    def test_reconhece_nomes_sensiveis(self):
        self.assertEqual(REGRAS.categoria_do_nome("Cpf").id, "cpf")
        self.assertEqual(REGRAS.categoria_do_nome("condicaoSaude").id, "saude")
        self.assertEqual(REGRAS.categoria_do_nome("ContatoFamiliar").id, "contato")
        self.assertEqual(REGRAS.categoria_do_nome("senha").id, "senha")

    def test_nome_protegido_nao_e_sensivel(self):
        self.assertIsNone(REGRAS.categoria_do_nome("CpfMascarado"))
        self.assertIsNone(REGRAS.categoria_do_nome("TemCondicaoSaude"))
        self.assertIsNone(REGRAS.categoria_do_nome("SenhaHash"))

    def test_cpf_valido_confere_digitos(self):
        self.assertTrue(regras.cpf_valido("529.982.247-25"))
        self.assertFalse(regras.cpf_valido("529.982.247-26"))
        self.assertFalse(regras.cpf_valido("111.111.111-11"))


class TaintAnalysis(unittest.TestCase):
    def test_cpf_direto_no_log_e_vazamento(self):
        r = analisar_codigo("""
            public class S {
                public void Salvar(Pessoa dados) {
                    log.LogInformation("CPF {Cpf}", dados.Cpf);
                }
            }""")
        [achado] = vazamentos(r)
        self.assertEqual((achado.categoria.id, achado.saida_id, achado.linha), ("cpf", "log", 4))

    def test_dado_propagado_por_variavel_e_rastreado(self):
        r = analisar_codigo("""
            public class S {
                public void Mostrar(Pessoa dados) {
                    var texto = $"Saúde: {dados.CondicaoSaude}";
                    var copia = texto;
                    Console.WriteLine(copia);
                }
            }""")
        [achado] = vazamentos(r)
        self.assertEqual(achado.categoria.id, "saude")
        self.assertEqual(achado.caminho[-1].linha, 6)
        self.assertEqual(achado.caminho[0].linha, 4)

    def test_parametro_sensivel_e_fonte(self):
        r = analisar_codigo("""
            public class S {
                public void Trocar(string usuario, string senha) {
                    log.LogWarning("Nova senha {S}", senha);
                }
            }""")
        self.assertEqual([a.categoria.id for a in vazamentos(r)], ["senha"])

    def test_sanitizador_bloqueia_o_vazamento(self):
        r = analisar_codigo("""
            public class S {
                public void Salvar(Pessoa dados) {
                    log.LogInformation("CPF {Cpf}", Mascarar(dados.Cpf));
                    log.LogInformation("CPF {Cpf}", dados.Cpf.Mascarado);
                }
            }""")
        self.assertEqual(vazamentos(r), [])

    def test_texto_fixo_com_a_palavra_cpf_nao_e_vazamento(self):
        r = analisar_codigo("""
            public class S {
                public void Validar(Pessoa dados) {
                    throw new DominioException("CPF inválido.");
                }
            }""")
        self.assertEqual(vazamentos(r), [])

    def test_derivacao_booleana_nao_carrega_o_dado(self):
        r = analisar_codigo("""
            public class S {
                public void Mostrar(Pessoa dados) {
                    var temCondicao = !string.IsNullOrWhiteSpace(dados.CondicaoSaude);
                    Console.WriteLine($"Tem condição: {temCondicao}");
                }
            }""")
        self.assertEqual(vazamentos(r), [])

    def test_reatribuicao_limpa_a_variavel(self):
        r = analisar_codigo("""
            public class S {
                public void Mostrar(Pessoa dados) {
                    var texto = dados.Cpf;
                    texto = "anonimo";
                    Console.WriteLine(texto);
                }
            }""")
        self.assertEqual(vazamentos(r), [])

    def test_objeto_de_negocio_nao_e_tratado_como_o_dado(self):
        r = analisar_codigo("""
            public class C {
                public IActionResult Cadastrar(Requisicao requisicao) {
                    var dados = new DadosCadastro(requisicao.Nome, requisicao.Cpf);
                    var cidadao = servico.Cadastrar(dados);
                    return Ok(CidadaoResposta.De(cidadao));
                }
            }""")
        self.assertEqual(vazamentos(r), [])

    def test_texto_montado_com_format_carrega_o_dado(self):
        r = analisar_codigo("""
            public class C {
                public void Registrar(Pessoa dados) {
                    var texto = string.Format("CPF {0}", dados.Cpf);
                    Console.WriteLine(texto);
                }
            }""")
        self.assertEqual([a.categoria.id for a in vazamentos(r)], ["cpf"])

    def test_java_log_e_resposta(self):
        r = analisar_codigo("""
            public class C {
                public ResponseEntity<String> buscar(String cpf) {
                    log.info("Buscando " + cpf);
                    return ResponseEntity.ok(cpf);
                }
            }""", nome="C.java")
        self.assertEqual(sorted(a.saida_id for a in vazamentos(r)), ["log", "resposta"])


class VarredurasEstaticas(unittest.TestCase):
    def test_cpf_valido_escrito_no_codigo(self):
        r = analisar_codigo('public class S { private const string X = "529.982.247-25"; }')
        self.assertEqual([a.tipo for a in r.achados], ["pii_literal"])

    def test_segredo_so_por_variavel_de_ambiente_nao_e_achado(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "application.properties"
            arquivo.write_text("jwt.secret=${JWT_SECRET}\napp.senha=${SENHA:dev123}\nbanco.password=fixa123\n", encoding="utf-8")
            r = analisador.analisar([arquivo], REGRAS, raiz=Path(pasta))
        self.assertEqual([(a.linha, a.exposicao) for a in r.achados], [(3, 4), (2, 2)])


class RiscoCidadao(unittest.TestCase):
    def test_sem_achados_e_zero(self):
        self.assertEqual(risco.indice([]), 0)

    def test_exemplo_com_vazamento_e_critico_e_corrigido_e_zero(self):
        ruim = analisador.analisar([EXEMPLOS / "com-vazamento"], REGRAS, raiz=EXEMPLOS)
        bom = analisador.analisar([EXEMPLOS / "corrigido"], REGRAS, raiz=EXEMPLOS)
        self.assertEqual(len(vazamentos(ruim)), 6)
        self.assertGreaterEqual(risco.indice(ruim.achados), 85)
        self.assertEqual(bom.achados, [])
        self.assertEqual(risco.indice(bom.achados), 0)


class Alertas(unittest.TestCase):
    def test_sem_llm_usa_texto_padrao(self):
        r = analisar_codigo("""
            public class S { public void A(Pessoa d) { Console.WriteLine(d.Cpf); } }""")
        self.assertEqual(llm.traduzir(r.achados), "texto padrao")
        self.assertIn("a tela e os registros do servidor", r.achados[0].alerta)


if __name__ == "__main__":
    unittest.main()
