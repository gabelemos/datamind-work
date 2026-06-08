import glob          # buscar arquivos por padrão (ex: *.dbc)
import tempfile      # criar arquivos temporários para conversão
from pathlib import Path  # manipular caminhos de forma multiplataforma
import pandas as pd       # manipulação de dados em DataFrame
from pyreaddbc import dbc2dbf  # converte .dbc do DataSUS para .dbf
from dbfread import DBF        # leitura de arquivos .dbf

# caminho padrão da pasta de dados
DATA_DIR = Path(__file__).parent / "data"

# colunas relevantes do SINAN MENTBR
COLUNAS_RELEVANTES = [
    "NU_ANO",       # ano de notificação
    "SG_UF_NOT",    # UF de notificação
    "CS_SEXO",      # sexo do paciente
    "NU_IDADE_N",   # idade
    "CS_RACA",      # raça/cor
    "CS_ESCOL_N",   # escolaridade
    "ID_OCUPA_N",   # ocupação
    "DT_NOTIFIC",   # data de notificação
    "EVOLUCAO",     # evolução do caso
]


def _extrair_ano(caminho: str) -> int:
    # pega o número do nome do arquivo (ex: MENTBR17 -> 2017)
    sufixo = Path(caminho).stem.replace("MENTBR", "")
    return 2000 + int(sufixo)


def carregar_dbc(caminho: str) -> pd.DataFrame:
    # converte .dbc para .dbf em arquivo temporário
    with tempfile.NamedTemporaryFile(suffix=".dbf", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        # dbc2dbf descomprime o arquivo do DataSUS
        dbc2dbf(caminho, tmp_path)

        # lê o .dbf gerado com encoding padrão do governo brasileiro
        tabela = DBF(tmp_path, encoding="iso-8859-1", load=True)
        df = pd.DataFrame(iter(tabela))
    except Exception as e:
        raise RuntimeError(f"Erro ao ler {caminho}: {e}")
    finally:
        # remove o arquivo temporário
        Path(tmp_path).unlink(missing_ok=True)

    # valida se o arquivo retornou dados
    if df is None or df.empty:
        raise ValueError(f"Arquivo vazio ou inválido: {caminho}")

    # adiciona coluna de ano baseada no nome do arquivo
    df["ANO"] = _extrair_ano(caminho)

    return df


def validar_schema(df: pd.DataFrame, caminho: str) -> pd.DataFrame:
    # verifica quais colunas esperadas estão faltando
    ausentes = [c for c in COLUNAS_RELEVANTES if c not in df.columns]

    # o layout do DataSUS muda entre anos, então adiciona as ausentes como NaN
    if ausentes:
        print(f"[AVISO] {Path(caminho).name}: colunas ausentes -> {ausentes}")
        for col in ausentes:
            df[col] = None

    return df


def tratar_erros(df: pd.DataFrame) -> pd.DataFrame:
    # remove linhas completamente vazias
    df = df.dropna(how="all")

    # converte idade para número
    if "NU_IDADE_N" in df.columns:
        df["NU_IDADE_N"] = pd.to_numeric(df["NU_IDADE_N"], errors="coerce")

    # padroniza sexo para M, F ou I (ignorado/inválido)
    if "CS_SEXO" in df.columns:
        df["CS_SEXO"] = df["CS_SEXO"].astype(str).str.strip().str.upper()
        df.loc[~df["CS_SEXO"].isin(["M", "F"]), "ID_SEXO"] = "I"

    return df


def carregar_todos(data_dir: str = None) -> pd.DataFrame:
    # define a pasta de dados
    pasta = Path(data_dir) if data_dir else DATA_DIR

    # busca todos os arquivos .dbc da pasta
    arquivos = sorted(glob.glob(str(pasta / "MENTBR*.dbc")))

    if not arquivos:
        raise FileNotFoundError(f"Nenhum .dbc encontrado em: {pasta}")

    frames = []

    # carrega, valida e trata cada arquivo
    for arquivo in arquivos:
        print(f"Carregando {Path(arquivo).name}...")
        try:
            df = carregar_dbc(arquivo)
            df = validar_schema(df, arquivo)
            df = tratar_erros(df)
            frames.append(df)
            print(f"  -> {len(df)} registros.")
        except Exception as e:
            print(f"  [ERRO] {Path(arquivo).name}: {e}")

    if not frames:
        raise RuntimeError("Nenhum arquivo carregado com sucesso.")

    # junta todos os anos em um único DataFrame
    consolidado = pd.concat(frames, ignore_index=True)
    print(f"\nTotal: {len(consolidado)} registros de {len(frames)} arquivo(s).")

    return consolidado


if __name__ == "__main__":
    # teste direto: carrega tudo e mostra as primeiras linhas
    df = carregar_todos()
    print(df.head())
    print(df.dtypes)
