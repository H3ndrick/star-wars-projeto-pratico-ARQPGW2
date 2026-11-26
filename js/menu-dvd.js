// Menu do disco: um único sabre percorre as opções, como o cursor de um DVD.
// A opção escolhida também muda a cor da luz do corredor.
// O sabre mira sempre o meio das letras maiúsculas do rótulo, em qualquer tamanho de tela.
export function iniciarMenu() {
  const hero = document.querySelector(".abertura");
  const menu = document.querySelector(".menu-dvd");
  const opcoes = [...menu.querySelectorAll("a")];
  const regua = document.createElement("canvas").getContext("2d");

  // marcador de altura zero apoiado na linha de base de cada rótulo
  for (const rotulo of menu.querySelectorAll(".menu-rotulo")) {
    const base = document.createElement("i");
    base.className = "linha-base";
    base.setAttribute("aria-hidden", "true");
    rotulo.append(base);
  }

  const alturaMaiusculas = (rotulo) => {
    const estilo = getComputedStyle(rotulo);
    regua.font = `${estilo.fontWeight} ${estilo.fontSize} ${estilo.fontFamily}`;
    return regua.measureText("H").actualBoundingBoxAscent;
  };

  // Calcula onde o rótulo ativo vai parar, não onde ele está agora: as legendas
  // abrem e fecham com animação, e a que fecha acima dele ainda ocupa espaço.
  // Assim o sabre faz um único deslize, sem correção no caminho.
  const posicionar = () => {
    const ativa = menu.querySelector(".ativa");
    const rotulo = ativa.querySelector(".menu-rotulo");
    const base = rotulo.querySelector(".linha-base");
    let acima = 0;
    for (const opcao of opcoes) {
      if (opcao === ativa) break;
      acima += opcao.querySelector(".menu-legenda").offsetHeight;
    }
    menu.style.setProperty("--cursor", `${base.offsetTop - acima - alturaMaiusculas(rotulo) / 2}px`);
  };

  const selecionar = (opcao) => {
    if (opcao.classList.contains("ativa")) return;
    opcoes.forEach((o) => o.classList.toggle("ativa", o === opcao));
    hero.dataset.luz = opcao.dataset.luz;
    posicionar();
    // reacende a lâmina a cada troca
    menu.classList.remove("acendendo");
    void menu.offsetWidth;
    menu.classList.add("acendendo");
  };

  opcoes.forEach((opcao, i) => {
    opcao.addEventListener("pointerenter", () => selecionar(opcao));
    opcao.addEventListener("focus", () => selecionar(opcao));
    opcao.addEventListener("keydown", (e) => {
      const passo = { ArrowDown: 1, ArrowUp: -1 }[e.key];
      if (!passo) return;
      e.preventDefault();
      opcoes[(i + passo + opcoes.length) % opcoes.length].focus();
    });
  });

  posicionar();
  menu.classList.add("acendendo");
  addEventListener("resize", posicionar);
  document.fonts?.ready.then(posicionar);
}

// Topo transparente sobre a abertura; ganha fundo depois de rolar.
export function iniciarTopo() {
  const topo = document.querySelector(".topo");
  const atualizar = () => topo.classList.toggle("solido", scrollY > 40);
  addEventListener("scroll", atualizar, { passive: true });
  atualizar();
  // menu do celular aberto também precisa de fundo
  // busca geral da navbar: só visual. Sem isto, o Enter recarregaria a página.
  document.querySelector(".busca-topo")?.addEventListener("submit", (e) => e.preventDefault());
  const menu = document.querySelector("#menu");
  if (!menu) return;
  menu.addEventListener("show.bs.collapse", () => topo.classList.add("aberto"));
  menu.addEventListener("hidden.bs.collapse", () => topo.classList.remove("aberto"));
  menu.querySelectorAll(".nav-link").forEach((link) =>
    link.addEventListener("click", () => bootstrap.Collapse.getInstance(menu)?.hide()));
}
