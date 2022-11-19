import warnings
from itertools import cycle
from typing import Mapping, Iterable

import numpy as np
import pandas as pd
from legendkit import ColorArt, CatLegend, ListLegend, SizeLegend
from matplotlib.cm import ScalarMappable
from matplotlib.colors import ListedColormap, TwoSlopeNorm, Normalize, \
    is_color_like
from matplotlib.offsetbox import AnchoredText

from .base import RenderPlan
from ..layout import close_ticks
from ..utils import relative_luminance, get_colormap

ECHARTS16 = [
    "#5470c6", "#91cc75", "#fac858", "#ee6666",
    "#9a60b4", "#73c0de", "#3ba272", "#fc8452",
    "#27727b", "#ea7ccc", "#d7504b", "#e87c25",
    "#b5c334", "#fe8463", "#26c0c0", "#f4e001"
]

default_label_props = {
    "left": dict(loc="center right", bbox_to_anchor=(0, 0.5)),
    "right": dict(loc="center left", bbox_to_anchor=(1, 0.5)),
    "top": dict(loc="lower center", bbox_to_anchor=(0.5, 1),
                prop=dict(rotation=90)),
    "bottom": dict(loc="upper center", bbox_to_anchor=(0.5, 0),
                   prop=dict(rotation=90)),
}

default_label_loc = {
    "top": "right",
    "bottom": "right",
    "left": "bottom",
    "right": "bottom",
}


def _add_label(label, ax, side, label_loc=None, props=None):
    if side != "main":
        if label_loc is None:
            label_loc = default_label_loc[side]
        label_props = default_label_props[label_loc]
        loc = label_props["loc"]
        bbox_to_anchor = label_props['bbox_to_anchor']
        prop = label_props.get('prop')
        if props is not None:
            prop.update(props)

        title = AnchoredText(label, loc=loc,
                             bbox_to_anchor=bbox_to_anchor,
                             prop=prop, pad=0.3, borderpad=0,
                             bbox_transform=ax.transAxes, frameon=False)
        ax.add_artist(title)


def _mask_data(data, mask=None):
    if isinstance(data, pd.DataFrame):
        data = data.to_numpy()
    else:
        data = np.asarray(data)
    if mask is not None:
        data = np.ma.masked_where(np.asarray(mask), data)
    if data.ndim == 1:
        data = data.reshape(1, -1)
    return data


class _MeshBase(RenderPlan):
    norm = None
    cmap = None
    render_main = True
    label: str = ""
    label_loc = None
    props = None

    def _process_cmap(self, data, vmin, vmax,
                      cmap, norm, center):
        self.cmap = "coolwarm" if cmap is None else cmap
        self.norm = norm

        self.vmin = np.nanmin(data) if vmin is None else vmin
        self.vmax = np.nanmax(data) if vmax is None else vmax

        if norm is None:
            self.norm = Normalize(vmin=self.vmin, vmax=self.vmax)

        if center is not None:
            self.norm = TwoSlopeNorm(center, vmin=vmin, vmax=vmax)

    def create_render_data(self, *args):
        datasets = args
        if self.h:
            datasets = [d.T for d in datasets]
        if not self.is_deform:
            return datasets

        datasets = [self.deform_func(d) for d in datasets]
        if self.is_split:
            return [d for d in zip(*datasets)]
        else:
            return datasets

    def render(self, axes):
        render_data = self.get_render_data()
        if self.is_split:
            for hax, arr in zip(axes, render_data):
                self.render_ax(hax, arr)

            if self.label_loc in ["top", "left"]:
                label_ax = axes[0]
            else:
                label_ax = axes[-1]
        else:
            self.render_ax(axes, render_data)
            label_ax = axes
        _add_label(self.label, label_ax, self.side, self.label_loc, self.props)


