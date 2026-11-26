"""Gera as imagens do site com acabamento PSX.
Uso: uv run --no-project --with pillow --with numpy python ferramentas/psx.py
"""
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

RAIZ = Path(__file__).resolve().parent.parent
REF = RAIZ / "referencias" / "referencias-estilo-star-wars"
OUT = RAIZ / "assets" / "img"
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 - 0.47


def psx(im, cores=40, forca=20):
    """Dithering ordenado + 15 bits (como o PSX) + paleta curta."""
    a = np.asarray(im.convert("RGB")).astype(float)
    h, w = a.shape[:2]
    a += np.tile(BAYER, (h // 4 + 1, w // 4 + 1))[:h, :w, None] * forca
    a = np.clip(np.round(a / 8) * 8, 0, 255).astype("uint8")
    return Image.fromarray(a).quantize(cores, dither=Image.Dither.NONE).convert("RGB")


def corte(nome, caixa, tam, saida, contraste=1.15, cores=40):
    if nome.endswith(".avif"):
        import pillow_avif  # noqa: F401
    im = Image.open(REF / nome).convert("RGB")
    W, H = im.size
    im = im.crop([int(v * s) for v, s in zip(caixa, (W, H, W, H))])
    # recorte central na proporção final, sem deformar
    r = tam[0] / tam[1]
    w, h = im.size
    if w / h > r:
        n = int(h * r); im = im.crop(((w - n) // 2, 0, (w - n) // 2 + n, h))
    else:
        n = int(w / r); im = im.crop((0, (h - n) // 2, w, (h - n) // 2 + n))
    im = ImageEnhance.Contrast(im.resize(tam, Image.Resampling.LANCZOS)).enhance(contraste)
    psx(im, cores).save(OUT / saida, optimize=True)


def hero():
    im = Image.open(REF / "refstarwars1.png").convert("RGB")
    k = 2048 / 1500
    x0, y0, w, h = 290, 1310, 900, 506
    im = im.crop([int(v * k) for v in (x0, y0, x0 + w, y0 + h)]).resize((640, 360), Image.Resampling.LANCZOS)
    cheio = psx(ImageEnhance.Contrast(im).enhance(1.1), 40, 16)
    cheio.save(OUT / "home/corredor.png", optimize=True)
    # região aproximada; a borda exata vem dos pixels escuros, linha a linha
    pts = [(322,93),(333,95),(340,102),(342,116),(346,134),(336,139),(350,146),(364,150),(371,160),(375,190),
           (379,240),(384,300),(388,360),(246,360),(252,310),(261,250),(267,200),(273,165),(280,150),
           (298,143),(309,138),(300,134),(303,116),(305,102),(311,95)]
    regiao = Image.new("L", (640, 360), 0)
    ImageDraw.Draw(regiao).polygon(pts, fill=255)
    regiao = np.asarray(regiao.filter(ImageFilter.MaxFilter(13))) > 0
    escuro = (np.asarray(im)[:, :, 0] < 115) & regiao
    m = np.zeros((360, 640), "uint8")
    for y in range(90, 360):
        if y < 250:
            xs = np.flatnonzero(escuro[y])
            if len(xs):
                m[y, xs[0]:xs[-1] + 1] = 255
        else:  # névoa esconde a borda: continua a linha da capa
            t = (y - 250) / 110
            m[y, round(266 - 17 * t):round(378 + 13 * t)] = 255
    m = Image.fromarray(m)
    cheio.putalpha(m)
    cheio.save(OUT / "home/vader.png", optimize=True)


def ruido(n, semente, oit=5):
    r = np.random.default_rng(semente); t = np.zeros((n, n))
    for o in range(oit):
        g = 3 * 2 ** o
        c = Image.fromarray((r.random((g, g)) * 255).astype("uint8")).resize((n, n), Image.Resampling.BICUBIC)
        t += np.asarray(c) / 255 / 2 ** o
    return (t - t.min()) / (t.max() - t.min())


QUADROS = 16


def planeta(pid, paleta, semente, faixas=False):
    """Tira horizontal com uma volta completa do planeta."""
    n = 96
    y, x = np.mgrid[-1.06:1.06:n * 1j, -1.06:1.06:n * 1j]
    r2 = x * x + y * y; z = np.sqrt(np.clip(1 - r2, 0, 1)); dentro = r2 <= 1
    t = ruido(256, semente)
    mistura = np.linspace(0, 1, 256)[None, :]          # emenda sem costura
    t = t * (1 - mistura) + np.roll(t, 128, 1) * mistura
    t[:, 224:] = t[:, 224:] * (1 - np.linspace(0, 1, 32)) + t[:, :1] * np.linspace(0, 1, 32)
    t = (t - t.min()) / (t.max() - t.min())
    lon = (np.arctan2(x, z) / (2 * np.pi)) * 256
    v = np.clip((np.arcsin(np.clip(y, -1, 1)) / np.pi + .5) * 255, 0, 255).astype(int)
    pal = np.array([[int(c[i:i + 2], 16) for i in (0, 2, 4)] for c in paleta], float)
    luz = np.clip(-.6 * x - .5 * y + .62 * z, 0, 1)
    tira = Image.new("RGB", (n * QUADROS, n))
    for q in range(QUADROS):
        val = t[v, (lon + 256 * q / QUADROS).astype(int) % 256]
        if faixas:
            val = np.clip(.5 + .4 * np.sin(y * 15 + val * 3), 0, 1)
        val = np.clip((val - .2) / .6, 0, 1)
        cor = np.stack([np.interp(val, np.linspace(0, 1, len(pal)), pal[:, i]) for i in range(3)], -1)
        cor *= (.06 + 1.05 * luz)[..., None]
        tira.paste(Image.fromarray(np.clip(cor, 0, 255).astype("uint8")), (n * q, 0))
    tira = psx(tira, 24, 26)
    tira.putalpha(Image.fromarray(np.tile((dentro * 255).astype("uint8"), (1, QUADROS))))
    tira.save(OUT / f"planetas/{pid}.png", optimize=True)


hero()
F = (208, 117)
corte("refstarwars9.jpeg", (.0, .0, 1, 1), F, "filmes/1.png")
corte("refstarwars3.jpg", (0, 0, 1, 1), F, "filmes/2.png")
corte("refstarwars4.jpeg", (0, 0, 1, 1), F, "filmes/3.png")
corte("images.jpeg", (0, .2, .7, 1), F, "filmes/5.png")
corte("ameaça-fantasma.webp", (.2, .012, 1, .689), F, "filmes/4.png")  # Episódio I: recorte alto, com a sombra do Vader inteira
corte("refstarwars6.jpg", (0, 0, 1, 1), F, "filmes/6.png")
P = (132, 165)
corte("refstarwar5.jpg", (.32, 0, .7, .62), P, "personagens/1.png")
corte("22143540096_0c88df0f2c_c.jpg", (.21, .03, .45, .56), P, "personagens/2.png")
corte("22143540096_0c88df0f2c_c.jpg", (.38, .34, .64, 1), P, "personagens/3.png")
corte("refstarwars2.jpg", (.24, .08, .45, .62), P, "personagens/4.png", 1.35)
corte("refstarwars5.jpg", (.26, .2, .52, .95), P, "personagens/5.png")
corte("refstarwars5.jpg", (.55, 0, .9, .78), P, "personagens/14.png")
corte("millenniumfalconnave.webp", (0, .06, 1, .9), (320, 180), "naves/10.png")
corte("refnavesstarwars.jpg", (0, 0, 1, 1), (320, 180), "naves/65.png")
# paleta pelo primeiro terreno reconhecido (escuro -> claro)
PALETAS = [
    (("gas giant",), ["5a3a6e", "9b5f8a", "d99a8c", "f3d6b8"]),
    (("desert", "arid", "barren", "ash", "rocky", "canyon", "mesa"), ["8a4f22", "c98a45", "e6b873", "f3dca6"]),
    (("ice", "glacier", "tundra", "frozen", "frigid"), ["6f93b5", "a9c6dc", "dcebf4", "ffffff"]),
    (("swamp", "bog", "murky", "fungus"), ["141f18", "2c3d2a", "4c5a38", "6f7a55"]),
    (("volcano", "lava", "superheated"), ["1a0a08", "5a1408", "c4330f", "ffb347"]),
    (("cityscape", "urban", "cities", "airless"), ["1d2230", "3b4256", "6b7590", "f0d48a"]),
    (("ocean", "sea", "reef", "island", "lake"), ["0c2a55", "1b4f8a", "3b86b8", "cfe8f0"]),
    (("jungle", "rainforest", "forest", "verdant", "vine"), ["12301f", "2d5a30", "5f8040", "a08a52"]),
    (("grass", "plain", "savanna", "field", "scrub", "hill"), ["12385f", "1f6a8c", "4d8a52", "c9dfe0"]),
    (("mountain", "rock", "cave", "valley", "cliff", "plateau"), ["3a3330", "6b5d52", "9c8b78", "d1c3ad"]),
]


def paleta(terreno):
    for termo in terreno.split(","):
        for chaves, cores in PALETAS:
            if any(c in termo for c in chaves):
                return cores, chaves == ("gas giant",)
    return ["2a2438", "4a4060", "7a6f94", "b9b0d4"], False


# planetas a partir da cópia local dos dados (assets/js/dados-exemplo.js)
texto = (RAIZ / "assets" / "js" / "dados-exemplo.js").read_text(encoding="utf-8")
for p in json.loads(texto.split("export const exemplo = ", 1)[1].rstrip().rstrip(";"))["planets"]:
        pid = int(p["url"].rstrip("/").split("/")[-1])
        cores, faixas = paleta(p["terrain"])
        planeta(pid, cores, pid, faixas)


def manifesto():
    """Lista as imagens existentes para o site não pedir arquivos que não há."""
    pastas = {"films": "filmes", "people": "personagens", "species": "especies",
              "planets": "planetas", "vehicles": "veiculos", "starships": "naves"}
    dados = {r: sorted(int(f.stem) for f in (OUT / d).glob("*.png") if f.stem.isdigit()) if (OUT / d).exists() else []
             for r, d in pastas.items()}
    (RAIZ / "assets" / "js" / "imagens.js").write_text(
        "// Gerado por ferramentas/psx.py: ids que têm imagem em assets/img.\n"
        f"export const imagens = {json.dumps(dados)};\n", encoding="utf-8")


def estrelas():
    """Ladrilho de estrelas em pixel, repetido no fundo da página."""
    r = np.random.default_rng(7)
    n = 320
    a = np.zeros((n, n, 4), "uint8")
    for _ in range(70):
        x, y = r.integers(0, n, 2)
        b = int(r.choice([90, 130, 180, 255], p=[.45, .3, .17, .08]))
        tom = r.choice([(255, 255, 255), (200, 220, 255), (255, 236, 200)])
        a[y, x] = (*tom, b)
        if b == 255:  # estrelas fortes ganham uma cruz de 1 px
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                a[(y + dy) % n, (x + dx) % n] = (*tom, 80)
    Image.fromarray(a, "RGBA").save(OUT / "home/estrelas.png", optimize=True)


estrelas()
manifesto()


def holograma(im, saida, alfa=None, limite=None):
    """Imagem em tons de cinza com transparência; a cor azul vem do CSS."""
    im = im.convert("RGBA")
    a = np.asarray(im).astype(float)
    lum = a[..., :3] @ [.3, .59, .11]
    if alfa is None:
        alfa = a[..., 3]
    if limite is not None:            # fundo escuro vira transparente
        alfa = np.clip((lum - limite) * 4, 0, 255) * (alfa / 255)
    dentro = alfa > 128                 # estica o contraste só dentro da figura
    if dentro.any():
        lo, hi = np.percentile(lum[dentro], [2, 98])
        lum = np.clip((lum - lo) / max(hi - lo, 1), 0, 1) ** .8 * 205 + 50
    out = np.dstack([lum, lum, lum, alfa]).astype("uint8")
    out = Image.fromarray(out, "RGBA")
    caixa = out.getbbox()
    out.crop(caixa).save(OUT / "holo" / saida, optimize=True)


def hologramas():
    (OUT / "holo").mkdir(exist_ok=True)
    holograma(Image.open(OUT / "home/vader.png"), "personagens.png")
    # C-3PO recortado do céu azul da foto (espécie: droide)
    im = Image.open(REF / "22143540096_0c88df0f2c_c.jpg").convert("RGB")
    W, H = im.size
    im = im.crop((int(.2 * W), int(.04 * H), int(.425 * W), int(.6 * H)))  # busto
    a = np.asarray(im).astype(int)
    ceu = (a[..., 2] > a[..., 0] + 25) & (a[..., 2] > 120)
    fundo = Image.fromarray((ceu * 255).astype("uint8")).filter(ImageFilter.MaxFilter(3))
    alfa = 255 - np.asarray(fundo).astype(float)
    holograma(im, "especies.png", alfa=alfa)
    holograma(Image.open(REF / "millenniumfalconnave.webp").convert("RGB").resize((1000, 750)), "naves.png", limite=45)
    # AT-AT: o arquivo já vem com fundo transparente
    im = Image.open(REF / "at-at.webp").convert("RGBA")
    im.thumbnail((420, 600), Image.Resampling.LANCZOS)   # exibido pequeno; poupa peso
    holograma(im, "veiculos.png")


hologramas()


def corredor(cor, saida):
    """Corredor imperial vazio, visto de dentro: molduras arredondadas em sequência,
    paredes iluminadas pela luz que vem do fundo."""
    W, H = 1280, 720
    cx, cy = W / 2, H * .46
    luz = np.array([int(cor[i:i + 2], 16) for i in (0, 2, 4)], float)
    y, x = np.mgrid[0:H, 0:W].astype(float)
    # "distância" em forma de retângulo arredondado (superelipse)
    nx, ny = np.abs(x - cx) / (W * .5), np.abs(y - cy) / (H * .62)
    d = (nx ** 5 + ny ** 5) ** .2 + 1e-4
    u = np.log(1 / d) / np.log(1.38)               # profundidade em "molduras"
    f = u - np.floor(u)                            # posição dentro de cada trecho
    perto = np.clip(1 - d, 0, 1)                   # 0 na borda, 1 no fundo
    parede = (.1 + .95 * perto ** 2.2) * (.45 + .55 * f)
    nervura = f < .14
    borda = (f >= .14) & (f < .2)                  # aresta acesa da moldura
    brilho = np.where(nervura, parede * .18, np.where(borda, parede * 1.7 + .08, parede))
    brilho *= np.where(y > cy, 1 - .35 * np.clip((y - cy) / (H * .5), 0, 1), 1)   # chão mais escuro
    a = brilho[..., None] * (luz * .95 + 25)
    r = np.sqrt(((x - cx) / (W * .16)) ** 2 + ((y - cy) / (H * .2)) ** 2)
    a += (np.clip(1 - r, 0, 1) ** 1.4)[..., None] * (luz * .7 + 110)         # névoa clara no fundo
    a *= np.clip(1.25 - np.sqrt(((x - cx) / W) ** 2 + ((y - cy) / H) ** 2) * 1.3, .2, 1)[..., None]
    ruido = np.random.default_rng(3).normal(0, 6, a.shape[:2])[..., None]
    im = Image.fromarray(np.clip(a + ruido, 0, 255).astype("uint8")).filter(ImageFilter.GaussianBlur(1))
    im = im.resize((640, 360), Image.Resampling.LANCZOS)
    psx(im, 32, 18).save(OUT / "capas" / saida, optimize=True)


def tvs():
    """Capa dos filmes: parede de TVs de tubo, uma por episódio, no escuro."""
    W, H = 1280, 720
    im = Image.new("RGB", (W, H), (3, 4, 7))
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(5)
    # episódio -> id do filme na API (sem imagem, a TV fica sem sinal)
    ep_id = {1: 4, 2: 5, 3: 6, 4: 1, 5: 2, 6: 3}
    # (x, y, largura) de cada TV: fila de cima menor, de baixo maior, como uma pilha de loja
    lugares = {1: (70, 70, 300), 2: (490, 40, 300), 3: (910, 70, 300),
               4: (20, 360, 380), 5: (450, 330, 380), 6: (880, 360, 380)}
    for ep, (x, y, w) in lugares.items():
        h = int(w * .8)
        d.rounded_rectangle((x, y, x + w, y + h), 22, fill=(26, 28, 33))                 # gabinete
        d.rounded_rectangle((x + 6, y + 6, x + w - 6, y + h - 6), 18, outline=(46, 49, 56), width=3)
        sx, sy, sw, sh = x + 22, y + 20, int(w * .74), h - 40                            # tela 4:3 aprox.
        fid = ep_id[ep]
        if fid:
            cena = Image.open(OUT / "filmes" / f"{fid}.png").convert("RGB")
            r = sw / sh
            cw, ch = cena.size
            nw = int(ch * r)
            cena = cena.crop(((cw - nw) // 2, 0, (cw - nw) // 2 + nw, ch)).resize((sw, sh), Image.Resampling.LANCZOS)
        else:
            cena = Image.fromarray((rng.random((sh // 3, sw // 3)) * 200).astype("uint8")).resize((sw, sh), Image.Resampling.NEAREST).convert("RGB")
        a = np.asarray(cena).astype(float)
        a[1::3] *= .55                                                                    # linhas de varredura
        yy, xx = np.mgrid[0:sh, 0:sw]
        v = 1 - .55 * (((xx - sw / 2) / (sw / 2)) ** 2 + ((yy - sh / 2) / (sh / 2)) ** 2)
        a *= np.clip(v, .25, 1)[..., None]                                                # tela abaulada
        tela = Image.fromarray(np.clip(a, 0, 255).astype("uint8"))
        m = Image.new("L", (sw, sh), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, sw - 1, sh - 1), 26, fill=255)
        im.paste(tela, (sx, sy), m)
        # painel lateral com botões
        px = sx + sw + 12
        for k in range(3):
            d.ellipse((px, sy + 14 + k * 30, px + 18, sy + 32 + k * 30), fill=(52, 55, 62))
        d.rectangle((px, sy + sh - 50, px + w * .12, sy + sh - 10), fill=(18, 19, 23))
        d.ellipse((px + 4, sy + sh - 8, px + 10, sy + sh - 2), fill=(200, 40, 30))        # luz de ligado
    # brilho das telas no escuro
    brilho = im.filter(ImageFilter.GaussianBlur(28))
    a = np.asarray(im).astype(float) + np.asarray(brilho).astype(float) * .5
    im = Image.fromarray(np.clip(a, 0, 255).astype("uint8")).resize((640, 360), Image.Resampling.LANCZOS)
    psx(im, 40, 14).save(OUT / "capas" / "films.png", optimize=True)


def capas():
    (OUT / "capas").mkdir(exist_ok=True)
    # cenas dos filmes, com o mesmo tratamento da tela inicial
    import pillow_avif  # noqa: F401  (abre o .avif dos veículos)
    for recurso, arquivo in {"people": "personagens-background2.webp", "species": "espécies background.jpg",
                             "planets": "plenatas-background.webp", "vehicles": "veiculos-background-starwars.avif",
                             "starships": "estrela-da-morte-background.jpg"}.items():
        im = Image.open(REF / arquivo).convert("RGB")
        im = im.resize((640, round(640 * im.height / im.width)), Image.Resampling.LANCZOS)
        psx(ImageEnhance.Contrast(im).enhance(1.1), 40, 16).save(OUT / "capas" / f"{recurso}.png", optimize=True)
    tvs()  # filmes: parede de TVs, uma por episódio


capas()


def previa():
    """Imagens provisórias para ver o design com todos os cards preenchidos.
    Recortes das referências; o site só usa se PREVIA = true em assets/js/previa.js."""
    import shutil
    pasta = OUT / "previa"
    shutil.rmtree(pasta, ignore_errors=True)
    recortes = {"people": [], "species": [], "vehicles": [], "starships": []}
    for y in (0, .29, .58):                                   # rostos da colagem
        for x in [i * .11 for i in range(9)]:
            recortes["people"].append(("personagens-background.jpeg", (x, y, x + .12, y + .42)))
    for y in (0, .35, .65):
        for x in (0, .25, .5, .75):
            recortes["species"].append(("personagens-background.jpeg", (x, y, x + .25, y + .35)))
    recortes["species"] += [("espécies background.jpg", (.1, .1, .45, .95)), ("espécies background.jpg", (.4, 0, 1, .95))]
    recortes["vehicles"] = [("veiculos-background-starwars.avif", c) for c in
                            [(.6, .15, 1, .85), (.05, .4, .5, .9), (.45, .55, .62, .85), (.2, .2, .4, .45), (0, 0, 1, 1)]]
    recortes["vehicles"].append(("at-at.webp", (0, .1, 1, .7)))
    recortes["starships"] = [("estrela-da-morte-background.jpg", c) for c in
                             [(.25, 0, 1, .55), (0, .35, .32, .9), (.6, .5, 1, .95), (.4, .45, .5, .6), (0, 0, 1, 1)]]
    recortes["starships"] += [("millenniumfalconnave.webp", (0, .06, 1, .9)), ("refnavesstarwars.jpg", (0, 0, 1, 1))]
    import pillow_avif  # noqa: F401
    total = {}
    for recurso, lista in recortes.items():
        (pasta / recurso).mkdir(parents=True)
        tam = (132, 165) if recurso == "people" else (208, 117)
        for n, (arquivo, caixa) in enumerate(lista):
            corte(arquivo, caixa, tam, f"previa/{recurso}/{n}.png")
        total[recurso] = len(lista)
    (RAIZ / "assets" / "js" / "previa.js").write_text(
        "// Modo prévia: preenche cards sem imagem com recortes provisórios das referências.\n"
        "// Para desligar, troque para false (ou apague este arquivo e o import em interface.js).\n"
        "export const PREVIA = true;\n"
        f"export const previa = {json.dumps(total)};\n", encoding="utf-8")


previa()
