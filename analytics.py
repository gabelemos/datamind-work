from __future__ import annotations

import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

AGE_BINS = [0, 18, 30, 45, 60, 120]
AGE_LABELS = ["0-17", "18-29", "30-44", "45-59", "60+"]
DEFAULT_RANK_SIZE = 10


def _ensure_year_column(df: pd.DataFrame) -> pd.DataFrame:
    if "ANO" not in df.columns and "NU_ANO" in df.columns:
        df = df.copy()
        df["ANO"] = pd.to_numeric(df["NU_ANO"], errors="coerce").astype("Int64")
    return df


def _parse_dates(df: pd.DataFrame, date_column: str = "DT_NOTIFIC") -> pd.DataFrame:
    if date_column not in df.columns:
        return df

    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column], errors="coerce", dayfirst=True)
    return df


def aggregate_counts(
    df: pd.DataFrame,
    group_by: Union[str, Sequence[str]],
    normalize: bool = False,
) -> pd.DataFrame:
    """Agrega contagens por uma ou mais colunas."""
    if isinstance(group_by, str):
        group_by = [group_by]

    result = df.groupby(group_by).size().reset_index(name="count")
    if normalize:
        result["share"] = result["count"] / result["count"].sum()

    return result.sort_values("count", ascending=False).reset_index(drop=True)


def rank_top(
    df: pd.DataFrame,
    group_by: str,
    n: int = DEFAULT_RANK_SIZE,
) -> pd.DataFrame:
    """Retorna o ranking dos principais valores para uma coluna."""
    ranking = aggregate_counts(df, group_by)
    return ranking.head(n).reset_index(drop=True)


def compare_year_ranges(
    df: pd.DataFrame,
    baseline_years: Union[Sequence[int], Tuple[int, int]] = (2017, 2019),
    target_years: Union[Sequence[int], Tuple[int, int]] = (2020, 2024),
    group_by: Optional[str] = None,
) -> pd.DataFrame:
    """Compara dois períodos e calcula variações absolutas e percentuais."""
    df = _ensure_year_column(df)
    year_col = "ANO"

    if isinstance(baseline_years, (list, tuple)) and len(baseline_years) == 2:
        baseline_mask = df[year_col].between(baseline_years[0], baseline_years[1])
        baseline_name = f"{baseline_years[0]}-{baseline_years[1]}"
    else:
        baseline_mask = df[year_col] == int(baseline_years)
        baseline_name = str(baseline_years)

    if isinstance(target_years, (list, tuple)) and len(target_years) == 2:
        target_mask = df[year_col].between(target_years[0], target_years[1])
        target_name = f"{target_years[0]}-{target_years[1]}"
    else:
        target_mask = df[year_col] == int(target_years)
        target_name = str(target_years)

    baseline_df = df[baseline_mask]
    target_df = df[target_mask]

    if group_by is None:
        baseline_count = len(baseline_df)
        target_count = len(target_df)
        change = target_count - baseline_count
        pct_change = (change / baseline_count * 100) if baseline_count else np.nan
        return pd.DataFrame(
            [
                {
                    "metric": "total_registros",
                    f"count_{baseline_name}": baseline_count,
                    f"count_{target_name}": target_count,
                    "change": change,
                    "pct_change": pct_change,
                }
            ]
        )

    baseline_count = aggregate_counts(baseline_df, group_by).rename(columns={"count": f"count_{baseline_name}"})
    target_count = aggregate_counts(target_df, group_by).rename(columns={"count": f"count_{target_name}"})

    merged = baseline_count.merge(target_count, on=group_by, how="outer").fillna(0)
    merged["change"] = merged[f"count_{target_name}"] - merged[f"count_{baseline_name}"]
    merged["pct_change"] = np.where(
        merged[f"count_{baseline_name}"] == 0,
        np.nan,
        merged["change"] / merged[f"count_{baseline_name}"] * 100,
    )
    return merged.sort_values("change", ascending=False).reset_index(drop=True)


