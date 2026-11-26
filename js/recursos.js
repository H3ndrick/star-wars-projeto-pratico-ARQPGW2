// Os seis discos: página, cor, o que a lista mostra e a ordem dos campos no modal.
// selo (opcional): texto grande sobre a imagem do card.
// ordem: campos que aparecem primeiro no modal; os demais vêm depois.
export const recursos = {
  people: {
    disco: 1, pagina: "personagens.html", titulo: "Personagens", pasta: "personagens", tipo: "Personagem",
    resumo: (p) => `Nascimento: ${valor(p.birth_year)}`,
    ordem: ["height", "mass", "birth_year", "gender", "homeworld", "films", "species", "vehicles", "starships"],
  },
  films: {
    disco: 2, pagina: "filmes.html", titulo: "Filmes", pasta: "filmes", tipo: "Filme",
    selo: (f) => romano(f.episode_id),
    resumo: (f) => `Episódio ${romano(f.episode_id)}, ${f.release_date.slice(0, 4)}`,
    ordem: ["episode_id", "release_date", "director", "producer"],
  },
  species: {
    disco: 3, pagina: "especies.html", titulo: "Espécies", pasta: "especies", tipo: "Espécie",
    resumo: (e) => valor(e.classification),
    ordem: ["classification", "designation", "language", "average_height", "average_lifespan", "homeworld", "people", "films"],
  },
  planets: {
    disco: 4, pagina: "planetas.html", titulo: "Planetas", pasta: "planetas", tipo: "Planeta",
    resumo: (p) => valor(p.climate),
    ordem: ["rotation_period", "orbital_period", "diameter", "climate", "gravity", "terrain", "surface_water", "population", "residents", "films"],
  },
  vehicles: {
    disco: 5, pagina: "veiculos.html", titulo: "Veículos", pasta: "veiculos", tipo: "Veículo",
    resumo: (v) => valor(v.vehicle_class),
    ordem: ["model", "manufacturer", "cost_in_credits", "length", "max_atmosphering_speed", "crew", "passengers", "cargo_capacity", "consumables", "vehicle_class", "pilots", "films"],
  },
  starships: {
    disco: 6, pagina: "naves.html", titulo: "Naves", pasta: "naves", tipo: "Nave",
    resumo: (n) => valor(n.starship_class),
    ordem: ["model", "manufacturer", "cost_in_credits", "length", "max_atmosphering_speed", "crew", "passengers", "cargo_capacity", "consumables", "hyperdrive_rating", "MGLT", "starship_class", "pilots", "films"],
  },
};

// Campos de controle da API: ficam discretos no fim do modal.
export const tecnicos = ["created", "edited", "url"];

export const rotulos = {
  episode_id: "Episódio", director: "Direção", producer: "Produção", release_date: "Lançamento",
  height: "Altura (cm)", mass: "Peso (kg)", hair_color: "Cabelo", skin_color: "Pele", eye_color: "Olhos",
  birth_year: "Ano de nascimento", gender: "Gênero", homeworld: "Planeta de origem", films: "Filmes", species: "Espécie",
  vehicles: "Veículos", starships: "Naves", characters: "Personagens", planets: "Planetas", people: "Personagens",
  rotation_period: "Período de rotação (h)", orbital_period: "Período orbital (dias)", diameter: "Diâmetro (km)", climate: "Clima",
  gravity: "Gravidade", terrain: "Terreno", surface_water: "Água na superfície (%)", population: "População",
  residents: "Residentes", model: "Modelo", manufacturer: "Fabricante", cost_in_credits: "Preço (créditos)",
  length: "Tamanho (m)", max_atmosphering_speed: "Velocidade máxima", crew: "Tripulação",
  passengers: "Passageiros", cargo_capacity: "Capacidade de carga (kg)", consumables: "Autonomia", hyperdrive_rating: "Hiperpropulsor",
  MGLT: "MGLT", starship_class: "Classe da nave", vehicle_class: "Classe do veículo", pilots: "Pilotos",
  classification: "Classificação", designation: "Designação", average_height: "Altura média (cm)",
  skin_colors: "Cores de pele", hair_colors: "Cores de cabelo", eye_colors: "Cores dos olhos",
  average_lifespan: "Expectativa de vida (anos)", language: "Idioma",
  created: "Registro criado", edited: "Registro editado", url: "Endereço na API",
};

export const nomeDe = (item) => item.title ?? item.name;
export const idDe = (url) => url.split("/").filter(Boolean).pop();
// "https://swapi.info/api/planets/1" -> "planets"
export const recursoDe = (url) => url.split("/").filter(Boolean).at(-2);
export const enderecoDe = (url) => `${recursos[recursoDe(url)].pagina}?id=${idDe(url)}`;

export function valor(v) {
  if (v === null || v === undefined || v === "" || v === "unknown") return "Desconhecido";
  if (v === "n/a") return "Não se aplica";
  if (v === "none") return "Nenhum";
  return String(v);
}

export const romano = (n) => ["", "I", "II", "III", "IV", "V", "VI"][n] ?? String(n);
