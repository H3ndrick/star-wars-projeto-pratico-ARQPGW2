// PONTO DE TROCA: a interface só conversa com os dados por estas duas funções.
// Mantenha os nomes e retornos, e troque o corpo por fetch + localStorage.
import { exemplo } from "./dados-exemplo.js";

// recurso: "films" | "people" | "planets" | "starships" | "vehicles" | "species"
// retorna: Promise com o array da API. Se falhar, lance um erro:
// a interface mostra a mensagem de falha sozinha.
export async function obterRecurso(recurso) {
  return exemplo[recurso] ?? [];
}

// Recebe a URL de uma relação e retorna Promise com o nome do item.
export async function obterNome(url) {
  for (const lista of Object.values(exemplo)) {
    const item = lista.find((i) => i.url === url);
    if (item) return item.title ?? item.name;
  }
  return url;
}