class ColorMesh(_MeshBase):
    """Continuous Heatmap

    Parameters
    ----------
    data : np.ndarray, pd.DataFrame
        2D data
    cmap : str or :class:`matplotlib.colors.Colormap`
        The colormap used to map the value to the color
    norm : :class:`matplotlib.colors.Normalize`
        A Normalize instance to map data
    vmin, vmax : number, optional
        Value to determine the value mapping behavior
    center : number, optional
        The value to center on colormap, notice that this is different from
        seaborn; If set, a :class:`matplotlib.colors.TwoSlopeNorm` will be used
        to center the colormap.
    mask : array of bool
        Indicate which cell will be masked and not rendered
    alpha : float
    linewidth
    linecolor
    annot
    fmt
    annot_kws
    cbar_kws
    label
    label_loc
    props
    kwargs :

    Examples
    --------

    .. plot::

        >>> from heatgraphy.plotter import ColorMesh
        >>> _, ax = plt.subplots(figsize=(5, .5))
        >>> data = np.arange(10)
        >>> ColorMesh(data, cmap="Blues", label="ColorMesh").render(ax)

    .. plot::
        :context: close-figs

        >>> import heatgraphy as hg
        >>> from heatgraphy.plotter import ColorMesh
        >>> data = np.random.randn(10, 8)
        >>> h = hg.Heatmap(data, square=True)
        >>> h.split_row(cut=[5])
        >>> h.add_dendrogram("left")
        >>> cmap1, cmap2 = "Purples", "Greens"
        >>> colors1 = ColorMesh(np.arange(10)+1, cmap=cmap1, label=cmap1, annot=True)
        >>> colors2 = ColorMesh(np.arange(10)+1, cmap=cmap2, label=cmap2)
        >>> h.add_right(colors1, size=.2, pad=.05)
        >>> h.add_right(colors2, size=.2, pad=.05)
        >>> h.render()


    """

    def __init__(self, data, cmap=None, norm=None, vmin=None, vmax=None,
                 mask=None, center=None, alpha=None, linewidth=None,
                 linecolor=None, annot=None, fmt=None, annot_kws=None,
                 cbar_kws=None, label=None, label_loc=None, props=None,
                 **kwargs,
                 ):
        self.data = _mask_data(data, mask)
        self.alpha = alpha
        self.linewidth = linewidth
        self.linecolor = linecolor
        self.annotated_texts = self.data
        self.annot = False
        if annot is not None:
            if isinstance(annot, bool):
                self.annot = annot
            else:
                self.annot = True
                self.annotated_texts = annot
        self.fmt = "0" if fmt is None else fmt
        self.annot_kws = {} if annot_kws is None else annot_kws
        self._process_cmap(data, vmin, vmax, cmap, norm, center)

        if cbar_kws is None:
            cbar_kws = {}
        self._legend_kws = cbar_kws
        self.label = label
        self.label_loc = label_loc
        self.props = props
        self.kwargs = kwargs

    def _annotate_text(self, ax, mesh, texts):
        """Add textual labels with the value in each cell."""
        mesh.update_scalarmappable()
        height, width = texts.shape
        xpos, ypos = np.meshgrid(np.arange(width) + .5, np.arange(height) + .5)
        for x, y, m, color, val in zip(xpos.flat, ypos.flat,
                                       mesh.get_array(), mesh.get_facecolors(),
                                       texts.flat):
            if m is not np.ma.masked:
                lum = relative_luminance(color)
                text_color = ".15" if lum > .408 else "w"
                annotation = ("{:" + self.fmt + "}").format(val)
                text_kwargs = dict(color=text_color, ha="center", va="center")
                text_kwargs.update(self.annot_kws)
                ax.text(x, y, annotation, **text_kwargs)

    def get_render_data(self):
        return self.create_render_data(self.data, self.annotated_texts)

    def set_legends(self, **kwargs):
        self._legend_kws.update(kwargs)

    def get_legends(self):
        mappable = ScalarMappable(norm=self.norm, cmap=self.cmap)
        return ColorArt(mappable, **self._legend_kws)

    def render_ax(self, ax, data):
        values, texts = data
        mesh = ax.pcolormesh(values, cmap=self.cmap, norm=self.norm,
                             linewidth=self.linewidth,
                             edgecolor=self.linecolor,
                             **self.kwargs,)
        if self.annot:
            self._annotate_text(ax, mesh, texts)
        # set the mesh for legend

        ax.invert_yaxis()
        ax.set_axis_off()


# transform input data to numeric
def encode_numeric(arr, encoder):
    orig_shape = arr.shape
    if np.ma.isMaskedArray(arr):
        re_arr = []
        for e in arr.flatten():
            if e is np.ma.masked:
                re_arr.append(np.nan)
            else:
                re_arr.append(encoder[e])
        re_arr = np.ma.masked_invalid(re_arr)
    else:
        re_arr = [encoder[e] for e in arr.flatten()]
    re_arr = np.array(re_arr).reshape(orig_shape)
    return re_arr


def _enough_colors(n_colors, n_cats):
    # Inform the user if the same color
    # will be used more than once
    if n_colors < n_cats:
        warnings.warn(f"Current colormap has only {n_colors} colors "
                      f"which is less that your input "
                      f"with {n_cats} elements")


