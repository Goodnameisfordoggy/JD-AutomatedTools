from __future__ import annotations
from typing import Iterable
import gradio as gr
from gradio.themes.base import Base
from gradio.themes.utils import colors, fonts, sizes


class PremiumBox(Base):
    def __init__(
        self,
        *,
        primary_hue: colors.Color | str = colors.pink,
        secondary_hue: colors.Color | str = colors.green,
        neutral_hue: colors.Color | str = colors.blue,
        spacing_size: sizes.Size | str = sizes.spacing_md,
        radius_size: sizes.Size | str = sizes.radius_md,
        text_size: sizes.Size | str = sizes.text_lg,
        font: fonts.Font
        | str
        | Iterable[fonts.Font | str] = (
            fonts.GoogleFont("Quicksand"),
            "ui-sans-serif",
            "sans-serif",
        ),
        font_mono: fonts.Font
        | str
        | Iterable[fonts.Font | str] = (
            fonts.GoogleFont("IBM Plex Mono"),
            "ui-monospace",
            "monospace",
        ),
    ):
        super().__init__(
            primary_hue=primary_hue,
            secondary_hue=secondary_hue,
            neutral_hue=neutral_hue,
            spacing_size=spacing_size,
            radius_size=radius_size,
            text_size=text_size,
            font=font,
            font_mono=font_mono,
        )
        super().set(
            body_background_fill="",
            body_background_fill_dark="",
            button_primary_background_fill="linear-gradient(45deg, *neutral_400 , *primary_300)",
            button_primary_background_fill_hover="linear-gradient(90deg, *primary_200, *neutral_300)",
            button_primary_text_color="white",
            button_primary_background_fill_dark="linear-gradient(45deg, *primary_600, *neutral_800)",
            slider_color="*neutral_400",
            slider_color_dark="*neutral_600",
            checkbox_border_color_selected="*secondary_800",

            block_title_text_weight="600",
            block_border_width="3px",
            block_shadow="*shadow_drop_lg",
            button_shadow="*shadow_drop_lg",
            button_large_padding="20px",
        )