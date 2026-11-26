// Renderização: listas, estados e modal. Não busca dados por conta própria.
import { recursos, rotulos, tecnicos, nomeDe, idDe, recursoDe, enderecoDe, valor } from "./recursos.js";
import { obterNome, obterRecurso } from "./dados.js";
import { imagens } from "./imagens.js";
import { PREVIA, previa } from "./previa.js";

const el = (tag, classe, texto) => {
  const no = document.createElement(tag);
  if (classe) no.className = classe;
  if (texto !== undefined) no.textContent = texto;
  return no;
};

// Recurso da página atual (data-recurso no <body>); vazio na tela inicial.
const recursoDaPagina = document.body.dataset.recurso;

function semImagem(quadro, item) {
  quadro.classList.add("sem-imagem");
  // iniciais das duas primeiras palavras: "Owen Lars" -> "OL", "Yoda" -> "YO"
  const palavras = nomeDe(item).split(/[\s-]+/).filter(Boolean);
  const letras = palavras.length > 1 ? palavras[0][0] + palavras[1][0] : palavras[0].slice(0, 2);
  const inicial = el("span", "sem-imagem-letra", letras);
  inicial.setAttribute("aria-hidden", "true");
  quadro.append(inicial, el("span", "sem-imagem-texto", "Sem imagem"));
}

function imagem(recurso, item, alt) {
  const quadro = el("span", "quadro");
  const id = Number(idDe(item.url));
  const temImagem = imagens[recurso]?.includes(id);
  const provisoria = !temImagem && PREVIA && previa[recurso];
  if (!temImagem && !provisoria) {
    semImagem(quadro, item);
    return quadro;
  }
  const img = el("img");
  img.alt = alt;
  img.loading = "lazy";
  img.addEventListener("error", () => { img.remove(); semImagem(quadro, item); });
  img.src = temImagem
    ? `assets/img/${recursos[recurso].pasta}/${id}.png`
    : `assets/img/previa/${recurso}/${id % previa[recurso]}.png`;
  quadro.append(img);
  return quadro;
}

// Substitui o conteúdo da lista. Serve para a carga inicial e para a busca.
// Se a página tiver um elemento [data-contagem], ele mostra quantos itens há.
export function renderizarLista(lista, recurso, itens) {
  const contagem = document.querySelector(`[data-contagem="${recurso}"]`);
  if (contagem) contagem.textContent = itens.length === 1 ? "1 registro" : `${itens.length} registros`;
  if (!itens.length) return mostrarEstado(lista, "vazio");
  lista.removeAttribute("aria-busy");
  lista.replaceChildren(...itens.map((item) => {
    const li = el("li", "item");
    const botao = el("button", "ficha");
    botao.type = "button";
    const texto = el("span", "ficha-texto");
    texto.append(
      el("span", "ficha-numero", `Nº ${idDe(item.url).padStart(3, "0")}`),
      el("span", "ficha-nome", nomeDe(item)),
      el("span", "ficha-resumo", recursos[recurso].resumo(item)),
    );
    const quadro = imagem(recurso, item, "");
    const selo = recursos[recurso].selo?.(item);
    if (selo) {
      const marca = el("span", "selo", selo);
      marca.setAttribute("aria-hidden", "true");
      quadro.append(marca);
    }
    botao.append(quadro, texto);
    botao.addEventListener("click", () => abrirDetalhe(recurso, item));
    li.append(botao);
    return li;
  }));
}

const mensagens = {
  carregando: "Lendo o disco",
  vazio: "Nenhum item encontrado. Confira o nome e tente de novo.",
  erro: "Não foi possível carregar os dados. Recarregue a página.",
};

// estado: "carregando" | "vazio" | "erro"
export function mostrarEstado(lista, estado) {
  lista.toggleAttribute("aria-busy", estado === "carregando");
  const li = el("li", `estado estado-${estado}`);
  li.setAttribute("role", "status");
  const luzes = el("span", "luzes");
  luzes.setAttribute("aria-hidden", "true");
  for (let i = 0; i < 5; i++) luzes.append(el("i"));
  li.append(luzes, el("span", "", mensagens[estado]));
  lista.replaceChildren(li);
}