class Colors(_MeshBase):
    """Categorical colors/heatmap

    Parameters
    ----------
    data : np.ndarray
    label : str
    label_loc : {'top', 'bottom', 'left', 'right'}
    palette : dict, array-like
        Could be a mapping of label and colors or an array match
        the shape of data
    cmap:

    """
    render_main = True

    def __init__(self, data, palette=None, cmap=None, mask=None,
                 label=None, label_loc=None, props=None, **kwargs):

        self.label = label
        self.label_loc = label_loc
        self.props = props
        self.kwargs = kwargs

        encoder = {}
        render_colors = []
        # get unique color
        if palette is not None:
            if isinstance(palette, Mapping):
                self.palette = palette
            else:
                self.palette = dict(zip(data.flat, palette.flat))

            for i, (label, color) in enumerate(palette.items()):
                encoder[label] = i
                render_colors.append(color)

        else:
            if cmap is not None:
                cmap = get_colormap(cmap)
                colors = cmap(np.arange(cmap.N))
            else:
                colors = ECHARTS16

            cats = np.unique(data)
            _enough_colors(len(colors), len(cats))
            palette = {}
            encoder = {}
            render_colors = []
            for i, (label, color) in enumerate(zip(cats, cycle(colors))):
                encoder[label] = i
                render_colors.append(color)
                palette[label] = color
            self.palette = palette

        self.render_cmap = ListedColormap(render_colors)
        self.vmax = len(render_colors)
        # Encode data into cmap range
        encode_data = encode_numeric(data, encoder)
        self.data = _mask_data(encode_data, mask=mask)
        # If the data is numeric, we don't change it
        if np.issubdtype(data.dtype, np.number):
            self.cluster_data = data
        else:
            self.cluster_data = encode_data

    def get_legends(self):
        colors = []
        labels = []
        for label, color in self.palette.items():
            labels.append(label)
            colors.append(color)
        return CatLegend(colors=colors, labels=labels, size=1,
                         title=self.label)

    def get_render_data(self):
        data = self.data
        if self.h:
            data = self.data.T

        if not self.is_deform:
            return data

        return self.deform_func(data)

    def render_ax(self, ax, data):
        ax.pcolormesh(data, cmap=self.render_cmap,
                      vmin=0, vmax=self.vmax, **self.kwargs)
        ax.set_axis_off()
        ax.invert_yaxis()


class SizedMesh(_MeshBase):
    """Mesh for sized elements

    .. note::
        If encode color as categorical data, `palette` must be used
        to assign color for each category.

    Parameters
    ----------
    size : 2d array
        Control the radius of circles, must be numeric
    color: color-like or 2d array
        The color of circles, could be numeric / categorical matrix
        If using one color name, all circles will have the same color.

    """

    def __init__(self, size, color=None, cmap=None, norm=None,
                 vmin=None, vmax=None, alpha=None,
                 center=None, sizes=(1, 200), size_norm=None,
                 edgecolor=None, linewidth=1,
                 frameon=True, palette=None, marker="o",
                 label=None, label_loc=None, props=None, **kwargs):
        # normalize size
        size = np.asarray(size)
        if size_norm is None:
            size_norm = Normalize()
            size_norm.autoscale(size)
        self.orig_size = size
        self.size = size_norm(size) * (sizes[1] - sizes[0]) + sizes[0]
        self.color = None
        self.color2d = None
        self.palette = palette
        self.marker = marker
        # process color
        # By default, the circles colors are uniform
        if color is None:
            color = "C0"
        if color is not None:
            if is_color_like(color):
                self.color = color
                self.color2d = np.repeat(color, size.size).reshape(size.shape)
            else:
                color = np.asarray(color)
                # categorical circle color
                if palette is not None:
                    encoder = {}
                    render_colors = []
                    for i, (label, c) in enumerate(palette.items()):
                        encoder[label] = i
                        render_colors.append(c)
                    self.cmap = ListedColormap(render_colors)
                    self.color2d = encode_numeric(color, encoder)
                else:
                    self._process_cmap(color, vmin, vmax, cmap,
                                       norm, center)
                    self.color2d = color
        self.alpha = alpha
        self.frameon = frameon
        self.edgecolor = edgecolor
        self.linewidth = linewidth
        self.label = label
        self.label_loc = label_loc
        self.props = props
        self.kwargs = kwargs

        self._collections = None

    def get_legends(self):
        if self.color is not None:
            size_color = self.color
        else:
            size_color = "black"
        handler_kw = dict(edgecolor=self.edgecolor,
                          linewidth=self.linewidth)
        size_legend = SizeLegend(self.size,
                                 array=self.orig_size,
                                 colors=size_color,
                                 dtype=self.orig_size.dtype,
                                 handler_kw=handler_kw,
                                 )

        if self.color2d is not None:
            if self.palette is not None:
                labels, colors = [], []
                for label, c in self.palette.items():
                    labels.append(label)
                    colors.append(c)
                color_legend = CatLegend(labels=labels, colors=colors,
                                         size="large",
                                         handle=self.marker,
                                         handle_kw=handler_kw,
                                         frameon=False,
                                         )
            else:
                mappable = ScalarMappable(norm=self.norm, cmap=self.cmap)
                color_legend = ColorArt(self._collections)
            return [size_legend, color_legend]
        else:
            return size_legend

    def get_render_data(self):
        return self.create_render_data(self.size, self.color2d)

    def render_ax(self, ax, data):
        size, color = data
        Y, X = size.shape
        xticks = np.arange(X) + 0.5
        yticks = np.arange(Y) + 0.5
        xv, yv = np.meshgrid(xticks, yticks)

        options = dict(s=size,  edgecolor=self.edgecolor,
                       linewidths=self.linewidth, marker=self.marker)

        if self.color is not None:
            options['c'] = self.color
        else:
            options.update(dict(c=color, norm=self.norm, cmap=self.cmap))
        self._collections = ax.scatter(xv, yv, **options, **self.kwargs)

        close_ticks(ax)
        if not self.frameon:
            ax.set_axis_off()
        ax.set_xlim(0, xticks[-1] + 0.5)
        ax.set_ylim(0, yticks[-1] + 0.5)
        ax.invert_yaxis()