def compute_trend(
    df: pd.DataFrame,
    date_col: str = "DT_NOTIFIC",
    freq: str = "YS",
    group_by: Optional[str] = None,
) -> pd.DataFrame:
    """Calcula séries temporais mensais ou anuais de casos."""
    df = _parse_dates(df, date_col)
    if date_col not in df.columns or df[date_col].isna().all():
        raise ValueError(f"Coluna de data inválida ou ausente: {date_col}")

    grouped = df.groupby(
        [pd.Grouper(key=date_col, freq=freq)] + ([group_by] if group_by else [])
    ).size().reset_index(name="count")

    if group_by:
        trend = grouped.pivot(index=date_col, columns=group_by, values="count").fillna(0)
        trend.columns.name = None
        return trend.reset_index()

    return grouped.sort_values(date_col).reset_index(drop=True)


def age_distribution(df: pd.DataFrame, bins: List[int] = AGE_BINS, labels: List[str] = AGE_LABELS) -> pd.DataFrame:
    """Agrupa casos em faixas etárias."""
    if "NU_IDADE_N" not in df.columns:
        return pd.DataFrame(columns=["age_range", "count"])

    ages = pd.to_numeric(df["NU_IDADE_N"], errors="coerce")
    distribution = pd.cut(ages, bins=bins, labels=labels, right=False)
    result = distribution.value_counts().sort_index().reset_index()
    result.columns = ["age_range", "count"]
    return result


def build_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Constrói KPIs e resultados analíticos a partir do DataFrame."""
    if df is None or df.empty:
        return {}

    df = _ensure_year_column(df)
    df = _parse_dates(df, "DT_NOTIFIC")

    total_registros = len(df)
    anos_disponiveis = sorted(df["ANO"].dropna().astype(int).unique().tolist())

    agrupamentos = {
        "casos_por_ano": aggregate_counts(df, "ANO"),
        "casos_por_estado": aggregate_counts(df, "SG_UF_NOT"),
        "casos_por_sexo": aggregate_counts(df, "CS_SEXO"),
        "casos_por_raca": aggregate_counts(df, "CS_RACA"),
        "casos_por_escolaridade": aggregate_counts(df, "CS_ESCOL_N"),
        "casos_por_evolucao": aggregate_counts(df, "EVOLUCAO"),
        "casos_por_faixa_idade": age_distribution(df),
    }

    rankings = {
        "top_estados": rank_top(df, "SG_UF_NOT"),
        "top_sexos": rank_top(df, "CS_SEXO"),
        "top_racas": rank_top(df, "CS_RACA"),
        "top_escolaridades": rank_top(df, "CS_ESCOL_N"),
        "top_evolucoes": rank_top(df, "EVOLUCAO"),
    }

    comparisons = {
        "before_after_pandemic": compare_year_ranges(df, (2017, 2019), (2020, 2024)),
        "sexo_before_after": compare_year_ranges(df, (2017, 2019), (2020, 2024), group_by="CS_SEXO"),
        "estado_before_after": compare_year_ranges(df, (2017, 2019), (2020, 2024), group_by="SG_UF_NOT"),
    }

    trends = {
        "trend_anual": compute_trend(df, date_col="DT_NOTIFIC", freq="YS"),
        "trend_mensal": compute_trend(df, date_col="DT_NOTIFIC", freq="MS"),
        "trend_por_sexo": compute_trend(df, date_col="DT_NOTIFIC", freq="YS", group_by="CS_SEXO"),
    }

    idade_valida = pd.to_numeric(df["NU_IDADE_N"], errors="coerce")
    idade_count = idade_valida.count()
    idade_media = float(idade_valida.mean()) if idade_count else np.nan
    idade_mediana = float(idade_valida.median()) if idade_count else np.nan

    kpis = {
        "total_registros": total_registros,
        "anos_disponiveis": anos_disponiveis,
        "media_idade": idade_media,
        "mediana_idade": idade_mediana,
        "top_estado": rankings["top_estados"].iloc[0].to_dict() if not rankings["top_estados"].empty else {},
        "top_sexo": rankings["top_sexos"].iloc[0].to_dict() if not rankings["top_sexos"].empty else {},
        "top_evolucao": rankings["top_evolucoes"].iloc[0].to_dict() if not rankings["top_evolucoes"].empty else {},
    }

    return {
        "kpis": kpis,
        "aggregations": agrupamentos,
        "rankings": rankings,
        "comparisons": comparisons,
        "trends": trends,
    }


if __name__ == "__main__":
    print("analytics.py não deve ser executado diretamente. Use build_kpis(df) em outra camada.")
