// Página de um disco: carrega a lista inteira do recurso do <body data-recurso>.
import { obterRecurso } from "./dados.js";
import { renderizarLista, mostrarEstado, abrirDetalhe } from "./interface.js";
import { iniciarTopo } from "./menu-dvd.js";
import { idDe } from "./recursos.js";

iniciarTopo();

const recurso = document.body.dataset.recurso;
const lista = document.querySelector("[data-lista]");

// Busca (sua parte): o campo é #busca. Filtre os itens pelo nome
// e chame renderizarLista(lista, recurso, filtrados).
document.querySelector(".busca")?.addEventListener("submit", (e) => e.preventDefault());

mostrarEstado(lista, "carregando");
try {
  const itens = await obterRecurso(recurso);
  renderizarLista(lista, recurso, itens);
  // personagens.html?id=1 abre direto o modal do item
  const id = new URLSearchParams(location.search).get("id");
  const item = id && itens.find((i) => idDe(i.url) === id);
  if (item) abrirDetalhe(recurso, item);
} catch (erro) {
  console.error(erro);
  mostrarEstado(lista, "erro");
}
