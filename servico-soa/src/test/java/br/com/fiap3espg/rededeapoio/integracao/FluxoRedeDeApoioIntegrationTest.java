package br.com.fiap3espg.rededeapoio.integracao;

import br.com.fiap3espg.rededeapoio.TestData;
import br.com.fiap3espg.rededeapoio.domain.cidadao.DadosCidadao;
import br.com.fiap3espg.rededeapoio.infra.apiprincipal.ApiPrincipalClient;
import br.com.fiap3espg.rededeapoio.infra.apiprincipal.ServicoExternoIndisponivelException;
import com.jayway.jsonpath.JsonPath;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;
import java.util.UUID;

import static org.hamcrest.Matchers.containsString;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

// Teste de integracao ponta a ponta: aplicacao completa + H2 migrado pelo Flyway
// (incluindo o coordenador da V3) + JWT real. Somente a API principal (C#) e
// simulada, porque e outro sistema. @Transactional desfaz tudo ao final de cada teste.
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@Transactional
class FluxoRedeDeApoioIntegrationTest {
    private static final String COORDENADOR = "coordenador@sombraamiga.dev";
    private static final String SENHA_COORDENADOR = "coordenador123";
    private static final UUID CIDADAO = UUID.fromString(TestData.CIDADAO_ID);

    @Autowired
    private MockMvc mvc;

    @MockitoBean
    private ApiPrincipalClient apiPrincipal;

    @Value("${app.servico.chave}")
    private String chaveServico;

    @BeforeEach
    void cidadaoExisteNaApiPrincipal() {
        when(apiPrincipal.buscarCidadao(CIDADAO)).thenReturn(Optional.of(TestData.cidadao()));
    }

