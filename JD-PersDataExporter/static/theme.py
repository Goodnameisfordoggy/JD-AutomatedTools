from __future__ import annotations
from typing import Iterable
import gradio as gr
from gradio.themes.base import Base
from gradio.themes.utils import colors, fonts, sizes


class PremiumBox(Base):
    """ light模式主题"""
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
            button_large_padding="20px",
        )

class GorgeousBlack(Base):
    def __init__(
        self,
        *,
        primary_hue: colors.Color | str = colors.stone,
        secondary_hue: colors.Color | str = colors.gray,
        neutral_hue: colors.Color | str = colors.zinc,
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
            fonts.GoogleFont("Source Sans Pr"),
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
            background_fill_primary='white',
            shadow_drop='rgba(0,0,0,0.05) 0px 1px 2px 0px',
            shadow_drop_lg='0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
            shadow_spread='3px',
            block_background_fill='*background_fill_primary',
            block_border_width='1px',
            block_border_width_dark='1px',
            block_label_background_fill='*background_fill_primary',
            block_label_background_fill_dark='*background_fill_secondary',
            block_label_text_color='*neutral_500',
            block_label_text_color_dark='*neutral_200',
            block_label_margin='0',
            block_label_padding='*spacing_sm *spacing_lg',
            block_label_radius='calc(*radius_lg - 1px) 0 calc(*radius_lg - 1px) 0',
            block_label_text_size='*text_sm',
            block_label_text_weight='400',
            block_title_background_fill='none',
            block_title_background_fill_dark='none',
            block_title_text_color='*neutral_500',
            block_title_text_color_dark='*neutral_200',
            block_title_padding='0',
            block_title_radius='none',
            block_title_text_weight='400',
            panel_border_width='0',
            panel_border_width_dark='0',
            checkbox_background_color_selected='*secondary_600',
            checkbox_background_color_selected_dark='*secondary_600',
            checkbox_border_color='*neutral_300',
            checkbox_border_color_dark='*neutral_700',
            checkbox_border_color_focus='*secondary_500',
            checkbox_border_color_focus_dark='*secondary_500',
            checkbox_border_color_selected='*secondary_600',
            checkbox_border_color_selected_dark='*secondary_600',
            checkbox_border_width='*input_border_width',
            checkbox_shadow='*input_shadow',
            checkbox_label_background_fill_selected='*checkbox_label_background_fill',
            checkbox_label_background_fill_selected_dark='*checkbox_label_background_fill',
            checkbox_label_shadow='none',
            checkbox_label_text_color_selected='*checkbox_label_text_color',
            input_background_fill='*neutral_100',
            input_border_color='*border_color_primary',
            input_shadow='none',
            input_shadow_dark='none',
            input_shadow_focus='*input_shadow',
            input_shadow_focus_dark='*input_shadow',
            slider_color='#2563eb',
            slider_color_dark='*neutral_950',
            button_shadow='*shadow_drop_lg',
            button_shadow_active='*shadow_drop_lg',
            button_shadow_hover='*shadow_drop_lg',
            button_primary_background_fill='*primary_200',
            button_primary_background_fill_hover='*button_primary_background_fill',
            button_primary_background_fill_dark="linear-gradient(60deg, #333333 , #CCCCCC)",
            button_primary_background_fill_hover_dark='linear-gradient(90deg, #CCCCCC, #333333)',
            button_primary_text_color='*primary_600',
            button_secondary_background_fill='*neutral_200',
            button_secondary_background_fill_hover='*button_secondary_background_fill',
            button_secondary_background_fill_hover_dark='*button_secondary_background_fill',
            button_secondary_text_color='*neutral_700',
            button_cancel_background_fill_hover='*button_cancel_background_fill',
            button_cancel_background_fill_hover_dark='*button_cancel_background_fill',
            table_even_background_fill_dark='#232323'
        )
