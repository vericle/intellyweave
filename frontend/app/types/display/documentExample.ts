/* eslint-disable @typescript-eslint/no-explicit-any */
export const documentResponse: any = {
  id: "doc-brazilian-immigration-001",
  query: "What does Article 9 of Decreto-Lei 7967 say about permanent visas?",
  messages: [
    {
      type: "User",
      id: "949a2d5a-acec-4b38-8653-ecd510451a5d",
      query_id: "b4c8ce36-0989-436e-966e-962efe8dacd3",
      conversation_id: "9eecf0fb-b3e2-4272-b8d3-050e0f2e7d95",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      payload: {
        type: "text",
        metadata: {},
        code: {
          language: "",
          title: "",
          text: "",
        },
        objects: ["What does Article 9 of Decreto-Lei 7967 say about permanent visas?"],
      },
    },
    {
      type: "text",
      id: "tex-75a69e92-5524-402f-b4ce-9778597a98fa",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "9eecf0fb-b3e2-4272-b8d3-050e0f2e7d95",
      query_id: "b4c8ce36-0989-436e-966e-962efe8dacd3",
      payload: {
        type: "response",
        metadata: {},
        objects: [
          {
            text: "I will search the uploaded documents collection to find information about Brazilian immigration law Decreto-Lei 7967 and its provisions regarding permanent visas.",
          },
        ],
      },
    },
    {
      type: "text",
      id: "tex-5748fd32-de1c-487d-85d2-c8ab1a54c07f",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "9eecf0fb-b3e2-4272-b8d3-050e0f2e7d95",
      query_id: "b4c8ce36-0989-436e-966e-962efe8dacd3",
      payload: {
        type: "response",
        metadata: {},
        objects: [
          {
            text: "I'm using a hybrid search on the content of the legislation documents collection to find the most relevant provisions about permanent visa requirements under Brazilian immigration law.",
          },
        ],
      },
    },
    {
      type: "result",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "9eecf0fb-b3e2-4272-b8d3-050e0f2e7d95",
      query_id: "b4c8ce36-0989-436e-966e-962efe8dacd3",
      id: "res-790f97c5-b9f9-42d5-8b4f-c131dd84c911",
      payload: {
        type: "document",
        objects: [
          {
            content:
              "DECRETO-LEI Nº 7.967, DE 18 DE SETEMBRO DE 1945\n\nDispõe sôbre a Imigração e Colonização, e dá outras providências.\n\nO PRESIDENTE DA REPÚBLICA, usando da atribuição que lhe confere o artigo 180 da Constituição e considerando que se faz necessário, cessada a guerra mundial, imprimir á política imigratória do Brasil uma orientação racional e definitiva, que atenda à dupla finalidade de proteger os interêsses do trabalhador nacional e de desenvolver a imigração que fôr fator de progresso para o país,\n\nDECRETA:\n\nTÍTULO I\nDa entrada de estrangeiros no Brasil\n\nCAPÍTULO I\nADMISSÃO\n\nArt. 1º Todo estrangeiro poderá, entrar no Brasil desde que satisfaça as condições estabelecidas por esta lei.\n\nArt. 2º Atender-se-á, na admissão dos imigrantes, à necessidade de preservar e desenvolver, na composição étnica da população, as características mais convenientes da sua ascendência européia, assim como a defesa do trabalhador nacional.",
            title: "Decreto-Lei 7967/1945 - Preâmbulo e Admissão",
            category: ["Legislation", "Immigration Law"],
            uuid: "2288bc03-5bfe-4bce-83d4-076d05a58444",
            collection_name: "ELYSIA_CHUNKED_elysia_uploaded_documents__",
            chunk_spans: [],
            _REF_ID: "query_ELYSIA_CHUNKED_elysia_uploaded_documents___0_0",
          },
          {
            content:
              "Art. 5º As autoridades brasileiras competentes no exterior pode conceder os seguintes vistos:\n\nI - Visto de trânsito;\nII - Visto temporário;\nIII - Visto temporário especial;\nIV - Visto permanente;\nV - Visto permanente especial;\nVI - Visto oficial;\nVII - Visto diplomático.\n\nVisto ao estrangeiro poderá, estender-se a pessoas que viram na sua dependência, observado o disposto n art.11.\n\nArt. 6º O visto de trânsito será concedido ao estrangeiro que pretenda passar pelo território nacional com destino a outro país, desde que não se demore mais de 30 dias.\n\nArt. 7º O vista temporário será concedido ao estrangeiro que não pretenda demorar-se mais de 180 dias.\n\nParágrafo único. A classificação de temporário compreende as seguintes categorias:\na) turistas;\nb) cientistas, professôres e homens de letras, em viagem cultural;\nc) pessoas em viagem de negócios;\nd) artistas, desportistas e congêneres.",
            title: "Decreto-Lei 7967/1945 - Tipos de Vistos",
            category: ["Legislation", "Immigration Law"],
            uuid: "c2678033-ee07-426b-a783-e663e21275cc",
            collection_name: "ELYSIA_CHUNKED_elysia_uploaded_documents__",
            chunk_spans: [],
            _REF_ID: "query_ELYSIA_CHUNKED_elysia_uploaded_documents___0_1",
          },
          {
            content:
              "Art. 9º O visto permanente será concedido ao estrangeiro que estiver em condições de permanecer definitivamente no Brasil e nêle pretenda fixar-se.\n\nArt. 10. O visto permanente especial será concedido ao estrangeiro que, estando nas condições do artigo anterior, seja excluído da cota de acôrdo com o estabelecido na letra d do artigo 4º.\n\nParágrafo único. A concessão de visto permanente especial depende de prévia seleção e classificação pela autoridade competente.\n\nArt. 11. Não se concederá visto ao estrangeiro:\n\nI - menor de 14 anos de idade, salvo se viajar em companhia de seus pais, ou responsáveis, ou vier para a sua companhia;\nII - indigente ou vagabundo;\nIII - que não satisfaça as exigências de saúde prefixadas;\nIV - nocivo à, ordem pública, á segurança nacional ou à estrutura das instituições;\nV - anteriormente expulso do país, salvo se a expulsão tiver sido revogada;\nVI - condenado em outro pais por crime de natureza que, segundo a lei brasileira, permita sua extradição.",
            title: "Decreto-Lei 7967/1945 - Artigo 9 (Visto Permanente)",
            category: ["Legislation", "Immigration Law"],
            uuid: "1a4a1e96-bf85-4457-b5c5-306b3b5b5d24",
            collection_name: "ELYSIA_CHUNKED_elysia_uploaded_documents__",
            chunk_spans: [],
            _REF_ID: "query_ELYSIA_CHUNKED_elysia_uploaded_documents___0_2",
          },
          {
            content:
              "Art. 12. Para obter visto permanente, o estrangeiro deve apresentar à autoridade consular:\n\nI - passaporte;\nII - prova de saúde.\n\n§ 1º O estrangeiro maior de 60 anos, que não viajar em companhia ou para junto de pessoa de sua família, deve provar que dispõe, para sua subsistência, de renda mensal estabelecida pelo órgão competente.\n\n§ 2º Pela concessão de visto permanente serão cobrados os emolumentos constantes da tabela anexa.\n\n§ 3º Será gratuita a concessão do visto permanente especial, a que se refere o art. 10.\n\nArt. 13. Para obter visto temporário, ou temporário especial, o estrangeiro deve apresentar à autoridade consular:\n\nI - passaporte;\nII - prova de saúde;\nIII - prova de meios de subsistência.",
            title: "Decreto-Lei 7967/1945 - Requisitos para Visto Permanente",
            category: ["Legislation", "Immigration Law"],
            uuid: "caa363c5-73c9-43b2-a0a6-a38b6eaa9640",
            collection_name: "ELYSIA_CHUNKED_elysia_uploaded_documents__",
            chunk_spans: [],
            _REF_ID: "query_ELYSIA_CHUNKED_elysia_uploaded_documents___0_3",
          },
          {
            content:
              "Art. 3º A corrente imigratória espontânea de cada país não ultrapassará, anualmente a cota de dois por cento sôbre o número dos respectivos nacionais que entraram no Brasil desde 1 de janeiro de 1884 até 31 de dezembro de 1933. O órgão competente poderá elevar a três mil pessoas a cota de uma nacionalidade e promover o aproveitamento dos saldos anteriores.\n\nParágrafo único. Quando se criar novo Estado, ser-1he-á fixada uma cota, tendo-se em vista especialmente a nacionalidade ou as nacionalidades nêle incluídas.\n\nArt. 4º Estão excluídos da cota:\na) a estrangeira casada com brasileiro, ou viúva de brasileiro, e o estrangeiro casado com brasileira;\nb) o estrangeiro que viajar em companhia do filho brasileiro;\nc) as imigrantes introduzidos no país de acôrdo com ò estabelecido no Capítulo I do Título III.",
            title: "Decreto-Lei 7967/1945 - Sistema de Cotas",
            category: ["Legislation", "Immigration Law"],
            uuid: "cd056a88-8be5-4f08-9f5f-dddb1c50457e",
            collection_name: "ELYSIA_CHUNKED_elysia_uploaded_documents__",
            chunk_spans: [],
            _REF_ID: "query_ELYSIA_CHUNKED_elysia_uploaded_documents___0_4",
          },
          {
            content:
              "CAPÍTULO II\nPRORROGAÇÃO DO PRAZO DE ENTRADA E TRANSFORMAÇÃO DA CLASSIFICAÇÃO\n\nArt. 34. Ao estrangeiro, registrado como temporário que possuir documento de nacionalidade, a serviço de registro local poderá conceder, até a máximo de seis meses, prorrogação do prazo de estada no país. Nos demais casos, a prorrogação será concedida pelo órgão federal competente.\n\nArt. 35. Ao estrangeiro registrado como temporário poderá, ser concedida a transformação de sua classificação para permanente, desde que se verifique satisfazer as condições de admisibi1idade e pague a taxa fixada na tabela anexa.\n\nCAPÍTULO III\nSAÍDA E RETÔRNO\n\nArt. 36. Para deixar o território brasileiro, o estrangeiro registrado como permanente deverá obter visto de saída, mediante o pagamento da taxa constante da tabela anexa e nas condições estabelecidas pelas dispositivos regulamentares.",
            title: "Decreto-Lei 7967/1945 - Transformação de Classificação",
            category: ["Legislation", "Immigration Law"],
            uuid: "8e057128-06f6-481b-b724-dda2c6048dac",
            collection_name: "ELYSIA_CHUNKED_elysia_uploaded_documents__",
            chunk_spans: [],
            _REF_ID: "query_ELYSIA_CHUNKED_elysia_uploaded_documents___0_5",
          },
        ],
        metadata: {
          collection_name: "ELYSIA_CHUNKED_elysia_uploaded_documents__",
          display_type: "document",
          needs_summarising: false,
          query_text: "What does Article 9 of Decreto-Lei 7967 say about permanent visas?",
          query_type: "hybrid",
          chunked: false,
          query_output: {
            target_collections: [
              "ELYSIA_CHUNKED_elysia_uploaded_documents__",
            ],
            search_type: "hybrid",
            search_query: "Article 9 Decreto-Lei 7967 permanent visa",
            sort_by: null,
            filter_buckets: null,
            limit: 10,
          },
          code: {
            language: "python",
            title: "Query",
            text: "collection.query.hybrid(\n    query='Article 9 Decreto-Lei 7967 permanent visa',\n    limit=10\n)",
          },
        },
        code: {
          language: "python",
          title: "Query",
          text: "collection.query.hybrid(\n    query='Article 9 Decreto-Lei 7967 permanent visa',\n    limit=10\n)",
        },
      },
    },
    {
      type: "result",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "9eecf0fb-b3e2-4272-b8d3-050e0f2e7d95",
      query_id: "b4c8ce36-0989-436e-966e-962efe8dacd3",
      id: "res-8c9c1f8d-0cf5-44d4-bf61-814bddb1999d",
      payload: {
        type: "document",
        objects: [
          {
            title: "Paul Stangl - Brazilian Consular Qualification Card",
            content:
              "# Brazilian Consular Qualification Card\n\n## Document Information\n**Document Type**: FICHA CONSULAR DE QUALIFICAÇÃO (Consular Qualification Card)\n**Country**: REPUBLICA DOS ESTADOS UNIDOS DO BRASIL (Republic of the United States of Brazil)\n\n## Personal Information\n- **Name**: Paul Stangl\n- **Nationality**: Austrian (Österreicher)\n- **Visa Type**: Permanent Visa (Visto Permanente)\n- **Legal Basis**: Article 9 of Decreto-Lei 7967 of 18 September 1945\n\n## Visa Details\n- **Classification**: Permanent resident intending to establish permanent residence in Brazil\n- **Requirements Met**: Passport and health certification as per Article 12\n- **Consular Processing**: Rome, Italy\n\n## Historical Context\nThis document represents one of the consular qualification cards issued to European nationals seeking permanent residence in Brazil during the post-World War II period. The use of Article 9 of Decreto-Lei 7967 indicates the individual met the requirements for permanent settlement as defined by Brazilian immigration law of 1945.\n\n## Source Reference\nDocument from Brazilian consular archives, Rome processing center.",
            category: ["Historical Document", "Immigration Record"],
            uuid: "198640fa-543d-4c5f-87e3-da9780e84970",
            collection_name: "ELYSIA_CHUNKED_elysia_uploaded_documents__",
            chunk_spans: [
              {
                start: 0,
                end: 500,
                uuid: "36646a4a-21ee-5514-8cea-cbb14dbb6678",
              },
              {
                start: 500,
                end: 1000,
                uuid: "1349145a-70c0-5b1e-b834-b4a259425a53",
              },
            ],
            _REF_ID: "query_ELYSIA_CHUNKED_elysia_uploaded_documents___1_0",
          },
          {
            title: "Decreto-Lei 7967/1945 - Full Text",
            content:
              "Legislação Informatizada - DECRETO-LEI Nº 7.967, DE 18 DE SETEMBRO DE 1945 - Publicação Original\n\nDECRETO-LEI Nº 7.967, DE 18 DE SETEMBRO DE 1945\n\nDispõe sôbre a Imigração e Colonização, e dá outras providências.\n\nO PRESIDENTE DA REPÚBLICA, usando da atribuição que lhe confere o artigo 180 da Constituição e considerando que se faz necessário, cessada a guerra mundial, imprimir á política imigratória do Brasil uma orientação racional e definitiva, que atenda à dupla finalidade de proteger os interêsses do trabalhador nacional e de desenvolver a imigração que fôr fator de progresso para o país.\n\nRio de Janeiro, 18 de setembro de 1945, 124º da Independência e 57º da República.\n\nGETÚLIO VARGAS\nAgamemnon Magalhães\nHenrique A. Guilhem\nP. Góes Monteiro\nP. Leão Veloso\nA. de Souza Costa\nJoão de Mendonça Lima\nApolonio Sales\nGustavo Capanema\nAlexandre Marcondes Filho\nJoaquim Pedro Salgado Filho\n\nPublicação:\nDiário Oficial da União - Seção 1 - 6/10/1945, Página 15825 (Publicação Original)",
            category: ["Legislation", "Immigration Law"],
            uuid: "2e092919-3292-4292-babd-6edae5994849",
            collection_name: "ELYSIA_CHUNKED_elysia_uploaded_documents__",
            chunk_spans: [
              {
                start: 0,
                end: 600,
                uuid: "3b153767-fb79-54e8-a6ed-8434038770c3",
              },
            ],
            _REF_ID: "query_ELYSIA_CHUNKED_elysia_uploaded_documents___1_1",
          },
        ],
        metadata: {
          collection_name: "ELYSIA_CHUNKED_elysia_uploaded_documents__",
          display_type: "document",
          needs_summarising: false,
          query_text: "Paul Stangl Brazilian visa Article 9",
          query_type: "hybrid",
          chunked: true,
          query_output: {
            target_collections: [
              "ELYSIA_CHUNKED_elysia_uploaded_documents__",
            ],
            search_type: "hybrid",
            search_query: "Paul Stangl Brazilian visa Article 9",
            sort_by: null,
            filter_buckets: null,
            limit: 10,
          },
          code: {
            language: "python",
            title: "Query",
            text: "collection.query.hybrid(\n    query='Paul Stangl Brazilian visa Article 9',\n    limit=10\n)",
          },
        },
        code: {
          language: "python",
          title: "Query",
          text: "collection.query.hybrid(\n    query='Paul Stangl Brazilian visa Article 9',\n    limit=10\n)",
        },
      },
    },
    {
      type: "text",
      id: "tex-648f906a-fcd5-40b7-a8eb-6d73c4c97229",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "9eecf0fb-b3e2-4272-b8d3-050e0f2e7d95",
      query_id: "b4c8ce36-0989-436e-966e-962efe8dacd3",
      payload: {
        type: "response",
        metadata: {},
        objects: [
          {
            text: "I found the relevant provisions of Decreto-Lei 7967 and related documentation. Let me summarize the key findings about Article 9 and permanent visas under Brazilian immigration law.",
          },
        ],
      },
    },
    {
      type: "text",
      id: "tex-0b8fd1ee-1de8-4a8a-9f31-5181b7f4e5b1",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "9eecf0fb-b3e2-4272-b8d3-050e0f2e7d95",
      query_id: "b4c8ce36-0989-436e-966e-962efe8dacd3",
      payload: {
        type: "text_with_citations",
        metadata: {
          title: "Brazilian Immigration Law: Article 9 of Decreto-Lei 7967/1945",
          author: "IntellyWeave Admin",
          date: "2025-12-10",
        },
        objects: [
          {
            text: "**Article 9 of Decreto-Lei 7967** (September 18, 1945) establishes the legal framework for permanent visas in Brazil. The article states: \"O visto permanente será concedido ao estrangeiro que estiver em condições de permanecer definitivamente no Brasil e nêle pretenda fixar-se.\" (The permanent visa shall be granted to the foreigner who is in a position to remain permanently in Brazil and intends to establish residence there.)",
            ref_ids: [
              "query_ELYSIA_CHUNKED_elysia_uploaded_documents___0_2",
            ],
          },
          {
            text: "\n\n**Requirements for Permanent Visa (Article 12)**: To obtain a permanent visa, the foreigner must present to the consular authority: (I) a passport; and (II) proof of health. Additionally, foreigners over 60 years of age who are not traveling with or to join family members must prove they have monthly income established by the competent authority for their subsistence.",
            ref_ids: [
              "query_ELYSIA_CHUNKED_elysia_uploaded_documents___0_3",
            ],
          },
          {
            text: "\n\n**Historical Context**: This law was enacted by President Getúlio Vargas on September 18, 1945, shortly after the end of World War II. Article 2 of the decree explicitly states that immigration admission shall consider \"the need to preserve and develop, in the ethnic composition of the population, the most convenient characteristics of its European ancestry.\" This eugenic provision reflects the immigration policies of the era and provided legal framework for selective European immigration.",
            ref_ids: [
              "query_ELYSIA_CHUNKED_elysia_uploaded_documents___0_0",
              "query_ELYSIA_CHUNKED_elysia_uploaded_documents___1_1",
            ],
          },
          {
            text: "\n\n**Application to Historical Cases**: The Paul Stangl consular qualification card demonstrates how Article 9 was applied in practice. The document shows that permanent visas were processed through Brazilian consulates (in this case, Rome), requiring passport documentation and health certification. The relatively minimal requirements—passport and health proof—made this provision potentially exploitable for individuals seeking to establish new identities in South America during the post-war period.",
            ref_ids: [
              "query_ELYSIA_CHUNKED_elysia_uploaded_documents___1_0",
            ],
          },
          {
            text: "\n\n**Exclusions from Visa (Article 11)**: The law did specify that visas should not be granted to individuals who were: (IV) harmful to public order, national security, or institutional structure; or (VI) convicted in another country of crimes that would permit extradition under Brazilian law. However, the effectiveness of these provisions depended entirely on the information available to Brazilian consular authorities at the time of application.",
            ref_ids: [
              "query_ELYSIA_CHUNKED_elysia_uploaded_documents___0_2",
            ],
          },
        ],
      },
    },
    {
      type: "suggestion",
      id: "dd824625-0b98-4b42-96b5-66a179939410",
      conversation_id: "9eecf0fb-b3e2-4272-b8d3-050e0f2e7d95",
      query_id: "b4c8ce36-0989-436e-966e-962efe8dacd3",
      user_id: "com-55ffea04-c8ec-4daf-811b-6c6abe9e09e0",
      payload: {
        error: "",
        suggestions: [
          "Was Brazilian immigration law exploited by the rat lines network?",
          "Compare Brazilian and Argentine immigration policies post-WWII",
          "Which Brazilian consulates processed permanent visa applications for European nationals 1945-1950?",
        ],
      },
    },
  ],
};