    private String login(String email, String senha) throws Exception {
        String resposta = mvc.perform(post("/api/auth/login").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"%s\",\"senha\":\"%s\"}".formatted(email, senha)))
                .andExpect(status().isOk())
                .andReturn().getResponse().getContentAsString();
        return "Bearer " + JsonPath.read(resposta, "$.tokenJWT");
    }

    private Integer cadastrarAgente(String coordenador, String email) throws Exception {
        String resposta = mvc.perform(post("/api/agentes").header("Authorization", coordenador)
                        .contentType(MediaType.APPLICATION_JSON).content("""
                                {"nome":"Agente Teste","email":"%s","senha":"senha12345",
                                 "bairro":"Brasilândia","tipo":"VOLUNTARIO","perfil":"AGENTE"}
                                """.formatted(email)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.senha").doesNotExist())
                .andReturn().getResponse().getContentAsString();
        return JsonPath.read(resposta, "$.id");
    }

    private Integer abrirPedido() throws Exception {
        String resposta = mvc.perform(post("/api/pedidos").header("X-Chave-Servico", chaveServico)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"cidadaoId\":\"%s\",\"latitude\":-23.462,\"longitude\":-46.681}".formatted(CIDADAO)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.status").value("ABERTO"))
                .andExpect(jsonPath("$.nomeCidadao").value("Lurdes Teste"))
                .andReturn().getResponse().getContentAsString();
        return JsonPath.read(resposta, "$.id");
    }

    @Test
    @DisplayName("F-10: login com senha errada responde 401 sem dizer qual dado errou")
    void loginInvalido() throws Exception {
        mvc.perform(post("/api/auth/login").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"%s\",\"senha\":\"errada\"}".formatted(COORDENADOR)))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.mensagem").value("E-mail ou senha inválidos."));
    }

    @Test
    @DisplayName("F-10: sem token ou com token invalido, os pedidos respondem 401")
    void semToken() throws Exception {
        mvc.perform(get("/api/pedidos")).andExpect(status().isUnauthorized());
        mvc.perform(get("/api/pedidos").header("Authorization", "Bearer token.invalido"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    @DisplayName("Perfil AGENTE nao cadastra outros agentes")
    void agenteNaoCadastraAgente() throws Exception {
        String coordenador = login(COORDENADOR, SENHA_COORDENADOR);
        cadastrarAgente(coordenador, "ana@teste.com");
        String ana = login("ana@teste.com", "senha12345");

        mvc.perform(post("/api/agentes").header("Authorization", ana).contentType(MediaType.APPLICATION_JSON)
                        .content("{}"))
                .andExpect(status().isForbidden());
    }

    @Test
    @DisplayName("E-mail repetido no cadastro de agente responde 400")
    void emailRepetido() throws Exception {
        String coordenador = login(COORDENADOR, SENHA_COORDENADOR);
        cadastrarAgente(coordenador, "ana@teste.com");

        mvc.perform(post("/api/agentes").header("Authorization", coordenador).contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {"nome":"Outra","email":"ana@teste.com","senha":"senha12345",
                                 "bairro":"Brasilândia","tipo":"VOLUNTARIO","perfil":"AGENTE"}
                                """))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("Agente desativado nao consegue mais fazer login")
    void agenteDesativado() throws Exception {
        String coordenador = login(COORDENADOR, SENHA_COORDENADOR);
        Integer id = cadastrarAgente(coordenador, "ana@teste.com");

        mvc.perform(delete("/api/agentes/" + id).header("Authorization", coordenador))
                .andExpect(status().isNoContent());
        mvc.perform(post("/api/auth/login").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"ana@teste.com\",\"senha\":\"senha12345\"}"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    @DisplayName("F-11: pedido aberto pela API principal, aceito e concluido pelo agente")
    void fluxoCompleto() throws Exception {
        String coordenador = login(COORDENADOR, SENHA_COORDENADOR);
        cadastrarAgente(coordenador, "ana@teste.com");
        String ana = login("ana@teste.com", "senha12345");
        Integer pedido = abrirPedido();

        mvc.perform(get("/api/pedidos").header("Authorization", ana))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content[0].id").value(pedido))
                .andExpect(jsonPath("$.content[0].status").value("ABERTO"));

        mvc.perform(post("/api/pedidos/" + pedido + "/aceitar").header("Authorization", ana))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("EM_ATENDIMENTO"))
                .andExpect(jsonPath("$.nomeAgente").value("Agente Teste"));

        mvc.perform(post("/api/pedidos/" + pedido + "/concluir").header("Authorization", ana)
                        .contentType(MediaType.APPLICATION_JSON).content("{\"observacao\":\"Levei água e acompanhei.\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("CONCLUIDO"));
    }

    @Test
    @DisplayName("F-11: pedido ja aceito por outro agente responde 409, e so o responsavel conclui")
    void pedidoDeOutroAgente() throws Exception {
        String coordenador = login(COORDENADOR, SENHA_COORDENADOR);
        cadastrarAgente(coordenador, "ana@teste.com");
        cadastrarAgente(coordenador, "bruno@teste.com");
        String ana = login("ana@teste.com", "senha12345");
        String bruno = login("bruno@teste.com", "senha12345");
        Integer pedido = abrirPedido();

        mvc.perform(post("/api/pedidos/" + pedido + "/aceitar").header("Authorization", ana))
                .andExpect(status().isOk());
        mvc.perform(post("/api/pedidos/" + pedido + "/aceitar").header("Authorization", bruno))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.mensagem", containsString("outro agente")));
        mvc.perform(post("/api/pedidos/" + pedido + "/concluir").header("Authorization", bruno)
                        .contentType(MediaType.APPLICATION_JSON).content("{\"observacao\":\"tentativa\"}"))
                .andExpect(status().isForbidden());
    }

    @Test
    @DisplayName("Conclusao sem observacao responde 400 com o campo invalido")
    void conclusaoSemObservacao() throws Exception {
        String coordenador = login(COORDENADOR, SENHA_COORDENADOR);
        Integer pedido = abrirPedido();
        mvc.perform(post("/api/pedidos/" + pedido + "/aceitar").header("Authorization", coordenador))
                .andExpect(status().isOk());

        mvc.perform(post("/api/pedidos/" + pedido + "/concluir").header("Authorization", coordenador)
                        .contentType(MediaType.APPLICATION_JSON).content("{\"observacao\":\"\"}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$[0].campo").value("observacao"));
    }

    @Test
    @DisplayName("Abrir pedido exige a chave de servico correta")
    void chaveDeServicoErrada() throws Exception {
        mvc.perform(post("/api/pedidos").header("X-Chave-Servico", "chave-errada")
                        .contentType(MediaType.APPLICATION_JSON).content("{\"cidadaoId\":\"%s\"}".formatted(CIDADAO)))
                .andExpect(status().isUnauthorized());
    }

    @Test
    @DisplayName("Segundo pedido do mesmo cidadao em andamento responde 409")
    void pedidoDuplicado() throws Exception {
        abrirPedido();

        mvc.perform(post("/api/pedidos").header("X-Chave-Servico", chaveServico)
                        .contentType(MediaType.APPLICATION_JSON).content("{\"cidadaoId\":\"%s\"}".formatted(CIDADAO)))
                .andExpect(status().isConflict());
    }

    @Test
    @DisplayName("Cidadao inexistente na API principal responde 404")
    void cidadaoInexistente() throws Exception {
        UUID desconhecido = UUID.randomUUID();
        when(apiPrincipal.buscarCidadao(desconhecido)).thenReturn(Optional.empty());

        mvc.perform(post("/api/pedidos").header("X-Chave-Servico", chaveServico)
                        .contentType(MediaType.APPLICATION_JSON).content("{\"cidadaoId\":\"%s\"}".formatted(desconhecido)))
                .andExpect(status().isNotFound());
    }

    @Test
    @DisplayName("API principal fora do ar responde 503")
    void apiPrincipalForaDoAr() throws Exception {
        when(apiPrincipal.buscarCidadao(any()))
                .thenThrow(new ServicoExternoIndisponivelException("fora do ar", null));

        mvc.perform(post("/api/pedidos").header("X-Chave-Servico", chaveServico)
                        .contentType(MediaType.APPLICATION_JSON).content("{\"cidadaoId\":\"%s\"}".formatted(CIDADAO)))
                .andExpect(status().isServiceUnavailable());
    }

    @Test
    @DisplayName("Health check e a documentacao do Swagger sao publicos")
    void rotasPublicas() throws Exception {
        mvc.perform(get("/health-check")).andExpect(status().isOk()).andExpect(jsonPath("$.status").value("UP"));
        mvc.perform(get("/v3/api-docs"))
                .andExpect(status().isOk())
                .andExpect(content().string(containsString("/api/pedidos/{id}/aceitar")));
    }

    @SuppressWarnings("unused")
    private static DadosCidadao cidadao() {
        return TestData.cidadao();
    }
}