class MarkerMesh(_MeshBase):
    render_main = True

    def __init__(self, data, color="black", marker="*",
                 label=None, label_loc=None, props=None, **kwargs):
        self.data = data
        self.color = color
        self.marker = marker
        self.label = label
        self.label_loc = label_loc
        self.props = props
        self.kwargs = kwargs

    def get_legends(self):
        return CatLegend(colors=[self.color], labels=[self.label],
                         handle=self.marker)

    def render_ax(self, ax, data):
        Y, X = data.shape
        xticks = np.arange(X) + 0.5
        yticks = np.arange(Y) + 0.5
        xv, yv = np.where(data)

        ax.scatter(xv + .5, yv + .5, s=50,
                   c=self.color, marker=self.marker, **self.kwargs)

        close_ticks(ax)
        ax.set_xlim(0, xticks[-1] + 0.5)
        ax.set_ylim(0, yticks[-1] + 0.5)
        ax.invert_yaxis()


# TODO: Maybe a text mesh
class TextMesh(_MeshBase):
    render_main = True


class LayersMesh(_MeshBase):
    render_main = True

    def __init__(self,
                 data=None,
                 layers=None,
                 pieces=None,
                 shrink=(.9, .9),
                 label=None, label_loc=None, props=None,
                 ):
        # render one layer
        # with different elements
        if data is not None:
            self.data = data
            if not isinstance(pieces, Mapping):
                msg = f"Expect pieces to be dict " \
                      f"but found {type(pieces)} instead."
                raise TypeError(msg)
            self.pieces_mapper = pieces
            self.mode = "cell"
        # render multiple layers
        # each layer is an elements
        else:
            self.data = layers
            if not isinstance(pieces, Iterable):
                msg = f"Expect pieces to be list " \
                      f"but found {type(pieces)} instead."
                raise TypeError(msg)
            self.pieces = pieces
            self.mode = "layer"
        self.x_offset = (1 - shrink[0]) / 2
        self.y_offset = (1 - shrink[1]) / 2
        self.width = shrink[0]
        self.height = shrink[1]
        self.label = label
        self.label_loc = label_loc
        self.props = props

    def get_render_data(self):
        data = self.data
        if self.h:
            data = self.data.T

        if not self.is_deform:
            return data

        if self.mode == "cell":
            return self.deform_func(data)
        else:
            trans_layers = [
                self.deform_func(layer) for layer in self.data]
            if self.is_split:
                return [chunk for chunk in zip(*trans_layers)]
            else:
                return trans_layers

    def get_legends(self):
        if self.mode == "cell":
            handles = list(self.pieces_mapper.values())
        else:
            handles = self.pieces
        labels = [h.get_label() for h in handles]
        handler_map = {h: h for h in handles}
        return ListLegend(handles=handles, labels=labels,
                          handler_map=handler_map)

    def render_ax(self, ax, data):
        if self.mode == "layer":
            Y, X = data[0].shape
        else:
            Y, X = data.shape
        ax.set_axis_off()
        ax.set_xlim(0, X)
        ax.set_ylim(0, Y)
        if self.mode == "layer":
            for layer, piece in zip(data, self.pieces):
                for iy, row in enumerate(layer):
                    for ix, v in enumerate(row):
                        if v:
                            art = piece.draw(ix + self.x_offset,
                                             iy + self.y_offset,
                                             self.width, self.height)
                            ax.add_artist(art)
        else:
            for iy, row in enumerate(data):
                for ix, v in enumerate(row):
                    piece = self.pieces_mapper[v]
                    art = piece.draw(ix + self.x_offset, iy + self.y_offset,
                                     self.width, self.height)
                    ax.add_artist(art)
