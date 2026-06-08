from pathlib import Path
from typing import Optional

import pandas as pd

from loader import carregar_todos, DATA_DIR, COLUNAS_RELEVANTES


# nome do arquivo de cache dentro da pasta data/
CACHE_NAME = "dataset.parquet"

# cache em memória para evitar leituras repetidas dentro do mesmo processo
_IN_MEMORY_CACHE: Optional[pd.DataFrame] = None


def _dbc_files() -> list[Path]:
    return sorted(Path(DATA_DIR).glob("MENTBR*.dbc"))


def _is_cache_stale(cache_path: Path) -> bool:
    """Retorna True se o cache não existir ou se algum .dbc for mais recente."""
    if not cache_path.exists():
        return True

    cache_mtime = cache_path.stat().st_mtime
    for f in _dbc_files():
        try:
            if f.stat().st_mtime > cache_mtime:
                return True
        except FileNotFoundError:
            # arquivo pode ter sido removido entre o glob e o stat
            return True

    return False


def get_dataset(force_reload: bool = False, cache_file: Optional[str] = None) -> pd.DataFrame:
    """Retorna o dataset pronto para uso pela dashboard.

    Estratégia para acelerar a inicialização da dashboard:
    - Mantém um cache em memória (_IN_MEMORY_CACHE) para chamadas repetidas na mesma sessão/processo.
    - Persiste um cache em disco em parquet (`data/dataset.parquet`).
    - Só reconstrói o dataset a partir dos arquivos `.dbc` se o cache estiver ausente
      ou se algum `.dbc` for mais recente que o cache em disco, a menos que `force_reload=True`.

    Parâmetros:
    - force_reload: força recarregar os .dbc mesmo que o cache exista.
    - cache_file: caminho customizado para o arquivo de cache (opcional).
    """
    global _IN_MEMORY_CACHE

    if _IN_MEMORY_CACHE is not None and not force_reload:
        print("[converter] usando cache em memória")
        return _IN_MEMORY_CACHE

    cache_path = Path(cache_file) if cache_file else Path(__file__).parent / "data" / CACHE_NAME

    should_reload = force_reload or _is_cache_stale(cache_path)

    if not should_reload:
        try:
            print(f"[converter] carregando dataset do cache em disco: {cache_path}")
            df = pd.read_parquet(cache_path)
            _IN_MEMORY_CACHE = df
            return df
        except Exception as e:
            print(f"[converter] falha ao ler cache ({e}), recarregando dos .dbc...")

    # carregar a partir dos .dbc e reconstruir o cache
    print("[converter] carregando raw .dbc e construindo cache...")
    df = carregar_todos(str(DATA_DIR))

    # escolher colunas relevantes para reduzir tamanho de cache
    cols_to_keep = [c for c in (["ANO"] + COLUNAS_RELEVANTES) if c in df.columns]
    df = df[cols_to_keep].copy()

    # salvar em parquet para leitura rápida posterior
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(cache_path, index=False, compression="snappy")
        print(f"[converter] cache salvo em: {cache_path}")
    except Exception as e:
        print(f"[converter] erro ao salvar cache em disco: {e}")

    _IN_MEMORY_CACHE = df
    return df


if __name__ == "__main__":
    # teste rápido
    df = get_dataset()
    print(df.head())
    print(df.dtypes)