// Aviso no canto da tela. Pronto para o cache: avisarMemoryCard("Disco 1 salvo")
export function avisarMemoryCard(texto) {
  const aviso = document.querySelector("#memory-card");
  aviso.querySelector("[data-texto]").textContent = texto;
  aviso.hidden = false;
  clearTimeout(avisarMemoryCard.tempo);
  avisarMemoryCard.tempo = setTimeout(() => { aviso.hidden = true; }, 2400);
}

function formatar(chave, bruto) {
  if (["created", "edited", "release_date"].includes(chave)) return bruto.slice(0, 10).split("-").reverse().join("/");
  return valor(bruto);
}

// Etiqueta de relação: vira link para o item na página do recurso dele.
function relacao(url) {
  const recurso = recursoDe(url);
  if (!recursos[recurso]) return el("span", "etiqueta", "…");
  const link = el("a", "etiqueta", "…");
  link.href = enderecoDe(url);
  // na própria página, abre o outro item sem recarregar
  if (recurso === recursoDaPagina) {
    link.addEventListener("click", async (e) => {
      e.preventDefault();
      const item = (await obterRecurso(recurso)).find((i) => i.url === url);
      if (item) abrirDetalhe(recurso, item);
    });
  }
  return link;
}

let pedido = 0;

export async function abrirDetalhe(recurso, item) {
  const atual = ++pedido;
  const config = recursos[recurso];
  const modal = document.querySelector("#modal-detalhe");
  modal.dataset.recurso = recurso;
  modal.querySelector("#modal-titulo").textContent = nomeDe(item);
  modal.querySelector("[data-tipo]").textContent = `Disco ${config.disco} · ${config.tipo} · Nº ${idDe(item.url).padStart(3, "0")}`;
  modal.querySelector("[data-imagem]").replaceChildren(imagem(recurso, item, `Imagem de ${nomeDe(item)}`));

  const abertura = modal.querySelector("[data-abertura]");
  abertura.hidden = !item.opening_crawl;
  abertura.querySelector("p").textContent = item.opening_crawl ?? "";

  const campos = modal.querySelector("[data-campos]");
  const relacoes = modal.querySelector("[data-relacoes]");
  const registro = modal.querySelector("[data-registro]");
  campos.replaceChildren();
  relacoes.replaceChildren();
  registro.replaceChildren();

  const chaves = [...config.ordem, ...Object.keys(item).filter((c) => !config.ordem.includes(c) && !tecnicos.includes(c)), ...tecnicos];
  const pendentes = [];
  for (const chave of chaves) {
    if (!(chave in item) || ["name", "title", "opening_crawl"].includes(chave)) continue;
    const bruto = item[chave];
    const ehRelacao = Array.isArray(bruto) || (chave === "homeworld" && bruto);
    const linha = el("div", ehRelacao ? "relacao" : "campo");
    const dd = el("dd");
    const dt = el("dt", "", rotulos[chave] ?? chave);
    linha.append(dt, dd);
    if (ehRelacao) {
      const urls = [bruto].flat();
      dt.append(el("span", "relacao-contagem", String(urls.length)));
      if (!urls.length) dd.textContent = "Nenhum registro";
      for (const url of urls) {
        const no = relacao(url);
        dd.append(no);
        pendentes.push([no, url]);
      }
      relacoes.append(linha);
    } else {
      dd.textContent = formatar(chave, bruto);
      (tecnicos.includes(chave) ? registro : campos).append(linha);
    }
  }

  if (recurso === recursoDaPagina) history.replaceState(null, "", `?id=${idDe(item.url)}`);
  bootstrap.Modal.getOrCreateInstance(modal).show();
  modal.querySelector(".modal-body").scrollTop = 0;

  await Promise.all(pendentes.map(async ([no, url]) => {
    const nome = await obterNome(url).catch(() => "Indisponível");
    if (atual === pedido) no.textContent = nome;
  }));
}

// Ao fechar o modal, o endereço volta a ser o da lista.
document.querySelector("#modal-detalhe")?.addEventListener("hidden.bs.modal", () => {
  if (recursoDaPagina && location.search) history.replaceState(null, "", location.pathname);
});
