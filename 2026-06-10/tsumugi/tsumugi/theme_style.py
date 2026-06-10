"""テーマ解析 - テーマ文字列から映像モチーフ・配色・情景フレーズを導出する。

API キーが無い(シミュレーション)環境でも、与えられたテーマが
成果物の見た目・脚本の語彙に反映されるようにするための軽量解析。
キーワード辞書ベースなので「理解」ではないが、決定論的で説明可能。
実APIを接続した場合は、ここでの導出は実モデルの出力で上書きされる。
"""

from __future__ import annotations

# キーワード -> (モチーフ, パレット, 情景フレーズ)
# モチーフは player の絵柄選択に使う: rain / snow / particles / bokeh
_THEME_TABLE: list[tuple[tuple[str, ...], dict]] = [
    (
        ("雨", "rain", "梅雨", "豪雨"),
        {
            "motif": "rain",
            "palette": ["#4A6FA5", "#7B9EBF", "#2B3A55", "#9FB8D9"],
            "imagery": ["濡れた路面に光が滲む", "雨粒が窓を流れる", "傘の波が交差点を渡る", "雨上がりの匂いが立ちのぼる"],
        },
    ),
    (
        ("雪", "snow", "冬", "吹雪"),
        {
            "motif": "snow",
            "palette": ["#DCE7F0", "#A8C0D6", "#6E8CA8", "#F5F9FC"],
            "imagery": ["雪が音を吸い込んでいく", "白い吐息が宙に解ける", "街灯の光暈に雪が舞う", "足跡が新雪に刻まれる"],
        },
    ),
    (
        ("ネオン", "neon", "都市", "渋谷", "新宿", "夜の街", "シティ", "サイバー"),
        {
            "motif": "bokeh",
            "palette": ["#FF2E97", "#00E5FF", "#7C4DFF", "#1A1033"],
            "imagery": ["ネオンサインが瞬く", "ビルの谷間を光が流れる", "信号の色が路面に反射する", "雑踏のざわめきが遠ざかる"],
        },
    ),
    (
        ("海", "sea", "ocean", "波", "浜", "島"),
        {
            "motif": "bokeh",
            "palette": ["#0E7490", "#22D3EE", "#155E75", "#A5F3FC"],
            "imagery": ["波が砂浜を撫でる", "水平線が光をたたえる", "潮騒がリズムを刻む", "海風が髪を揺らす"],
        },
    ),
    (
        ("星", "star", "夜空", "宇宙", "銀河", "天体"),
        {
            "motif": "bokeh",
            "palette": ["#1E1B4B", "#818CF8", "#FBBF24", "#0F0A2E"],
            "imagery": ["星々が静かに瞬く", "天の川が空を横切る", "流星が一瞬の弧を描く", "夜の深さに吸い込まれる"],
        },
    ),
    (
        ("森", "forest", "緑", "山", "木漏れ日"),
        {
            "motif": "particles",
            "palette": ["#166534", "#4ADE80", "#365314", "#D9F99D"],
            "imagery": ["木漏れ日が揺れる", "葉擦れの音が満ちる", "苔の緑が深く沈む", "鳥の声が梢を渡る"],
        },
    ),
    (
        ("炎", "fire", "焚き火", "祭", "花火"),
        {
            "motif": "particles",
            "palette": ["#EA580C", "#FBBF24", "#7C2D12", "#FEF3C7"],
            "imagery": ["火の粉が夜に舞い上がる", "炎が顔を照らす", "熱気が頬を撫でる", "残り火が静かに燃える"],
        },
    ),
    (
        ("夕", "sunset", "黄昏", "夕焼け", "夕暮"),
        {
            "motif": "bokeh",
            "palette": ["#F97316", "#FCD34D", "#BE185D", "#7C2D12"],
            "imagery": ["空が茜色に染まる", "影が長く伸びる", "一日の終わりが滲む", "残光が建物の縁を縁取る"],
        },
    ),
    (
        ("夜明け", "dawn", "朝", "黎明", "日の出"),
        {
            "motif": "particles",
            "palette": ["#FDA4AF", "#FCD34D", "#93C5FD", "#FFF7ED"],
            "imagery": ["東の空が白み始める", "最初の光が街に差し込む", "空気が澄んで冷たい", "街がゆっくり目を覚ます"],
        },
    ),
    (
        ("桜", "sakura", "春", "花びら"),
        {
            "motif": "particles",
            "palette": ["#FBCFE8", "#F472B6", "#FDF2F8", "#9D174D"],
            "imagery": ["花びらが風に流れる", "薄紅が空を覆う", "春の光が柔らかい", "花吹雪が舞い散る"],
        },
    ),
]

_DEFAULT = {
    "motif": "particles",
    "palette": ["#C084FC", "#5EEAD4", "#FBBF24", "#1B1830"],
    "imagery": ["光が静かに揺れる", "時間がゆっくり流れる", "情景が移ろっていく", "余韻が残る"],
}


def analyze(theme: str) -> dict:
    """テーマ文字列を解析し、{motif, palette, imagery} を返す。

    複数のキーワードに合致した場合は最初に合致したものを主とし、
    情景フレーズは合致した全候補から集める。
    """
    matched: list[dict] = []
    for keywords, style in _THEME_TABLE:
        if any(k in theme for k in keywords):
            matched.append(style)
    if not matched:
        return dict(_DEFAULT)
    primary = matched[0]
    imagery: list[str] = []
    for style in matched:
        imagery.extend(style["imagery"])
    return {"motif": primary["motif"], "palette": list(primary["palette"]), "imagery": imagery}
